# 📥 Download HAM10000 Dataset - Complete Guide

This guide will help you download the HAM10000 dataset (~2.5GB, 25,000 images) and organize it for training.

---

## 🔑 Step 1: Get Kaggle API Credentials

### Create Kaggle Account (if needed)
1. Go to: https://www.kaggle.com
2. Sign up (free account)

### Get API Token
1. Go to: https://www.kaggle.com/account/api
2. Scroll down to "API" section
3. Click **"Create New API Token"**
   - This downloads `kaggle.json`
4. Save this file to your computer

### Place Credentials in Right Location

**On Windows:**

1. Press `Win + R`, type: `%userprofile%`
2. Create folder: `.kaggle` (with the dot at the start)
3. Copy `kaggle.json` into `.kaggle/` folder
4. Your path should be: `C:\Users\YOUR_NAME\.kaggle\kaggle.json`

**Verify it worked:**
```powershell
Test-Path "$env:USERPROFILE\.kaggle\kaggle.json"
# Should return: True
```

---

## 💾 Step 2: Install Required Package

Already done! (kagglehub was installed when you ran the previous commands)

Verify:
```powershell
& "c:\Users\FAZAL\OneDrive\Desktop\charmada rog\.venv\Scripts\python.exe" -c "import kagglehub; print('kagglehub OK')"
```

---

## ⬇️ Step 3: Download and Organize Dataset

### Run the Download Script

From the project root directory:

```powershell
cd "c:\Users\FAZAL\OneDrive\Desktop\charmada rog\skin_diagnosis_project"

& "c:\Users\FAZAL\OneDrive\Desktop\charmada rog\.venv\Scripts\python.exe" download_dataset.py
```

### What the Script Does

```
[Step 1] Download HAM10000 dataset from Kaggle (~2.5GB)
         ↓
[Step 2] Extract and read metadata
         ↓
[Step 3] Create project directory structure
         ↓
[Step 4] Organize 25,000+ images into 7 classes
         ↓
[Step 5] Verify dataset integrity
         ↓
[✅ READY] Dataset organized and ready for training!
```

### Download Time Estimate

| Speed | Estimated Time |
|-------|----------------|
| 1 Mbps (slow) | 30-40 minutes |
| 5 Mbps (normal) | 7-10 minutes |
| 10+ Mbps (fast) | 3-5 minutes |

Plus organization time: 5-10 minutes

**Total: ~15-50 minutes depending on speed**

---

## 📊 Expected Dataset Structure

After download completes, you'll have:

```
skin_diagnosis_project/
└── dataset/
    ├── melanoma/              (~1500 images)
    ├── nevus/                 (~6700 images)
    ├── basal_cell_carcinoma/  (~500 images)
    ├── actinic_keratosis/     (~300 images)
    ├── benign_keratosis/      (~1100 images)
    ├── dermatofibroma/        (~100 images)
    └── vascular_lesion/       (~400 images)
```

**Total: ~10,000+ images**

---

## ✅ Step 4: Verify Dataset

After download completes, validate the dataset:

```powershell
cd "c:\Users\FAZAL\OneDrive\Desktop\charmada rog\skin_diagnosis_project\skin_diagnosis_backend"

& "c:\Users\FAZAL\OneDrive\Desktop\charmada rog\.venv\Scripts\python.exe" diagnosis/validate_dataset.py ../../dataset
```

**Expected output:**
```
✓ All 7 classes present
✓ All classes have at least 100 images
✓ Dataset is ready for training!
```

---

## 🚀 Step 5: Start Training

Once dataset is validated, run the training:

```powershell
cd "c:\Users\FAZAL\OneDrive\Desktop\charmada rog\skin_diagnosis_project\skin_diagnosis_backend"

& "c:\Users\FAZAL\OneDrive\Desktop\charmada rog\.venv\Scripts\python.exe" diagnosis/train_model.py --epochs 20
```

Training will take:
- **CPU:** 30-60 minutes
- **GPU:** 5-15 minutes

---

## 🐛 Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'kagglehub'"

**Solution:**
```powershell
& "c:\Users\FAZAL\OneDrive\Desktop\charmada rog\.venv\Scripts\python.exe" -m pip install kagglehub
```

### Issue: "Kaggle API token not found"

**This means:**
- You haven't set up `kaggle.json`
- Or it's not in the right location

**Fix:**
1. Create file: `C:\Users\FAZAL\.kaggle\kaggle.json`
2. Copy the downloaded `kaggle.json` content there
3. Run the download script again

### Issue: "Dataset downloaded but no images organized"

**Possible causes:**
1. Kaggle changed their dataset format
2. CSV metadata file name is different

**Solution:**
```powershell
# Check what files were downloaded
Get-ChildItem "kagglehub_cache_path" -Recurse | Select-Object Name, Length | Head -20
```

### Issue: Download is slow/stuck

**Try:**
1. Check internet connection
2. Close other downloads
3. Run again (Kaggle will resume if interrupted)

### Issue: Not enough disk space

**HAM10000 requires:**
- ~2.5GB for download
- ~5GB total (download + organized)

**Solution:**
- Free up disk space
- Or download to external drive

---

## 📋 Quick Checklist

- [ ] Kaggle account created
- [ ] API token downloaded (`kaggle.json`)
- [ ] Saved to: `C:\Users\FAZAL\.kaggle\kaggle.json`
- [ ] Verified: `Test-Path C:\Users\FAZAL\.kaggle\kaggle.json` returns `True`
- [ ] Installed kagglehub: `pip install kagglehub`
- [ ] Run: `python download_dataset.py`
- [ ] Validated: `python validate_dataset.py`
- [ ] Ready to train! 🎉

---

## 📝 Full Command Sequence

Copy and paste (one at a time):

```powershell
# 1. Verify Kaggle credentials are set up
Test-Path "$env:USERPROFILE\.kaggle\kaggle.json"

# 2. Install kagglehub (if not done)
& "c:\Users\FAZAL\OneDrive\Desktop\charmada rog\.venv\Scripts\python.exe" -m pip install kagglehub

# 3. Navigate to project
cd "c:\Users\FAZAL\OneDrive\Desktop\charmada rog\skin_diagnosis_project"

# 4. Download and organize dataset
& "c:\Users\FAZAL\OneDrive\Desktop\charmada rog\.venv\Scripts\python.exe" download_dataset.py

# 5. Validate dataset
cd skin_diagnosis_backend
& "c:\Users\FAZAL\OneDrive\Desktop\charmada rog\.venv\Scripts\python.exe" diagnosis/validate_dataset.py ../../dataset

# 6. Start training!
& "c:\Users\FAZAL\OneDrive\Desktop\charmada rog\.venv\Scripts\python.exe" diagnosis/train_model.py --epochs 20
```

---

## ❓ Need Help?

1. **Kaggle API issues?** → Check: https://github.com/Kaggle/kaggle-api
2. **Dataset format changed?** → Check: https://www.kaggle.com/datasets/kmader/skin-cancer-mnist-ham10000
3. **Training issues?** → See: `TRAINING_GUIDE.md`

---

**Ready to download? Start with the commands above!** ⬇️
