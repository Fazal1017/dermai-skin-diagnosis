# Phase 2: Dataset Setup Guide

## Dataset Selection: DermNet

The **DermNet Image Library** is a free, publicly available dataset of skin condition images. It's one of the most popular datasets for skin disease classification.

### Option 1: Download from DermNet Official Website (Recommended)

1. **Visit the DermNet Dataset Page:**
   - Go to: https://www.dermnetnz.org/image-library
   - Or search for "DermNet image library" online

2. **Download Images:**
   - Browse through the different skin conditions
   - Download images for:
     - Melanoma
     - Nevus (Moles)
     - Basal Cell Carcinoma
     - Actinic Keratosis
     - Benign Keratosis
     - Dermatofibroma
     - Vascular Lesion

3. **Organize Downloaded Images:**
   - Create the folder structure as shown below
   - Place images in their corresponding class folders

### Option 2: Use HAM10000 Dataset (Alternative)

If you prefer an already-organized dataset, use HAM10000:
- **Download:** https://www.kaggle.com/datasets/kmader/skin-cancer-mnist-ham10000
- **Size:** ~25,000 images across 7 classes
- **Format:** Already organized by class

### Folder Structure

After downloading and organizing images, your dataset should look like this:

```
skin_diagnosis_project/
└── dataset/
    ├── melanoma/                    (100+ images)
    │   ├── image1.jpg
    │   ├── image2.jpg
    │   └── ...
    ├── nevus/                       (100+ images)
    │   ├── image1.jpg
    │   ├── image2.jpg
    │   └── ...
    ├── basal_cell_carcinoma/        (100+ images)
    ├── actinic_keratosis/           (100+ images)
    ├── benign_keratosis/            (100+ images)
    ├── dermatofibroma/              (100+ images)
    └── vascular_lesion/             (100+ images)
```

**Minimum Requirements:**
- At least 100 images per class for a proof-of-concept
- Ideally 200-300 images per class for better results
- Images should be `.jpg`, `.jpeg`, or `.png` format
- Image size doesn't matter - they'll be resized to 224×224

## Preparing Your Dataset

### Step 1: Download Images

1. Go to DermNet or HAM10000
2. Download images for each skin condition
3. Save them in the appropriate folders in `dataset/`

### Step 2: Verify Dataset Structure

Run this command to check your dataset:

```powershell
Get-ChildItem -Recurse "dataset" | Where-Object { $_.PSIsContainer } | Measure-Object | Select-Object Count
```

### Step 3: Check Image Count Per Class

```python
from diagnosis.dataset_loader import DatasetLoader

loader = DatasetLoader('./dataset')
# This will print the number of images in each class
```

## Training the Model

Once your dataset is ready, train the model:

### Option 1: From Python Script

```python
from diagnosis.train_model import ModelTrainer

trainer = ModelTrainer(
    dataset_path='../../../dataset',
    model_output_path='models/'
)

trainer.prepare_dataset()
trainer.build_model()
trainer.train(epochs=20, initial_epochs=10)
model_path = trainer.save_model()
```

### Option 2: From Command Line

```powershell
# Navigate to the backend directory
cd skin_diagnosis_backend

# Run training script
& "c:/Users/FAZAL/OneDrive/Desktop/charmada rog/.venv/Scripts/python.exe" `
  diagnosis/train_model.py `
  --dataset ../../../dataset `
  --epochs 20 `
  --initial-epochs 10 `
  --output models/
```

## Training Parameters

- **Epochs:** Number of times the model sees the entire dataset
  - Start with 20 epochs
  - Increase to 50-100 for better results
  
- **Batch Size:** How many images processed at once
  - Default: 32 (adjust if you get memory errors)
  
- **Image Size:** 224×224 pixels (fixed for MobileNetV2)

## Expected Training Results

### Phase 1 (Frozen Base Model - 10 epochs):
- Training time: ~5-15 minutes (depends on GPU)
- Expected accuracy: ~85-90%

### Phase 2 (Fine-tuning - 10 epochs):
- Training time: ~10-30 minutes
- Expected accuracy: ~90-95%

## Output Files

After training, you'll find:

```
skin_diagnosis_backend/
└── models/
    ├── skin_diagnosis_model_YYYYMMDD_HHMMSS.h5   # Trained model
    └── model_summary_YYYYMMDD_HHMMSS.txt         # Model architecture
```

## Troubleshooting

### Issue: "No class subdirectories found"
- **Solution:** Make sure dataset folder has subdirectories like `melanoma/`, `nevus/`, etc.

### Issue: "Error loading image - unsupported format"
- **Solution:** Ensure all images are `.jpg`, `.jpeg`, or `.png`. Delete other formats.

### Issue: "Out of memory" error
- **Solution:** Reduce batch size or reduce image count per class

### Issue: Low accuracy
- **Possible causes:**
  1. Not enough training data (get at least 200 images per class)
  2. Images are too small or poor quality
  3. Class imbalance (some classes have way fewer images)
  4. Need more epochs

## Next Steps

After training:
1. ✅ Model trained and saved
2. ✅ Evaluate on test set
3. Next: Integrate model with Django API (Phase 3)
4. Next: Create web frontend (Phase 4)
