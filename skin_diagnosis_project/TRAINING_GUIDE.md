# 🚀 Quick Training Guide

## What Was Created

Your CNN training scripts are now ready to use:

| File | Location | Purpose |
|------|----------|---------|
| `train_model.py` | `skin_diagnosis_backend/diagnosis/` | **Main training script** (recommended) |
| `train_simple.py` | `skin_diagnosis_backend/` | Alternative training script |

Both scripts do the same thing but are in different locations for flexibility.

---

## Quick Start (3 Steps)

### Step 1: Prepare Your Dataset

Organize your dataset like this:
```
dataset/
├── melanoma/          (add .jpg/.png images here)
├── nevus/             (add .jpg/.png images here)
├── basal_cell_carcinoma/
├── actinic_keratosis/
├── benign_keratosis/
├── dermatofibroma/
└── vascular_lesion/
```

**Target:** 100+ images per class (700+ total)

### Step 2: Validate Dataset (Optional but Recommended)

```powershell
cd skin_diagnosis_backend
& "..\..\.venv\Scripts\python.exe" diagnosis/validate_dataset.py ../../dataset
```

### Step 3: Train the Model

```powershell
cd skin_diagnosis_backend
& "..\..\.venv\Scripts\python.exe" diagnosis/train_model.py --dataset ../../dataset --epochs 20
```

---

## Using the Training Script

### From `skin_diagnosis_backend/` Directory

```powershell
# Default settings (20 epochs)
& "..\..\.venv\Scripts\python.exe" diagnosis/train_model.py

# Custom epochs
& "..\..\.venv\Scripts\python.exe" diagnosis/train_model.py --epochs 50

# Custom batch size (use 16 if you get memory errors)
& "..\..\.venv\Scripts\python.exe" diagnosis/train_model.py --batch-size 16

# Custom dataset path
& "..\..\.venv\Scripts\python.exe" diagnosis/train_model.py --dataset D:/my_dataset

# All custom options
& "..\..\.venv\Scripts\python.exe" diagnosis/train_model.py `
  --dataset ../../dataset `
  --epochs 50 `
  --batch-size 16 `
  --output models/
```

### Or Use Alternative Script

```powershell
cd skin_diagnosis_backend
& "..\..\.venv\Scripts\python.exe" train_simple.py --epochs 30
```

---

## What The Script Does

The training script performs these steps automatically:

### ✅ Step 1: Load and Augment Data
- Loads images from `dataset/` folder
- Normalizes pixel values (0-1 range)
- Applies data augmentation:
  - Random rotations (±20°)
  - Random shifts (±20%)
  - Random zoom (±20%)
  - Horizontal flips
- Splits data: 80% training, 20% validation

### ✅ Step 2: Build CNN Model
```
Input Image (224×224×RGB)
    ↓
Conv2D (32 filters) → MaxPool
    ↓
Conv2D (64 filters) → MaxPool
    ↓
Conv2D (128 filters) → MaxPool
    ↓
Flatten
    ↓
Dense (512) → Dropout(50%)
    ↓
Dense (7 classes) → Softmax
    ↓
Output Probabilities
```

### ✅ Step 3: Train the Model
- Phase 1: Standard training (20 epochs)
- Applies early stopping if no improvement for 5 epochs
- Reduces learning rate if progress stalls
- Displays training progress each epoch

### ✅ Step 4: Save Results
- **Model file:** `models/skin_diagnosis_model_YYYYMMDD_HHMMSS.h5`
- **Summary file:** `models/model_summary_YYYYMMDD_HHMMSS.txt`

---

## Expected Output

During training, you'll see:

```
================================================================================
                    SKIN DIAGNOSIS CNN - MODEL TRAINING
================================================================================

[INFO] Checking dataset structure...
       Dataset path: C:\path\to\dataset

[INFO] Scanning for class folders:

       ✓ melanoma............................ 245 images
       ✓ nevus........................... 230 images
       ✓ basal_cell_carcinoma............. 240 images
       ✓ actinic_keratosis................. 220 images
       ✓ benign_keratosis.................. 235 images
       ✓ dermatofibroma.................... 225 images
       ✓ vascular_lesion................... 238 images

       Total images found: 1633
       Classes with data: 7/7

================================================================================
[Step 1] Loading and augmenting data...
================================================================================

[INFO] Loading training generator...
[INFO] Loading validation generator...

[INFO] Data loading complete:
       - Training samples: 1306
       - Validation samples: 327
       - Image size: 224x224
       - Batch size: 32
       - Training epochs: 20

================================================================================
[Step 2] Building the CNN model...
================================================================================

[INFO] Model Summary:
_________________________________________________________________
 Layer (type)                Output Shape              Param #   
=================================================================
 conv2d (Conv2D)             (None, 222, 222, 32)     896       
 max_pooling2d (MaxPooling2D (None, 111, 111, 32)     0         
 conv2d_1 (Conv2D)           (None, 109, 109, 64)     18496     
 max_pooling2d_1 (MaxPooling (None, 54, 54, 64)       0         
 conv2d_2 (Conv2D)           (None, 52, 52, 128)      73856     
 max_pooling2d_2 (MaxPooling (None, 26, 26, 128)      0         
 flatten (Flatten)           (None, 86528)            0         
 dense (Dense)               (None, 512)              44301312  
 dropout (Dropout)           (None, 512)              0         
 dense_1 (Dense)             (None, 7)                3591      
=================================================================
Total params: 44,398,151
Trainable params: 44,398,151
Non-trainable params: 0
_________________________________________________________________

================================================================================
[Step 3] Training the model...
================================================================================

[INFO] Training configuration:
       - Steps per epoch: 40
       - Total epochs: 20
       - Validation steps: 10

[INFO] Starting training...

Epoch 1/20
40/40 [==============================] - 45s 1s/step - loss: 1.8231 - accuracy: 0.3412 - val_loss: 1.6342 - val_accuracy: 0.4234
Epoch 2/20
40/40 [==============================] - 43s 1s/step - loss: 1.2324 - accuracy: 0.5634 - val_loss: 1.0234 - val_accuracy: 0.6342
...
Epoch 20/20
40/40 [==============================] - 42s 1s/step - loss: 0.2103 - accuracy: 0.9342 - val_loss: 0.2891 - val_accuracy: 0.9156

================================================================================
[Step 4] Saving the trained model...
================================================================================

[INFO] Saving model to: models/skin_diagnosis_model_20260421_143022.h5
[✓] Model saved successfully!
[INFO] Saving model summary to: models/model_summary_20260421_143022.txt
[✓] Model summary saved successfully!

================================================================================
                           TRAINING COMPLETE!
================================================================================

[RESULTS]
  Training Accuracy:   93.42%
  Validation Accuracy: 91.56%
  Training Loss:       0.2103
  Validation Loss:     0.2891

[SAVED FILES]
  Model:   models/skin_diagnosis_model_20260421_143022.h5
  Summary: models/model_summary_20260421_143022.txt

[NEXT STEPS]
  1. Use this model for predictions in your Django API
  2. Load the model: keras.models.load_model('models/skin_diagnosis_model_20260421_143022.h5')
  3. Deploy to production when satisfied with results
```

---

## Congratulations! 🎉

Your model is now trained and saved!

### What's Next?

The model file (`.h5`) can now be:

1. **Used in Django API** - Load it to make predictions
2. **Tested with images** - Verify accuracy on new photos
3. **Deployed** - Use in production web/mobile apps

---

## Troubleshooting

### Issue: "Dataset path not found"
```powershell
# Make sure dataset folder exists
Test-Path "dataset"

# Check it has subdirectories
Get-ChildItem dataset
```

### Issue: "No images found"
```powershell
# Verify images are in class folders
Get-ChildItem dataset -Recurse -File | Measure-Object

# Check image formats (.jpg, .png, .jpeg)
Get-ChildItem dataset -Recurse -File | Select-Object Name, Extension
```

### Issue: Out of memory error
Edit the command to use smaller batch size:
```powershell
& "..\..\.venv\Scripts\python.exe" diagnosis/train_model.py --batch-size 8
```

### Issue: Training is very slow
- Use GPU (install CUDA support for TensorFlow)
- Reduce image size in code
- Use fewer images per class

### Issue: Very low accuracy (< 70%)
Check:
1. Dataset quality (are images actual skin conditions?)
2. Image diversity (enough variations of each class?)
3. Image count (need at least 100 per class)
4. Run `validate_dataset.py` to confirm setup

---

## Command Reference

```powershell
# Basic training
python diagnosis/train_model.py

# With custom epochs
python diagnosis/train_model.py --epochs 50

# With custom batch size
python diagnosis/train_model.py --batch-size 16

# With custom dataset
python diagnosis/train_model.py --dataset D:/skin_images

# With custom output directory
python diagnosis/train_model.py --output trained_models/

# All options
python diagnosis/train_model.py `
  --dataset ../../dataset `
  --epochs 50 `
  --batch-size 16 `
  --output models/

# Get help
python diagnosis/train_model.py --help
```

---

**Your CNN training scripts are ready! Start training your model now.** 🚀
