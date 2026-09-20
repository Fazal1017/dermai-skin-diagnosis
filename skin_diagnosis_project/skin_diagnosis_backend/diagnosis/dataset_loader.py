import os
import numpy as np
from PIL import Image
from sklearn.model_selection import train_test_split

class DatasetLoader:
    """
    Loads and preprocesses skin lesion images from the dataset folder
    """
    
    def __init__(self, dataset_path, target_size=(224, 224), batch_size=32):
        """
        Initialize the dataset loader
        
        Args:
            dataset_path: Path to the dataset folder containing class subdirectories
            target_size: Size to resize images to (default 224x224 for MobileNetV2)
            batch_size: Batch size for training
        """
        self.dataset_path = dataset_path
        self.target_size = target_size
        self.batch_size = batch_size
        self.class_names = []
        self.class_to_idx = {}
        self.total_images = 0
        
        self._validate_dataset()
    
    def _validate_dataset(self):
        """Validate that the dataset folder exists and contains subdirectories"""
        if not os.path.exists(self.dataset_path):
            raise FileNotFoundError(f"Dataset path not found: {self.dataset_path}")
        
        # Get class directories
        for item in os.listdir(self.dataset_path):
            item_path = os.path.join(self.dataset_path, item)
            if os.path.isdir(item_path):
                self.class_names.append(item)
                self.class_to_idx[item] = len(self.class_to_idx)
        
        if not self.class_names:
            raise ValueError(f"No class subdirectories found in {self.dataset_path}")
        
        self.class_names.sort()
        # Rebuild index after sorting
        self.class_to_idx = {name: idx for idx, name in enumerate(self.class_names)}
        
        # Count total images
        for class_name in self.class_names:
            class_path = os.path.join(self.dataset_path, class_name)
            num_images = len([f for f in os.listdir(class_path) 
                            if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
            self.total_images += num_images
            print(f"Found {num_images} images in {class_name}")
    
    def load_images_with_labels(self):
        """
        Load all images and their labels from the dataset
        
        Returns:
            images: numpy array of shape (N, 224, 224, 3)
            labels: numpy array of shape (N,) with class indices
        """
        images = []
        labels = []
        
        print(f"Loading {self.total_images} images...")
        
        for class_name in self.class_names:
            class_path = os.path.join(self.dataset_path, class_name)
            class_idx = self.class_to_idx[class_name]
            
            for img_file in os.listdir(class_path):
                if img_file.lower().endswith(('.jpg', '.jpeg', '.png')):
                    img_path = os.path.join(class_path, img_file)
                    try:
                        # Load image
                        img = Image.open(img_path).convert('RGB')
                        # Resize
                        img = img.resize(self.target_size)
                        # Convert to array
                        img_array = np.array(img) / 255.0  # Normalize to 0-1
                        
                        images.append(img_array)
                        labels.append(class_idx)
                    except Exception as e:
                        print(f"Error loading {img_path}: {e}")
        
        return np.array(images), np.array(labels)
    
    def create_data_generators(self, validation_split=0.2, test_split=0.1):
        """
        Create training, validation, and test datasets using ImageDataGenerator
        
        Args:
            validation_split: Fraction of data for validation
            test_split: Fraction of data for testing
        
        Returns:
            train_generator, validation_generator, test_generator
        """
        raise RuntimeError(
            "create_data_generators() is not available in this build because TensorFlow is not listed in the project dependencies. Use create_generators_from_memory() instead."
        )
    
    def create_generators_from_memory(self, validation_split=0.2, test_split=0.1):
        """
        Load all images into memory and create generators
        Useful when dataset size is manageable
        
        Returns:
            train_images, train_labels, val_images, val_labels, test_images, test_labels
        """
        print("Loading all images into memory...")
        images, labels = self.load_images_with_labels()
        
        # Convert labels to one-hot encoding
        labels_one_hot = np.eye(len(self.class_names), dtype=np.float32)[labels]
        
        # Split into train + val, then split val into val and test
        X_train, X_temp, y_train, y_temp = train_test_split(
            images, labels_one_hot, 
            test_size=(validation_split + test_split),
            random_state=42,
            stratify=np.argmax(labels_one_hot, axis=1)
        )
        
        # Split temp into validation and test
        val_test_ratio = test_split / (validation_split + test_split)
        X_val, X_test, y_val, y_test = train_test_split(
            X_temp, y_temp,
            test_size=val_test_ratio,
            random_state=42,
            stratify=np.argmax(y_temp, axis=1)
        )
        
        print(f"Train set: {X_train.shape[0]} images")
        print(f"Validation set: {X_val.shape[0]} images")
        print(f"Test set: {X_test.shape[0]} images")
        
        return X_train, y_train, X_val, y_val, X_test, y_test
    
    def get_class_weights(self):
        """
        Calculate class weights to handle imbalanced datasets
        Returns weights that give more importance to rare classes
        """
        from sklearn.utils.class_weight import compute_class_weight
        
        images, labels = self.load_images_with_labels()
        
        class_weights = compute_class_weight(
            'balanced',
            classes=np.unique(labels),
            y=labels
        )
        
        return dict(enumerate(class_weights))
