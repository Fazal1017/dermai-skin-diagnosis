"""
Simple CNN Training Script for Skin Diagnosis
Based on the basic training template with 7 skin condition classes

This script:
1. Loads images from the dataset folder
2. Performs data augmentation
3. Builds a CNN model
4. Trains the model
5. Saves the trained model

Usage:
    python train_simple.py --dataset ./../../dataset --epochs 20
    
Or with default dataset path:
    python train_simple.py
"""

import os
import sys
import argparse
import numpy as np
from datetime import datetime

import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau

# ============================================================================
# --- 1. CONFIGURATION ---
# ============================================================================

# Default configuration (can be overridden via command line)
DATASET_PATH = '../../../dataset'  # Path to your dataset folder
IMG_HEIGHT = 224
IMG_WIDTH = 224
BATCH_SIZE = 32
EPOCHS = 20
NUM_CLASSES = 7

# Class names - must match your dataset folder names
CLASS_NAMES = [
    'melanoma',
    'nevus',
    'basal_cell_carcinoma',
    'actinic_keratosis',
    'benign_keratosis',
    'dermatofibroma',
    'vascular_lesion'
]

MODEL_OUTPUT_DIR = 'models'

print("=" * 70)
print("SKIN DIAGNOSIS CNN - SIMPLE TRAINING SCRIPT")
print("=" * 70)

# ============================================================================
# --- 2. PARSE COMMAND LINE ARGUMENTS ---
# ============================================================================

parser = argparse.ArgumentParser(description='Train skin diagnosis CNN model')
parser.add_argument('--dataset', type=str, default=DATASET_PATH,
                   help='Path to dataset folder (default: ../../../dataset)')
parser.add_argument('--epochs', type=int, default=EPOCHS,
                   help='Number of training epochs (default: 20)')
parser.add_argument('--batch-size', type=int, default=BATCH_SIZE,
                   help='Batch size for training (default: 32)')
parser.add_argument('--output', type=str, default=MODEL_OUTPUT_DIR,
                   help='Output directory for trained models (default: models/)')

args = parser.parse_args()

DATASET_PATH = os.path.abspath(args.dataset)
EPOCHS = args.epochs
BATCH_SIZE = args.batch_size
MODEL_OUTPUT_DIR = args.output

# Create output directory if it doesn't exist
os.makedirs(MODEL_OUTPUT_DIR, exist_ok=True)

# ============================================================================
# --- 3. VERIFY DATASET ---
# ============================================================================

print(f"\n[*] Checking dataset at: {DATASET_PATH}")

if not os.path.exists(DATASET_PATH):
    print(f"[ERROR] Dataset path not found: {DATASET_PATH}")
    sys.exit(1)

# Check for class folders
found_classes = []
for class_name in CLASS_NAMES:
    class_path = os.path.join(DATASET_PATH, class_name)
    if os.path.isdir(class_path):
        num_images = len([f for f in os.listdir(class_path) 
                         if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
        found_classes.append((class_name, num_images))
        print(f"    ✓ {class_name}: {num_images} images")
    else:
        print(f"    ✗ {class_name}: NOT FOUND")

if len(found_classes) < NUM_CLASSES:
    print(f"\n[WARNING] Only {len(found_classes)}/{NUM_CLASSES} classes found")

# ============================================================================
# --- 4. LOAD AND AUGMENT DATA ---
# ============================================================================

print("\n[Step 1] Loading and augmenting data...")
print("-" * 70)

# Data augmentation helps the model generalize better and avoid overfitting
train_datagen = ImageDataGenerator(
    rescale=1./255,                    # Normalize pixel values to 0-1
    rotation_range=20,                 # Random rotation ±20 degrees
    width_shift_range=0.2,             # Random horizontal shift ±20%
    height_shift_range=0.2,            # Random vertical shift ±20%
    shear_range=0.2,                   # Shear transformation
    zoom_range=0.2,                    # Random zoom ±20%
    horizontal_flip=True,              # Random horizontal flip
    validation_split=0.2               # Use 20% of data for validation
)

# Load training images from the dataset folder
train_generator = train_datagen.flow_from_directory(
    DATASET_PATH,
    target_size=(IMG_HEIGHT, IMG_WIDTH),
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    subset='training',
    shuffle=True
)

# Load validation images
validation_generator = train_datagen.flow_from_directory(
    DATASET_PATH,
    target_size=(IMG_HEIGHT, IMG_WIDTH),
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    subset='validation',
    shuffle=False
)

num_training_samples = train_generator.samples
num_validation_samples = validation_generator.samples

print(f"Found {num_training_samples} training images")
print(f"Found {num_validation_samples} validation images")
print(f"Training epochs: {EPOCHS}")
print(f"Batch size: {BATCH_SIZE}")

# ============================================================================
# --- 5. BUILD CNN MODEL ---
# ============================================================================

print("\n[Step 2] Building the CNN model...")
print("-" * 70)

# Build a Convolutional Neural Network (CNN)
model = models.Sequential([
    # First convolutional block
    layers.Conv2D(32, (3, 3), activation='relu', input_shape=(IMG_HEIGHT, IMG_WIDTH, 3)),
    layers.MaxPooling2D((2, 2)),
    
    # Second convolutional block
    layers.Conv2D(64, (3, 3), activation='relu'),
    layers.MaxPooling2D((2, 2)),
    
    # Third convolutional block
    layers.Conv2D(128, (3, 3), activation='relu'),
    layers.MaxPooling2D((2, 2)),
    
    # Flatten and dense layers
    layers.Flatten(),
    layers.Dense(512, activation='relu'),
    layers.Dropout(0.5),  # Helps prevent overfitting
    
    # Output layer for 7 classes
    layers.Dense(NUM_CLASSES, activation='softmax')
])

# ============================================================================
# --- 6. COMPILE THE MODEL ---
# ============================================================================

model.compile(
    optimizer='adam',
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

print("\nModel Architecture:")
print("-" * 70)
model.summary()

# ============================================================================
# --- 7. TRAIN THE MODEL ---
# ============================================================================

print("\n[Step 3] Starting training...")
print("-" * 70)

# Calculate steps per epoch
steps_per_epoch = num_training_samples // BATCH_SIZE
validation_steps = num_validation_samples // BATCH_SIZE

# Add callbacks for better training
callbacks = [
    EarlyStopping(
        monitor='val_loss',
        patience=5,
        restore_best_weights=True,
        verbose=1
    ),
    ReduceLROnPlateau(
        monitor='val_loss',
        factor=0.5,
        patience=3,
        min_lr=1e-7,
        verbose=1
    )
]

# Train the model
history = model.fit(
    train_generator,
    steps_per_epoch=steps_per_epoch,
    epochs=EPOCHS,
    validation_data=validation_generator,
    validation_steps=validation_steps,
    callbacks=callbacks,
    verbose=1
)

# ============================================================================
# --- 8. SAVE THE TRAINED MODEL ---
# ============================================================================

print("\n[Step 4] Saving the trained model...")
print("-" * 70)

# Generate unique filename with timestamp
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
model_filename = f"skin_diagnosis_model_{timestamp}.h5"
model_path = os.path.join(MODEL_OUTPUT_DIR, model_filename)

# Save the model
model.save(model_path)
print(f"✓ Model saved to: {model_path}")

# Save model summary
summary_filename = f"model_summary_{timestamp}.txt"
summary_path = os.path.join(MODEL_OUTPUT_DIR, summary_filename)

with open(summary_path, 'w') as f:
    model.summary(print_fn=lambda x: f.write(x + '\n'))
    f.write(f"\n\nTraining Configuration:\n")
    f.write(f"- Dataset: {DATASET_PATH}\n")
    f.write(f"- Training samples: {num_training_samples}\n")
    f.write(f"- Validation samples: {num_validation_samples}\n")
    f.write(f"- Epochs: {EPOCHS}\n")
    f.write(f"- Batch size: {BATCH_SIZE}\n")
    f.write(f"- Classes: {NUM_CLASSES}\n")

print(f"✓ Model summary saved to: {summary_path}")

# ============================================================================
# --- 9. PRINT FINAL STATISTICS ---
# ============================================================================

print("\n" + "=" * 70)
print("TRAINING COMPLETE!")
print("=" * 70)

print(f"\nFinal Training Accuracy: {history.history['accuracy'][-1]:.4f}")
print(f"Final Validation Accuracy: {history.history['val_accuracy'][-1]:.4f}")
print(f"Final Training Loss: {history.history['loss'][-1]:.4f}")
print(f"Final Validation Loss: {history.history['val_loss'][-1]:.4f}")

print(f"\n[✓] Model available at: {model_path}")
print(f"[✓] Use this model for: Django API predictions, web deployment, etc.")

print("\nNext steps:")
print("1. Integrate this model into your Django API")
print("2. Test predictions with sample images")
print("3. Deploy to production")

print("\n" + "=" * 70)
