from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Avg, Q
from django.utils import timezone
import numpy as np
from PIL import Image
import io
import csv
from datetime import datetime, timedelta
import os
import json

from .models import DiagnosisResult, Disease, PatientDiagnosis
from .serializers import DiagnosisResultSerializer, DiagnosisPredictionSerializer
from .forms import ImageUploadForm

LOG_FILE = 'predictions_log.csv'

def log_prediction(request, disease, confidence):
    """Append a prediction record to CSV file."""
    file_exists = os.path.isfile(LOG_FILE)
    with open(LOG_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['timestamp', 'ip', 'disease', 'confidence'])
        writer.writerow([datetime.now().isoformat(), 
                         request.META.get('REMOTE_ADDR'), 
                         disease, 
                         f"{confidence:.2f}%"])

# Lazy-load the ML model (avoid blocking on startup)
skin_model = None

def get_model():
    """Lazy load the ML model on first use"""
    global skin_model
    if skin_model is None:
        from .ml_model import SkinDiagnosisModel
        skin_model = SkinDiagnosisModel()
    return skin_model


@login_required
def index(request):
    """
    Home page with:
    - API info (JSON)
    - Web interface (HTML)
    
    Serves different content based on request Accept header
    """
    # If requesting HTML, serve the web interface
    if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
        return render(request, 'diagnosis/index.html', {'form': ImageUploadForm()})
    
    # Otherwise serve API info as JSON
    return JsonResponse({
        'message': 'Welcome to Skin Diagnosis System',
        'version': '3.0',
        'status': 'API Running',
        'endpoints': {
            'predict': '/api/diagnoses/predict/',
            'list_diagnoses': '/api/diagnoses/',
            'get_diagnosis': '/api/diagnoses/{id}/',
            'diagnosis_history': '/api/diagnoses/history/',
            'web_interface': '/',
            'admin': '/admin/',
        },
        'model_info': {
            'type': 'ResNet50',
            'classes': 7,
            'classes_list': [
                'actinic_keratosis',
                'basal_cell_carcinoma',
                'benign_keratosis',
                'dermatofibroma',
                'melanoma',
                'nevus',
                'vascular_lesion'
            ]
        }
    })


class DiagnosisViewSet(viewsets.ModelViewSet):
    """
    ViewSet for skin diagnosis predictions
    Handles CRUD operations and prediction requests
    """
    queryset = DiagnosisResult.objects.all()
    serializer_class = DiagnosisResultSerializer
    parser_classes = (MultiPartParser, FormParser)
    
    @action(detail=False, methods=['post'])
    def predict(self, request):
        """
        Endpoint for skin lesion diagnosis prediction
        
        Accepts:
        - image: Image file (PNG, JPG, etc.)
        - patient_id: Optional patient identifier
        - notes: Optional clinical notes
        
        Returns:
        - predicted_condition: The diagnosed skin condition
        - confidence_score: Confidence of the prediction (0-1)
        - all_predictions: Scores for all conditions
        - diagnosis_result: Full DiagnosisResult object
        """
        
        # Validate input
        serializer = DiagnosisPredictionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Extract image
            image_file = request.FILES.get('image')
            if not image_file:
                return Response(
                    {'error': 'No image file provided'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Validate image file size
            if image_file.size > 5 * 1024 * 1024:  # 5MB limit
                return Response(
                    {'error': 'Image file too large (max 5MB)'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Auto-assign patient ID if the user is a customer
            patient_id = ''
            if request.user.is_authenticated and hasattr(request.user, 'customer_profile'):
                patient_id = request.user.customer_profile.patient_id
                
            notes = request.data.get('notes', '').strip()[:500]  # Max 500 chars
            
            # Preprocess image
            try:
                image = Image.open(image_file)
            except Exception as e:
                return Response(
                    {'error': f'Invalid image file: {str(e)}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            image_array = self._preprocess_image(image)
            
            # Make prediction using the ML model with Test-Time Augmentation
            try:
                model = get_model()
                predicted_condition, all_scores = model.predict_with_tta(image_array, n_aug=5)
                confidence_score = float(max(all_scores.values()))
            except Exception as e:
                return Response(
                    {'error': f'Prediction failed: {str(e)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            # Validate prediction results
            if not predicted_condition or not all_scores:
                return Response(
                    {'error': 'Model returned invalid prediction'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            # Get top 3 predictions sorted by confidence
            sorted_scores = sorted(all_scores.items(), key=lambda x: x[1], reverse=True)
            top_3_predictions = [
                {'condition': cond, 'confidence': round(score * 100, 2)}
                for cond, score in sorted_scores[:3]
            ]
            
            # Log the prediction to CSV
            try:
                log_prediction(request, predicted_condition, confidence_score * 100)
            except Exception as e:
                # Don't fail if logging fails
                pass
            
            # Create diagnosis result
            try:
                diagnosis_result = DiagnosisResult.objects.create(
                    image=image_file,
                    image_filename=image_file.name,
                    predicted_condition=predicted_condition,
                    confidence_score=confidence_score,
                    all_predictions=all_scores,
                    patient_id=patient_id if patient_id else None,
                    notes=notes if notes else None
                )
            except Exception as e:
                return Response(
                    {'error': f'Failed to save diagnosis: {str(e)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            patient_diagnosis = None
            # Save PatientDiagnosis record if user is authenticated
            if request.user.is_authenticated:
                try:
                    disease_name_display = predicted_condition.replace('_', ' ').title()
                    disease_obj = Disease.objects.filter(name__icontains=disease_name_display).first()
                    patient_diagnosis = PatientDiagnosis.objects.create(
                        user=request.user,
                        disease_name=disease_name_display,
                        confidence=confidence_score * 100,
                        image=image_file,
                        disease=disease_obj,
                    )
                    
                    from .models import DiagnosisDocumentHistory
                    DiagnosisDocumentHistory.objects.create(
                        document=patient_diagnosis,
                        action='CREATED',
                        performed_by=request.user,
                        details='Initial AI diagnosis generated from uploaded image.'
                    )
                except Exception:
                    pass  # Don't fail if patient diagnosis save fails
            
            # Find recommended doctors
            recommended_doctors = []
            if patient_diagnosis and request.user.is_authenticated:
                specialization_map = {
                    'acne': 'DER',
                    'eczema': 'DER',
                    'melanoma': 'ONC',
                    'psoriasis': 'DER',
                    'urticaria': 'ALL',
                }
                
                disease_lower = predicted_condition.lower()
                required_specialization = specialization_map.get(disease_lower, 'DER')
                
                customer_profile = getattr(request.user, 'customer_profile', None)
                if customer_profile:
                    city = customer_profile.city
                    
                    # Assuming we imported Doctor at the top, or we can just import here
                    from accounts.models import Doctor
                    available_doctors = Doctor.objects.filter(
                        specialization=required_specialization,
                        is_active=True
                    )
                    
                    if city:
                        available_doctors = available_doctors.filter(hospital__city__iexact=city)
                    
                    for doc in available_doctors[:5]:
                        recommended_doctors.append({
                            'id': doc.id,
                            'name': doc.name,
                            'specialization': doc.get_specialization_display(),
                            'hospital': doc.hospital.name,
                        })

            # Serialize and return
            result_serializer = DiagnosisResultSerializer(diagnosis_result)
            return Response({
                'success': True,
                'message': 'Prediction completed successfully',
                'predicted_condition': predicted_condition,
                'confidence_score': confidence_score,
                'all_predictions': all_scores,
                'top_3_predictions': top_3_predictions,
                'diagnosis_result': result_serializer.data,
                'patient_diagnosis_id': patient_diagnosis.id if patient_diagnosis else None,
                'recommended_doctors': recommended_doctors
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            # Catch any unexpected errors
            import traceback
            traceback.print_exc()
            return Response({
                'success': False,
                'error': f'Unexpected error: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'])
    def details(self, request, pk=None):
        """Get detailed diagnosis information"""
        diagnosis = self.get_object()
        serializer = self.get_serializer(diagnosis)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def history(self, request):
        """Get diagnosis history (latest 10)"""
        queryset = self.get_queryset()[:10]
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def _preprocess_image(self, image, target_size=(224, 224)):
        """
        Preprocess image for model prediction
        """
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Resize image
        image = image.resize(target_size)
        
        # Convert to numpy array
        image_array = np.array(image, dtype=np.float32)
        
        # Normalize to 0-1 range
        image_array = image_array / 255.0
        
        
        # Add batch dimension
        image_array = np.expand_dims(image_array, axis=0)
        
        return image_array

def metrics(request):
    """Enhanced metrics dashboard using database queries"""
    context = {}
    
    # Query database for accurate metrics
    all_diagnoses = DiagnosisResult.objects.all()
    
    if all_diagnoses.exists():
        # Calculate statistics
        total = all_diagnoses.count()
        avg_confidence = all_diagnoses.aggregate(Avg('confidence_score'))['confidence_score__avg'] or 0
        
        # Get disease distribution
        disease_counts = dict(
            all_diagnoses.values('predicted_condition')
            .annotate(count=Count('id'))
            .order_by('-count')
            .values_list('predicted_condition', 'count')
        )
        
        most_common = max(disease_counts.items(), key=lambda x: x[1])[0] if disease_counts else "None"
        
        # Get high confidence predictions (>80%)
        high_confidence_count = all_diagnoses.filter(confidence_score__gte=0.8).count()
        
        # Get data from last 7 days
        week_ago = timezone.now() - timedelta(days=7)
        recent_diagnoses = all_diagnoses.filter(created_at__gte=week_ago)
        
        context = {
            'total_predictions': total,
            'most_common_disease': most_common.replace('_', ' ').title(),
            'average_confidence': f"{avg_confidence*100:.1f}%",
            'high_confidence_count': high_confidence_count,
            'recent_count': recent_diagnoses.count(),
            'disease_counts': disease_counts,
        }
    
    return render(request, 'diagnosis/metrics.html', context)


@login_required
def diagnosis_history(request):
    """Display diagnosis history with filtering"""
    queryset = DiagnosisResult.objects.all().order_by('-created_at')
    
    # Filter by disease if specified
    disease_filter = request.GET.get('disease', '')
    if disease_filter:
        queryset = queryset.filter(predicted_condition=disease_filter)
    
    # Filter by confidence range
    min_confidence = request.GET.get('min_conf', '0')
    if min_confidence:
        queryset = queryset.filter(confidence_score__gte=float(min_confidence)/100)
    
    # Get all diseases for filter dropdown
    all_diseases = DiagnosisResult.objects.values_list('predicted_condition', flat=True).distinct()
    
    context = {
        'diagnoses': queryset[:50],  # Paginate: show 50 latest
        'all_diseases': all_diseases,
        'selected_disease': disease_filter,
        'selected_confidence': min_confidence,
        'total_count': DiagnosisResult.objects.count(),
    }
    
    return render(request, 'diagnosis/history.html', context)


@login_required
def export_predictions(request):
    """Export diagnosis predictions as CSV or JSON"""
    format_type = request.GET.get('format', 'csv')
    
    queryset = DiagnosisResult.objects.all().order_by('-created_at')
    
    if format_type == 'json':
        data = []
        for diagnosis in queryset:
            data.append({
                'id': diagnosis.id,
                'date': diagnosis.created_at.isoformat(),
                'condition': diagnosis.predicted_condition,
                'confidence': f"{diagnosis.confidence_score*100:.2f}%",
                'patient_id': diagnosis.patient_id or 'N/A',
                'notes': diagnosis.notes or '',
            })
        
        response = HttpResponse(
            json.dumps(data, indent=2),
            content_type='application/json'
        )
        response['Content-Disposition'] = 'attachment; filename="predictions_export.json"'
        return response
    
    else:  # CSV format
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="predictions_export.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['ID', 'Date', 'Condition', 'Confidence', 'Patient ID', 'Notes'])
        
        for diagnosis in queryset:
            writer.writerow([
                diagnosis.id,
                diagnosis.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                diagnosis.predicted_condition.replace('_', ' ').title(),
                f"{diagnosis.confidence_score*100:.2f}%",
                diagnosis.patient_id or 'N/A',
                diagnosis.notes or '',
            ])
        
        return response


@login_required
def dashboard_view(request):
    """Patient dashboard with diagnosis history and charts"""
    from collections import Counter
    
    # Get all diagnoses for this user, ordered newest first
    diagnoses = PatientDiagnosis.objects.filter(user=request.user).select_related('disease').order_by('-created_at')
    
    # Get the most recent diagnosis
    latest = diagnoses.first()
    
    # Prepare chart data (disease frequency)
    disease_names = [d.disease_name for d in diagnoses]
    counts = Counter(disease_names)
    chart_labels = list(counts.keys())
    chart_data = list(counts.values())
    
    context = {
        'diagnoses': diagnoses,
        'latest': latest,
        'chart_labels': json.dumps(chart_labels),
        'chart_data': json.dumps(chart_data),
        'total_diagnoses': diagnoses.count(),
    }
    return render(request, 'diagnosis/dashboard.html', context)
