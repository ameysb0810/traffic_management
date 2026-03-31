from datetime import timedelta
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import VehicleCount, Incident, Alert


@receiver(post_save, sender=VehicleCount)
def vehicle_count_alert(sender, instance, created, **kwargs):
    if not created:
        return
    if instance.congestion_level == 'CRITICAL':
        today = timezone.now().date()
        existing = Alert.objects.filter(
            intersection=instance.intersection,
            alert_type='WARNING',
            is_active=True,
            created_at__date=today,
        )
        if not existing.exists():
            Alert.objects.create(
                title='Critical congestion alert',
                message=f'Critical congestion detected at {instance.intersection.name}.',
                alert_type='WARNING',
                intersection=instance.intersection,
                expires_at=timezone.now() + timedelta(hours=2),
            )


@receiver(post_save, sender=Incident)
def incident_alert(sender, instance, created, **kwargs):
    if not created:
        return
    if instance.severity == 'CRITICAL' and not instance.is_resolved:
        Alert.objects.create(
            title=f'Critical Incident: {instance.incident_type}',
            message=instance.description,
            alert_type='DANGER',
            intersection=instance.intersection,
            expires_at=timezone.now() + timedelta(hours=4),
        )
