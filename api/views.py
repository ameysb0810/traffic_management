from django.utils import timezone
from django.db.models import Avg, Sum
from rest_framework import generics, permissions, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from core.models import Intersection, TrafficSignal, VehicleCount, Incident, Alert
from .serializers import (
    IntersectionSerializer,
    TrafficSignalSerializer,
    VehicleCountSerializer,
    IncidentSerializer,
    AlertSerializer,
)


class IntersectionViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Intersection.objects.all()
    serializer_class = IntersectionSerializer


class TrafficSignalListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TrafficSignalSerializer

    def get_queryset(self):
        queryset = TrafficSignal.objects.all()
        intersection_id = self.request.query_params.get('intersection_id')
        if intersection_id:
            queryset = queryset.filter(intersection_id=intersection_id)
        return queryset


class VehicleCountListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = VehicleCountSerializer

    def get_queryset(self):
        queryset = VehicleCount.objects.select_related('intersection', 'signal').order_by('-timestamp')[:50]
        intersection_id = self.request.query_params.get('intersection_id')
        level = self.request.query_params.get('level')
        if intersection_id:
            queryset = queryset.filter(intersection_id=intersection_id)
        if level:
            queryset = queryset.filter(congestion_level=level.upper())
        return queryset


class IncidentListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = IncidentSerializer

    def get_queryset(self):
        return Incident.objects.filter(is_resolved=False).order_by('-reported_at')

    def perform_create(self, serializer):
        serializer.save()


class AlertListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Alert.objects.filter(is_active=True).order_by('-created_at')
    serializer_class = AlertSerializer


class DashboardStatsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        today = timezone.now().date()
        total_intersections = Intersection.objects.count()
        active_signals = TrafficSignal.objects.filter(is_operational=True).count()
        critical_incidents_count = Incident.objects.filter(is_resolved=False, severity='CRITICAL').count()
        active_alerts_count = Alert.objects.filter(is_active=True).count()
        todays_vehicle_total = VehicleCount.objects.filter(timestamp__date=today).aggregate(total=Sum('count'))['total'] or 0
        avg_congestion_score = VehicleCount.objects.filter(timestamp__date=today).aggregate(avg=Avg('count'))['avg'] or 0
        return Response({
            'total_intersections': total_intersections,
            'active_signals': active_signals,
            'critical_incidents_count': critical_incidents_count,
            'active_alerts_count': active_alerts_count,
            'todays_vehicle_total': todays_vehicle_total,
            'avg_congestion_score': round(avg_congestion_score, 1),
        })
