import cv2
import re
import easyocr


class PotOCRReader:
    def __init__(self):
        self.reader = easyocr.Reader(['en'], gpu=False)

    def preprocess_image(self, crop_img):
        gray = cv2.cvtColor(crop_img, cv2.COLOR_BGR2GRAY)
        resized = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
        return resized

    def extract_pot_value(self, crop_img):
        if crop_img is None or crop_img.size == 0:
            return 0.0

        processed = self.preprocess_image(crop_img)
        results = self.reader.readtext(processed, detail=0)
        raw_text = " ".join(results)

        cleaned_text = raw_text.replace(',', '.')
        match = re.search(r'\d+(?:\.\d+)?', cleaned_text)

        if match:
            try:
                return float(match.group())
            except ValueError:
                return 0.0
        return 0.0