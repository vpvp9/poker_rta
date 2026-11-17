from pathlib import Path
import sqlite3
from src.gto.normalizer import normalize_hand

# Определяем корень проекта и путь к базе данных
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DB_PATH = PROJECT_ROOT / "data" / "gto_strategy.db"


class GTOAnalyzer:

  def __init__(self, db_path=DB_PATH):
    self.db_path = db_path

  def get_strategy(self, street: str, card1: str, card2: str):
    """Делает запрос к базе данных gto_strategy.db

    и возвращает оптимальное действие, EV и пояснение для руки.
    """
    if not self.db_path.exists():
      print(f" Ошибка: База данных не найдена по пути: {self.db_path}")
      return None

    # Получаем нормализованную нотацию руки (например, 'AKo', 'AdAs' и т.д.)
    normalized_hand = normalize_hand(card1, card2)

    # Также сформируем прямую пару из карт на случай точного совпадения в базе
    exact_hand_1 = f"{card1}{card2}"
    exact_hand_2 = f"{card2}{card1}"

    conn = sqlite3.connect(self.db_path)
    cursor = conn.cursor()

    # Ищем запись по улице и одному из вариантов написания руки в БД
    query = """
            SELECT action, ev, explanation 
            FROM gto_strategies 
            WHERE street = ? AND (hero_hand = ? OR hero_hand = ? OR hero_hand = ?)
        """

    cursor.execute(
        query,
        (street.upper(), normalized_hand, exact_hand_1, exact_hand_2),
    )
    row = cursor.fetchone()

    conn.close()

    if row:
      return {"action": row[0], "ev": row[1], "explanation": row[2]}

    return None


if __name__ == "__main__":
  # Быстрый тест модуля
  analyzer = GTOAnalyzer()
  # Проверим тестовую руку 'AdAs', которая есть в базе
  result = analyzer.get_strategy(street="PREFLOP", card1="Ad", card2="As")
  if result:
    print(f" Найдено решение для AdAs:")
    print(f"  • Действие: {result['action']}")
    print(f"  • EV: {result['ev']}")
    print(f"  • Пояснение: {result['explanation']}")
  else:
    print("Решение не найдено.")