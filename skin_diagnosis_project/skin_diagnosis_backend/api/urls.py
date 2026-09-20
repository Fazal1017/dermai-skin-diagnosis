from django.urls import path
from .views import UserDiagnosesAPI

urlpatterns = [
    path('diagnoses/', UserDiagnosesAPI.as_view(), name='api_user_diagnoses'),
]
