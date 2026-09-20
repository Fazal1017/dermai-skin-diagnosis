from django.db import models
from django.core.files.storage import default_storage
from django.contrib.auth.models import User
import json

class DiagnosisResult(models.Model):
    """Model to store skin diagnosis predictions"""
    
    CONDITION_CHOICES = [
        ('melanoma', 'Melanoma'),
        ('nevus', 'Nevus'),
        ('basal_cell_carcinoma', 'Basal Cell Carcinoma'),
        ('actinic_keratosis', 'Actinic Keratosis'),
        ('benign_keratosis', 'Benign Keratosis'),
        ('dermatofibroma', 'Dermatofibroma'),
        ('vascular_lesion', 'Vascular Lesion'),
    ]
    
    # Image info
    image = models.ImageField(upload_to='diagnosis_images/')
    image_filename = models.CharField(max_length=255)
    
    # Prediction results
    predicted_condition = models.CharField(max_length=50, choices=CONDITION_CHOICES)
    confidence_score = models.FloatField()  # 0 to 1
    
    # All predictions (JSON format for all classes)
    all_predictions = models.JSONField(default=dict)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # User info (optional)
    patient_id = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Diagnosis Result'
        verbose_name_plural = 'Diagnosis Results'
    
    def __str__(self):
        return f"{self.predicted_condition} - {self.confidence_score:.2%} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"


class Disease(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    
    # Medical prescription / first-line treatment
    prescription = models.TextField(help_text="Recommended medicines or treatment")
    
    # Which doctor to visit
    doctor_specialty = models.CharField(max_length=200, help_text="e.g., Dermatologist, Oncologist")
    referral_needed = models.BooleanField(default=False, help_text="Requires GP referral?")
    
    urgency_level = models.CharField(
        max_length=20,
        choices=[('Low', 'Low - Can wait for routine appointment'),
                 ('Medium', 'Medium - See doctor within 2 weeks'),
                 ('High', 'High - Seek immediate medical attention')],
        default='Medium'
    )
    
    # Precautions
    precautions = models.TextField(help_text="List of precautions, one per line")
    
    def __str__(self):
        return self.name


class PatientDiagnosis(models.Model):
    """Model to track individual patient diagnosis records"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='diagnoses')
    disease_name = models.CharField(max_length=100)
    confidence = models.FloatField(default=0.0)
    image = models.ImageField(upload_to='diagnosis_images/', blank=True, null=True)
    disease = models.ForeignKey(Disease, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Patient Diagnosis'
        verbose_name_plural = 'Patient Diagnoses'

    def __str__(self):
        return f"{self.user.username} - {self.disease_name} ({self.created_at.date()})"


class DiagnosisDocumentHistory(models.Model):
    """
    Dedicated table for tracking document (diagnosis) history.
    Separates document logs from patient and staff records.
    """
    ACTION_CHOICES = [
        ('CREATED', 'Document Created'),
        ('VIEWED', 'Document Viewed'),
        ('UPDATED', 'Document Updated'),
        ('SHARED', 'Document Shared'),
        ('DELETED', 'Document Deleted'),
    ]
    
    document = models.ForeignKey(PatientDiagnosis, on_delete=models.CASCADE, related_name='history_logs')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    performed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.TextField(blank=True, help_text="Additional metadata about the action")
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Diagnosis Document History'
        verbose_name_plural = 'Diagnosis Document Histories'

    def __str__(self):
        return f"{self.get_action_display()} on {self.document.id} at {self.timestamp}"
