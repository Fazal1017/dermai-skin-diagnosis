from django.urls import path
from . import views

urlpatterns = [
    path('chat/<int:appointment_id>/', views.appointment_chat, name='appointment_chat'),
]
