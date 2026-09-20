# Quick Start: Phase 2 - Training Your CNN Model

## 🚀 5-Minute Quick Start

### 1. **Prepare Your Dataset** (if not already done)

```powershell
# Copy images into the dataset folders
# Example for Windows:
Copy-Item "C:\path\to\melanoma\images\*" "dataset\melanoma\" -Force
Copy-Item "C:\path\to\nevus\images\*" "dataset\nevus\" -Force
# ... repeat for other classes
```

### 2. **Validate Your Dataset**

```powershell
cd skin_diagnosis_backend

# Check if dataset is ready
& "..\..\.venv\Scripts\python.exe" diagnosis/validate_dataset.py ../../../dataset
```

**Expected output:**
```
✅ All 7 classes present
✅ All classes have at least 100 images
✅ Dataset is ready for training!
```

### 3. **Train the Model**

```powershell
# One command to train
& "..\..\.venv\Scripts\python.exe" diagnosis/train_model.py `
  --dataset ../../../dataset `
  --epochs 20 `
  --output models/
```

### 4. **Wait for Training to Complete**

You should see:
- Phase 1 training progress (10 epochs) - ~10-15 minutes
- Phase 2 fine-tuning (10 epochs) - ~15-25 minutes
- Test set evaluation

### 5. **Find Your Trained Model**

```powershell
# List saved models
Get-ChildItem skin_diagnosis_backend/models/

# You'll see:
# - skin_diagnosis_model_YYYYMMDD_HHMMSS.h5
# - model_summary_YYYYMMDD_HHMMSS.txt
```

## 📊 What Each Phase Does

### Phase 1: Transfer Learning (10 epochs)
- Uses pre-trained weights from ImageNet
- Trains only top custom layers
- **Time:** 5-15 min
- **Accuracy:** ~85-90%

### Phase 2: Fine-Tuning (10 epochs)  
- Unfreezes and fine-tunes deeper layers
- Uses lower learning rate
- **Time:** 10-25 min
- **Accuracy:** ~92-95%

## 🔍 Monitor Your Training

Watch for these metrics:

| Metric | Phase 1 | Phase 2 | Test |
|--------|---------|---------|------|
| Train Accuracy | 85-92% | 93-97% | - |
| Val Accuracy | 82-88% | 90-93% | - |
| Test Accuracy | - | - | 90-94% |

## ⚙️ Advanced Options

### Train with Custom Parameters

```powershell
& "..\..\.venv\Scripts\python.exe" diagnosis/train_model.py `
  --dataset ../../../dataset `
  --epochs 50 `                    # Total epochs
  --initial-epochs 25 `            # Phase 1 epochs
  --output models/custom/
```

### Train with Fewer Epochs (Quick Test)

```powershell
& "..\..\.venv\Scripts\python.exe" diagnosis/train_model.py `
  --dataset ../../../dataset `
  --epochs 10 `
  --initial-epochs 5 `
  --output models/
```

## 🐛 Troubleshooting

### "Dataset path not found"
```powershell
# Make sure you're in skin_diagnosis_backend directory
cd skin_diagnosis_backend
```

### "Module not found"
```powershell
# Reinstall requirements
& "..\..\.venv\Scripts\python.exe" -m pip install -r requirements.txt
```

### Memory error or very slow training
```python
# Edit train_model.py and find:
batch_size=32

# Change to:
batch_size=16  # or 8
```

### Very low accuracy (< 70%)
1. Check dataset folder has correct structure
2. Verify images are actual skin lesion photos
3. Ensure at least 100 images per class
4. Run `validate_dataset.py` to check

## 📁 Before You Start - Checklist

- [ ] Dataset folders created (`dataset/melanoma/`, `dataset/nevus/`, etc.)
- [ ] Images downloaded and organized
- [ ] At least 100 images per class
- [ ] Images in `.jpg`, `.jpeg`, or `.png` format
- [ ] Validation script passes: `python validate_dataset.py`
- [ ] Virtual environment activated
- [ ] All packages installed (Django, TensorFlow, etc.)

## 📈 What Happens During Training

You'll see output like:

```
==================================================
Phase 1: Training with frozen base model (10 epochs)
==================================================
Epoch 1/10
23/23 [==============================] - 45s 2s/step - loss: 1.2341 - accuracy: 0.6234 - val_loss: 0.8342 - val_accuracy: 0.7234
Epoch 2/10
23/23 [==============================] - 43s 2s/step - loss: 0.9123 - accuracy: 0.7456 - val_loss: 0.6234 - val_accuracy: 0.8123
...
```

**This is normal!** Accuracy should increase over time.

## 🎉 Success Indicators

After training completes, you should see:

✅ Model saved to `models/skin_diagnosis_model_*.h5`
✅ Training accuracy > 90%
✅ Validation accuracy > 85%
✅ Test accuracy > 90%
✅ Low loss values (< 0.3)

## 📚 Next Steps

Once training is complete:

1. **Phase 3:** Integrate model with Django API
2. **Phase 4:** Build web frontend
3. **Phase 5:** Deploy to production

## 💡 Pro Tips

1. **First time?** Run with default parameters (20 epochs)
2. **Need better accuracy?** Add more training data or increase epochs to 50+
3. **Running on CPU?** Ensure dataset is ready before starting (it will take longer)
4. **Want to experiment?** Create a copy of your dataset with fewer images for testing

## 📞 Getting Help

See full documentation in:
- `PHASE2_README.md` - Comprehensive Phase 2 guide
- `DATASET_SETUP.md` - Dataset download and organization
- `diagnosis/dataset_loader.py` - Data loading code
- `diagnosis/train_model.py` - Training pipeline code

---

**Ready?** Run the validation script first, then start training! 🚀
