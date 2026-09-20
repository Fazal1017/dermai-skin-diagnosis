"""
Simple CNN Training Script for Skin Diagnosis
Based on the basic training template with 7 skin condition classes

This script:
1. Loads images from the dataset folder
2. Performs data augmentation
3. Builds a CNN model
4. Trains the model
5. Saves the trained model

USAGE:
    From skin_diagnosis_backend directory:
    python diagnosis/train_model.py --dataset ../../dataset --epochs 20

EXAMPLES:
    # Default settings
    python diagnosis/train_model.py
    
    # Custom number of epochs
    python diagnosis/train_model.py --epochs 50
    
    # Custom dataset path
    python diagnosis/train_model.py --dataset D:/my_dataset
    
    # Custom batch size
    python diagnosis/train_model.py --batch-size 16
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
DATASET_PATH = '../../dataset'          # Path to your dataset folder
IMG_HEIGHT = 224                        # MobileNetV2 standard size
IMG_WIDTH = 224
BATCH_SIZE = 32                         # Reduce to 16 or 8 if out of memory
EPOCHS = 20                             # Total training epochs
NUM_CLASSES = 7                         # 7 skin condition classes

# Class names - MUST match your dataset folder names exactly
CLASS_NAMES = [
    'melanoma',
    'nevus',
    'basal_cell_carcinoma',
    'actinic_keratosis',
    'benign_keratosis',
    'dermatofibroma',
    'vascular_lesion'
]

MODEL_OUTPUT_DIR = 'models'             # Where to save trained models

print("=" * 80)
print(" " * 20 + "SKIN DIAGNOSIS CNN - MODEL TRAINING")
print("=" * 80)

# ============================================================================
# --- 2. PARSE COMMAND LINE ARGUMENTS ---
# ============================================================================

parser = argparse.ArgumentParser(
    description='Train a CNN model for skin diagnosis',
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog="""
Examples:
  python train_model.py                     # Default settings
  python train_model.py --epochs 50         # Train for 50 epochs
  python train_model.py --batch-size 16     # Use smaller batch size
  python train_model.py --output my_models/ # Save to different directory
    """
)

parser.add_argument('--dataset', type=str, default=DATASET_PATH,
                   help='Path to dataset folder (default: ../../dataset)')
parser.add_argument('--epochs', type=int, default=EPOCHS,
                   help='Number of training epochs (default: 20)')
parser.add_argument('--batch-size', type=int, default=BATCH_SIZE,
                   help='Batch size for training (default: 32)')
parser.add_argument('--output', type=str, default=MODEL_OUTPUT_DIR,
                   help='Output directory for trained models (default: models/)')

args = parser.parse_args()

# Apply arguments
DATASET_PATH = os.path.abspath(args.dataset)
EPOCHS = args.epochs
BATCH_SIZE = args.batch_size
MODEL_OUTPUT_DIR = args.output

# Create output directory
os.makedirs(MODEL_OUTPUT_DIR, exist_ok=True)

# ============================================================================
# --- 3. VERIFY DATASET ---
# ============================================================================

print(f"\n[INFO] Checking dataset structure...")
print(f"       Dataset path: {DATASET_PATH}\n")

if not os.path.exists(DATASET_PATH):
    print(f"[ERROR] Dataset path not found!")
    print(f"        Expected: {DATASET_PATH}")
    print(f"\n        Create the dataset folder with subdirectories:")
    for class_name in CLASS_NAMES:
        print(f"          - {class_name}/")
    sys.exit(1)

# Check for class folders and image counts
print("[INFO] Scanning for class folders:\n")
found_classes = []
total_images = 0

for class_name in CLASS_NAMES:
    class_path = os.path.join(DATASET_PATH, class_name)
    if os.path.isdir(class_path):
        # Count image files
        images = [f for f in os.listdir(class_path) 
                 if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        num_images = len(images)
        found_classes.append((class_name, num_images))
        total_images += num_images
        
        status = "✓" if num_images > 0 else "✗"
        print(f"       {status} {class_name:.<30} {num_images:>4} images")
    else:
        print(f"       ✗ {class_name:.<30} NOT FOUND")

print(f"\n       Total images found: {total_images}")
print(f"       Classes with data: {len(found_classes)}/{len(CLASS_NAMES)}")

if len(found_classes) < len(CLASS_NAMES):
    print(f"\n[WARNING] Some classes are missing. Add images before training.")

if total_images == 0:
    print(f"\n[ERROR] No images found in dataset!")
    sys.exit(1)

# ============================================================================
# Step 1: LOAD AND AUGMENT DATA
# ============================================================================

print("\n" + "=" * 80)
print("[Step 1] Loading and augmenting data...")
print("=" * 80)

# Data augmentation creates variations of training images
# This helps the model generalize better and avoid overfitting
train_datagen = ImageDataGenerator(
    rescale=1./255,                    # Normalize pixel values to 0-1 range
    rotation_range=20,                 # Random rotation ±20 degrees
    width_shift_range=0.2,             # Random horizontal shift ±20%
    height_shift_range=0.2,            # Random vertical shift ±20%
    shear_range=0.2,                   # Shear transformation (skew)
    zoom_range=0.2,                    # Random zoom ±20%
    horizontal_flip=True,              # Randomly flip horizontally
    vertical_flip=False,               # No vertical flips (skin lesions shouldn't be upside down)
    validation_split=0.2               # Use 20% of data for validation (not training)
)

print(f"\n[INFO] Data augmentation applied:")
print(f"       - Normalization: pixel values / 255")
print(f"       - Rotation: ±20°")
print(f"       - Shifts: ±20% width and height")
print(f"       - Zoom: ±20%")
print(f"       - Horizontal flip: Yes")
print(f"       - Train/Validation split: 80%/20%")

# Load training images from dataset folder
# flow_from_directory automatically:
# - Reads images from class subdirectories
# - Converts class folders to one-hot encoded labels
# - Applies specified augmentations
print(f"\n[INFO] Loading training generator...")
train_generator = train_datagen.flow_from_directory(
    DATASET_PATH,
    target_size=(IMG_HEIGHT, IMG_WIDTH),
    batch_size=BATCH_SIZE,
    class_mode='categorical',          # Multi-class classification
    subset='training',                 # Get only training subset (80%)
    shuffle=True                       # Shuffle training data
)

# Load validation images (same pipeline, different subset)
print(f"[INFO] Loading validation generator...")
validation_generator = train_datagen.flow_from_directory(
    DATASET_PATH,
    target_size=(IMG_HEIGHT, IMG_WIDTH),
    batch_size=BATCH_SIZE,
    class_mode='categorical',          # Multi-class classification
    subset='validation',               # Get only validation subset (20%)
    shuffle=False                      # Don't shuffle validation data
)

num_training_samples = train_generator.samples
num_validation_samples = validation_generator.samples

print(f"\n[INFO] Data loading complete:")
print(f"       - Training samples: {num_training_samples}")
print(f"       - Validation samples: {num_validation_samples}")
print(f"       - Image size: {IMG_HEIGHT}x{IMG_WIDTH}")
print(f"       - Batch size: {BATCH_SIZE}")
print(f"       - Training epochs: {EPOCHS}")

# ============================================================================
# Step 2: BUILD CNN MODEL
# ============================================================================

print("\n" + "=" * 80)
print("[Step 2] Building the CNN model...")
print("=" * 80)

# This architecture uses 3 convolutional blocks:
# - Each block extracts features from images
# - MaxPooling reduces spatial dimensions (computational efficiency)
# - Filters increase: 32 → 64 → 128 (learn more complex features)
# - Flatten converts 2D features to 1D for dense layers
# - Dense layers for classification
# - Dropout prevents overfitting

model = models.Sequential([
    # === First Convolutional Block ===
    # Extract low-level features (edges, textures)
    layers.Conv2D(
        filters=32,                     # Number of filters (feature detectors)
        kernel_size=(3, 3),             # 3x3 filter size
        activation='relu',              # ReLU activation
        input_shape=(IMG_HEIGHT, IMG_WIDTH, 3)  # Input shape: 224x224x3 (RGB)
    ),
    layers.MaxPooling2D((2, 2)),        # Reduce spatial dimensions by half
    
    # === Second Convolutional Block ===
    # Extract mid-level features (corners, shapes)
    layers.Conv2D(64, (3, 3), activation='relu'),
    layers.MaxPooling2D((2, 2)),
    
    # === Third Convolutional Block ===
    # Extract high-level features (objects, patterns)
    layers.Conv2D(128, (3, 3), activation='relu'),
    layers.MaxPooling2D((2, 2)),
    
    # === Flattening ===
    # Convert 2D feature maps to 1D vector
    layers.Flatten(),
    
    # === Dense Layers ===
    # Classification using extracted features
    layers.Dense(512, activation='relu'),       # Fully connected layer with 512 units
    
    # === Dropout ===
    # Randomly disable 50% of units during training to prevent overfitting
    layers.Dropout(0.5),
    
    # === Output Layer ===
    # One unit per class with softmax for probability distribution
    layers.Dense(NUM_CLASSES, activation='softmax')
])

print("\n[INFO] Model architecture:")
print(f"       - Convolutional blocks: 3")
print(f"       - Filters: 32 → 64 → 128")
print(f"       - Dense layer: 512 units")
print(f"       - Dropout: 50%")
print(f"       - Output classes: {NUM_CLASSES}")

# ============================================================================
# Step 3: COMPILE THE MODEL
# ============================================================================

# Compilation needs:
# - Optimizer: How to update weights (Adam = adaptive learning rate)
# - Loss: How to measure prediction errors (categorical for multi-class)
# - Metrics: What to monitor (accuracy)

model.compile(
    optimizer='adam',                  # Adam optimizer (good general-purpose choice)
    loss='categorical_crossentropy',   # Multi-class classification loss
    metrics=['accuracy']               # Monitor accuracy during training
)

print("\n[INFO] Model compilation:")
print(f"       - Optimizer: adam")
print(f"       - Loss: categorical_crossentropy")
print(f"       - Metrics: accuracy")

print("\n[INFO] Model Summary:")
print("       " + "-" * 60)
model.summary()
print("       " + "-" * 60)

# ============================================================================
# Step 4: TRAIN THE MODEL
# ============================================================================

print("\n" + "=" * 80)
print("[Step 3] Training the model...")
print("=" * 80)

# Calculate steps per epoch (how many batches to process all data)
steps_per_epoch = num_training_samples // BATCH_SIZE
validation_steps = num_validation_samples // BATCH_SIZE

print(f"\n[INFO] Training configuration:")
print(f"       - Steps per epoch: {steps_per_epoch}")
print(f"       - Total epochs: {EPOCHS}")
print(f"       - Validation steps: {validation_steps}")

# Callbacks improve training control
# Early stopping: Stop if validation loss doesn't improve for 5 epochs
# ReduceLROnPlateau: Reduce learning rate if progress stalls

callbacks = [
    EarlyStopping(
        monitor='val_loss',
        patience=5,                     # Stop if no improvement for 5 epochs
        restore_best_weights=True,     # Use best model weights
        verbose=1
    ),
    ReduceLROnPlateau(
        monitor='val_loss',
        factor=0.5,                     # Multiply learning rate by 0.5
        patience=3,                     # Wait 3 epochs before reducing
        min_lr=1e-7,                    # Minimum learning rate
        verbose=1
    )
]

print("\n[INFO] Starting training...\n")

# Train the model using data generators
history = model.fit(
    train_generator,
    steps_per_epoch=steps_per_epoch,
    epochs=EPOCHS,
    validation_data=validation_generator,
    validation_steps=validation_steps,
    callbacks=callbacks,
    verbose=1                           # Print progress
)

# ============================================================================
# Step 5: SAVE THE TRAINED MODEL
# ============================================================================

print("\n" + "=" * 80)
print("[Step 4] Saving the trained model...")
print("=" * 80)

# Generate unique filename with timestamp
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
model_filename = f"skin_diagnosis_model_{timestamp}.h5"
model_path = os.path.join(MODEL_OUTPUT_DIR, model_filename)

# Save model (includes architecture, weights, and optimizer state)
print(f"\n[INFO] Saving model to: {model_path}")
model.save(model_path)
print(f"[✓] Model saved successfully!")

# Save model summary to text file for reference
summary_filename = f"model_summary_{timestamp}.txt"
summary_path = os.path.join(MODEL_OUTPUT_DIR, summary_filename)

print(f"[INFO] Saving model summary to: {summary_path}")
with open(summary_path, 'w') as f:
    # Write architecture
    f.write("=" * 80 + "\n")
    f.write("CNN MODEL SUMMARY\n")
    f.write("=" * 80 + "\n\n")
    
    model.summary(print_fn=lambda x: f.write(x + '\n'))
    
    # Write training configuration
    f.write("\n" + "=" * 80 + "\n")
    f.write("TRAINING CONFIGURATION\n")
    f.write("=" * 80 + "\n\n")
    
    f.write(f"Dataset Path: {DATASET_PATH}\n")
    f.write(f"Training Samples: {num_training_samples}\n")
    f.write(f"Validation Samples: {num_validation_samples}\n")
    f.write(f"Image Size: {IMG_HEIGHT}x{IMG_WIDTH}\n")
    f.write(f"Batch Size: {BATCH_SIZE}\n")
    f.write(f"Epochs: {EPOCHS}\n")
    f.write(f"Classes: {NUM_CLASSES}\n")
    f.write(f"Class Names:\n")
    for i, class_name in enumerate(CLASS_NAMES):
        f.write(f"  {i}: {class_name}\n")
    
    # Write final metrics
    f.write("\n" + "=" * 80 + "\n")
    f.write("FINAL TRAINING METRICS\n")
    f.write("=" * 80 + "\n\n")
    
    f.write(f"Final Training Accuracy: {history.history['accuracy'][-1]:.4f}\n")
    f.write(f"Final Validation Accuracy: {history.history['val_accuracy'][-1]:.4f}\n")
    f.write(f"Final Training Loss: {history.history['loss'][-1]:.4f}\n")
    f.write(f"Final Validation Loss: {history.history['val_loss'][-1]:.4f}\n")

print(f"[✓] Model summary saved successfully!")

# ============================================================================
# FINAL SUMMARY
# ============================================================================

print("\n" + "=" * 80)
print(" " * 25 + "TRAINING COMPLETE!")
print("=" * 80)

print(f"\n[RESULTS]")
print(f"  Training Accuracy:   {history.history['accuracy'][-1]:.2%}")
print(f"  Validation Accuracy: {history.history['val_accuracy'][-1]:.2%}")
print(f"  Training Loss:       {history.history['loss'][-1]:.4f}")
print(f"  Validation Loss:     {history.history['val_loss'][-1]:.4f}")

print(f"\n[SAVED FILES]")
print(f"  Model:   {model_path}")
print(f"  Summary: {summary_path}")

print(f"\n[NEXT STEPS]")
print(f"  1. Use this model for predictions in your Django API")
print(f"  2. Load the model: keras.models.load_model('{model_path}')")
print(f"  3. Deploy to production when satisfied with results")

print("\n" + "=" * 80 + "\n")
