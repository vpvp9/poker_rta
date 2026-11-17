RANK_VALUES = {
    "2": 2,
    "3": 3,
    "4": 4,
    "5": 5,
    "6": 6,
    "7": 7,
    "8": 8,
    "9": 9,
    "T": 10,
    "J": 11,
    "Q": 12,
    "K": 13,
    "A": 14,
}


def normalize_hand(card1: str, card2: str) -> str:
  """Превращает две карты (например, 'Ah', 'Kd')

  в стандартную покерную нотацию GTO (например, 'AKo', '77', 'AKs').
  """
  if not card1 or not card2 or len(card1) != 2 or len(card2) != 2:
    return "??"

  r1, s1 = card1[0], card1[1]
  r2, s2 = card2[0], card2[1]

  if r1 not in RANK_VALUES or r2 not in RANK_VALUES:
    return "??"

  val1 = RANK_VALUES[r1]
  val2 = RANK_VALUES[r2]

  # 1. Карманная пара (например, '7s', '7h' -> '77')
  if val1 == val2:
    return f"{r1}{r1}"

  # 2. Сортируем по старшинству (высший номинал всегда первый)
  if val1 < val2:
    r1, r2 = r2, r1
    val1, val2 = val2, val1
    s1, s2 = s2, s1

  # 3. Определяем масть: 's' (suited - одномастные), 'o' (offsuit - разномастные)
  suffix = "s" if s1 == s2 else "o"

  return f"{r1}{r2}{suffix}"


if __name__ == "__main__":
  # Быстрые тесты для проверки
  print(normalize_hand("Ah", "Kd"))  # Ожидается: AKo
  print(normalize_hand("Jc", "Tc"))  # Ожидается: JTs
  print(normalize_hand("7s", "7c"))  # Ожидается: 77
  print(normalize_hand("2c", "Ah"))  # Ожидается: A2o