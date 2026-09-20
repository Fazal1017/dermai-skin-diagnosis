#!/usr/bin/env python
"""
Dataset validation script
Checks if dataset is properly organized before training
"""

import os
import sys
from pathlib import Path
from PIL import Image

def check_dataset(dataset_path):
    """Validate dataset structure and content"""
    
    print("=" * 60)
    print("DATASET VALIDATION Script")
    print("=" * 60)
    
    # Check if dataset path exists
    if not os.path.exists(dataset_path):
        print(f"❌ Dataset path not found: {dataset_path}")
        return False
    
    print(f"✅ Dataset path found: {dataset_path}")
    
    # Expected classes
    expected_classes = [
        'melanoma',
        'nevus',
        'basal_cell_carcinoma',
        'actinic_keratosis',
        'benign_keratosis',
        'dermatofibroma',
        'vascular_lesion'
    ]
    
    # Check for class directories
    print("\n" + "-" * 60)
    print("Checking class folders...")
    print("-" * 60)
    
    missing_classes = []
    found_classes = {}
    
    for class_name in expected_classes:
        class_path = os.path.join(dataset_path, class_name)
        
        if os.path.isdir(class_path):
            # Count images
            images = [f for f in os.listdir(class_path) 
                     if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            found_classes[class_name] = len(images)
            
            status = "✅" if len(images) >= 100 else "⚠️"
            print(f"{status} {class_name}: {len(images)} images", end="")
            
            if len(images) < 100:
                print(" (need at least 100)")
            else:
                print()
        else:
            missing_classes.append(class_name)
            print(f"❌ {class_name}: NOT FOUND")
    
    # Summary
    print("\n" + "-" * 60)
    print("SUMMARY")
    print("-" * 60)
    
    total_images = sum(found_classes.values())
    total_classes = len(found_classes)
    
    print(f"Classes found: {total_classes}/7")
    print(f"Total images: {total_images}")
    print(f"Images per class:")
    for class_name, count in sorted(found_classes.items()):
        avg_needed = 100
        percent = (count / avg_needed) * 100
        bar = "█" * int(percent / 5) + "░" * (20 - int(percent / 5))
        print(f"  {class_name:.<30} {count:>4} [{bar}]")
    
    # Validation checks
    print("\n" + "-" * 60)
    print("VALIDATION CHECKS")
    print("-" * 60)
    
    all_good = True
    
    # Check 1: All classes present
    if len(missing_classes) == 0:
        print("✅ All 7 classes present")
    else:
        print(f"❌ Missing classes: {', '.join(missing_classes)}")
        all_good = False
    
    # Check 2: Minimum images per class
    min_images = min(found_classes.values()) if found_classes else 0
    if min_images >= 100:
        print(f"✅ All classes have at least 100 images (minimum: {min_images})")
    else:
        print(f"⚠️  Some classes have fewer than 100 images (minimum: {min_images})")
        all_good = False
    
    # Check 3: Total images
    if total_images >= 700:
        print(f"✅ Good amount of data ({total_images} images total)")
    else:
        print(f"⚠️  Consider adding more images ({total_images} images total, target: 700+)")
        all_good = False
    
    # Check 4: Image format validation (sample check)
    print("\n" + "-" * 60)
    print("IMAGE FORMAT CHECK (sampling 3 images)")
    print("-" * 60)
    
    format_ok = True
    checked = 0
    
    for class_name in found_classes:
        if checked >= 3:
            break
        
        class_path = os.path.join(dataset_path, class_name)
        images = [f for f in os.listdir(class_path) 
                 if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        
        if images:
            img_path = os.path.join(class_path, images[0])
            try:
                img = Image.open(img_path)
                print(f"✅ {images[0]}: {img.format} {img.size}")
                checked += 1
            except Exception as e:
                print(f"❌ {images[0]}: Error - {e}")
                format_ok = False
    
    # Final recommendation
    print("\n" + "=" * 60)
    print("RECOMMENDATION")
    print("=" * 60)
    
    if all_good and format_ok:
        print("✅ Dataset is ready for training!")
        print("\nYou can now run:")
        print("  python diagnosis/train_model.py --dataset ./dataset")
        return True
    else:
        print("⚠️  Dataset needs more preparation")
        print("\nBefore training, please:")
        if missing_classes:
            print(f"  1. Add images for: {', '.join(missing_classes)}")
        if min_images < 100:
            print(f"  2. Add more images (need at least 100 per class)")
        if not format_ok:
            print(f"  3. Verify image formats are .jpg, .jpeg, or .png")
        return False


def print_usage():
    """Print usage instructions"""
    print("""
USAGE:
  python validate_dataset.py [dataset_path]

EXAMPLES:
  python validate_dataset.py                    # Check './dataset' folder
  python validate_dataset.py ../dataset         # Check '../dataset' folder
  python validate_dataset.py /absolute/path     # Check specific path
    """)


if __name__ == '__main__':
    # Get dataset path from arguments or use default
    if len(sys.argv) > 1:
        dataset_path = sys.argv[1]
    else:
        # Default path relative to this script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        dataset_path = os.path.join(script_dir, '../../dataset')
    
    # Make path absolute
    dataset_path = os.path.abspath(dataset_path)
    
    # Validate
    success = check_dataset(dataset_path)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)
