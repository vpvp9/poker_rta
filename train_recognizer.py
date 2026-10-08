from pathlib import Path
import cv2
from PIL import Image
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms

from src.vision.card_recognizer import RANKS, SUITS, CardCornerNet

# Корень проекта D:\py\poker_rta
PROJECT_ROOT = Path(__file__).resolve().parent
DATASET_DIR = PROJECT_ROOT / "data" / "dataset_corners" / "train"
MODEL_SAVE_PATH = PROJECT_ROOT / "models" / "card_recognizer.pth"


class CardCornerDataset(Dataset):

    def __init__(self, root_dir, transform=None):
        self.samples = []
        self.transform = transform

        root_path = Path(root_dir)
        if not root_path.exists():
            raise FileNotFoundError(
                f"Папка датасета не найдена по пути: {root_path.resolve()}"
            )

        rank_to_idx = {r: i for i, r in enumerate(RANKS)}
        suit_to_idx = {s: i for i, s in enumerate(SUITS)}

        # Сканируем подпапки формата '2c', 'Qs', 'Ad' внутри train/
        for folder in root_path.iterdir():
            if folder.is_dir() and len(folder.name) == 2:
                rank_str, suit_str = folder.name[0], folder.name[1]
                if rank_str in rank_to_idx and suit_str in suit_to_idx:
                    r_idx = rank_to_idx[rank_str]
                    s_idx = suit_to_idx[suit_str]

                    # Поддерживаем и .png, и .jpg файлы
                    img_files = list(folder.glob("*.png")) + list(
                        folder.glob("*.jpg")
                    )
                    for img_file in img_files:
                        self.samples.append((img_file, r_idx, s_idx))

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        img_path, r_idx, s_idx = self.samples[idx]

        img_bgr = cv2.imread(str(img_path))
        if img_bgr is None:
            raise ValueError(
                f"Не удалось прочитать файл изображения: {img_path}"
            )

        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(img_rgb)

        if self.transform:
            tensor = self.transform(pil_img)
        else:
            tensor = transforms.functional.to_tensor(
                transforms.functional.resize(pil_img, (48, 32))
            )

        return tensor, r_idx, s_idx


def train():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Используем устройство: {device}")
    print(f"Проверка пути к датасету: {DATASET_DIR.resolve()}")

    # Аугментация: симулирует левые/правые сдвиги и колебания цвета
    train_transforms = transforms.Compose([
        transforms.Resize((48, 32)),
        transforms.RandomRotation(degrees=4),
        transforms.RandomAffine(
            degrees=0, translate=(0.06, 0.06), scale=(0.95, 1.05)
        ),
        transforms.ColorJitter(brightness=0.2, contrast=0.2),
        transforms.ToTensor(),
    ])

    try:
        dataset = CardCornerDataset(DATASET_DIR, transform=train_transforms)
    except FileNotFoundError as e:
        print(f"\n Ошибка: {e}")
        return

    if len(dataset) == 0:
        print(f"\n Внимание: Не найдено картинок по пути {DATASET_DIR}")
        print("Убедись, что внутри папок (например '2c') содержатся .png файлы.")
        return

    print(f"Успешно загружено файлов углов: {len(dataset)}")

    batch_size = min(8, len(dataset))
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

    model = CardCornerNet().to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

    epochs = 40
    print("\nЗапуск процесса обучения...")

    for epoch in range(epochs):
        model.train()
        total_loss = 0.0
        r_correct = 0
        s_correct = 0
        total_samples = 0

        for images, r_targets, s_targets in loader:
            images = images.to(device)
            r_targets = r_targets.to(device)
            s_targets = s_targets.to(device)

            optimizer.zero_grad()
            r_logits, s_logits = model(images)

            loss_r = criterion(r_logits, r_targets)
            loss_s = criterion(s_logits, s_targets)
            loss = loss_r + loss_s

            loss.backward()
            optimizer.step()

            total_loss += loss.item()

            r_correct += (
                (r_logits.argmax(dim=1) == r_targets).sum().item()
            )
            s_correct += (
                (s_logits.argmax(dim=1) == s_targets).sum().item()
            )
            total_samples += r_targets.size(0)

        if (epoch + 1) % 5 == 0 or epoch == epochs - 1:
            r_acc = (r_correct / total_samples) * 100
            s_acc = (s_correct / total_samples) * 100
            avg_loss = total_loss / len(loader)
            print(
                f"Эпоха [{epoch+1:02d}/{epochs}] | Loss: {avg_loss:.4f} | Rank Acc: {r_acc:.1f}% | Suit Acc: {s_acc:.1f}%"
            )

    MODEL_SAVE_PATH.parent.mkdir(parents=True, exist_ok=True)
    torch.save(model.state_dict(), MODEL_SAVE_PATH)
    print(f"\n Готово! Веса сохранены в: {MODEL_SAVE_PATH.resolve()}")


if __name__ == "__main__":
    train()