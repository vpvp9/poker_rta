import time
from pathlib import Path
import cv2
import mss
import numpy as np
import pygetwindow as gw

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SAVE_DIR = PROJECT_ROOT / "data" / "raw_screenshots"


def list_active_windows():
    """Выводит список всех видимых окон на экране для удобного выбора."""
    print("=== Список активных окон на вашем компьютере ===")
    titles = [w.title for w in gw.getAllWindows() if w.title.strip()]
    for idx, t in enumerate(titles):
        print(f" [{idx}] {t}")
    print("=" * 48 + "\n")


def get_poker_window_rect(title_keyword: str):
    """
    Ищет окно с указанным ключевым словом,
    строго игнорируя окно PyCharm/poker_rta.
    """
    windows = gw.getWindowsWithTitle(title_keyword)
    for win in windows:
        title_lower = win.title.lower()
        # Пропускаем PyCharm и сам проект
        if "pycharm" in title_lower or "poker_rta" in title_lower:
            continue
        if win.title.strip():
            if win.isMinimized:
                win.restore()
            return {
                "top": win.top,
                "left": win.left,
                "width": win.width,
                "height": win.height
            }, win.title
    return None, None


def main():
    SAVE_DIR.mkdir(parents=True, exist_ok=True)

    # Покажем пользователю заголовок браузера/клиента
    list_active_windows()

    target_keyword = input("Введите ключевое слово из названия окна с покером (например, Maxline или Chrome): ").strip()
    if not target_keyword:
        target_keyword = "Maxline"

    counter = 0
    with mss.MSS() as sct:
        while True:
            monitor, found_title = get_poker_window_rect(target_keyword)

            if not monitor:
                print(f"⚠️ Окно с ключевым словом '{target_keyword}' не найдено!")
                print("Убедитесь, что браузер/клиент открыт и не перекрыт PyCharm.")
                retry = input("Нажмите Enter для повторного поиска (или 'q' для выхода): ")
                if retry.strip().lower() == 'q':
                    break
                continue

            cmd = input(f"[{counter}] Захват окна '{found_title}' | Enter — скриншот, 'q' — выход: ")
            if cmd.strip().lower() == 'q':
                print("Сбор завершен.")
                break

            screenshot = sct.grab(monitor)
            frame_bgr = cv2.cvtColor(np.array(screenshot), cv2.COLOR_BGRA2BGR)

            filepath = SAVE_DIR / f"table_{int(time.time())}_{counter}.jpg"
            cv2.imwrite(str(filepath), frame_bgr)
            print(f"  -> Сохранено: {filepath.name}\n")
            counter += 1


if __name__ == "__main__":
    main()