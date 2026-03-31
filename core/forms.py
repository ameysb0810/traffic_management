from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from .models import Intersection, Incident, TrafficSignal, Alert


class SignupForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'placeholder': 'Email'}))

    class Meta:
        model = get_user_model()
        fields = ('username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'placeholder': 'Username', 'class': 'form-control bg-dark text-light'})
        self.fields['email'].widget.attrs.update({'class': 'form-control bg-dark text-light'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control bg-dark text-light'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control bg-dark text-light'})
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Create Account'))


class IntersectionForm(forms.ModelForm):
    class Meta:
        model = Intersection
        fields = ['name', 'location', 'latitude', 'longitude', 'num_lanes', 'is_active']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Save Intersection'))


class IncidentForm(forms.ModelForm):
    class Meta:
        model = Incident
        fields = ['intersection', 'incident_type', 'description', 'severity']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Report Incident'))


class SignalControlForm(forms.ModelForm):
    class Meta:
        model = TrafficSignal
        fields = ['current_phase', 'green_duration', 'red_duration', 'yellow_duration', 'is_operational']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Update Signal'))


class AlertForm(forms.ModelForm):
    expires_at = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'})
    )

    class Meta:
        model = Alert
        fields = ['title', 'message', 'alert_type', 'intersection', 'expires_at']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Save Alert'))
