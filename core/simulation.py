import random
from datetime import datetime, timedelta
from django.utils import timezone
from .models import Intersection, TrafficSignal, VehicleCount, Incident, Alert
from .utils import get_congestion_level

VEHICLE_TYPES = ['CAR', 'TRUCK', 'MOTORCYCLE', 'BUS']
BASE_COUNTS = {'CAR': 20, 'TRUCK': 5, 'MOTORCYCLE': 15, 'BUS': 3}


def simulate_vehicle_count(signal):
    current_hour = timezone.now().hour
    multiplier = 1.0
    if 8 <= current_hour <= 10 or 17 <= current_hour <= 19:
        multiplier = 2.5
    vehicle_type = random.choices(VEHICLE_TYPES, weights=[50, 10, 25, 15], k=1)[0]
    base = BASE_COUNTS.get(vehicle_type, 10)
    count = max(0, int(random.gauss(base * multiplier, 5)))
    speed = max(8.0, 60.0 - (count * 0.8) + random.uniform(-3, 3))
    congestion_level = get_congestion_level(count)
    return VehicleCount(
        intersection=signal.intersection,
        signal=signal,
        count=count,
        vehicle_type=vehicle_type,
        average_speed=round(speed, 1),
        congestion_level=congestion_level,
    )


def simulate_signal_phase_change(signal):
    cycle = {'RED': 'GREEN', 'GREEN': 'YELLOW', 'YELLOW': 'RED'}
    signal.current_phase = cycle.get(signal.current_phase, 'RED')
    signal.save(update_fields=['current_phase', 'last_changed'])
    return signal


tick_counter = 0


def run_simulation_tick():
    global tick_counter
    operational_signals = TrafficSignal.objects.filter(is_operational=True)
    records_created = 0
    for signal in operational_signals:
        vc = simulate_vehicle_count(signal)
        vc.save()
        records_created += 1
    tick_counter += 1
    if tick_counter % 3 == 0:
        for signal in operational_signals:
            simulate_signal_phase_change(signal)
    return records_created


def seed_demo_data():
    if Intersection.objects.exists():
        return 0
    names = [
        ('MG Road', 'MG Road intersection, central district', 12.971598, 77.594566),
        ('Station Road', 'Station Road corridor', 12.976347, 77.599930),
        ('Brigade Road', 'Brigade junction', 12.971891, 77.605446),
        ('Forest Gate', 'Forest Gate crossing', 12.981123, 77.590234),
    ]
    created = 0
    for name, location, lat, lon in names:
        intersection = Intersection.objects.create(
            name=name,
            location=location,
            latitude=lat,
            longitude=lon,
        )
        directions = ['NORTH', 'SOUTH', 'EAST', 'WEST']
        for direction in directions:
            TrafficSignal.objects.create(
                intersection=intersection,
                direction=direction,
                current_phase=random.choice(['RED', 'GREEN', 'YELLOW']),
            )
        created += 1
    signals = TrafficSignal.objects.all()
    for signal in signals:
        for _ in range(48):
            vc = simulate_vehicle_count(signal)
            vc.timestamp = timezone.now() - timedelta(hours=random.randint(0, 48))
            vc.save()
    if names:
        first = Intersection.objects.first()
        Incident.objects.create(
            intersection=first,
            incident_type='ACCIDENT',
            description='Minor collision slowing traffic flow.',
            severity='MEDIUM',
            reported_by=None,
        )
        Incident.objects.create(
            intersection=first,
            incident_type='BREAKDOWN',
            description='Vehicle stalled near the traffic light.',
            severity='LOW',
            reported_by=None,
        )
        Alert.objects.create(
            title='Overloaded junction',
            message='Traffic volume is above normal levels for this intersection.',
            alert_type='WARNING',
            intersection=first,
            expires_at=timezone.now() + timedelta(hours=6),
        )
        Alert.objects.create(
            title='Routine signal check',
            message='Signal calibration scheduled after midnight.',
            alert_type='INFO',
        )
        Alert.objects.create(
            title='Weather advisory',
            message='Light showers expected in the evening hours.',
            alert_type='INFO',
        )
    return created
