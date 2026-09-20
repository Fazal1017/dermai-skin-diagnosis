#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test the Django API with a real skin image from the dataset.
This script will:
1. Find a real skin image from the dataset
2. Send it to the API for prediction
3. Display the result
"""

import os
import sys
import requests
import random
from pathlib import Path

# Configuration
DATASET_PATH = r"C:\Users\FAZAL\OneDrive\Desktop\charmada rog\dataset"
API_URL = "http://127.0.0.1:8000/api/diagnoses/predict/"

def find_random_image():
    """Find a random image from the dataset"""
    dataset_dir = Path(DATASET_PATH)
    
    if not dataset_dir.exists():
        print(f"[ERROR] Dataset path not found: {dataset_dir.resolve()}")
        return None
    
    # Find all images in any subdirectory
    image_files = list(dataset_dir.rglob('*.jpg')) + list(dataset_dir.rglob('*.png')) + list(dataset_dir.rglob('*.jpeg'))
    
    if not image_files:
        print(f"[ERROR] No images found in {dataset_dir.resolve()}")
        return None
    
    return random.choice(image_files)


def test_api_prediction(image_path):
    """Send image to API and get prediction"""
    
    if not os.path.exists(image_path):
        print(f"[ERROR] Image not found: {image_path}")
        return False
    
    print(f"\n[INFO] Testing API with image: {image_path}")
    print(f"[INFO] Image size: {os.path.getsize(image_path) / 1024:.1f} KB")
    
    try:
        with open(image_path, 'rb') as f:
            files = {
                'image': (os.path.basename(image_path), f, 'image/jpeg')
            }
            data = {
                'patient_id': 'TEST_001',
                'notes': 'API test prediction'
            }
            
            print(f"\n[INFO] Sending request to {API_URL}...")
            response = requests.post(API_URL, files=files, data=data)
        
        if response.status_code == 201:
            result = response.json()
            
            print("\n[SUCCESS] Prediction received!")
            print("-" * 60)
            print(f"Predicted Condition: {result['predicted_condition']}")
            print(f"Confidence: {result['confidence_score']:.2%}")
            print("\nAll Predictions:")
            
            for condition, score in sorted(result['all_predictions'].items(), 
                                          key=lambda x: x[1], 
                                          reverse=True):
                print(f"  {condition:<25} {score:>6.2%}")
            
            print("-" * 60)
            print(f"\nDiagnosis ID: {result['diagnosis_result']['id']}")
            print(f"Timestamp: {result['diagnosis_result']['created_at']}")
            return True
        else:
            print(f"[ERROR] API returned status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("[ERROR] Could not connect to API")
        print("Is the Django server running? (python manage.py runserver)")
        return False
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("=" * 60)
    print("[TEST] Django API Prediction Test")
    print("=" * 60)
    
    # Find a random image
    print("\n[INFO] Looking for test image in dataset...")
    image_path = find_random_image()
    
    if not image_path:
        print("[ERROR] Could not find test image")
        sys.exit(1)
    
    # Test the API
    success = test_api_prediction(str(image_path))
    
    if not success:
        sys.exit(1)
    
    print("\n[SUCCESS] API test completed successfully!")
    print("\nAPI is ready for production use.")


if __name__ == '__main__':
    main()
