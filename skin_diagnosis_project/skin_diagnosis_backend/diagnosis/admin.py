from django.contrib import admin
from django.utils.html import mark_safe
from .models import DiagnosisResult, Disease, PatientDiagnosis


@admin.register(DiagnosisResult)
class DiagnosisResultAdmin(admin.ModelAdmin):
    """Admin configuration for DiagnosisResult model"""
    
    list_display = [
        'id',
        'predicted_condition',
        'confidence_score',
        'patient_id',
        'created_at',
        'updated_at'
    ]
    
    list_filter = [
        'predicted_condition',
        'created_at',
        'updated_at'
    ]
    
    search_fields = [
        'patient_id',
        'image_filename',
        'predicted_condition',
        'notes'
    ]
    
    readonly_fields = [
        'predicted_condition',
        'confidence_score',
        'all_predictions',
        'created_at',
        'updated_at',
        'image_preview'
    ]
    
    fieldsets = (
        ('Image Information', {
            'fields': ('image', 'image_preview', 'image_filename')
        }),
        ('Prediction Results', {
            'fields': ('predicted_condition', 'confidence_score', 'all_predictions')
        }),
        ('Patient Information', {
            'fields': ('patient_id', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    @admin.display(description='Image Preview')
    def image_preview(self, obj):
        """Display image preview in admin"""
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="200" height="200" />')
        return 'No image'


@admin.register(Disease)
class DiseaseAdmin(admin.ModelAdmin):
    list_display = ('name', 'doctor_specialty', 'urgency_level', 'referral_needed')
    search_fields = ('name',)
    list_filter = ('urgency_level', 'referral_needed')


@admin.register(PatientDiagnosis)
class PatientDiagnosisAdmin(admin.ModelAdmin):
    list_display = ('user', 'disease_name', 'created_at', 'confidence')
    list_filter = ('disease_name', 'created_at')
    search_fields = ('user__username',)

