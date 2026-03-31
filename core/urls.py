from django.urls import path
from . import views

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('intersections/', views.IntersectionListView.as_view(), name='intersection_list'),
    path('intersections/<int:pk>/', views.IntersectionDetailView.as_view(), name='intersection_detail'),
    path('signals/<int:pk>/control/', views.SignalControlView.as_view(), name='signal_control'),
    path('incidents/', views.IncidentListView.as_view(), name='incidents'),
    path('incidents/new/', views.IncidentCreateView.as_view(), name='incident_create'),
    path('incidents/<int:pk>/resolve/', views.resolve_incident, name='resolve_incident'),
    path('analytics/', views.AnalyticsView.as_view(), name='analytics'),
    path('alerts/', views.AlertListView.as_view(), name='alerts'),
    path('register/', views.SignupView.as_view(), name='register'),
    path('simulate/run/', views.RunSimulationView.as_view(), name='run_simulation'),
    path('simulate/seed/', views.SeedDataView.as_view(), name='seed_data'),
]
