from pathlib import Path
import cv2
import numpy as np
from ultralytics import YOLO

# Автоматически определяем корень проекта (на 2 уровня выше, чем src/vision/)
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MODEL_PATH = (
    PROJECT_ROOT / "runs" / "segment" / "train-3" / "weights" / "yolo_seg.pt"
)


class VisionParser:

    def __init__(self, model_path=DEFAULT_MODEL_PATH):
        # Преобразуем Path в строку для YOLO
        self.model = YOLO(str(model_path))

    def parse_frame(self, image_input):
        """Принимает путь к файлу или BGR-массив OpenCV."""
        # 1. original_img — это массив пикселей изображения (numpy ndarray)
        if isinstance(image_input, str):
            original_img = cv2.imread(image_input)
        else:
            original_img = image_input

        if original_img is None:
            print("Ошибка: не удалось загрузить изображение")
            return None, None

        # 2. results — это список результатов детекции/сегментации от YOLO
        results = self.model(original_img, verbose=False)

        # 3. Извлекаем очищенные карты
        left_card, right_card = extract_hero_cards(results, original_img)

        return left_card, right_card


def extract_hero_cards(results, original_img):
    h, w, _ = original_img.shape
    detected_hero_cards = []

    for result in results:
        if result.masks is None:
            continue

        for box, mask in zip(result.boxes, result.masks.data):
            cls_id = int(box.cls[0])
            class_name = result.names[cls_id]

            if "hero_card" in class_name:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
                x_center = (x1 + x2) / 2

                # Маску приводим к размеру исходного кадра
                mask_np = mask.cpu().numpy()
                mask_resized = cv2.resize(mask_np, (w, h))
                binary_mask = (mask_resized > 0.5).astype(np.uint8) * 255

                detected_hero_cards.append(
                    {
                        "x_center": x_center,
                        "box": (x1, y1, x2, y2),
                        "mask": binary_mask,
                    }
                )

    # Сортируем карты слева направо по координате X
    detected_hero_cards.sort(key=lambda c: c["x_center"])

    left_card_crop = None
    right_card_crop = None

    if len(detected_hero_cards) >= 1:
        left_card_crop = crop_card_with_mask(
            original_img, detected_hero_cards[0]
        )

    if len(detected_hero_cards) >= 2:
        right_card_crop = crop_card_with_mask(
            original_img, detected_hero_cards[1]
        )

    return left_card_crop, right_card_crop


def crop_card_with_mask(img, card_data):
    mask = card_data["mask"]
    x1, y1, x2, y2 = card_data["box"]

    # Обрезаем маску под размер рамки (bounding box)
    crop_mask = mask[y1:y2, x1:x2]
    crop_img = img[y1:y2, x1:x2]

    # Применяем маску: всё вне карты станет чёрным (#000000)
    cleaned = cv2.bitwise_and(crop_img, crop_img, mask=crop_mask)
    return cleaned


# --- ТЕСТОВЫЙ БЛОК ДЛЯ ЗАПУСКА ФАЙЛА НАПРЯМУЮ ---
if __name__ == "__main__":
    parser = VisionParser()

    # Берем один из твоих скриншотов из папки data/raw_screenshots/
    test_image_path = "data/raw_screenshots/table_1790331089_0.jpg"

    left_card, right_card = parser.parse_frame(test_image_path)

    if left_card is not None:
        cv2.imwrite("test_left_cleaned.png", left_card)
        print("Левая карта сохранена в test_left_cleaned.png")

    if right_card is not None:
        cv2.imwrite("test_right_cleaned.png", right_card)
        print("Правая карта сохранена в test_right_cleaned.png")