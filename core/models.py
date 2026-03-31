from django.conf import settings
from django.db import models
from django.utils import timezone


class Intersection(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=200)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    num_lanes = models.PositiveIntegerField(default=4)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class TrafficSignal(models.Model):
    DIRECTION_CHOICES = [
        ('NORTH', 'North'),
        ('SOUTH', 'South'),
        ('EAST', 'East'),
        ('WEST', 'West'),
    ]
    PHASE_CHOICES = [
        ('RED', 'Red'),
        ('YELLOW', 'Yellow'),
        ('GREEN', 'Green'),
    ]

    intersection = models.ForeignKey('core.Intersection', on_delete=models.CASCADE, related_name='signals')
    direction = models.CharField(max_length=10, choices=DIRECTION_CHOICES)
    current_phase = models.CharField(max_length=10, choices=PHASE_CHOICES, default='RED')
    green_duration = models.PositiveIntegerField(default=30, help_text='seconds')
    red_duration = models.PositiveIntegerField(default=60)
    yellow_duration = models.PositiveIntegerField(default=5)
    last_changed = models.DateTimeField(auto_now=True)
    is_operational = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.intersection.name} - {self.direction}"


class VehicleCount(models.Model):
    VEHICLE_TYPE_CHOICES = [
        ('CAR', 'Car'),
        ('TRUCK', 'Truck'),
        ('MOTORCYCLE', 'Motorcycle'),
        ('BUS', 'Bus'),
    ]
    CONGESTION_CHOICES = [
        ('LOW', 'Low'),
        ('MODERATE', 'Moderate'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    ]

    intersection = models.ForeignKey('core.Intersection', on_delete=models.CASCADE, related_name='vehicle_counts')
    signal = models.ForeignKey('core.TrafficSignal', on_delete=models.CASCADE, related_name='vehicle_counts')
    timestamp = models.DateTimeField(auto_now_add=True)
    count = models.PositiveIntegerField(default=0)
    vehicle_type = models.CharField(max_length=12, choices=VEHICLE_TYPE_CHOICES, default='CAR')
    average_speed = models.FloatField(default=0.0, help_text='km/h')
    congestion_level = models.CharField(max_length=10, choices=CONGESTION_CHOICES, default='LOW')

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.intersection.name} {self.signal.direction} {self.count}"


class Incident(models.Model):
    INCIDENT_TYPE_CHOICES = [
        ('ACCIDENT', 'Accident'),
        ('BREAKDOWN', 'Breakdown'),
        ('ROADBLOCK', 'Roadblock'),
        ('EMERGENCY', 'Emergency'),
        ('WEATHER', 'Weather'),
    ]
    SEVERITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    ]

    intersection = models.ForeignKey('core.Intersection', on_delete=models.CASCADE, related_name='incidents')
    incident_type = models.CharField(max_length=15, choices=INCIDENT_TYPE_CHOICES)
    description = models.TextField()
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES)
    reported_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    is_resolved = models.BooleanField(default=False)
    reported_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.incident_type} at {self.intersection.name}"

    @property
    def duration(self):
        end_time = self.resolved_at or timezone.now()
        return end_time - self.reported_at


class Alert(models.Model):
    ALERT_TYPE_CHOICES = [
        ('INFO', 'Info'),
        ('WARNING', 'Warning'),
        ('DANGER', 'Danger'),
        ('SUCCESS', 'Success'),
    ]

    title = models.CharField(max_length=200)
    message = models.TextField()
    alert_type = models.CharField(max_length=10, choices=ALERT_TYPE_CHOICES)
    intersection = models.ForeignKey('core.Intersection', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title


class TrafficAnalytics(models.Model):
    intersection = models.ForeignKey('core.Intersection', on_delete=models.CASCADE, related_name='analytics')
    date = models.DateField()
    hour = models.PositiveIntegerField()
    avg_vehicle_count = models.FloatField(default=0)
    peak_count = models.PositiveIntegerField(default=0)
    avg_speed = models.FloatField(default=0)
    avg_congestion_score = models.FloatField(default=0)

    class Meta:
        unique_together = [['intersection', 'date', 'hour']]

    def __str__(self):
        return f"Analytics {self.intersection.name} {self.date} {self.hour}"
