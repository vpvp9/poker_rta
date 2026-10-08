from pathlib import Path
import cv2
import numpy as np
import torch
import torch.nn as nn

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RANKS = ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"]
SUITS = ["s", "c", "h", "d"]


class CardCornerNet(nn.Module):
    """Легкая сверточная сеть для распознавания номинала и масти."""

    def __init__(self):
        super().__init__()
        # Общий экстрактор признаков
        self.features = nn.Sequential(
            nn.Conv2d(3, 16, kernel_size=3, padding=1),
            nn.BatchNorm2d(16),
            nn.ReLU(),
            nn.MaxPool2d(2, 2),  # -> 19x26
            nn.Conv2d(16, 32, kernel_size=3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.MaxPool2d(2, 2),  # -> 9x13
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.AdaptiveAvgPool2d((4, 4)),
        )

        # Голова 1: Номинал (13 классов)
        self.rank_head = nn.Sequential(
            nn.Flatten(),
            nn.Linear(64 * 4 * 4, 64),
            nn.ReLU(),
            nn.Linear(64, len(RANKS)),
        )

        # Голова 2: Масть (4 класса)
        self.suit_head = nn.Sequential(
            nn.Flatten(),
            nn.Linear(64 * 4 * 4, 32),
            nn.ReLU(),
            nn.Linear(32, len(SUITS)),
        )

    def forward(self, x):
        feat = self.features(x)
        rank_logits = self.rank_head(feat)
        suit_logits = self.suit_head(feat)
        return rank_logits, suit_logits


class CardRecognizer:

    def __init__(self, model_weights_path=None):
        self.device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu"
        )
        self.model = CardCornerNet().to(self.device)
        self.model.eval()

        if model_weights_path and Path(model_weights_path).exists():
            self.model.load_state_dict(
                torch.load(model_weights_path, map_location=self.device)
            )

    def preprocess(self, img_crop):
        """Приводит угол к стандартному размеру и нормализует для PyTorch."""
        img_resized = cv2.resize(img_crop, (32, 48))
        img_rgb = cv2.cvtColor(img_resized, cv2.COLOR_BGR2RGB)
        tensor = (
            torch.from_numpy(img_rgb).permute(2, 0, 1).float() / 255.0
        )
        return tensor.unsqueeze(0).to(self.device)

    def predict(self, img_crop):
        """Возвращает строковый код карты, например 'Kh' или 'Td'."""
        if img_crop is None or img_crop.size == 0:
            return None

        tensor = self.preprocess(img_crop)

        with torch.no_grad():
            rank_logits, suit_logits = self.model(tensor)
            rank_idx = torch.argmax(rank_logits, dim=1).item()
            suit_idx = torch.argmax(suit_logits, dim=1).item()

        return f"{RANKS[rank_idx]}{SUITS[suit_idx]}"