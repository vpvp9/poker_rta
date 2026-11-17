from pathlib import Path
import cv2
import torch

from src.vision.card_recognizer import CardRecognizer
from src.vision.vision_parser import VisionParser

PROJECT_ROOT = Path(__file__).resolve().parent.parent  # для файлов в папке tests/ или scripts/
WEIGHTS_PATH = PROJECT_ROOT / "models" / "card_recognizer.pth"
RAW_SCREENSHOTS_DIR = PROJECT_ROOT / "data" / "raw_screenshots"

CONFIDENCE_THRESHOLD = 0.5  # Порог фильтрации слабых предсказаний


def main():
    print("Инициализация пайплайна...")

    if not WEIGHTS_PATH.exists():
        print(f"Ошибка: Не найдены веса модели: {WEIGHTS_PATH.resolve()}")
        return

    parser = VisionParser()
    recognizer = CardRecognizer(model_weights_path=WEIGHTS_PATH)

    if not RAW_SCREENSHOTS_DIR.exists():
        print(f"Папка со скриншотами не найдена: {RAW_SCREENSHOTS_DIR}")
        return

    image_files = list(RAW_SCREENSHOTS_DIR.glob("*.jpg")) + list(
        RAW_SCREENSHOTS_DIR.glob("*.png")
    )
    if not image_files:
        print(f"В папке {RAW_SCREENSHOTS_DIR} нет изображений!")
        return

    print(f"Найдено скриншотов: {len(image_files)}\n" + "=" * 50)

    for img_path in image_files:
        print(f"Файл: {img_path.name}")

        left_crop, right_crop = parser.parse_frame(img_path)

        # Распознаем левую карту с фильтрацией по порогу
        if left_crop is not None and left_crop.size > 0:
            left_card, left_conf = recognizer.predict_with_confidence(
                left_crop
            )
            if left_conf < CONFIDENCE_THRESHOLD:
                left_card, left_conf = "??", left_conf
        else:
            left_card, left_conf = "??", 0.0

            # Распознаем правую карту с фильтрацией по порогу
        if right_crop is not None and right_crop.size > 0:
            right_card, right_conf = recognizer.predict_with_confidence(
                right_crop
            )
            if right_conf < CONFIDENCE_THRESHOLD:
                right_card, right_conf = "??", 0.0
        else:
            right_card, right_conf = "??", 0.0

        print(
            f"   -> Рука героя: [{left_card} (conf: {left_conf:.2f})]  [{right_card} (conf: {right_conf:.2f})]"
        )
        print("-" * 50)

    print("\n Тест завершен.")


if __name__ == "__main__":
    main()