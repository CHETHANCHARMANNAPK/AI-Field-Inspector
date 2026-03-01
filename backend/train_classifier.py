"""
Train a crack detection classifier on the local dataset.

Usage:
    python -m backend.train_classifier

This trains a lightweight CNN on dataset/cracked and dataset/uncracked,
then saves the model to models/crack_classifier.pth
"""

import os
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, random_split
from torchvision import datasets, transforms, models
from pathlib import Path


# ── Configuration ─────────────────────────────────────────────────────────────
DATASET_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "dataset")
MODEL_SAVE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models", "crack_classifier.pth")
CLASS_NAMES = ["uncracked", "cracked"]  # folder alphabetical order: cracked=0, uncracked=1 → we remap
IMG_SIZE = 224
BATCH_SIZE = 16
EPOCHS = 10
LEARNING_RATE = 0.001
VALIDATION_SPLIT = 0.2
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


# ── Data Transforms ──────────────────────────────────────────────────────────
train_transform = transforms.Compose([
    transforms.Resize((IMG_SIZE, IMG_SIZE)),
    transforms.RandomHorizontalFlip(),
    transforms.RandomRotation(15),
    transforms.ColorJitter(brightness=0.2, contrast=0.2),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225]),
])

val_transform = transforms.Compose([
    transforms.Resize((IMG_SIZE, IMG_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225]),
])


# ── Model ─────────────────────────────────────────────────────────────────────
def create_model(num_classes=2):
    """Create a MobileNetV2-based classifier (lightweight & fast)."""
    model = models.mobilenet_v2(weights=models.MobileNet_V2_Weights.DEFAULT)
    # Freeze early layers
    for param in model.features[:-4].parameters():
        param.requires_grad = False
    # Replace classifier head
    model.classifier = nn.Sequential(
        nn.Dropout(0.3),
        nn.Linear(model.last_channel, num_classes),
    )
    return model


def train():
    """Train the crack classifier and save weights."""
    print(f"[train] Device: {DEVICE}")
    print(f"[train] Dataset: {DATASET_DIR}")

    # ── Load dataset ──────────────────────────────────────────────────────────
    full_dataset = datasets.ImageFolder(DATASET_DIR, transform=train_transform)
    class_to_idx = full_dataset.class_to_idx
    print(f"[train] Classes found: {class_to_idx}")
    print(f"[train] Total images: {len(full_dataset)}")

    # Split into train / val
    val_size = int(len(full_dataset) * VALIDATION_SPLIT)
    train_size = len(full_dataset) - val_size
    train_dataset, val_dataset = random_split(full_dataset, [train_size, val_size])

    # Override val transform (no augmentation)
    val_dataset.dataset = datasets.ImageFolder(DATASET_DIR, transform=val_transform)

    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False, num_workers=0)

    print(f"[train] Train: {train_size}, Val: {val_size}")

    # ── Model, Loss, Optimizer ────────────────────────────────────────────────
    model = create_model(num_classes=2).to(DEVICE)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(filter(lambda p: p.requires_grad, model.parameters()), lr=LEARNING_RATE)
    scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=5, gamma=0.5)

    # ── Training loop ─────────────────────────────────────────────────────────
    best_val_acc = 0.0

    for epoch in range(EPOCHS):
        # Train
        model.train()
        running_loss = 0.0
        correct = 0
        total = 0

        for images, labels in train_loader:
            images, labels = images.to(DEVICE), labels.to(DEVICE)
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item()
            _, predicted = outputs.max(1)
            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()

        train_acc = 100.0 * correct / total
        avg_loss = running_loss / len(train_loader)

        # Validate
        model.eval()
        val_correct = 0
        val_total = 0
        with torch.no_grad():
            for images, labels in val_loader:
                images, labels = images.to(DEVICE), labels.to(DEVICE)
                outputs = model(images)
                _, predicted = outputs.max(1)
                val_total += labels.size(0)
                val_correct += predicted.eq(labels).sum().item()

        val_acc = 100.0 * val_correct / max(val_total, 1)

        print(f"[train] Epoch {epoch+1}/{EPOCHS} — "
              f"Loss: {avg_loss:.4f}, Train Acc: {train_acc:.1f}%, Val Acc: {val_acc:.1f}%")

        # Save best model
        if val_acc >= best_val_acc:
            best_val_acc = val_acc
            os.makedirs(os.path.dirname(MODEL_SAVE_PATH), exist_ok=True)

            save_data = {
                "model_state_dict": model.state_dict(),
                "class_to_idx": class_to_idx,
                "idx_to_class": {v: k for k, v in class_to_idx.items()},
                "img_size": IMG_SIZE,
                "val_accuracy": val_acc,
                "epoch": epoch + 1,
            }
            torch.save(save_data, MODEL_SAVE_PATH)
            print(f"[train] ✓ Best model saved ({val_acc:.1f}% val accuracy)")

        scheduler.step()

    print(f"\n[train] Training complete! Best Val Accuracy: {best_val_acc:.1f}%")
    print(f"[train] Model saved to: {MODEL_SAVE_PATH}")


if __name__ == "__main__":
    train()
