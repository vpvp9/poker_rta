import cv2
import numpy as np
import os
import time
from src.config import TEMPLATES_DIR, UNKNOWN_TEMPLATES_DIR, MATCH_THRESHOLD


class CardRecognizer:
    def __init__(self, templates_dir=TEMPLATES_DIR):
        self.templates_dir = templates_dir
        self.unknown_dir = UNKNOWN_TEMPLATES_DIR
        self.board_templates = {}
        self.hero_left_templates = {}
        self.hero_right_templates = {}

        if not os.path.exists(self.unknown_dir):
            os.makedirs(self.unknown_dir)

        self.load_templates()

    def load_templates(self):
        paths = {
            'board_cards': self.board_templates,
            'hero_left': self.hero_left_templates,
            'hero_right': self.hero_right_templates
        }

        for folder_name, template_dict in paths.items():
            folder_path = os.path.join(self.templates_dir, folder_name)
            if os.path.exists(folder_path):
                for filename in os.listdir(folder_path):
                    if filename.endswith(('.png', '.jpg')):
                        name = os.path.splitext(filename)[0]
                        img = cv2.imread(os.path.join(folder_path, filename))
                        if img is not None:
                            template_dict[name] = img

        print(
            f"Шаблоны загружены -> Борд: {len(self.board_templates)} | "
            f"Левая рука: {len(self.hero_left_templates)} | "
            f"Правая рука: {len(self.hero_right_templates)}"
        )

    def recognize_card(self, card_crop, position='board'):
        if card_crop is None or card_crop.size == 0:
            return "Unknown"

        if position == 'hero_left':
            templates = self.hero_left_templates
        elif position == 'hero_right':
            templates = self.hero_right_templates
        else:
            templates = self.board_templates

        if len(templates) == 0:
            self._save_unknown_card(card_crop, position)
            return "Unknown"

        best_match = "Unknown"
        best_score = -1.0

        for card_name, template in templates.items():
            # Ресайз кропа строго под габариты шаблона
            th, tw = template.shape[:2]
            resized_crop = cv2.resize(card_crop, (tw, th))

            res = cv2.matchTemplate(resized_crop, template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, _ = cv2.minMaxLoc(res)

            if max_val > best_score:
                best_score = max_val
                best_match = card_name

        if best_score < MATCH_THRESHOLD:
            self._save_unknown_card(card_crop, position)
            return "Unknown"

        return best_match

    def _save_unknown_card(self, card_crop, position):
        timestamp = int(time.time() * 1000)
        filename = f"unknown_{position}_{timestamp}.png"
        filepath = os.path.join(self.unknown_dir, filename)
        cv2.imwrite(filepath, card_crop)