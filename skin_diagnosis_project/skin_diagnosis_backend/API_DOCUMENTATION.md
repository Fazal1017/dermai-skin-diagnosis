# Skin Diagnosis Backend API Documentation

## Overview
The Skin Diagnosis Backend is a Django REST Framework API for skin lesion diagnosis using machine learning. It provides endpoints for image classification, prediction history, and result management.

## Project Structure
```
skin_diagnosis_backend/
├── manage.py                          # Django management script
├── db.sqlite3                         # SQLite database
├── requirements.txt                   # Project dependencies
├── diagnosis/                         # Main Django app
│   ├── models.py                      # Database models (DiagnosisResult)
│   ├── views.py                       # API views and viewsets
│   ├── serializers.py                 # DRF serializers
│   ├── urls.py                        # App URL configuration
│   ├── admin.py                       # Django admin configuration
│   ├── ml_model.py                    # TensorFlow model implementation
│   └── migrations/                    # Database migrations
└── skin_diagnosis_backend/            # Project settings
    ├── settings.py                    # Django settings
    ├── urls.py                        # Main URL routing
    ├── asgi.py                        # ASGI configuration
    └── wsgi.py                        # WSGI configuration
```

## API Endpoints

### 1. Make Prediction
**Endpoint:** `POST /api/diagnoses/predict/`

**Description:** Analyze a skin lesion image and generate a diagnosis prediction.

**Request:**
```json
{
  "image": <ImageFile>,
  "patient_id": "P001",        // Optional
  "notes": "Right arm lesion"   // Optional
}
```

**Response:**
```json
{
  "success": true,
  "message": "Prediction completed successfully",
  "predicted_condition": "melanoma",
  "confidence_score": 0.92,
  "all_predictions": {
    "melanoma": 0.92,
    "nevus": 0.05,
    "basal_cell_carcinoma": 0.02,
    "actinic_keratosis": 0.01,
    "benign_keratosis": 0.00,
    "dermatofibroma": 0.00,
    "vascular_lesion": 0.00
  },
  "diagnosis_result": {
    "id": 1,
    "image": "media/diagnosis_images/image.jpg",
    "image_filename": "image.jpg",
    "predicted_condition": "melanoma",
    "confidence_score": 0.92,
    "all_predictions": {...},
    "patient_id": "P001",
    "notes": "Right arm lesion",
    "created_at": "2026-04-21T10:30:00Z",
    "updated_at": "2026-04-21T10:30:00Z"
  }
}
```

### 2. List All Diagnoses
**Endpoint:** `GET /api/diagnoses/`

**Description:** Retrieve all diagnosis results with pagination.

**Query Parameters:**
- `page`: Page number (default: 1)
- `page_size`: Number of results per page (default: 10)

**Response:**
```json
{
  "count": 25,
  "next": "http://api.example.com/api/diagnoses/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "image": "media/diagnosis_images/image1.jpg",
      "image_filename": "image1.jpg",
      "predicted_condition": "melanoma",
      "confidence_score": 0.92,
      "all_predictions": {...},
      "patient_id": "P001",
      "notes": "Primary lesion",
      "created_at": "2026-04-21T10:30:00Z",
      "updated_at": "2026-04-21T10:30:00Z"
    }
  ]
}
```

### 3. Get Diagnosis Details
**Endpoint:** `GET /api/diagnoses/{id}/details/`

**Description:** Retrieve detailed information about a specific diagnosis.

**URL Parameters:**
- `id`: Diagnosis result ID

**Response:**
```json
{
  "id": 1,
  "image": "media/diagnosis_images/image.jpg",
  "image_filename": "image.jpg",
  "predicted_condition": "melanoma",
  "confidence_score": 0.92,
  "all_predictions": {...},
  "patient_id": "P001",
  "notes": "Right arm lesion",
  "created_at": "2026-04-21T10:30:00Z",
  "updated_at": "2026-04-21T10:30:00Z"
}
```

### 4. Get Diagnosis History
**Endpoint:** `GET /api/diagnoses/history/`

**Description:** Retrieve the latest 10 diagnosis results.

**Response:**
```json
[
  {
    "id": 1,
    "image": "media/diagnosis_images/image.jpg",
    "image_filename": "image.jpg",
    "predicted_condition": "melanoma",
    "confidence_score": 0.92,
    "all_predictions": {...},
    "patient_id": "P001",
    "notes": "Right arm lesion",
    "created_at": "2026-04-21T10:30:00Z",
    "updated_at": "2026-04-21T10:30:00Z"
  }
]
```

### 5. Update Diagnosis Notes
**Endpoint:** `PUT /api/diagnoses/{id}/`

**Description:** Update notes for a diagnosis result.

**Request:**
```json
{
  "notes": "Updated clinical notes"
}
```

**Response:**
```json
{
  "id": 1,
  "image": "media/diagnosis_images/image.jpg",
  "image_filename": "image.jpg",
  "predicted_condition": "melanoma",
  "confidence_score": 0.92,
  "all_predictions": {...},
  "patient_id": "P001",
  "notes": "Updated clinical notes",
  "created_at": "2026-04-21T10:30:00Z",
  "updated_at": "2026-04-21T10:35:00Z"
}
```

### 6. Delete Diagnosis
**Endpoint:** `DELETE /api/diagnoses/{id}/`

**Description:** Delete a diagnosis result.

**Response:** Status 204 No Content

## Skin Condition Classes
The model predicts one of the following skin conditions:
- `melanoma`: Malignant skin cancer
- `nevus`: Common mole
- `basal_cell_carcinoma`: Non-melanoma skin cancer
- `actinic_keratosis`: Precancerous lesion
- `benign_keratosis`: Benign, non-cancerous lesion
- `dermatofibroma`: Fibrous growth in dermis
- `vascular_lesion`: Blood vessel-related lesion

## Getting Started

### Prerequisites
- Python 3.11+ (3.14+ not recommended for TensorFlow compatibility)
- pip
- virtualenv

### Installation

1. **Clone or navigate to the project:**
```bash
cd skin_diagnosis_backend
```

2. **Create and activate virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Apply migrations:**
```bash
python manage.py migrate
```

5. **Create superuser:**
```bash
python manage.py createsuperuser
```

6. **Run development server:**
```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000/api/`

## Admin Portal

Access the Django admin panel at `http://localhost:8000/admin/`

Features:
- View all diagnosis results
- Filter by condition and date
- Search by patient ID or filename
- View image previews
- Edit clinical notes
- Delete records

## Feature Highlights

### 1. TensorFlow Model Integration
- Uses MobileNetV2 transfer learning
- 7-class skin lesion classification
- Confidence scoring for each prediction

### 2. Image Preprocessing
- Automatic format conversion (RGB)
- Resizing to model input size (224x224)
- Normalization to 0-1 range

### 3. Medical Data Management
- Patient ID tracking
- Clinical notes storage
- Timestamp tracking
- Image upload and storage

### 4. REST API
- Standard HTTP methods (GET, POST, PUT, DELETE)
- JSON request/response format
- Comprehensive error handling
- Pagination support

## Example Usage

### Using cURL

```bash
# Make a prediction
curl -X POST http://localhost:8000/api/diagnoses/predict/ \
  -F "image=@/path/to/lesion.jpg" \
  -F "patient_id=P001" \
  -F "notes=Right arm lesion"

# Get all diagnoses
curl http://localhost:8000/api/diagnoses/

# Get diagnosis details
curl http://localhost:8000/api/diagnoses/1/details/

# Get recent history
curl http://localhost:8000/api/diagnoses/history/

# Update diagnosis notes
curl -X PUT http://localhost:8000/api/diagnoses/1/ \
  -H "Content-Type: application/json" \
  -d '{"notes": "Updated notes"}'

# Delete diagnosis
curl -X DELETE http://localhost:8000/api/diagnoses/1/
```

### Using Python Requests

```python
import requests
from PIL import Image

# Make a prediction
with open('lesion.jpg', 'rb') as img:
    files = {'image': img}
    data = {'patient_id': 'P001', 'notes': 'Right arm lesion'}
    response = requests.post(
        'http://localhost:8000/api/diagnoses/predict/',
        files=files,
        data=data
    )
    print(response.json())
```

## Model Training

To train a custom model:

```python
from diagnosis.ml_model import SkinDiagnosisModel
import tensorflow as tf

# Create the model
model = SkinDiagnosisModel()

# Train on your data
# (Add your training code here)

# Save the model
model.model.save('path/to/model.h5')
```

## Settings

### Update ALLOWED_HOSTS
In `skin_diagnosis_backend/settings.py`:
```python
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'your-domain.com']
```

### Enable CORS (if needed)
```bash
pip install django-cors-headers
```

Add to `settings.py`:
```python
INSTALLED_APPS = [
    ...
    'corsheaders',
    ...
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    ...
]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8080",
]
```

## Deployment

### Production Checklist
1. Set `DEBUG = False` in settings.py
2. Update `ALLOWED_HOSTS` with your domain
3. Use environment variables for `SECRET_KEY`
4. Configure a production database (PostgreSQL recommended)
5. Use a production-grade server (Gunicorn, uWSGI)
6. Enable HTTPS with SSL certificates
7. Configure CORS for your frontend

### Using Gunicorn

```bash
pip install gunicorn
gunicorn skin_diagnosis_backend.wsgi:application --bind 0.0.0.0:8000
```

### Using AWS/Heroku/Azure

Refer to the specific platform's Django deployment documentation.

## Performance Considerations

- Image preprocessing is done on-the-fly; consider caching for large deployments
- Use database indexing for patient_id and created_at fields
- Consider implementing request rate limiting
- Use CDN for media files in production

## Troubleshooting

### TensorFlow Not Found
The project includes a fallback mock model. Install TensorFlow with:
```bash
pip install tensorflow==2.21.0
```

### Port Already in Use
```bash
python manage.py runserver 8001
```

### Database Issues
Reset the database:
```bash
rm db.sqlite3
python manage.py migrate
python manage.py createsuperuser
```

## License
Open source project

## Contact & Support
For issues or requests, please create an issue in the project repository.
