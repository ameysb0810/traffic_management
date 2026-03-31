import json
from datetime import datetime
from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Avg, Count, Q, Sum
from django.http import JsonResponse, HttpResponseForbidden, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import TemplateView, ListView, DetailView, UpdateView, CreateView
from .forms import IncidentForm, SignalControlForm, SignupForm
from .models import Intersection, TrafficSignal, VehicleCount, Incident, Alert
from .simulation import run_simulation_tick, seed_demo_data
from .utils import generate_traffic_summary, get_congestion_score


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'core/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()
        active_alerts = Alert.objects.filter(
            is_active=True,
        ).filter(Q(expires_at__gt=now) | Q(expires_at__isnull=True)).order_by('-created_at')
        critical_incidents = Incident.objects.filter(is_resolved=False, severity='CRITICAL')
        recent_counts = VehicleCount.objects.select_related('intersection', 'signal')[:10]
        congestion_counts = VehicleCount.objects.values('congestion_level').annotate(count=Count('id'))
        congestion_summary = {item['congestion_level']: item['count'] for item in congestion_counts}
        context.update({
            'total_intersections': Intersection.objects.count(),
            'active_signals': TrafficSignal.objects.filter(is_operational=True).count(),
            'critical_incidents': critical_incidents.count(),
            'active_alerts': active_alerts,
            'recent_counts': recent_counts,
            'congestion_summary': congestion_summary,
        })
        return context


class IntersectionListView(LoginRequiredMixin, ListView):
    model = Intersection
    template_name = 'core/dashboard.html'
    context_object_name = 'intersections'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        counts = {
            intersection.id: intersection.signals.count()
            for intersection in context['intersections']
        }
        context['signal_counts'] = counts
        return context


class IntersectionDetailView(LoginRequiredMixin, DetailView):
    model = Intersection
    template_name = 'core/intersection_detail.html'
    context_object_name = 'intersection'

    def get_context_data(self, **kwargs):
        intersection = self.object
        context = super().get_context_data(**kwargs)
        context['signals'] = intersection.signals.all()
        context['recent_counts'] = VehicleCount.objects.filter(intersection=intersection).select_related('signal')[:20]
        context['incidents'] = intersection.incidents.filter(is_resolved=False).order_by('-reported_at')
        context['summary'] = generate_traffic_summary(intersection)
        return context


class SignalControlView(LoginRequiredMixin, UpdateView):
    model = TrafficSignal
    form_class = SignalControlForm
    template_name = 'core/signal_control.html'
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Signal configuration updated successfully.')
        return response


class IncidentCreateView(LoginRequiredMixin, CreateView):
    model = Incident
    form_class = IncidentForm
    template_name = 'core/incidents.html'
    success_url = reverse_lazy('incidents')

    def form_valid(self, form):
        form.instance.reported_by = self.request.user
        messages.success(self.request, 'Incident reported successfully.')
        return super().form_valid(form)


class IncidentListView(LoginRequiredMixin, ListView):
    model = Incident
    template_name = 'core/incidents.html'
    context_object_name = 'incidents'

    def get_queryset(self):
        return Incident.objects.filter(is_resolved=False).order_by('-severity', 'reported_at')


@login_required
def resolve_incident(request, pk):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    incident = get_object_or_404(Incident, pk=pk)
    incident.is_resolved = True
    incident.resolved_at = timezone.now()
    incident.save(update_fields=['is_resolved', 'resolved_at'])
    messages.success(request, 'Incident resolved successfully.')
    return redirect('incidents')


class AnalyticsView(LoginRequiredMixin, TemplateView):
    template_name = 'core/analytics.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        intersections = Intersection.objects.all()
        selected_id = self.request.GET.get('intersection_id')
        selected = intersections.first()
        if selected_id:
            selected = intersections.filter(id=selected_id).first() or selected
        hourly = VehicleCount.objects.filter(intersection=selected).extra(
            select={'hour': "strftime('%H', timestamp)"}
        ).values('hour').annotate(avg_count=Avg('count'), avg_speed=Avg('average_speed')).order_by('hour')
        hourly_data = [
            {'hour': int(entry['hour']), 'avg_count': round(entry['avg_count'] or 0, 1), 'avg_speed': round(entry['avg_speed'] or 0, 1)}
            for entry in hourly
        ]
        vehicle_type_distribution = VehicleCount.objects.filter(intersection=selected).values('vehicle_type').annotate(total=Sum('count')).order_by('-total')
        type_labels = [entry['vehicle_type'] for entry in vehicle_type_distribution]
        type_values = [entry['total'] for entry in vehicle_type_distribution]
        today = timezone.now().date()
        heatmap_rows = []
        for intersection in intersections:
            hourly_scores = []
            for hour in range(24):
                average_count = VehicleCount.objects.filter(
                    intersection=intersection,
                    timestamp__date=today,
                    timestamp__hour=hour,
                ).aggregate(avg=Avg('count'))['avg'] or 0
                intensity = min(max(average_count / 100, 0.08), 0.85)
                hourly_scores.append({'value': int(average_count), 'opacity': round(intensity, 2)})
            heatmap_rows.append({'intersection': intersection.name, 'scores': hourly_scores})
        peak_hours = sorted(hourly_data, key=lambda item: item['avg_count'], reverse=True)[:3]
        context.update({
            'intersections': intersections,
            'selected_intersection': selected,
            'hourly_data_json': json.dumps(hourly_data),
            'type_labels': json.dumps(type_labels),
            'type_values': json.dumps(type_values),
            'hour_range': list(range(24)),
            'heatmap_rows': heatmap_rows,
            'peak_hours': peak_hours,
        })
        return context


class AlertListView(LoginRequiredMixin, ListView):
    model = Alert
    template_name = 'core/alerts.html'
    context_object_name = 'alerts'

    def get_queryset(self):
        now = timezone.now()
        return Alert.objects.filter(is_active=True).filter(Q(expires_at__gt=now) | Q(expires_at__isnull=True)).order_by('-created_at')


class SignupView(View):
    template_name = 'registration/signup.html'

    def get(self, request, *args, **kwargs):
        form = SignupForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            messages.success(request, 'Account created successfully. You are now logged in.')
            return redirect('dashboard')
        return render(request, self.template_name, {'form': form})


class RunSimulationView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return HttpResponseForbidden('Staff access required')
        records_created = run_simulation_tick()
        return JsonResponse({'records_created': records_created})


class SeedDataView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return HttpResponseForbidden('Staff access required')
        count = seed_demo_data()
        messages.success(request, f'Seeded demo data for {count} intersections.')
        return redirect('dashboard')


def handler404(request, exception):
    return render(request, 'core/error.html', {'title': 'Page not found', 'message': 'The requested page could not be found.'}, status=404)


def handler500(request):
    return render(request, 'core/error.html', {'title': 'Server error', 'message': 'An unexpected error occurred on the server.'}, status=500)
