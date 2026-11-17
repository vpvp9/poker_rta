import sys
from pathlib import Path
import cv2
import numpy as np
from ultralytics import YOLO

# Добавляем корень проекта в системный путь
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.vision.position_detector import PositionDetector
from src.vision.card_recognizer import CardRecognizer
from src.vision.ocr_parser import OCRParser  # Подключаем наш OCR-парсер

DEFAULT_YOLO_PATH = PROJECT_ROOT / "models" / "yolo.pt"
DEFAULT_YOLO2_PATH = PROJECT_ROOT / "models" / "yolo2.pt"
DEFAULT_RECOGNIZER_PATH = PROJECT_ROOT / "models" / "card_recognizer.pth"


class VisionParser:
    def __init__(
            self,
            model_path=DEFAULT_YOLO_PATH,
            yolo2_path=DEFAULT_YOLO2_PATH,
            recognizer_path=DEFAULT_RECOGNIZER_PATH
    ):
        print("👁️ Инициализация VisionParser и OCR...")
        self.model = YOLO(str(model_path))
        self.position_detector = PositionDetector(model_path=yolo2_path)
        self.card_recognizer = CardRecognizer(model_weights_path=recognizer_path)
        self.ocr_parser = OCRParser()  # Инициализируем распознаватель текста/цифр

    def _load_image(self, image_input):
        if isinstance(image_input, (str, Path)):
            file_path = Path(image_input)
            if not file_path.exists():
                print(f"❌ Ошибка: файл не найден по пути -> {file_path.resolve()}")
                return None
            return cv2.imread(str(file_path))
        elif isinstance(image_input, np.ndarray):
            return image_input
        else:
            print(f"❌ Ошибка: неподдерживаемый тип данных -> {type(image_input)}")
            return None

    def _crop_and_recognize_cards(self, original_img, card_boxes, crop_h_ratio, crop_w_ratio, padding):
        """Вспомогательный метод для нарезки уголков и прогона через CardRecognizer."""
        img_h, img_w = original_img.shape[:2]
        recognized_cards = []

        card_boxes.sort(key=lambda b: b[0])

        for x1, y1, x2, y2 in card_boxes:
            box_w = x2 - x1
            box_h = y2 - y1

            start_x = max(0, x1 - padding)
            start_y = max(0, y1 - padding)

            corner_w = int(box_w * crop_w_ratio) + padding
            corner_h = int(box_h * crop_h_ratio) + padding

            end_x = min(img_w, start_x + corner_w)
            end_y = min(img_h, start_y + corner_h)

            corner_crop = original_img[start_y:end_y, start_x:end_x]
            card_name = self.card_recognizer.predict(corner_crop)
            if card_name:
                recognized_cards.append(card_name)

        return recognized_cards

    def parse_full_state(
            self,
            image_input,
            crop_height_ratio=0.60,
            crop_width_ratio=0.55,
            padding=3
    ):
        """Главный метод для RTA: возвращает карты, борд, позицию и финансовые данные стола."""
        original_img = self._load_image(image_input)
        if original_img is None:
            return None

        results = self.model(original_img, verbose=False)[0]

        hero_boxes = []
        board_boxes = []
        bets_data = []
        stacks_data = []
        pot_values = []

        for box in results.boxes:
            cls_id = int(box.cls[0].item())
            class_name = results.names[cls_id]
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)

            if class_name in ["left_hero", "right_hero"]:
                hero_boxes.append((x1, y1, x2, y2))
            elif class_name == "board_card":
                board_boxes.append((x1, y1, x2, y2))
            elif class_name in ["player_bet", "hero_bet"]:
                # Вырезаем кроп ставки и распознаем число
                crop = original_img[y1:y2, x1:x2]
                val = self.ocr_parser.extract_number(crop)
                if val is not None:
                    bets_data.append({"box": (x1, y1, x2, y2), "value": val})
            elif class_name in ["player_stack", "hero_stack"]:
                # Вырезаем кроп стека
                crop = original_img[y1:y2, x1:x2]
                val = self.ocr_parser.extract_number(crop)
                if val is not None:
                    stacks_data.append({"box": (x1, y1, x2, y2), "value": val})
            elif class_name == "pot":
                # Передаем весь бокс целиком — OCR сам прочтет "Банк: 24 ББ", а наш метод очистит текст до числа 24.0
                crop = original_img[y1:y2, x1:x2]
                val = self.ocr_parser.extract_number(crop)
                if val is not None:
                    pot_values.append(val)

        # Распознаем карты
        hero_cards = self._crop_and_recognize_cards(
            original_img, hero_boxes, crop_height_ratio, crop_width_ratio, padding
        )
        board_cards = self._crop_and_recognize_cards(
            original_img, board_boxes, crop_height_ratio, crop_width_ratio, padding
        )

        # Определяем позицию
        position = self.position_detector.detect_position(image_input)

        # Общий банк (берем максимальное или первое успешное распознавание pot)
        total_pot = pot_values[0] if pot_values else 0.0

        return {
            "hero_cards": hero_cards,
            "board_cards": board_cards,
            "position": position,
            "pot": total_pot,
            "bets": bets_data,
            "stacks": stacks_data
        }


# --- ТЕСТОВЫЙ БЛОК ---
if __name__ == "__main__":
    parser = VisionParser()
    screenshots_dir = PROJECT_ROOT / "data" / "raw_screenshots"

    test_images = list(screenshots_dir.glob("*.jpg")) + list(screenshots_dir.glob("*.png"))

    if not test_images:
        print(f"⚠️ В папке {screenshots_dir} не найдено тестовых изображений!")
    else:
        print(f"\n🧪 Запуск полного тест-пайплайна для {len(test_images)} скриншотов:\n" + "=" * 50)

        for img_path in test_images:
            print(f"📁 Файл: {img_path.name}")
            state = parser.parse_full_state(img_path)
            if state:
                print(f"   ♠️ Карты героя: {state['hero_cards']}")
                print(f"   🃏 Карты борда: {state['board_cards']}")
                print(f"   📍 Позиция: {state['position']}")
                print(f"   💰 Банк (Pot): {state['pot']}")
                print(f"   🎯 Ставки: {[b['value'] for b in state['bets']]}")
                print(f"   🧱 Стеки: {[s['value'] for s in state['stacks']]}")
            print("-" * 50)