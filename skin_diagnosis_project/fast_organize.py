#!/usr/bin/env python3
"""
Fast image organization script using OS commands for better performance
"""
import os
import csv
import sys
from pathlib import Path

# HAM10000 diagnosis to folder mapping
HAM_MAP = {
    'MEL': 'melanoma',
    'NV': 'nevus',
    'BCC': 'basal_cell_carcinoma',
    'AKIEC': 'actinic_keratosis',
    'BKL': 'benign_keratosis',
    'DF': 'dermatofibroma',
    'VASC': 'vascular_lesion'
}

source_base = r"C:\Users\FAZAL\OneDrive\Desktop\charmada rog\skin_diagnosis_project\dataset\IMAGES OF SKIN DISEASES"
dataset_root = r"C:\Users\FAZAL\OneDrive\Desktop\charmada rog\skin_diagnosis_project\dataset"

# Read metadata
metadata = {}
csv_path = os.path.join(source_base, "HAM10000_metadata.csv")
print(f"Reading metadata from: {csv_path}")
with open(csv_path, 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        img_id = row.get('image_id', '').strip()
        dx = row.get('dx', '').strip().upper()
        if img_id and dx:
            metadata[img_id] = HAM_MAP.get(dx, '')

print(f"Loaded metadata for {len(metadata)} images")

# Count images to organize
img_part1 = Path(source_base) / "HAM10000_images_part_1"
img_part2 = Path(source_base) / "HAM10000_images_part_2"

images = list(img_part1.glob('*.jpg')) + list(img_part2.glob('*.jpg'))
print(f"Found {len(images)} images to organize")

# Organize using PowerShell commands for speed
copied = 0
skipped = 0

for img_path in images:
    img_id = img_path.stem
    target_class = metadata.get(img_id)
    
    if not target_class:
        skipped += 1
        continue
    
    dest_folder = os.path.join(dataset_root, target_class)
    dest_path = os.path.join(dest_folder, img_path.name)
    
    try:
        os.makedirs(dest_folder, exist_ok=True)
        # Use fast copy
        os.system(f'copy "{img_path}" "{dest_path}" >nul 2>&1')
        copied += 1
        
        if copied % 500 == 0:
            print(f"  Progress: {copied} images copied...")
    except Exception as e:
        print(f"Error: {e}")
        skipped += 1

print(f"\n✓ Completed!")
print(f"  - Copied: {copied} images")
print(f"  - Skipped: {skipped} images")
print(f"\nImage distribution:")
for cls_folder in HAM_MAP.values():
    folder_path = os.path.join(dataset_root, cls_folder)
    count = len(list(Path(folder_path).glob('*.jpg')))
    print(f"  - {cls_folder}: {count}")
