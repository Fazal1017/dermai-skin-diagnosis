from rest_framework import serializers
from .models import DiagnosisResult


class DiagnosisResultSerializer(serializers.ModelSerializer):
    """Serializer for DiagnosisResult model"""
    
    class Meta:
        model = DiagnosisResult
        fields = [
            'id',
            'image',
            'image_filename',
            'predicted_condition',
            'confidence_score',
            'all_predictions',
            'patient_id',
            'notes',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'predicted_condition', 'confidence_score', 'all_predictions']


class DiagnosisPredictionSerializer(serializers.Serializer):
    """Serializer for prediction request"""
    
    image = serializers.ImageField(required=True)
    patient_id = serializers.CharField(max_length=100, required=False, allow_blank=True)
    notes = serializers.CharField(max_length=500, required=False, allow_blank=True)
