import cv2
import os
import random
from src.vision.vision_parser import PokerVisionParser


def collect_from_train():
    parser = PokerVisionParser()
    dataset_dir = 'dataset/train/images'  # <--- Берем основной массив train
    output_dir = 'data/templates_raw'

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    if not os.path.exists(dataset_dir):
        print(f"Ошибка: папка не найдена -> {dataset_dir}")
        return

    files = [f for f in os.listdir(dataset_dir) if f.endswith('.jpg')]
    print(f"Найдено картинок в TRAIN датасете: {len(files)}")

    # Перемешиваем, чтобы взятьрандомные раздачи, а не первые попавшиеся
    random.shuffle(files)

    saved_count = 0
    # Ограничим пока первыми 200 кадрами из train, чтобы не забить диск тысячами файлов
    max_frames = 200

    for idx, filename in enumerate(files[:max_frames]):
        img_path = os.path.join(dataset_dir, filename)
        parsed = parser.parse_frame(img_path)

        # Сохраняем карты борда
        for i, card in enumerate(parsed['board_cards']):
            if card is not None and card.size > 0:
                cv2.imwrite(f"{output_dir}/board_{idx}_{i}.png", card)
                saved_count += 1

        # Сохраняем карманные карты
        for i, card in enumerate(parsed['hero_cards']):
            if card is not None and card.size > 0:
                card_type = "hero_left" if i == 0 else "hero_right"
                cv2.imwrite(f"{output_dir}/{card_type}_{idx}_{i}.png", card)
                saved_count += 1

        if idx % 20 == 0 and idx > 0:
            print(f"Обработано кадров: {idx}/{max_frames}...")

    print(f"Готово! Сохранено новых кропов в '{output_dir}': {saved_count}")


if __name__ == '__main__':
    collect_from_train()