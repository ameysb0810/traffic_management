from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    IntersectionViewSet,
    TrafficSignalListView,
    VehicleCountListView,
    IncidentListCreateView,
    AlertListView,
    DashboardStatsView,
)

router = DefaultRouter()
router.register('intersections', IntersectionViewSet, basename='api_intersections')

urlpatterns = [
    path('', include(router.urls)),
    path('signals/', TrafficSignalListView.as_view(), name='api_signals'),
    path('counts/', VehicleCountListView.as_view(), name='api_counts'),
    path('incidents/', IncidentListCreateView.as_view(), name='api_incidents'),
    path('alerts/', AlertListView.as_view(), name='api_alerts'),
    path('stats/', DashboardStatsView.as_view(), name='api_stats'),
]
