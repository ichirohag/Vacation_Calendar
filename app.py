# app.py
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from ui import setup_ui
from data import load_data, save_data
from calendar_logic import update_calendar
from shared import update_employee_list
from shared import cache_vacations

class VacationCalendarApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Календарь отпусков")
        self.root.geometry("1610x900")
        self.root.minsize(1610, 900)
        self.root.resizable(False, False)

        # Инициализация переменных
        self.employees = []
        self.holidays = set()
        self.workdays = set()
        self.weekends = set()
        self.current_year = datetime.now().year
        self.today = datetime.now().date()
        self.data_modified = False
        self.resize_timer = None
        self.last_width = self.root.winfo_width()
        self.last_height = self.root.winfo_height()
        self.vacation_cache = {}
        self.month_frames = []
        self.day_widgets = {}  # { "YYYY-MM-DD": (day_frame, lbl) }

        # Настройка интерфейса
        setup_ui(self)

        # Загрузка данных
        load_data(self)

        # Обновление интерфейса
        update_employee_list(self)
        cache_vacations(self)
        update_calendar(self)

        # Активируем поле поиска
        if hasattr(self, 'search_entry'):
            self.root.after(500, lambda: [self.search_entry.focus_set(), self.search_entry.select_range(0, tk.END)])

        # Привязка обработчиков
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.bind("<FocusIn>", self.on_window_focus)

        # Принудительная активация окна
        self.root.update()
        self.root.focus_force()
        if hasattr(self, 'search_entry'):
            self.search_entry.focus_set()

    def on_window_focus(self, event):
        if hasattr(self, 'search_entry'):
            self.search_entry.focus_set()

    def on_closing(self):
        if self.data_modified:
            if messagebox.askyesno("Сохранение данных", "Сохранить изменения перед выходом?"):
                save_data(self)
        self.root.destroy()