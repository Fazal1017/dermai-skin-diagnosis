"""
Download and Organize HAM10000 Dataset for Skin Diagnosis

This script:
1. Downloads HAM10000 dataset from Kaggle using kagglehub
2. Extracts and organizes images into the project's dataset folder
3. Automatically maps HAM10000 class labels to your project's 7 skin conditions

Usage:
    python download_dataset.py

Prerequisites:
    - Kaggle account (free)
    - Kaggle API token saved at ~/.kaggle/kaggle.json
    - Install: pip install kagglehub
"""

import os
import sys
import shutil
import csv
import json
from pathlib import Path
from tqdm import tqdm

# Check if kagglehub is installed
try:
    import kagglehub
except ImportError:
    print("[ERROR] kagglehub not installed!")
    print("Install with: pip install kagglehub")
    sys.exit(1)

# ============================================================================
# --- CONFIGURATION ---
# ============================================================================

KAGGLE_DATASET = "kmader/skin-cancer-mnist-ham10000"

# Get project root directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
DATASET_DIR = os.path.join(PROJECT_ROOT, 'dataset')

print("=" * 80)
print("              HAM10000 DATASET DOWNLOADER & ORGANIZER")
print("=" * 80)

print(f"\n[INFO] Project root: {PROJECT_ROOT}")
print(f"[INFO] Dataset destination: {DATASET_DIR}")

# ============================================================================
# --- STEP 1: DOWNLOAD DATASET ---
# ============================================================================

print("\n" + "=" * 80)
print("[Step 1] Downloading HAM10000 dataset from Kaggle...")
print("=" * 80)

# Check if Kaggle credentials are set up
kaggle_json = Path.home() / '.kaggle' / 'kaggle.json'
if not kaggle_json.exists():
    print(f"\n[ERROR] Kaggle API token not found!")
    print(f"        Location: {kaggle_json}")
    print(f"\n[INSTRUCTIONS]")
    print(f"  1. Go to: https://www.kaggle.com/account/api")
    print(f"  2. Click 'Create New API Key'")
    print(f"  3. Save the kaggle.json file to: ~/.kaggle/")
    print(f"  4. Set permissions: chmod 600 ~/.kaggle/kaggle.json (on Linux/Mac)")
    print(f"\n  Or on Windows:")
    print(f"  1. Download kaggle.json from Kaggle")
    print(f"  2. Save to: {kaggle_json}")
    print(f"  3. Run this script again")
    sys.exit(1)

print(f"[✓] Kaggle credentials found at: {kaggle_json}")

print(f"\n[INFO] Downloading from Kaggle: {KAGGLE_DATASET}")
print(f"       This may take a few minutes (dataset is ~25,000 images, ~2.5GB)...")

try:
    downloaded_path = kagglehub.dataset_download(KAGGLE_DATASET)
    print(f"\n[✓] Dataset downloaded to: {downloaded_path}")
except Exception as e:
    print(f"\n[ERROR] Failed to download dataset:")
    print(f"        {str(e)}")
    print(f"\n[HINT] Make sure your Kaggle API token is valid")
    sys.exit(1)

# ============================================================================
# --- STEP 2: UNDERSTAND DATASET STRUCTURE ---
# ============================================================================

print("\n" + "=" * 80)
print("[Step 2] Understanding dataset structure...")
print("=" * 80)

# HAM10000 class mapping
HAM10000_CLASS_MAP = {
    'MEL': 'melanoma',
    'NV': 'nevus',
    'BCC': 'basal_cell_carcinoma',
    'AKIEC': 'actinic_keratosis',
    'BKL': 'benign_keratosis',
    'DF': 'dermatofibroma',
    'VASC': 'vascular_lesion'
}

print("\n[INFO] HAM10000 to Project Class Mapping:")
for ham_class, project_class in HAM10000_CLASS_MAP.items():
    print(f"       {ham_class} → {project_class}")

# Look for metadata file
metadata_files = list(Path(downloaded_path).glob('**/*metadata*'))
if metadata_files:
    print(f"\n[INFO] Found metadata files: {len(metadata_files)}")
    for mf in metadata_files:
        print(f"       - {mf.name}")

# Look for image files
image_extensions = ('.jpg', '.jpeg', '.png')
image_files = [f for f in Path(downloaded_path).rglob('*') 
               if f.is_file() and f.suffix.lower() in image_extensions]

print(f"\n[INFO] Found {len(image_files)} image files")

# ============================================================================
# --- STEP 3: CREATE PROJECT DATASET DIRECTORIES ---
# ============================================================================

print("\n" + "=" * 80)
print("[Step 3] Creating project dataset directories...")
print("=" * 80)

# Create dataset directory structure
os.makedirs(DATASET_DIR, exist_ok=True)

class_dirs = {}
for project_class in HAM10000_CLASS_MAP.values():
    class_path = os.path.join(DATASET_DIR, project_class)
    os.makedirs(class_path, exist_ok=True)
    class_dirs[project_class] = class_path
    print(f"[✓] Created: {class_path}")

# ============================================================================
# --- STEP 4: ORGANIZE IMAGES ---
# ============================================================================

print("\n" + "=" * 80)
print("[Step 4] Organizing images into class folders...")
print("=" * 80)

# Look for CSV metadata in HAM10000 format
csv_files = list(Path(downloaded_path).glob('**/*.csv'))
ham_metadata = {}

if csv_files:
    print(f"[INFO] Found CSV metadata file")
    for csv_file in csv_files:
        if 'HAM10000_metadata' in csv_file.name or 'metadata' in csv_file.name:
            print(f"       Reading: {csv_file.name}")
            try:
                with open(csv_file, 'r') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        image_id = row.get('image_id')
                        diagnosis = row.get('diagnosis')
                        if image_id and diagnosis:
                            ham_metadata[image_id] = diagnosis
                print(f"       Loaded metadata for {len(ham_metadata)} images")
            except Exception as e:
                print(f"       [WARNING] Could not read CSV: {e}")

# Organize images
files_organized = 0
files_skipped = 0

print(f"\nOrganizing images...")
progress_bar = tqdm(total=len(image_files), desc="Organizing", unit="file")

for image_path in image_files:
    image_name = image_path.stem  # Without extension
    extension = image_path.suffix
    
    # Try to find class from metadata
    target_class = None
    
    # Method 1: Look in CSV metadata
    if image_name in ham_metadata:
        ham_class = ham_metadata[image_name]
        if ham_class in HAM10000_CLASS_MAP:
            target_class = HAM10000_CLASS_MAP[ham_class]
    
    # Method 2: Try to extract from folder structure
    if not target_class:
        # Check if image is in a class-specific folder
        for ham_code, project_class in HAM10000_CLASS_MAP.items():
            if ham_code in str(image_path).upper():
                target_class = project_class
                break
    
    # Method 3: Check if image path contains disease indicators
    if not target_class:
        path_str = str(image_path).upper()
        for ham_code, project_class in HAM10000_CLASS_MAP.items():
            if ham_code in path_str:
                target_class = project_class
                break
    
    # If we found a target class, copy the image
    if target_class and target_class in class_dirs:
        dest_path = os.path.join(class_dirs[target_class], image_name + extension)
        try:
            shutil.copy2(image_path, dest_path)
            files_organized += 1
        except Exception as e:
            files_skipped += 1
    else:
        files_skipped += 1
    
    progress_bar.update(1)

progress_bar.close()

# ============================================================================
# --- STEP 5: VERIFY AND REPORT ---
# ============================================================================

print("\n" + "=" * 80)
print("[Step 5] Verification and Summary")
print("=" * 80)

print(f"\n[RESULTS]")
print(f"  Files organized: {files_organized}")
print(f"  Files skipped: {files_skipped}")

print(f"\n[CLASS DISTRIBUTION]")
for project_class in sorted(HAM10000_CLASS_MAP.values()):
    class_path = class_dirs[project_class]
    image_count = len([f for f in os.listdir(class_path) 
                      if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
    status = "✓" if image_count > 0 else "✗"
    print(f"  {status} {project_class:.<30} {image_count:>5} images")

total_images = sum(len([f for f in os.listdir(class_dirs[c]) 
                        if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
                   for c in class_dirs)

print(f"\n  Total images: {total_images}")

# ============================================================================
# --- STEP 6: READY FOR TRAINING ---
# ============================================================================

if total_images > 0:
    print("\n" + "=" * 80)
    print("✅ DATASET READY FOR TRAINING!")
    print("=" * 80)
    
    print(f"\n[NEXT STEPS]")
    print(f"  1. Navigate to: skin_diagnosis_backend/")
    print(f"  2. Run training script:")
    print(f"     python diagnosis/train_model.py --epochs 20")
    print(f"\n[OPTIONAL] Validate dataset first:")
    print(f"     python diagnosis/validate_dataset.py ../../dataset")
    
else:
    print("\n[WARNING] No images were organized!")
    print("          Check the CSV metadata file format")

print("\n" + "=" * 80)
