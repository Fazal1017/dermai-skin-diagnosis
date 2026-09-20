# 🚀 QUICK START - Download & Train in 5 Commands

## ⚡ Ultra-Quick Setup

### Step 1: Verify Kaggle Credentials
```powershell
Test-Path "$env:USERPROFILE\.kaggle\kaggle.json"
```
Should return: `True`

If `False`: Download `kaggle.json` from https://www.kaggle.com/account/api and save to `C:\Users\FAZAL\.kaggle\`

---

### Step 2: Install & Download Dataset
```powershell
cd "c:\Users\FAZAL\OneDrive\Desktop\charmada rog\skin_diagnosis_project"

# Install kagglehub
& ".\.venv\Scripts\python.exe" -m pip install kagglehub -q

# Download HAM10000 dataset (this may take 10-50 minutes)
& ".\.venv\Scripts\python.exe" download_dataset.py
```

---

### Step 3: Validate Dataset
```powershell
cd skin_diagnosis_backend
& ".\.venv\Scripts\python.exe" diagnosis/validate_dataset.py ../../dataset
```

---

### Step 4: Train Model
```powershell
# Quick test (5 epochs, ~5 minutes)
& ".\.venv\Scripts\python.exe" diagnosis/train_model.py --epochs 5

# Full training (20 epochs, ~30-60 minutes on CPU)
& ".\.venv\Scripts\python.exe" diagnosis/train_model.py --epochs 20
```

---

### Step 5: Done! 🎉
Check results in: `models/skin_diagnosis_model_*.h5`

---

## 📋 Full Copy-Paste Sequence

Run these commands in PowerShell one by one:

```powershell
# Navigate to project
cd "c:\Users\FAZAL\OneDrive\Desktop\charmada rog\skin_diagnosis_project"

# Download dataset
& ".\.venv\Scripts\python.exe" -m pip install kagglehub -q
& ".\.venv\Scripts\python.exe" download_dataset.py

# Validate
cd skin_diagnosis_backend
& ".\.venv\Scripts\python.exe" diagnosis/validate_dataset.py ../../dataset

# Train (change --epochs value as needed)
& ".\.venv\Scripts\python.exe" diagnosis/train_model.py --epochs 20
```

---

## ⏱️ Time Estimates

| Step | Depends On | Estimated Time |
|------|-----------|-----------------|
| Install kagglehub | Internet speed | 1-2 minutes |
| Download dataset | Internet speed | 10-50 minutes |
| Validate dataset | - | 1 minute |
| Train (5 epochs) | CPU/GPU | 5-15 minutes |
| Train (20 epochs) | CPU/GPU | 30-60 minutes |
| **TOTAL** | **All above** | **45 min - 2 hours** |

---

## 🆘 Common Issues

| Issue | Fix |
|-------|-----|
| "Kaggle API token not found" | Save kaggle.json to `C:\Users\FAZAL\.kaggle\` |
| "ModuleNotFoundError: kagglehub" | Run: `pip install kagglehub` |
| Download is slow | Normal - HAM10000 is 2.5GB. Just wait. |
| Out of memory | Reduce batch size: `--batch-size 8` |
| Low accuracy | Normal for quick test. Full training helps. |

---

## 📁 What Gets Created

After Step 3, you'll have:
```
dataset/
├── melanoma/              (1500+ images)
├── nevus/                 (6700+ images)
├── basal_cell_carcinoma/  (500+ images)
├── actinic_keratosis/     (300+ images)
├── benign_keratosis/      (1100+ images)
├── dermatofibroma/        (100+ images)
└── vascular_lesion/       (400+ images)
```

After Step 5, you'll have:
```
models/
├── skin_diagnosis_model_20260421_143022.h5  (trained model)
└── model_summary_20260421_143022.txt        (model info)
```

---

**That's it! You're ready to go.** 🚀
