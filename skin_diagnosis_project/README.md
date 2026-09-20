# Skin Diagnosis Project

A comprehensive skin lesion diagnosis system using Django REST Framework and TensorFlow/Keras for machine learning-powered dermatological image analysis.

## 🎯 Features

✅ **Deep Learning Model**
- MobileNetV2 transfer learning architecture
- 7-class skin lesion classification
- High accuracy predictions with confidence scores

✅ **REST API**
- Django REST Framework for robust API
- Multiple endpoints for predictions and history
- Comprehensive error handling

✅ **Medical Data Management**
- Patient ID tracking
- Clinical notes storage
- Diagnosis history
- Image uploads with storage

✅ **Admin Dashboard**
- Django admin interface
- Visual diagnosis management
- Image preview functionality
- Search and filtering

✅ **Production Ready**
- Database migrations
- User authentication
- CSRF protection
- Scalable architecture

## 📁 Project Structure

```
skin_diagnosis_project/
├── requirements.txt                    # Python dependencies
├── skin_diagnosis_backend/             # Django project
│   ├── manage.py
│   ├── db.sqlite3                      # Development database
│   ├── API_DOCUMENTATION.md            # Detailed API docs
│   ├── diagnosis/                      # Main application
│   │   ├── models.py                   # DiagnosisResult model
│   │   ├── views.py                    # API views
│   │   ├── serializers.py              # Data serialization
│   │   ├── urls.py                     # App URLs
│   │   ├── admin.py                    # Admin configuration
│   │   ├── ml_model.py                 # TensorFlow model
│   │   ├── migrations/                 # Database migrations
│   │   └── tests.py                    # Unit tests
│   ├── skin_diagnosis_backend/         # Project config
│   │   ├── settings.py                 # Django settings
│   │   ├── urls.py                     # Main URL router
│   │   ├── asgi.py
│   │   └── wsgi.py
│   └── media/                          # User uploaded images
└── venv/                               # Virtual environment
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11 or higher (3.13 recommended)
- pip and virtualenv
- At least 2GB free disk space (for TensorFlow)

### Setup Instructions

1. **Clone/Navigate to project:**
```bash
cd skin_diagnosis_project
```

2. **Create and activate virtual environment:**
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Run migrations (already done):**
```bash
cd skin_diagnosis_backend
python manage.py migrate
```

5. **Create superuser (if not done):**
```bash
python manage.py createsuperuser
```

6. **Start development server:**
```bash
python manage.py runserver
```

7. **Access the application:**
   - API: http://localhost:8000/api/
   - Admin: http://localhost:8000/admin/
   - Prediction endpoint: http://localhost:8000/api/diagnoses/predict/

## 📚 API Quick Reference

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/diagnoses/predict/` | POST | Make a skin diagnosis prediction |
| `/api/diagnoses/` | GET | List all diagnoses |
| `/api/diagnoses/{id}/` | GET | Get specific diagnosis |
| `/api/diagnoses/{id}/details/` | GET | Get detailed diagnosis info |
| `/api/diagnoses/history/` | GET | Get recent diagnoses (10) |
| `/api/diagnoses/{id}/` | PUT | Update diagnosis notes |
| `/api/diagnoses/{id}/` | DELETE | Delete a diagnosis |

## 📸 Making Predictions

### Using cURL:
```bash
curl -X POST http://localhost:8000/api/diagnoses/predict/ \
  -F "image=@lesion.jpg" \
  -F "patient_id=P001" \
  -F "notes=Right arm lesion"
```

### Using Python:
```python
import requests

with open('lesion.jpg', 'rb') as img:
    files = {'image': img}
    data = {'patient_id': 'P001', 'notes': 'Lesion on arm'}
    response = requests.post(
        'http://localhost:8000/api/diagnoses/predict/',
        files=files,
        data=data
    )
print(response.json())
```

## 🏥 Supported Skin Conditions

The model classifies lesions into 7 categories:
1. **Melanoma** - Malignant skin cancer
2. **Nevus** - Common mole
3. **Basal Cell Carcinoma** - Non-melanoma skin cancer
4. **Actinic Keratosis** - Precancerous lesion
5. **Benign Keratosis** - Non-cancerous lesion
6. **Dermatofibroma** - Fibrous tissue growth
7. **Vascular Lesion** - Blood vessel-related lesion

## ⚙️ Configuration

### Settings File Location
`skin_diagnosis_backend/skin_diagnosis_backend/settings.py`

### Key Settings to Modify

**Allowed Hosts (for production):**
```python
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']
```

**Database (production):**
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'skin_diagnosis_db',
        'USER': 'db_user',
        'PASSWORD': 'secure_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

**Debug Mode:**
```python
DEBUG = False  # Set to False in production
```

## 📊 Database Schema

### DiagnosisResult Model
```python
- id: Primary Key
- image: ImageField (uploaded image)
- image_filename: CharField
- predicted_condition: CharField (7 choices)
- confidence_score: FloatField (0-1)
- all_predictions: JSONField (all class scores)
- patient_id: CharField (optional)
- notes: TextField (optional)
- created_at: DateTimeField
- updated_at: DateTimeField
```

## 🔧 Development Commands

```bash
# Create app migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run tests
python manage.py test

# Django shell
python manage.py shell

# Collect static files
python manage.py collectstatic

# Check for issues
python manage.py check
```

## 🚢 Deployment

### Deploy to Heroku
```bash
heroku login
heroku create your-app-name
heroku config:set DEBUG=False
git push heroku main
heroku run python manage.py migrate
heroku run python manage.py createsuperuser
```

### Deploy to AWS
Use Elastic Beanstalk:
```bash
eb init -p python-3.11 skin-diagnosis
eb create production
eb deploy
```

### Deploy to Docker
Create a `Dockerfile`:
```dockerfile
FROM python:3.11

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["gunicorn", "skin_diagnosis_backend.wsgi:application", "--bind", "0.0.0.0:8000"]
```

## 📁 Media Files Storage

Uploaded images are stored in `media/diagnosis_images/`

For production, configure cloud storage:
```bash
pip install django-storages boto3  # For AWS S3
```

## 🔒 Security Considerations

- ✅ CSRF protection enabled
- ✅ SQL injection protection via ORM
- ✅ XSS protection enabled
- ⚠️ Use HTTPS in production
- ⚠️ Set `SECRET_KEY` from environment variables
- ⚠️ Configure CORS properly for frontend

## 📝 Environment Variables

Create a `.env` file:
```
DEBUG=False
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com
DB_ENGINE=django.db.backends.postgresql
DB_NAME=skin_diagnosis_db
DB_USER=postgres
DB_PASSWORD=password
DB_HOST=localhost
DB_PORT=5432
```

## 🐛 Troubleshooting

### Issue: TensorFlow Import Error
**Solution:**
```bash
pip install tensorflow==2.21.0
```

### Issue: Port 8000 Already in Use
**Solution:**
```bash
python manage.py runserver 8001
```

### Issue: Database Locked
**Solution:**
```bash
rm db.sqlite3
python manage.py migrate
```

### Issue: Static Files Not Loading
**Solution:**
```bash
python manage.py collectstatic --noinput
```

## 📖 API Documentation

For detailed API documentation, see [API_DOCUMENTATION.md](./skin_diagnosis_backend/API_DOCUMENTATION.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

## 📞 Support

For issues and questions:
- Create an issue in the GitHub repository
- Check existing documentation
- Review API logs in Django admin

## 🎓 Model Information

### Architecture
- **Base Model:** MobileNetV2 (pre-trained on ImageNet)
- **Transfer Learning:** Yes
- **Input Size:** 224x224x3
- **Output Classes:** 7
- **Optimization:** Adam with categorical cross-entropy loss

### Performance
- **Inference Time:** ~200-300ms per image
- **Memory Usage:** ~500MB
- **Storage:** ~150MB (model weights)

## 🗺️ Roadmap

- [ ] Real-time model predictions
- [ ] Batch prediction API
- [ ] Advanced reporting and analytics
- [ ] Multi-model ensemble support
- [ ] Mobile app backend integration
- [ ] Patient management system
- [ ] Electronic health records (EHR) integration
- [ ] HIPAA compliance features

## 📚 Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [TensorFlow Documentation](https://www.tensorflow.org/docs)
- [Keras API](https://keras.io/api/)
- [Python Requests](https://requests.readthedocs.io/)

---

**Current Status:** ✅ Development Complete
**Last Updated:** April 21, 2026
**Version:** 1.0.0
