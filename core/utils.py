import json
from datetime import timedelta
from django.db.models import Avg, Count, Sum
from django.utils import timezone
from .models import TrafficAnalytics, VehicleCount


def get_congestion_level(count: int) -> str:
    if count < 10:
        return 'LOW'
    if count < 25:
        return 'MODERATE'
    if count < 40:
        return 'HIGH'
    return 'CRITICAL'


def get_congestion_score(level: str) -> int:
    return {
        'LOW': 10,
        'MODERATE': 40,
        'HIGH': 70,
        'CRITICAL': 95,
    }.get(level, 0)


def calculate_optimal_green_time(vehicle_count: int, base_green: int = 30) -> int:
    interval = base_green + min(30, vehicle_count // 3)
    return max(15, min(90, interval))


def get_signal_phase_color(phase: str) -> str:
    return {
        'RED': 'danger',
        'YELLOW': 'warning',
        'GREEN': 'success',
    }.get(phase, 'secondary')


def format_duration(td) -> str:
    if not td:
        return '0s'
    total_seconds = int(td.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    parts = []
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    if seconds or not parts:
        parts.append(f"{seconds}s")
    return ' '.join(parts)


def get_peak_hours(intersection_id: int) -> list:
    analytics = TrafficAnalytics.objects.filter(intersection_id=intersection_id)
    peak = analytics.order_by('-avg_vehicle_count').values_list('hour', flat=True)[:3]
    return list(peak)


def generate_traffic_summary(intersection):
    today = timezone.now().date()
    counts = VehicleCount.objects.filter(intersection=intersection, timestamp__date=today)
    total = counts.aggregate(total_vehicles=Sum('count'))['total_vehicles'] or 0
    avg_speed = counts.aggregate(avg_speed=Avg('average_speed'))['avg_speed'] or 0
    level_counts = counts.values('congestion_level').annotate(count=Count('id'))
    dominant = 'LOW'
    if level_counts:
        dominant = max(level_counts, key=lambda entry: (entry['count'], entry['congestion_level']))['congestion_level']
    return {
        'total_vehicles': int(total),
        'avg_speed': round(avg_speed, 1),
        'dominant_congestion': dominant,
    }
