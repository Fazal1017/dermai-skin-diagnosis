#!/usr/bin/env python3
"""
CNN Training Script using PyTorch
Trains a ResNet50-based model on skin disease classification
"""
import os
import sys
import argparse
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, random_split
from torchvision import datasets, transforms, models
from pathlib import Path
import json
from datetime import datetime

# Device
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Using device: {device}")

def parse_args():
    parser = argparse.ArgumentParser(description='Train CNN for skin disease classification')
    parser.add_argument('--dataset', '-d', default='../../dataset', help='Path to dataset')
    parser.add_argument('--epochs', '-e', type=int, default=20, help='Number of epochs')
    parser.add_argument('--batch-size', '-b', type=int, default=32, help='Batch size')
    parser.add_argument('--lr', type=float, default=0.001, help='Learning rate')
    parser.add_argument('--output', '-o', default='models/', help='Output directory for models')
    return parser.parse_args()

def main():
    args = parse_args()
    
    dataset_path = os.path.abspath(args.dataset)
    output_dir = args.output
    os.makedirs(output_dir, exist_ok=True)
    
    if not os.path.isdir(dataset_path):
        print(f"❌ Dataset path not found: {dataset_path}")
        sys.exit(1)
    
    print("=" * 60)
    print("🚀 SKIN DISEASE CNN TRAINING - PyTorch")
    print("=" * 60)
    print(f"\n📂 Dataset: {dataset_path}")
    print(f"💾 Output: {output_dir}")
    print(f"📊 Epochs: {args.epochs}")
    print(f"⚙️ Batch size: {args.batch_size}")
    print(f"🎓 Learning rate: {args.lr}")
    
    # Data transforms
    train_transforms = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(20),
        transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406],
                           std=[0.229, 0.224, 0.225])
    ])
    
    val_transforms = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406],
                           std=[0.229, 0.224, 0.225])
    ])
    
    # Load dataset
    print("\n📥 Loading dataset...")
    full_dataset = datasets.ImageFolder(dataset_path, transform=train_transforms)
    classes = full_dataset.classes
    
    print(f"   Classes: {classes}")
    print(f"   Total images: {len(full_dataset)}")
    
    # Split dataset
    train_size = int(0.8 * len(full_dataset))
    val_size = len(full_dataset) - train_size
    train_dataset, val_dataset = random_split(full_dataset, [train_size, val_size])
    
    # Override val_dataset transforms
    val_dataset.dataset.transform = val_transforms
    
    train_loader = DataLoader(train_dataset, batch_size=args.batch_size, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_dataset, batch_size=args.batch_size, shuffle=False, num_workers=0)
    
    print(f"   Training samples: {len(train_dataset)}")
    print(f"   Validation samples: {len(val_dataset)}")
    
    # Model
    print("\n🧠 Building model...")
    model = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V2)
    
    # Modify final layer for 7 classes
    num_ftrs = model.fc.in_features
    model.fc = nn.Linear(num_ftrs, len(classes))
    model = model.to(device)
    
    # Loss and optimizer
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=args.lr)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', factor=0.5, patience=3)
    
    # Training loop
    print("\n🏃 Training started...")
    print("-" * 60)
    
    best_val_acc = 0
    training_history = {
        'epochs': [],
        'train_loss': [],
        'val_loss': [],
        'train_acc': [],
        'val_acc': []
    }
    
    for epoch in range(args.epochs):
        # Train
        model.train()
        train_loss = 0.0
        train_correct = 0
        train_total = 0
        
        for batch_idx, (inputs, targets) in enumerate(train_loader):
            inputs, targets = inputs.to(device), targets.to(device)
            
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, targets)
            loss.backward()
            optimizer.step()
            
            train_loss += loss.item()
            _, predicted = torch.max(outputs.data, 1)
            train_total += targets.size(0)
            train_correct += (predicted == targets).sum().item()
            
            if (batch_idx + 1) % 10 == 0:
                print(f"   Batch {batch_idx + 1}/{len(train_loader)}")
        
        train_loss /= len(train_loader)
        train_acc = 100 * train_correct / train_total
        
        # Validate
        model.eval()
        val_loss = 0.0
        val_correct = 0
        val_total = 0
        
        with torch.no_grad():
            for inputs, targets in val_loader:
                inputs, targets = inputs.to(device), targets.to(device)
                outputs = model(inputs)
                loss = criterion(outputs, targets)
                
                val_loss += loss.item()
                _, predicted = torch.max(outputs.data, 1)
                val_total += targets.size(0)
                val_correct += (predicted == targets).sum().item()
        
        val_loss /= len(val_loader)
        val_acc = 100 * val_correct / val_total
        
        scheduler.step(val_loss)
        
        training_history['epochs'].append(epoch + 1)
        training_history['train_loss'].append(train_loss)
        training_history['val_loss'].append(val_loss)
        training_history['train_acc'].append(train_acc)
        training_history['val_acc'].append(val_acc)
        
        print(f"Epoch {epoch + 1}/{args.epochs}")
        print(f"  Train Loss: {train_loss:.4f} | Train Acc: {train_acc:.2f}%")
        print(f"  Val Loss:   {val_loss:.4f} | Val Acc:   {val_acc:.2f}%")
        
        # Save best model
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            model_path = os.path.join(output_dir, f'skin_diagnosis_model_{timestamp}.pt')
            torch.save({
                'epoch': epoch + 1,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'classes': classes,
                'accuracy': val_acc,
                'loss': val_loss
            }, model_path)
            print(f"  ✅ Model saved: {model_path}")
    
    print("\n" + "=" * 60)
    print("✅ TRAINING COMPLETED")
    print("=" * 60)
    print(f"Best validation accuracy: {best_val_acc:.2f}%")
    print(f"Models saved in: {output_dir}")
    
    # Save history
    history_path = os.path.join(output_dir, 'training_history.json')
    with open(history_path, 'w') as f:
        json.dump(training_history, f, indent=2)
    print(f"Training history saved: {history_path}")

if __name__ == '__main__':
    main()
