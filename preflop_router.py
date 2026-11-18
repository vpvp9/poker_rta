import json
from pathlib import Path
from typing import Dict, List, Optional

# Импортируем готовый нормализатор из проекта
try:
    from src.gto.normalizer import normalize_hand
except ImportError:
    # Запасной вариант, если запуск идет из папки src/gto
    from normalizer import normalize_hand


class PreflopRouter:

  def __init__(
      self, base_cash_dir: str = r"D:\py\DEEPFOLD-SOLVER\gto_output\cash"
  ):
    self.base_cash_dir = Path(base_cash_dir)
    self._cache: Dict[Path, dict] = {}

  def _load_json(self, file_path: Path) -> Optional[dict]:
    if file_path in self._cache:
      return self._cache[file_path]
    if not file_path.exists():
      return None
    with open(file_path, "r", encoding="utf-8") as f:
      data = json.load(f)
    self._cache[file_path] = data
    return data

  def _parse_upi_string(self, upi_str: str) -> Dict[str, float]:
    """Парсит строку вида 'AA:1.000,ATs:0.510,K8o:0.000' в словарь."""
    result = {}
    if not upi_str:
      return result
    for item in upi_str.split(","):
      item = item.strip()
      if not item:
        continue
      if ":" in item:
        hand, weight = item.split(":", 1)
        result[hand.strip()] = float(weight)
      else:
        result[item] = 1.0
    return result

  def resolve_chart_path(
      self,
      hero_pos: str,
      scenario: str,
      spot_filename: Optional[str] = None,
      profile: str = "6max_100bb_2_5x_500rake",
  ) -> Optional[Path]:
    """Подбирает путь к файлу префлоп-чарта в папке DEEPFOLD."""
    hero_pos = hero_pos.upper()
    scenario_dir = self.base_cash_dir / profile / scenario / hero_pos

    if not scenario_dir.exists():
      return None

    if scenario == "RFI":
      target = scenario_dir / f"{hero_pos}.json"
      return target if target.exists() else None

    if spot_filename:
      if not spot_filename.endswith(".json"):
        spot_filename += ".json"
      exact = scenario_dir / spot_filename
      if exact.exists():
        return exact

      # Фолбэк по префиксу позиции, если точного сайзинга нет
      candidates = list(scenario_dir.glob("*.json"))
      # Ищем файл, где упоминается позиция героя или сайзинг, иначе берём первый доступный в папке позиции
      for c in candidates:
        if f"_{hero_pos}" in c.name:
          return c
      if candidates:
        return candidates[0]

    return None

  def get_strategy(
      self,
      hole_cards: List[str],
      hero_pos: str,
      scenario: str = "RFI",
      spot_filename: Optional[str] = None,
      profile: str = "6max_100bb_2_5x_500rake",
  ) -> dict:
    """Главный метод: принимает карты от vision_parser и выдает частоты GTO."""
    if len(hole_cards) != 2:
      return {"status": "error", "message": "Ожидалось ровно 2 карманные карты"}

    # Используем готовый нормализатор проекта (например, ['Ks', '8h'] -> 'K8o')
    canonical_hand = normalize_hand(hole_cards[0], hole_cards[1])
    if canonical_hand == "??":
      return {"status": "error", "message": f"Неверный формат карт: {hole_cards}"}

    chart_path = self.resolve_chart_path(
        hero_pos, scenario, spot_filename, profile
    )

    if not chart_path:
      return {
          "status": "not_found",
          "hand": canonical_hand,
          "position": hero_pos,
          "scenario": scenario,
          "actions": {},
      }

    data = self._load_json(chart_path)
    upi_ranges = data.get("strategy", {}).get("upi_ranges", {})

    action_frequencies: Dict[str, float] = {}
    for action_name, range_str in upi_ranges.items():
      parsed_range = self._parse_upi_string(range_str)
      freq = parsed_range.get(canonical_hand, 0.0)
      if freq > 0.0:
        action_frequencies[action_name] = round(freq, 3)

    # Если сумма вероятностей не равна 1.0 и нет явного Fold, добавляем его
    total_prob = sum(action_frequencies.values())
    if total_prob < 0.999 and "Fold" not in action_frequencies:
      action_frequencies["Fold"] = round(1.0 - total_prob, 3)

    return {
        "status": "ok",
        "hand": canonical_hand,
        "position": hero_pos,
        "scenario": scenario,
        "source_file": chart_path.name,
        "actions": action_frequencies,
    }


if __name__ == "__main__":
  router = PreflopRouter()
  # Тестируем на картах из твоего vision_parser лога: ['Ks', '8h'] на позиции MP
  res = router.get_strategy(hole_cards=["Ks", "8h"], hero_pos="MP", scenario="RFI")
  print(json.dumps(res, ensure_ascii=False, indent=2))