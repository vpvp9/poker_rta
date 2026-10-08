from typing import Optional
from src.logic.schemas import PokerState, Street


class GameStateTracker:
    """
    Класс для отслеживания динамики игры между кадрами.
    Определяет, изменилась ли ситуация на столе и нужен ли вызов GTO-солвера.
    """

    def __init__(self):
        self.current_state: Optional[PokerState] = None
        self.previous_state: Optional[PokerState] = None

    def update(self, new_state: PokerState) -> bool:
        """
        Обновляет состояние игры.
        Возвращает True, если ситуация изменилась и требуется реакция ассистента.
        Возвращает False, если кадр идентичен предыдущему.
        """
        # 1. Первый кадр раздачи
        if self.current_state is None:
            self.current_state = new_state
            print(f"[Tracker] Начало отслеживания раздачи. Улица: {new_state.street.value}")
            return True

        # 2. Проверка ключевых изменений
        street_changed = self.current_state.street != new_state.street
        cards_changed = (self.current_state.hero_cards != new_state.hero_cards or
                         self.current_state.board != new_state.board)

        # Сравниваем банк и стек с небольшой погрешностью (чтобы не реагировать на мигание OCR)
        pot_changed = abs(self.current_state.total_pot_bb - new_state.total_pot_bb) > 0.2
        stack_changed = abs(self.current_state.effective_stack_bb - new_state.effective_stack_bb) > 0.5

        has_state_changed = street_changed or cards_changed or pot_changed or stack_changed

        if has_state_changed:
            self.previous_state = self.current_state
            self.current_state = new_state
            print(f"[Tracker] ⚡ Изменение состояния! [{new_state.street.value.upper()}] "
                  f"Банк: {new_state.total_pot_bb} BB | Борд: {new_state.board}")
            return True

        # Состояние не изменилось — пропускаем вычисления
        return False

    def reset(self):
        """Сбрасывает историю при закрытии стола или смене участников."""
        self.current_state = None
        self.previous_state = None
        print("[Tracker] Состояние игры сброшено.")