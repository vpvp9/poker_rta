import sqlite3
import os
from typing import Optional, Dict


class GTODatabase:
    """
    Управляет локальной базой данных SQLite с предпросчитанными GTO-решениями.
    """

    def __init__(self, db_path: str = "data/gto_strategy.db"):
        self.db_path = db_path
        # Создаем директорию data/, если ее еще нет
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        """Создает структуру таблиц и наполняет базовыми решениями при первом запуске."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Таблица GTO-решений
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS gto_strategies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    street TEXT NOT NULL,
                    hero_hand TEXT NOT NULL,
                    board_texture TEXT DEFAULT '',
                    action TEXT NOT NULL,
                    ev REAL NOT NULL,
                    explanation TEXT NOT NULL,
                    UNIQUE(street, hero_hand, board_texture)
                )
            """)

            # Тестовое наполнение базы (Сид-данные)
            sample_data = [
                ('PREFLOP', 'AdAs', '', 'RAISE 3x', 4.85,
                 'Префлоп: Натсовый премиум-хэнд. Обязательный 3-бет / 4-бет на ценность.'),
                ('PREFLOP', 'KdKs', '', 'RAISE 3x', 4.12,
                 'Префлоп: Сильная премиум-пара. Открытие или рейз на ценность.'),
                ('FLOP', 'KdKs', '9s,4d,7d', 'BET 33%', 3.42,
                 'Флоп: Оверпара на сухой текстуре. Маленький контбет (c-bet) на ценность.'),
                ('FLOP', 'AhKh', 'Th,2d,5s', 'CHECK / CALL', 1.15,
                 'Флоп: Две оверкарты + бэкдор ФД. Чек/колл по шансам банка.'),
                ('TURN', 'KdKs', '9s,4d,7d,2c', 'BET 66%', 4.10,
                 'Терн: Бланк на терне. Увеличиваем сайзинг ставки для добора со средних пар.')
            ]

            cursor.executemany("""
                INSERT OR IGNORE INTO gto_strategies 
                (street, hero_hand, board_texture, action, ev, explanation)
                VALUES (?, ?, ?, ?, ?, ?)
            """, sample_data)

            conn.commit()

    def find_strategy(self, street: str, hero_cards: list, board: list) -> Optional[Dict]:
        """
        Ищет оптимальное решение в базе по текущему состоянию.
        """
        # Сортируем карты для корректного поиска (например, ["Ks", "Kd"] -> "KdKs")
        hero_str = "".join(sorted(hero_cards))
        board_str = ",".join(board) if board else ""

        with self._get_connection() as conn:
            cursor = conn.cursor()

            # 1. Попытка точного совпадения (Улица + Рука + Борд)
            cursor.execute("""
                SELECT action, ev, explanation FROM gto_strategies
                WHERE street = ? AND hero_hand = ? AND board_texture = ?
            """, (street.upper(), hero_str, board_str))

            row = cursor.fetchone()

            # 2. Если точной текстуры нет — ищем дефолтное решение для этой руки на улице
            if not row and street.upper() != "PREFLOP":
                cursor.execute("""
                    SELECT action, ev, explanation FROM gto_strategies
                    WHERE street = ? AND hero_hand = ?
                    LIMIT 1
                """, (street.upper(), hero_str))
                row = cursor.fetchone()

            if row:
                return {
                    "action": row[0],
                    "ev": row[1],
                    "explanation": row[2]
                }

        return None