# Phase 2: Building Your CNN Model (Days 3-7)

This phase covers building and training your neural network model for skin lesion diagnosis.

## What You'll Build

✅ **Dataset Loader** - Loads and preprocesses skin images from folders
✅ **Training Pipeline** - Trains the CNN using transfer learning
✅ **Model Architecture** - MobileNetV2 with custom layers for classification
✅ **Data Augmentation** - Increases training data variety

## Files Created in Phase 2

```
skin_diagnosis_backend/diagnosis/
├── dataset_loader.py      # Load and prepare images
├── train_model.py         # Training script
└── models/                # Saved trained models (created after training)

dataset/
├── melanoma/              # 100+ images
├── nevus/                 # 100+ images
├── basal_cell_carcinoma/  # 100+ images
├── actinic_keratosis/     # 100+ images
├── benign_keratosis/      # 100+ images
├── dermatofibroma/        # 100+ images
└── vascular_lesion/       # 100+ images
```

## Step-by-Step Guide

### Step 1: Download Dataset

See [DATASET_SETUP.md](./DATASET_SETUP.md) for detailed instructions on:
- Where to download images
- How to organize them
- What format they need to be in

**Quick Summary:**
1. Download from DermNet or HAM10000
2. Organize into the `dataset/` folder
3. Aim for 100+ images per skin condition class
4. Supported formats: `.jpg`, `.jpeg`, `.png`

### Step 2: Verify Your Dataset

Python script to check if your dataset is ready:

```python
from diagnosis.dataset_loader import DatasetLoader

# Point to your dataset folder
loader = DatasetLoader('../../../dataset')

# This will print:
# - Number of images per class
# - Total images found
# - Class names detected
```

PowerShell command to list contents:

```powershell
Get-ChildItem dataset -Recurse -File | Measure-Object | Select-Object Count
```

### Step 3: Train the Model

#### Option A: Run Training Script

```powershell
cd skin_diagnosis_backend

# Run training
& "..\..\.venv\Scripts\python.exe" diagnosis/train_model.py `
  --dataset ../../../dataset `
  --epochs 20 `
  --initial-epochs 10 `
  --output models/
```

#### Option B: Train from Python

Create a file `train_custom.py`:

```python
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'diagnosis'))

from diagnosis.train_model import ModelTrainer

# Initialize trainer
trainer = ModelTrainer(
    dataset_path='./dataset',
    model_output_path='./models/'
)

# Train
trainer.prepare_dataset()
trainer.build_model()
trainer.train(epochs=20, initial_epochs=10)
trainer.save_model()
trainer.save_model_summary()

print("Training complete!")
```

Then run:

```powershell
& "..\..\.venv\Scripts\python.exe" train_custom.py
```

### Step 4: Monitor Training Progress

During training, you'll see:

```
==================================================
Preparing Dataset
==================================================
Found 250 images in melanoma
Found 230 images in nevus
Found 240 images in basal_cell_carcinoma
...
Total: 1625 images found

==================================================
Building Model
==================================================
Model built with 7 output classes
Total parameters: 2,475,431

==================================================
Training Model
==================================================
Loading training data...
Train set: 1381 images
Validation set: 206 images
Test set: 206 images

==================================================
Phase 1: Training with frozen base model (10 epochs)
==================================================
Epoch 1/10
23/23 [==============================] - 45s 2s/step - loss: 1.2341 - accuracy: 0.6234 - val_loss: 0.8342 - val_accuracy: 0.7234
...
```

## Understanding the Training Process

### Two-Phase Training Strategy

#### Phase 1: Transfer Learning (Frozen Base)
- Uses pre-trained MobileNetV2 weights
- Trains only the top custom layers
- Fast convergence, good starting point
- Epochs: 10 (configurable)

#### Phase 2: Fine-Tuning
- Unfreezes the last 30% of base model layers
- Fine-tunes the entire network
- Improves accuracy on your specific task
- Epochs: 10 (configurable)
- Lower learning rate (1e-5 vs 1e-4)

### Key Training Features

✅ **Data Augmentation**
- Random rotations (±20°)
- Width/height shifts (±20%)
- Horizontal flips
- Zoom (±20%)
- Shear transformations

✅ **Early Stopping**
- Stops training if validation loss doesn't improve for 5 epochs
- Prevents overfitting

✅ **Learning Rate Reduction**
- Reduces learning rate if progress stalls
- Improves fine-tuning convergence

✅ **Class Weights**
- Handles imbalanced datasets
- Gives more importance to rare classes

## Model Architecture

```
Input (224×224×3)
    ↓
Rescaling Layer (normalize pixel values)
    ↓
MobileNetV2 (pre-trained on ImageNet)
    ├─ 150+ convolutional layers
    └─ Freezable for transfer learning
    ↓
Global Average Pooling
    ↓
Dense Layer (256 units, ReLU)
    ↓
Batch Normalization
    ↓
Dropout (50%)
    ↓
Dense Layer (128 units, ReLU)
    ↓
Batch Normalization
    ↓
Dropout (30%)
    ↓
Output Layer (7 units, Softmax)
    ↓
Output Probabilities
```

## Expected Results

### Timeline
- **Phase 1:** ~10-15 minutes (GPU: 2-3 minutes)
- **Phase 2:** ~15-25 minutes (GPU: 5-10 minutes)
- **Total:** ~30-40 minutes (GPU: ~8-13 minutes)

### Accuracy Progression
```
Phase 1:
- Epoch 1:  ~60-65% train, ~55-60% val
- Epoch 5:  ~85-88% train, ~82-85% val
- Epoch 10: ~88-92% train, ~85-88% val

Phase 2:
- Epoch 1:  ~90-92% train, ~87-90% val
- Epoch 5:  ~93-95% train, ~90-93% val
- Epoch 10: ~95-97% train, ~92-95% val

Test Set: ~90-94% (final model)
```

## Troubleshooting

### Common Issues

#### Issue: "No module named 'dataset_loader'"
```powershell
# Make sure you're in the right directory
cd skin_diagnosis_backend
```

#### Issue: Memory Error
```python
# Reduce batch size in training
# In train_model.py, change:
batch_size=32  # Change to 16 or 8
```

#### Issue: Very Low Accuracy (< 70%)
Check:
1. Dataset folder structure is correct
2. Images are actual skin lesion photos
3. You have at least 100 images per class
4. Images are in correct formats (.jpg, .png)

#### Issue: Training is very slow
- Use GPU instead of CPU (install CUDA)
- Reduce number of images
- Reduce image size from 224×224 to 160×160

## Output Files

After training completes, you'll have:

```
models/
├── skin_diagnosis_model_20260421_143022.h5  # Trained weights
└── model_summary_20260421_143022.txt        # Model architecture
```

The `.h5` file contains:
- All trained weights
- Model architecture
- Training configuration

## Next Steps

✅ Complete: Dataset preparation
✅ Complete: Model training
⏭️ Next: Integrate model with Django API (Phase 3)

### Phase 3 Preview
- Load trained model into Django
- Create API endpoint for predictions
- Test with sample images
- Add confidence scores

## Additional Resources

- **TensorFlow Documentation:** https://www.tensorflow.org/
- **MobileNetV2 Paper:** https://arxiv.org/abs/1801.04381
- **Transfer Learning Guide:** https://www.tensorflow.org/tutorials/images/transfer_learning
- **Data Augmentation:** https://www.tensorflow.org/tutorials/images/data_augmentation

## Disk Space Requirements

Estimated space needed:
- Dataset: 300MB - 1GB (depends on image count/size)
- Trained model: 50-100MB
- Total: ~1-1.5GB

## Estimated Time

- Dataset preparation: 1-2 hours
- Model training: 30-60 minutes
- **Total Phase 2: 2-3 hours**

---

**Need help?** Check DATASET_SETUP.md for dataset issues or review this guide's troubleshooting section.
