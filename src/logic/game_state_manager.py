class GameState:
    """Класс, описывающий единое состояние покерного стола в конкретный момент времени."""
    def __init__(self, hero_cards, board_cards, position, pot, bets, stacks):
        self.hero_cards = hero_cards          # Список карт героя (например, ['Ad', 'Qh'])
        self.board_cards = board_cards        # Карты борда (флоп, терн, ривер)
        self.position = position              # Позиция героя (BTN, SB, BB, UTG и т.д.)
        self.pot = pot                        # Размер банка
        self.bets = bets                      # Список ставок игроков со стола
        self.stacks = stacks                  # Список стеков игроков со стола

    def summary(self):
        """Красивый вывод текущего состояния для отладки или RTA-интерфейса."""
        return (
            f"\n{'='*40}\n"
            f" 🃏 СОСТОЯНИЕ СТОЛА (RTA GAME STATE)\n"
            f"{'='*40}\n"
            f" • Карты героя  : {self.hero_cards}\n"
            f" • Борд         : {self.board_cards if self.board_cards else 'Префлоп'}\n"
            f" • Позиция      : {self.position}\n"
            f" • Общий банк   : {self.pot} ББ\n"
            f" • Ставки на кон: {[b['value'] for b in self.bets]}\n"
            f" • Стеки за столом: {[s['value'] for s in self.stacks]}\n"
            f"{'='*40}"
        )


class GameStateManager:
    """
    Менеджер состояния: принимает сырые данные от VisionParser,
    валидирует их, связывает между собой и готовит объект для стратегического движка (солвера).
    """
    def __init__(self):
        print("🧠 Инициализация GameStateManager...")
        self.previous_state = None

    def update_state(self, vision_data: dict) -> GameState:
        """
        Принимает словарь, возвращаемый методом VisionParser.parse_full_state(),
        и преобразует его в структурированный GameState.
        """
        if not vision_data:
            return None

        # Извлекаем данные
        hero_cards = vision_data.get("hero_cards", [])
        board_cards = vision_data.get("board_cards", [])
        position = vision_data.get("position", "UNKNOWN")
        pot = vision_data.get("pot", 0.0)
        bets = vision_data.get("bets", [])
        stacks = vision_data.get("stacks", [])

        # Создаем объект текущего состояния
        current_state = GameState(
            hero_cards=hero_cards,
            board_cards=board_cards,
            position=position,
            pot=pot,
            bets=bets,
            stacks=stacks
        )

        # Здесь в будущем можно будет добавить логику истории действий (например, чекал оппонент или рейзил)
        self.previous_state = current_state
        return current_state