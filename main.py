import os
import random
from src.config import DATASET_TRAIN_DIR, DATASET_VALID_DIR
from src.vision.vision_parser import PokerVisionParser
from src.vision.pot_ocr import PotOCRReader
from src.vision.card_recognizer import CardRecognizer


class PokerRTAAssistant:
    def __init__(self):
        print("Инициализация RTA-ассистента Maxline...")
        self.parser = PokerVisionParser()
        self.pot_reader = PotOCRReader()
        self.recognizer = CardRecognizer()
        print("Все модули успешно загружены!\n")

    def analyze_table_image(self, image_path):
        if not os.path.exists(image_path):
            return

        parsed_data = self.parser.parse_frame(image_path)

        # Распознавание банка
        pot_val = 0.0
        if parsed_data['pot'] is not None:
            pot_val = self.pot_reader.extract_pot_value(parsed_data['pot'])

        # Распознавание карт борда
        board_cards = []
        for card_crop in parsed_data['board_cards']:
            card_name = self.recognizer.recognize_card(card_crop, position='board')
            board_cards.append(card_name)

        # Распознавание карманных карт
        hero_cards = []
        hero_crops = parsed_data['hero_cards']
        for i, card_crop in enumerate(hero_crops):
            pos = 'hero_left' if (len(hero_crops) == 2 and i == 0) or len(hero_crops) == 1 else 'hero_right'
            card_name = self.recognizer.recognize_card(card_crop, position=pos)
            hero_cards.append(card_name)

        print(f"Кадр: {os.path.basename(image_path)} | Банк: {pot_val} ББ | Рука: {hero_cards} | Борд: {board_cards}")


if __name__ == '__main__':
    assistant = PokerRTAAssistant()

    if os.path.exists(DATASET_TRAIN_DIR):
        files = [f for f in os.listdir(DATASET_TRAIN_DIR) if f.endswith('.jpg')]
        print(f"Найдено скриншотов в TRAIN: {len(files)}")
        random.shuffle(files)

        # Прогон по первым 100 кадрам
        for idx, filename in enumerate(files[:100]):
            sample_file = os.path.join(DATASET_TRAIN_DIR, filename)
            assistant.analyze_table_image(sample_file)