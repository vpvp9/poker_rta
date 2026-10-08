import cv2
import numpy as np
from typing import Dict, List, Optional
from ultralytics import YOLO


class TableDetector:
    """
    Детектор элементов покерного стола на базе YOLOv8.
    Сканирует кадр и вырезает точные области карт, банка и элементов UI.
    """

    def __init__(self, weights_path: str = "data/weights/yolo_seg.pt"):
        self.weights_path = weights_path
        self.model = None

        # Пытаемся загрузить обученные веса YOLO
        try:
            self.model = YOLO(weights_path)
            print(f"[Detector] Модель YOLOv8 успешно загружена из {weights_path}")
        except Exception:
            print(f"[Detector Warning] Файл весов '{weights_path}' не найден. "
                  "Используется режим резервных координат (fallback).")

    def process_frame(self, frame_bgr: np.ndarray) -> Dict[str, List[np.ndarray]]:
        """
        Сканирует BGR-кадр и возвращает словарь с вырезанными изображениями (crops).
        """
        crops = {
            "hero_cards": [],
            "board_cards": [],
            "pot": None
        }

        # 1. Режим без нейросети (Fallback), если файл весов еще не создан/не обучен
        if self.model is None:
            h, w, _ = frame_bgr.shape
            crops["pot"] = frame_bgr[int(h * 0.40):int(h * 0.46), int(w * 0.45):int(w * 0.55)]
            return crops

        # 2. Полноценная детекция через YOLOv8
        results = self.model(frame_bgr, verbose=False)[0]

        for box in results.boxes:
            cls_id = int(box.cls[0])
            class_name = self.model.names[cls_id]
            x1, y1, x2, y2 = map(int, box.xyxy[0])

            # Вырезаем область найденного объекта из кадра
            crop = frame_bgr[y1:y2, x1:x2]

            if class_name == "hero_card":
                crops["hero_cards"].append(crop)
            elif class_name == "board_card":
                crops["board_cards"].append(crop)
            elif class_name == "pot":
                crops["pot"] = crop

        return crops