from django.utils import timezone
from django.contrib import admin
from .models import Intersection, TrafficSignal, VehicleCount, Incident, Alert, TrafficAnalytics


@admin.register(Intersection)
class IntersectionAdmin(admin.ModelAdmin):
    list_display = ['name', 'location', 'num_lanes', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'location']


@admin.register(TrafficSignal)
class TrafficSignalAdmin(admin.ModelAdmin):
    list_display = ['intersection', 'direction', 'current_phase', 'is_operational']
    list_filter = ['current_phase', 'direction']
    list_editable = ['current_phase']


@admin.register(VehicleCount)
class VehicleCountAdmin(admin.ModelAdmin):
    list_display = ['intersection', 'vehicle_type', 'count', 'congestion_level', 'timestamp']
    list_filter = ['congestion_level', 'vehicle_type']
    date_hierarchy = 'timestamp'


@admin.register(Incident)
class IncidentAdmin(admin.ModelAdmin):
    list_display = ['intersection', 'incident_type', 'severity', 'is_resolved', 'reported_at']
    list_filter = ['severity', 'is_resolved', 'incident_type']
    actions = ['mark_resolved']

    def mark_resolved(self, request, queryset):
        updated = queryset.filter(is_resolved=False).update(is_resolved=True, resolved_at=timezone.now())
        self.message_user(request, f"{updated} incident(s) marked as resolved.")
    mark_resolved.short_description = 'Mark selected incidents as resolved'


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ['title', 'alert_type', 'is_active', 'created_at']
    list_filter = ['alert_type', 'is_active']


@admin.register(TrafficAnalytics)
class TrafficAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['intersection', 'date', 'hour', 'avg_vehicle_count', 'avg_speed']
    list_filter = ['date', 'intersection']
