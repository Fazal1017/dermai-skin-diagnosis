"""
Organize a locally downloaded/extracted HAM10000 dataset into project `dataset/`

Usage:
  python organize_local_ham10000.py --source "C:/path/to/HAM10000" 

The script expects the HAM10000 extracted folder to contain image files and a
CSV metadata file (e.g., HAM10000_metadata.csv). It will create the
`dataset/` folder at the project root and copy images into the 7 class
subfolders matching the project's labels.
"""
import os
import sys
import argparse
import csv
import shutil
from pathlib import Path

HAM_MAP = {
    'MEL': 'melanoma',
    'NV': 'nevus',
    'BCC': 'basal_cell_carcinoma',
    'AKIEC': 'actinic_keratosis',
    'BKL': 'benign_keratosis',
    'DF': 'dermatofibroma',
    'VASC': 'vascular_lesion'
}

parser = argparse.ArgumentParser(description='Organize local HAM10000 into project dataset folder')
parser.add_argument('--source', '-s', required=True, help='Path to extracted HAM10000 folder')
args = parser.parse_args()

source = os.path.abspath(args.source)
if not os.path.isdir(source):
    print(f"Source path not found: {source}")
    sys.exit(1)

# Project root = parent of this file's parent (same as other scripts)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
DATASET_DIR = os.path.join(PROJECT_ROOT, 'dataset')

os.makedirs(DATASET_DIR, exist_ok=True)
for v in HAM_MAP.values():
    os.makedirs(os.path.join(DATASET_DIR, v), exist_ok=True)

# Find CSV metadata
csv_paths = list(Path(source).rglob('*.csv'))
metadata = {}
if csv_paths:
    # Prefer HAM10000_metadata.csv if present
    csv_file = None
    for p in csv_paths:
        if 'HAM10000' in p.name.upper() or 'METADATA' in p.name.upper():
            csv_file = p
            break
    if not csv_file:
        csv_file = csv_paths[0]
    print(f"Using metadata file: {csv_file}")
    with open(csv_file, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            image_id = row.get('image_id')
            diag = row.get('dx') or row.get('diagnosis') or row.get('dx_type')
            if image_id and diag:
                metadata[image_id] = diag
else:
    print("No CSV metadata found in source folder. Proceeding without metadata.")

# Collect image files
image_files = [p for p in Path(source).rglob('*') if p.suffix.lower() in ('.jpg','.jpeg','.png')]
print(f"Found {len(image_files)} image files in source")

copied = 0
skipped = 0
for p in image_files:
    image_id = p.stem
    target_class = None
    diag = metadata.get(image_id)
    if diag:
        diag = diag.strip().upper()
        # Some diag values are codes like 'nv' or full names
        if diag in HAM_MAP:
            target_class = HAM_MAP[diag]
        else:
            # Try to map full names by checking first 4 letters
            for code, cls in HAM_MAP.items():
                if code in diag or cls.replace('_',' ').upper() in diag:
                    target_class = cls
                    break
    # Fallback: try to infer from path
    if not target_class:
        path_upper = str(p.parent).upper()
        for code, cls in HAM_MAP.items():
            if code in path_upper or cls.replace('_',' ').upper() in path_upper:
                target_class = cls
                break
    if not target_class:
        skipped += 1
        continue
    dest = os.path.join(DATASET_DIR, target_class, p.name)
    try:
        shutil.copy2(p, dest)
        copied += 1
    except Exception as e:
        print(f"Failed to copy {p}: {e}")
        skipped += 1

print(f"Copied {copied} images into {DATASET_DIR}")
print(f"Skipped {skipped} images (no class mapping)")
print("Done. You can now run: python diagnosis/validate_dataset.py ../../dataset")
