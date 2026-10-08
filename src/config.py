import os

# Корень проекта (D:\py\poker_rta)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Пути к данным и шаблонам
DATASET_TRAIN_DIR = os.path.join(BASE_DIR, 'dataset', 'train', 'images')
DATASET_VALID_DIR = os.path.join(BASE_DIR, 'dataset', 'valid', 'images')

TEMPLATES_DIR = os.path.join(BASE_DIR, 'data', 'templates')
UNKNOWN_TEMPLATES_DIR = os.path.join(TEMPLATES_DIR, 'unknown')
RAW_TEMPLATES_DIR = os.path.join(BASE_DIR, 'data', 'templates_raw')

# Веса модели YOLO
# Стало (правильно):
YOLO_MODEL_PATH = os.path.join(BASE_DIR, "models", "yolo_seg.pt")

# Параметры детекции и сравнения
YOLO_CONF_THRESHOLD = 0.50
MATCH_THRESHOLD = 0.88

# Классы YOLO
CLASS_HERO_CARD = 'hero_card'
CLASS_BOARD_CARD = 'board_card'
CLASS_POT = 'pot'