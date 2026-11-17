import sys
from pathlib import Path

# Добавляем корень проекта в системный путь
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.vision.vision_parser import VisionParser
from src.logic.game_state_manager import GameStateManager


def main():
    print("🚀 Запуск RTA Poker Pipeline...")

    # 1. Инициализируем компоненты
    parser = VisionParser()
    state_manager = GameStateManager()

    # 2. Указываем путь к папке со скриншотами
    screenshots_dir = PROJECT_ROOT / "data" / "raw_screenshots"
    if not screenshots_dir.exists():
        print(f"❌ Ошибка: папка со скриншотами не найдена -> {screenshots_dir}")
        return

    # Ищем все изображения (.jpg, .png)
    test_images = sorted(list(screenshots_dir.glob("*.jpg")) + list(screenshots_dir.glob("*.png")))

    if not test_images:
        print(f"⚠️ В папке {screenshots_dir} не найдено тестовых изображений!")
        return

    print(f"\n📂 Найдено скриншотов для анализа: {len(test_images)}\n" + "=" * 50)

    # 3. Прогоняем каждый скриншот через пайплайн
    for img_path in test_images:
        print(f"\n📸 Обработка файла: {img_path.name}")

        # Шаг А: Зрение считывает сырые данные (карты, позиция, пот, стеки, ставки)
        raw_vision_data = parser.parse_full_state(img_path)

        if not raw_vision_data:
            print(f"❌ Не удалось распарсить кадр: {img_path.name}")
            continue

        # Шаг Б: Менеджер состояния упаковывает это в структурированный объект
        game_state = state_manager.update_state(raw_vision_data)

        # Шаг В: Выводим красивый отчет по раздаче
        if game_state:
            print(game_state.summary())

    print("\n✅ Обработка всех кадров завершена!")


if __name__ == "__main__":
    main()