from rest_framework import serializers
from core.models import Intersection, TrafficSignal, VehicleCount, Incident, Alert
from core.utils import format_duration


class IntersectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Intersection
        fields = '__all__'


class TrafficSignalSerializer(serializers.ModelSerializer):
    intersection_name = serializers.SerializerMethodField()

    class Meta:
        model = TrafficSignal
        fields = [
            'id', 'intersection', 'direction', 'current_phase', 'green_duration',
            'red_duration', 'yellow_duration', 'last_changed', 'is_operational',
            'intersection_name',
        ]

    def get_intersection_name(self, obj):
        return obj.intersection.name if obj.intersection else None


class VehicleCountSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleCount
        fields = '__all__'


class IncidentSerializer(serializers.ModelSerializer):
    duration = serializers.SerializerMethodField()

    class Meta:
        model = Incident
        fields = [
            'id', 'intersection', 'incident_type', 'description', 'severity',
            'reported_at', 'resolved_at', 'is_resolved', 'reported_by', 'duration',
        ]

    def get_duration(self, obj):
        return format_duration(obj.duration)


class AlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alert
        fields = '__all__'
