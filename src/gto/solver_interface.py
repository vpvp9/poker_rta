from dataclasses import dataclass
from src.logic.schemas import PokerState
from src.gto.gto_db import GTODatabase


@dataclass
class GTORecommendation:
    primary_action: str
    ev_bb: float
    explanation: str


class GTOSolverInterface:
    """
    Интерфейс обращения к GTO-движку через локальную базу данных SQLite.
    """
    def __init__(self):
        self.db = GTODatabase()

    def get_recommendation(self, state: PokerState) -> GTORecommendation:
        # Ищем готовый вариант решения в SQLite
        db_result = self.db.find_strategy(
            street=state.street.value,
            hero_cards=state.hero_cards,
            board=state.board
        )

        if db_result:
            return GTORecommendation(
                primary_action=db_result["action"],
                ev_bb=db_result["ev"],
                explanation=db_result["explanation"]
            )

        # Резервный дефолтный ответ, если конкретная комбинация еще не внесена в БД
        return GTORecommendation(
            primary_action="CHECK / FOLD",
            ev_bb=0.00,
            explanation=f"Комбинация {state.hero_cards} для улицы {state.street.value} не найдена в базе GTO."
        )