from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import DiagnosisSerializer
from diagnosis.models import PatientDiagnosis
from rest_framework.permissions import IsAuthenticated

class UserDiagnosesAPI(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        diagnoses = PatientDiagnosis.objects.filter(user=request.user)
        serializer = DiagnosisSerializer(diagnoses, many=True)
        return Response(serializer.data)
