import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from preflop_router import PreflopRouter
from src.logic.game_state_manager import GameStateManager
from src.vision.vision_parser import VisionParser


def detect_preflop_scenario(hero_pos: str, bets: list) -> tuple[str | None, str | None]:
    """
    Определяет префлоп-сценарий по списку ставок game_state.bets ([{'value': 2.5}, ...]).
    Возвращает (scenario, spot_filename).
    """
    # Вытаскиваем числовые значения ставок и фильтруем стандартные блайнды (0.5 и 1.0 ББ)
    bet_values = sorted([float(b["value"]) for b in bets if float(b.get("value", 0)) > 1.0])

    if len(bet_values) == 0:
        # Никто не рейзил (только блайнды 0.5 / 1.0)
        if hero_pos == "BB":
            return None, None  # На BB без опен-рейза RFI не существует
        return "RFI", None

    if len(bet_values) == 1:
        # Один игрок открылся (например, 2.5 ББ) -> играем против опен-рейза
        opener_size = bet_values[0]
        # Передаём подсказку по сайзингу/позиции героя, если точный оппонент ещё не привязан
        return "vs_Open", f"_{opener_size}bb_{hero_pos}"

    if len(bet_values) == 2:
        # Две ставки > 1 ББ (наш опен + 3-бет оппонента, либо опен + 3-бет перед нами)
        return "vs_3B", f"_{hero_pos}"

    return "vs_4B", f"_{hero_pos}"


def main():
    print("🚀 Запуск RTA Poker Pipeline...")

    parser = VisionParser()
    state_manager = GameStateManager()
    router = PreflopRouter()

    screenshots_dir = PROJECT_ROOT / "data" / "raw_screenshots"
    if not screenshots_dir.exists():
        print(f"❌ Ошибка: папка со скриншотами не найдена -> {screenshots_dir}")
        return

    test_images = sorted(
        list(screenshots_dir.glob("*.jpg")) + list(screenshots_dir.glob("*.png"))
    )
    if not test_images:
        print(f"⚠️ В папке {screenshots_dir} не найдено тестовых изображений!")
        return

    print(f"\n📂 Найдено скриншотов для анализа: {len(test_images)}\n" + "=" * 50)

    for img_path in test_images:
        print(f"\n🔍 Обработка файла: {img_path.name}")

        raw_vision_data = parser.parse_full_state(img_path)
        if not raw_vision_data:
            print(f"❌ Не удалось распознать кадр: {img_path.name}")
            continue

        game_state = state_manager.update_state(raw_vision_data)

        if game_state:
            print(game_state.summary())

            hero_pos = game_state.position
            hole_cards = game_state.hero_cards
            board_cards = game_state.board_cards
            is_preflop = not board_cards or len(board_cards) == 0

            if is_preflop and len(hole_cards) == 2:
                scenario, spot_hint = detect_preflop_scenario(hero_pos, game_state.bets)

                if scenario is None:
                    print("\nℹ️ [INFO] Позиция BB без рейзов до героя — чарт RFI не применяется.")
                else:
                    gto_result = router.get_strategy(
                        hole_cards=hole_cards,
                        hero_pos=hero_pos,
                        scenario=scenario,
                        spot_filename=spot_hint,
                    )
                    print("\n🎯 [GTO PREFLOP RECOMMENDATION]")
                    print(json.dumps(gto_result, ensure_ascii=False, indent=2))
            else:
                print("\n🌐 [GTO POSTFLOP] Обнаружен постфлоп, интеграция с .json.gz в процессе")
            print("=" * 50)

    print("\n✅ Обработка всех кадров завершена!")


if __name__ == "__main__":
    main()