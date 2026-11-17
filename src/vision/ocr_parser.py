import cv2
import re
import numpy as np
from typing import Optional
import easyocr


class OCRParser:
    """
    Надежный OCR-парсер: читает текстовый блок целиком без ограничений allowlist,
    а затем очищает строку от мусора, букв (ББ, BB) и переводит в число.
    """

    def __init__(self, languages: list = ['en']):
        print("🚀 Инициализация OCRParser (GPU mode)...")
        self.reader = easyocr.Reader(languages, gpu=True)

    def preprocess_for_ocr(self, img: np.ndarray) -> np.ndarray:
        """
        Увеличиваем картинку и повышаем контрастность для стабильного распознавания мелких шрифтов.
        """
        if img is None or img.size == 0:
            return np.array([])

        resized = cv2.resize(img, dsize=(0, 0), fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC)
        gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return thresh

    def extract_number(self, img: np.ndarray) -> Optional[float]:
        """
        Читает весь текст из кропа, убирает слова ('Банк', 'ББ', 'BB'),
        заменяет запятые на точки и возвращает чистое число float.
        """
        if img is None or img.size == 0:
            return None

        processed_img = self.preprocess_for_ocr(img)
        if processed_img.size == 0:
            return None

        # Читаем текст БЕЗ allowlist — пусть OCR распознает символы как есть
        results = self.reader.readtext(processed_img, detail=0)
        if not results:
            return None

        # Объединяем все куски текста в одну строку (например: ["Банк:", "24", "ББ"] -> "Банк: 24 ББ")
        full_text = " ".join(results)

        # Очищаем строку:
        # 1. Приводим к верхнему регистру для удобства поиска
        # 2. Удаляем слова-паразиты и буквы блайндов ("БАНК", "ББ", "BB")
        cleaned = full_text.upper()
        cleaned = cleaned.replace("БАНК", "").replace("POT", "").replace("ББ", "").replace("BB", "")

        # Заменяем запятые на точки
        cleaned = cleaned.replace(",", ".")

        # Ищем первое полноценное число с плавающей точкой (или целое) в очищенной строке
        match = re.search(r'\d+(?:\.\d+)?', cleaned)
        if match:
            try:
                val = float(match.group(0))
                # Защита от гигантских ложных срабатываний (если захватило ID стола)
                if val > 100000:
                    return None
                return val
            except ValueError:
                return None

        return None