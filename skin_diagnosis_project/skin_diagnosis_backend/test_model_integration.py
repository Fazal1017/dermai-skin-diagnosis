#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify the trained model integrates correctly with Django.
Run this BEFORE starting the server to catch any issues early.
"""

import os
import sys
import io
import django

# Fix encoding for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skin_diagnosis_backend.settings')
django.setup()

from diagnosis.ml_model import SkinDiagnosisModel
from PIL import Image
import numpy as np

def test_model_loading():
    """Test 1: Can we load the model?"""
    print("=" * 60)
    print("Test 1: Loading trained model...")
    print("=" * 60)
    
    try:
        model = SkinDiagnosisModel()
        print("[OK] Model loaded successfully!")
        print("   Device: " + str(model.device))
        print("   Classes: " + str(model.classes))
        print("   Number of classes: " + str(len(model.classes)))
        return True, model
    except Exception as e:
        print("[ERROR] Failed to load model: " + str(e))
        import traceback
        traceback.print_exc()
        return False, None


def test_model_prediction(model):
    """Test 2: Can we make a prediction?"""
    print("\n" + "=" * 60)
    print("Test 2: Making a test prediction...")
    print("=" * 60)
    
    try:
        # Create a dummy image (224x224 RGB)
        dummy_image = np.random.randint(0, 256, (224, 224, 3), dtype=np.uint8)
        
        # Normalize to 0-1 range
        dummy_array = dummy_image.astype(np.float32) / 255.0
        
        # Add batch dimension
        dummy_array = np.expand_dims(dummy_array, axis=0)
        
        # Make prediction
        predicted_condition, all_scores = model.predict(dummy_array)
        
        print("[OK] Prediction successful!")
        print("   Predicted condition: " + predicted_condition)
        print("   Confidence: {:.4f}".format(max(all_scores.values())))
        print("\n   All predictions:")
        for condition, score in sorted(all_scores.items(), key=lambda x: x[1], reverse=True):
            print("     - {}: {:.4f}".format(condition, score))
        return True
    except Exception as e:
        print("[ERROR] Prediction failed: " + str(e))
        import traceback
        traceback.print_exc()
        return False


def test_django_integration():
    """Test 3: Can Django load the model through views?"""
    print("\n" + "=" * 60)
    print("Test 3: Django integration...")
    print("=" * 60)
    
    try:
        from diagnosis.views import get_model
        model = get_model()
        print("[OK] Django can access the model!")
        print("   Model type: " + type(model).__name__)
        return True
    except Exception as e:
        print("[ERROR] Django integration failed: " + str(e))
        import traceback
        traceback.print_exc()
        return False


def main():
    print("\n[TEST] TESTING MODEL-DJANGO INTEGRATION\n")
    
    # Run tests
    success1, model = test_model_loading()
    
    if not success1:
        print("\n[ERROR] Tests failed. Cannot proceed.\n")
        sys.exit(1)
    
    success2 = test_model_prediction(model)
    success3 = test_django_integration()
    
    print("\n" + "=" * 60)
    if success2 and success3:
        print("[SUCCESS] ALL TESTS PASSED!")
        print("=" * 60)
        print("\n[INFO] Your model is ready! You can now:")
        print("   1. Start the Django server: python manage.py runserver")
        print("   2. Test the API endpoint: POST /api/diagnoses/predict/")
        print("\n")
    else:
        print("[ERROR] Some tests failed. Please check the errors above.")
        print("=" * 60)
        sys.exit(1)


if __name__ == '__main__':
    main()
