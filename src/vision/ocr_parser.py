import cv2
import re
import numpy as np
from typing import Optional
import easyocr


class OCRParser:
    """
    Класс для считывания числовых значений (размеры банков, ставок и стеков)
    с вырезанных фрагментов экрана.
    """

    def __init__(self, languages: list = ['en']):
        # Инициализация EasyOCR для распознавания цифр и символов
        self.reader = easyocr.Reader(languages, gpu=False)

    def preprocess_for_ocr(self, img: np.ndarray) -> np.ndarray:
        """
        Увеличивает фрагмент и повышает контрастность для улучшения качества распознавания.
        """
        if img is None or img.size == 0:
            return np.array([])

        # Увеличиваем масштаб в 2 раза для четкости мелких шрифтов
        resized = cv2.resize(img, (0, 0), fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC)
        gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)

        # Автоматический порог бинаризации Оцу
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return thresh

    def extract_number(self, img: np.ndarray) -> Optional[float]:
        """
        Принимает вырезанный фрагмент с текстом и возвращает распознанное число.
        """
        if img is None or img.size == 0:
            return None

        # Ограничиваем список символов только цифрами и точкой
        results = self.reader.readtext(img, allowlist='0123456789.,')
        if not results:
            return None

        # Объединяем найденные фрагменты и заменяем запятую на точку
        text = "".join([res[1] for res in results]).replace(',', '.')

        # Выделяем числовой паттерн с помощью регулярного выражения
        match = re.search(r'\d+(\.\d+)?', text)
        if match:
            return float(match.group(0))

        return None