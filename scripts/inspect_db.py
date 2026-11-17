from pathlib import Path
import sqlite3

# Путь к корню проекта (если файл лежит в scripts/, поднимаемся на уровень выше)
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Проверяем возможные пути к базе данных (в папке data/ или в корне)
POSSIBLE_PATHS = [
    PROJECT_ROOT / "data" / "gto_strategy.db",
    PROJECT_ROOT / "gto_strategy.db",
]


def inspect_database():
  db_path = None
  for path in POSSIBLE_PATHS:
    if path.exists():
      db_path = path
      break

  if not db_path:
    print(" Ошибка: Файл gto_strategy.db не найден ни в data/, ни в корне проекта!")
    return

  print(f"Подключаемся к базе данных: {db_path.resolve()}\n")

  conn = sqlite3.connect(db_path)
  cursor = conn.cursor()

  # Получаем список всех таблиц в базе
  cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
  tables = cursor.fetchall()

  if not tables:
    print("В базе данных не найдено ни одной таблицы.")
    conn.close()
    return
  
  for (table_name,) in tables:
      # Получаем количество строк в таблице
      cursor.execute(f"SELECT COUNT(*) FROM '{table_name}'")
      row_count = cursor.fetchone()[0]

      print(f"📦 Таблица: {table_name} (всего строк: {row_count})")
      print("-" * 45)

      # Получаем информацию о колонках таблицы
      cursor.execute(f"PRAGMA table_info('{table_name}')")
      columns = cursor.fetchall()
      # ... остальной код вывода колонок и примеров строк ...
  for (table_name,) in tables:
    print(f"📦 Таблица: {table_name}")
    print("-" * 45)

    # Получаем информацию о колонках таблицы
    cursor.execute(f"PRAGMA table_info('{table_name}')")
    columns = cursor.fetchall()

    for col in columns:
      col_id, col_name, col_type, notnull, default_val, pk = col
      pk_label = " [PRIMARY KEY]" if pk else ""
      notnull_label = " NOT NULL" if notnull else ""
      print(
          f"  • {col_name} : {col_type}{notnull_label}{pk_label}"
      )

    # Выведем пример первой строки из таблицы, чтобы понять формат данных
    try:
      cursor.execute(f"SELECT * FROM '{table_name}' LIMIT 1;")
      sample_row = cursor.fetchone()
      if sample_row:
        print(f"\n  📝 Пример строки: {sample_row}")
    except Exception as e:
      print(f"  (Не удалось прочитать пример строки: {e})")

    print("\n" + "=" * 45 + "\n")

  conn.close()


if __name__ == "__main__":
  inspect_database()