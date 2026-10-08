import cv2
import numpy as np
from typing import Optional, Tuple, List


class CardClassifier:
    """
    Класс для распознавания номинала и масти карты по её изображению.

    Обозначения мастей:
    s = Spades (Пики), h = Hearts (Черви), d = Diamonds (Бубны), c = Clubs (Трефы)
    """

    RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
    SUITS = ['s', 'h', 'd', 'c']

    def __init__(self, templates_dir: Optional[str] = None):
        self.templates_dir = templates_dir
        self.templates = {}
        # В будущем здесь будут загружаться эталонные шаблоны символов карт

    def preprocess_card(self, card_img: np.ndarray) -> np.ndarray:
        """
        Приводит вырезанную карту к стандартному размеру и бинаризует (делает ч/б).
        """
        if card_img is None or card_img.size == 0:
            return np.array([])

        # 1. Приводим к единому размеру
        resized = cv2.resize(card_img, (120, 160))

        # 2. Переводим в оттенки серого
        gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)

        # 3. Применяем порог (бинаризация) для выделения четких контуров значков
        _, thresh = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY_INV)

        return thresh

    def extract_corner(self, card_img: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Вырезает верхний левый угол карты и разделяет его на ROI номинала и масти.
        """
        h, w = card_img.shape[:2]

        # Берем верхнюю левую область (45% высоты и 35% ширины)
        corner = card_img[0:int(h * 0.45), 0:int(w * 0.35)]

        ch, cw = corner.shape[:2]
        # Верхняя часть угла — номинал, нижняя — масть
        rank_roi = corner[0:int(ch * 0.55), :]
        suit_roi = corner[int(ch * 0.45):, :]

        return rank_roi, suit_roi

    def predict(self, card_img: np.ndarray) -> Optional[str]:
        """
        Принимает изображение одной карты и возвращает строку (например, 'Ah', 'Kd').
        """
        if card_img is None or card_img.size == 0:
            return None

        processed = self.preprocess_card(card_img)
        if processed.size == 0:
            return None

        rank_roi, suit_roi = self.extract_corner(processed)

        # Логика сравнения с шаблонами будет подключена после создания базы шаблонов.
        # Пока метод возвращает None, готовый к интеграции.
        return None