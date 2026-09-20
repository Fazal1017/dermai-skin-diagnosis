from rest_framework import serializers
from diagnosis.models import PatientDiagnosis

class DiagnosisSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientDiagnosis
        fields = ['disease_name', 'confidence', 'created_at']
