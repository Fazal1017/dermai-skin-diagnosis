from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DiagnosisViewSet, diagnosis_history, export_predictions

# Create a router and register the ViewSet
router = DefaultRouter()
router.register(r'diagnoses', DiagnosisViewSet, basename='diagnosis')

urlpatterns = [
    path('', include(router.urls)),
    path('history/', diagnosis_history, name='history'),
    path('export/', export_predictions, name='export'),
]
