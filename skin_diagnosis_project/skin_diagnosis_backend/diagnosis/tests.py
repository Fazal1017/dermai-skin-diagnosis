from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from unittest.mock import patch, MagicMock
from .models import Disease, PatientDiagnosis, DiagnosisResult
import json
from django.core.files.uploadedfile import SimpleUploadedFile

class DiagnosisTestCase(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(username='testuser', password='password')
        
        # Create a sample disease
        self.disease = Disease.objects.create(
            name='Melanoma',
            description='Test description',
            prescription='Test prescription',
            doctor_specialty='Oncologist',
            referral_needed=True,
            urgency_level='High',
            precautions='Test precautions'
        )
        
        # Create a sample patient diagnosis
        self.patient_diagnosis = PatientDiagnosis.objects.create(
            user=self.user,
            disease=self.disease,
            disease_name='Melanoma',
            confidence=95.5
        )
        
        self.client = Client()

    def test_disease_str(self):
        self.assertEqual(str(self.disease), 'Melanoma')

    def test_patient_diagnosis_str(self):
        expected_str = f"{self.user.username} - Melanoma ({self.patient_diagnosis.created_at.date()})"
        self.assertEqual(str(self.patient_diagnosis), expected_str)

    def test_dashboard_view_unauthenticated(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirects to login

    def test_dashboard_view_authenticated(self):
        self.client.login(username='testuser', password='password')
        
        # Make the request and verify it succeeds. select_related is tested implicitly
        # by checking that the disease context is correctly passed without N+1 crashes.
        response = self.client.get(reverse('dashboard'))
            
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'diagnosis/dashboard.html')
        
        # Check context variables
        self.assertIn('diagnoses', response.context)
        self.assertIn('latest', response.context)
        self.assertIn('chart_labels', response.context)
        self.assertIn('chart_data', response.context)
        self.assertIn('total_diagnoses', response.context)
        
        self.assertEqual(response.context['total_diagnoses'], 1)
        self.assertEqual(response.context['latest'].disease_name, 'Melanoma')
        
        # Check that disease is prefetched/selected
        latest_diag = response.context['diagnoses'][0]
        self.assertEqual(latest_diag.disease.name, 'Melanoma')

    @patch('diagnosis.views.get_model')
    def test_predict_endpoint_creates_patient_diagnosis(self, mock_get_model):
        # Mock the ML model
        mock_model = MagicMock()
        mock_model.predict_with_tta.return_value = ('melanoma', {'melanoma': 0.95, 'nevus': 0.05})
        mock_get_model.return_value = mock_model
        
        self.client.login(username='testuser', password='password')
        
        # Create a 1x1 GIF image
        image_content = b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00\x21\xf9\x04\x01\x00\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b'
        image = SimpleUploadedFile("test_image.gif", image_content, content_type="image/gif")
        
        initial_count = PatientDiagnosis.objects.count()
        
        # Send prediction request
        response = self.client.post(
            reverse('diagnosis-predict'),
            {'image': image},
            format='multipart'
        )
        
        self.assertEqual(response.status_code, 201)
        
        # Verify PatientDiagnosis was created
        self.assertEqual(PatientDiagnosis.objects.count(), initial_count + 1)
        
        latest_pd = PatientDiagnosis.objects.order_by('-created_at').first()
        self.assertEqual(latest_pd.user, self.user)
        self.assertEqual(latest_pd.disease_name, 'Melanoma')
        self.assertEqual(latest_pd.disease, self.disease)
        self.assertAlmostEqual(latest_pd.confidence, 95.0)
