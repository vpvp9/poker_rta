import tkinter as tk
from typing import Optional
from src.gto.solver_interface import GTORecommendation


class RTAOverlayApp:
    """
    Минималистичный поверхностный оверлей (HUD) для отображения
    рекомендаций GTO-солвера поверх игрового стола.
    """

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Poker RTA Assistant")

        # Размеры и позиционирование окна
        self.root.geometry("320x180+50+50")
        self.root.attributes("-topmost", True)  # Поверх всех окон
        self.root.configure(bg="#1e1e2e")
        self.root.resizable(False, False)

        # Заголовок
        self.title_label = tk.Label(
            self.root,
            text="🤖 GTO ASSISTANT",
            font=("Consolas", 12, "bold"),
            fg="#cdd6f4",
            bg="#1e1e2e"
        )
        self.title_label.pack(pady=(10, 5))

        # Основное действие (Primary Action)
        self.action_label = tk.Label(
            self.root,
            text="WAITING FOR HAND...",
            font=("Consolas", 16, "bold"),
            fg="#a6adc8",
            bg="#1e1e2e"
        )
        self.action_label.pack(pady=5)

        # Ожидаемый EV
        self.ev_label = tk.Label(
            self.root,
            text="EV: --",
            font=("Consolas", 10),
            fg="#a6e3a1",
            bg="#1e1e2e"
        )
        self.ev_label.pack(pady=2)

        # Обоснование
        self.info_label = tk.Label(
            self.root,
            text="Ожидание действий...",
            font=("Segoe UI", 9, "italic"),
            fg="#bac2de",
            bg="#1e1e2e",
            wraplength=290
        )
        self.info_label.pack(pady=5)

    def update_recommendation(self, rec: GTORecommendation):
        """Обновляет текст и цвет элементов на основе полученной рекомендации."""
        self.action_label.config(text=rec.primary_action,
                                 fg="#a6e3a1" if "BET" in rec.primary_action or "RAISE" in rec.primary_action else "#f38ba8")
        self.ev_label.config(text=f"Expected Value: +{rec.ev_bb} BB")
        self.info_label.config(text=rec.explanation)
        self.root.update()

    def run(self):
        """Запуск главного цикла Tkinter."""
        self.root.mainloop()