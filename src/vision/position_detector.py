from pathlib import Path
import cv2
import numpy as np
from ultralytics import YOLO

# Определяем корень проекта (poker_rta)
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_YOLO2_PATH = PROJECT_ROOT / "models" / "yolo2.pt"


class PositionDetector:
    def __init__(self, model_path=DEFAULT_YOLO2_PATH):
        self.model = YOLO(str(model_path))
        self.class_names = self.model.names

    def detect_position(self, image_path):
        img = cv2.imread(str(image_path))
        if img is None:
            raise FileNotFoundError(f"Не удалось загрузить изображение: {image_path}")

        results = self.model(img, verbose=False)[0]

        seats = []
        hero_box = None
        dealer_box = None

        for box in results.boxes:
            cls_id = int(box.cls[0].item())
            cls_name = self.class_names[cls_id]
            xyxy = box.xyxy[0].cpu().numpy()

            center_x = (xyxy[0] + xyxy[2]) / 2
            center_y = (xyxy[1] + xyxy[3]) / 2

            if cls_name == "seat":
                seats.append({"box": xyxy, "center": (center_x, center_y)})
            elif cls_name == "hero":
                hero_box = {"box": xyxy, "center": (center_x, center_y)}
            elif cls_name == "dealer_button":
                dealer_box = {"box": xyxy, "center": (center_x, center_y)}

        if not seats:
            return "Unknown (No seats found)"

        if hero_box is None:
            return "Unknown (Hero cards not detected)"

        # 1. Центр стола как среднее центров всех кресел
        seat_centers = np.array([s["center"] for s in seats])
        table_center = np.mean(seat_centers, axis=0)

        # 2. Сортируем кресла по часовой стрелке вокруг центра
        def get_angle(seat):
            dx = seat["center"][0] - table_center[0]
            dy = seat["center"][1] - table_center[1]
            return np.arctan2(dy, dx)

        seats.sort(key=get_angle)

        # 3. Находим кресло Hero по близости его карт к слоту
        hero_seat_idx = min(
            range(len(seats)),
            key=lambda i: np.linalg.norm(np.array(seats[i]["center"]) - np.array(hero_box["center"]))
        )

        # 4. Находим кресло дилера
        dealer_seat_idx = 0
        if dealer_box is not None:
            dealer_seat_idx = min(
                range(len(seats)),
                key=lambda i: np.linalg.norm(np.array(seats[i]["center"]) - np.array(dealer_box["center"]))
            )

        # 5. Считаем шаги по часовой стрелке
        num_seats = len(seats)
        steps_from_dealer = (hero_seat_idx - dealer_seat_idx) % num_seats

        position = self._map_steps_to_position(steps_from_dealer, num_seats)

        print(f"\n🔍 [POSITION DEBUG ({num_seats}-max)]")
        print(f"   Слот Дилера: {dealer_seat_idx} | Слот Hero: {hero_seat_idx}")
        print(f"   Шагов от BTN до Hero: {steps_from_dealer} -> Позиция: {position}")

        return position

    def _map_steps_to_position(self, steps, num_seats):
        if num_seats == 6:
            mapping = {0: "BTN", 1: "SB", 2: "BB", 3: "UTG", 4: "MP", 5: "CO"}
        elif num_seats == 8:
            mapping = {0: "BTN", 1: "SB", 2: "BB", 3: "UTG1", 4: "UTG2", 5: "MP1", 6: "MP2", 7: "CO"}
        else:
            if steps == 0: return "BTN"
            if steps == 1: return "SB"
            if steps == 2: return "BB"
            return f"Seat+{steps}"

        return mapping.get(steps, "Unknown")