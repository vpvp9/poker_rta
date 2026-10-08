from pathlib import Path
import cv2
import numpy as np
from ultralytics import YOLO

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MODEL_PATH = PROJECT_ROOT / "models" / "yolo_seg.pt"


class VisionParser:

    def __init__(self, model_path=DEFAULT_MODEL_PATH):
        self.model = YOLO(str(model_path))

    def parse_frame(
        self,
        image_input,
        crop_height_ratio=0.60,  # Запас по высоте (масть гарантированно влезает)
        crop_width_ratio=0.55,  # Запас по ширине
        padding=3,  # Расширение рамки НАРУЖУ (чтобы ничего не срезать)
    ):
        """Принимает путь к файлу (str, Path) или BGR-массив (np.ndarray).

        Возвращает полные и устойчивые вырезы углов с запасом безопасности.
        """
        # 1. Проверка и загрузка изображения
        if isinstance(image_input, (str, Path)):
            file_path = Path(image_input)
            if not file_path.exists():
                print(
                    f"Ошибка: файл не найден по пути -> {file_path.resolve()}"
                )
                return None, None
            original_img = cv2.imread(str(file_path))

        elif isinstance(image_input, np.ndarray):
            original_img = image_input
        else:
            print(f"Ошибка: неподдерживаемый тип данных -> {type(image_input)}")
            return None, None

        if original_img is None:
            print("Ошибка: cv2.imread не смог декодировать изображение")
            return None, None

        img_h, img_w = original_img.shape[:2]

        # 2. Детекция через YOLO
        results = self.model(original_img, verbose=False)
        detected_cards = []

        # 3. Собираем рамки карт
        for result in results:
            if result.boxes is None:
                continue

            for box in result.boxes:
                cls_id = int(box.cls[0])
                class_name = result.names[cls_id]

                if "hero_card" in class_name:
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
                    detected_cards.append((x1, y1, x2, y2))

        # Сортируем карты слева направо по X1
        detected_cards.sort(key=lambda b: b[0])

        corners = []

        # 4. Вырезаем углы с запасом безопасности наружу
        for x1, y1, x2, y2 in detected_cards:
            box_w = x2 - x1
            box_h = y2 - y1

            # Расширяем рамку наружу, защищая границы кадра
            start_x = max(0, x1 - padding)
            start_y = max(0, y1 - padding)

            # Рассчитываем ширину/высоту угла с учетом запаса
            corner_w = int(box_w * crop_width_ratio) + padding
            corner_h = int(box_h * crop_height_ratio) + padding

            end_x = min(img_w, start_x + corner_w)
            end_y = min(img_h, start_y + corner_h)

            # Точный срез из оригинала
            corner_crop = original_img[start_y:end_y, start_x:end_x]
            corners.append(corner_crop)

        left_corner = corners[0] if len(corners) >= 1 else None
        right_corner = corners[1] if len(corners) >= 2 else None

        return left_corner, right_corner


# --- ТЕСТОВЫЙ БЛОК ---
if __name__ == "__main__":
    parser = VisionParser()

    test_image_path = (
        PROJECT_ROOT / "data" / "raw_screenshots" / "table_1790331089_0.jpg"
    )

    left_corner, right_corner = parser.parse_frame(test_image_path)

    if left_corner is not None:
        cv2.imwrite("test_left_corner.png", left_corner)
        print("Левый угол сохранен в test_left_corner.png")

    if right_corner is not None:
        cv2.imwrite("test_right_corner.png", right_corner)
        print("Правый угол сохранен в test_right_corner.png")