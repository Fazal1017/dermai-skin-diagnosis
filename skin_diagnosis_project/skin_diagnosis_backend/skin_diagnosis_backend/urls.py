"""
URL configuration for skin_diagnosis_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from diagnosis import views  # Import views from diagnosis app

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='diagnosis'),          # Home page
    path('dashboard/', views.dashboard_view, name='dashboard'),  # Patient Dashboard
    path('metrics/', views.metrics, name='metrics'),
    path('history/', views.diagnosis_history, name='history'),
    path('export/', views.export_predictions, name='export'),
    path('api/', include('diagnosis.urls')),
    path('api/v1/', include('api.urls')),
    path('accounts/', include('accounts.urls')),  # Auth & profile routes
    path('analytics/', include('analytics.urls')),
    path('messaging/', include('messaging.urls')),
]

# Serve media files during development (do not use in production)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
