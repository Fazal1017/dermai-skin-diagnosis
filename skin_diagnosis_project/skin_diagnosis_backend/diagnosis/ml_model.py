"""
SkinDiagnosisModel - PyTorch inference wrapper for skin lesion classification.

Loads a trained ResNet50-based PyTorch model and provides prediction capabilities
for the Django REST API.
"""

import os
import glob
import numpy as np
import torch
import torch.nn as nn
from torchvision import models, transforms
from pathlib import Path


class SkinDiagnosisModel:
    """
    Wraps the trained PyTorch ResNet50 model for inference.
    
    The model classifies skin lesion images into 7 categories:
    - melanoma, nevus, basal_cell_carcinoma, actinic_keratosis,
      benign_keratosis, dermatofibroma, vascular_lesion
    """
    
    # Default class names (fallback if not stored in checkpoint)
    DEFAULT_CLASSES = [
        'actinic_keratosis',
        'basal_cell_carcinoma',
        'benign_keratosis',
        'dermatofibroma',
        'melanoma',
        'nevus',
        'vascular_lesion',
    ]
    
    def __init__(self, model_path=None):
        """
        Initialize the model.
        
        Args:
            model_path: Path to the .pt checkpoint file. If None, auto-discovers
                        the latest model in the 'models/' directory.
        """
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = None
        self.classes = None
        
        # ImageNet normalization transform (must match training preprocessing)
        self.normalize = transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        )
        
        # Find and load the model
        if model_path is None:
            model_path = self._find_latest_model()
        
        self._load_model(model_path)
        print(f"[ML Model] Loaded model from: {model_path}")
        print(f"[ML Model] Using device: {self.device}")
        print(f"[ML Model] Classes: {self.classes}")
    
    def _find_latest_model(self):
        """Auto-discover the latest .pt model file in the diagnosis folder."""
        # Look in the diagnosis folder (same directory as this file)
        diagnosis_dir = Path(__file__).resolve().parent
        
        # Find all .pt files and pick the latest by modification time
        pt_files = list(diagnosis_dir.glob('*.pt'))
        
        if not pt_files:
            raise FileNotFoundError(
                f"No .pt model files found in: {diagnosis_dir}\n"
                "Please train a model first using: python diagnosis/train_pytorch.py\n"
                "and ensure the .pt file is placed in the diagnosis/ directory."
            )
        
        # Sort by modification time (latest first)
        pt_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
        return str(pt_files[0])
    
    def _load_model(self, model_path):
        """Load the PyTorch model from a checkpoint file."""
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")
        
        # Load checkpoint
        checkpoint = torch.load(model_path, map_location=self.device, weights_only=False)
        
        # Get class names from checkpoint (or use defaults)
        self.classes = checkpoint.get('classes', self.DEFAULT_CLASSES)
        num_classes = len(self.classes)
        
        # Rebuild the model architecture (ResNet50 with custom final layer)
        self.model = models.resnet50(weights=None)
        num_ftrs = self.model.fc.in_features
        self.model.fc = nn.Linear(num_ftrs, num_classes)
        
        # Load trained weights
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.model.to(self.device)
        self.model.eval()  # Set to evaluation mode
        
        # Log checkpoint info
        if 'accuracy' in checkpoint:
            print(f"[ML Model] Checkpoint accuracy: {checkpoint['accuracy']:.2f}%")
        if 'epoch' in checkpoint:
            print(f"[ML Model] Trained for {checkpoint['epoch']} epochs")
    
    def _to_tensor(self, image_array):
        """Convert preprocessed numpy array to normalized PyTorch tensor.
        
        Args:
            image_array: numpy array of shape (1, 224, 224, 3), values in 0-1 range.
        
        Returns:
            Tensor of shape (1, 3, 224, 224), ImageNet-normalized.
        """
        tensor = torch.from_numpy(image_array).permute(0, 3, 1, 2).float()
        tensor = self.normalize(tensor.squeeze(0)).unsqueeze(0)
        return tensor.to(self.device)

    def _probs_from_tensor(self, tensor):
        """Run a forward pass and return softmax probabilities as numpy array."""
        outputs = self.model(tensor)
        probabilities = torch.nn.functional.softmax(outputs, dim=1)
        return probabilities.cpu().numpy()[0]

    def _build_results(self, probs):
        """Convert a probability array into (predicted_condition, all_scores)."""
        predicted_idx = int(np.argmax(probs))
        predicted_condition = self.classes[predicted_idx]
        all_scores = {
            self.classes[i]: round(float(probs[i]), 6)
            for i in range(len(self.classes))
        }
        return predicted_condition, all_scores

    def predict(self, image_array):
        """
        Make a prediction on a preprocessed image.
        
        Args:
            image_array: numpy array of shape (1, 224, 224, 3), values in 0-1 range.
                         This is the format provided by views.py._preprocess_image().
        
        Returns:
            predicted_condition: string name of the predicted skin condition
            all_scores: dict mapping class names to confidence scores
        """
        with torch.no_grad():
            tensor = self._to_tensor(image_array)
            probs = self._probs_from_tensor(tensor)
        return self._build_results(probs)

    def predict_with_tta(self, image_array, n_aug=5):
        """
        Test-Time Augmentation: average predictions over multiple augmented
        versions of the same image for more robust results.
        
        Augmentations applied (small, non-destructive):
        - Random brightness adjustment (±10%)
        - Random small translation (up to 2% of image size)
        - Random horizontal flip
        
        Args:
            image_array: numpy array of shape (1, 224, 224, 3), values in 0-1 range.
            n_aug: Number of augmented copies to average (default 5).
                   Higher = more robust but slower (linear scaling).
        
        Returns:
            predicted_condition: string name of the predicted skin condition
            all_scores: dict mapping class names to confidence scores
        """
        # TTA augmentation pipeline (applied BEFORE ImageNet normalization)
        tta_augment = transforms.Compose([
            transforms.ColorJitter(brightness=0.1),                # ±10% brightness
            transforms.RandomAffine(degrees=0, translate=(0.02, 0.02)),  # ±2% shift
            transforms.RandomHorizontalFlip(p=0.5),
        ])

        all_probs = []

        with torch.no_grad():
            # 1) Original (un-augmented) prediction
            tensor_orig = self._to_tensor(image_array)
            all_probs.append(self._probs_from_tensor(tensor_orig))

            # 2) Augmented predictions
            # Work on the raw 0-1 tensor BEFORE normalization so augments are meaningful
            raw_tensor = torch.from_numpy(image_array).permute(0, 3, 1, 2).float().squeeze(0)  # (3, H, W)

            for _ in range(n_aug - 1):
                aug_tensor = tta_augment(raw_tensor)                     # (3, H, W)
                normed = self.normalize(aug_tensor).unsqueeze(0)          # (1, 3, H, W)
                normed = normed.to(self.device)
                all_probs.append(self._probs_from_tensor(normed))

        # Average all softmax outputs
        avg_probs = np.mean(all_probs, axis=0)
        return self._build_results(avg_probs)
