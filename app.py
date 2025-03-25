# app.py
import json
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from ui import setup_ui
from data import load_data  
from calendar_logic import update_calendar
from shared import update_employee_list
from shared import cache_vacations
from constants import DATA_FILE

class VacationCalendarApp:
    """Приложение для управления календарем отпусков сотрудников."""
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
        # self.root.bind("<FocusIn>", self.on_window_focus)
        self.root.bind("<Unmap>", self.on_minimize)
        self.root.bind("<Map>", self.on_window_restore)  # Добавляем обработчик восстановления окна

        # Принудительная активация окна при запуске
        self.root.update()
        self.root.focus_force()
        if hasattr(self, 'search_entry'):
            self.search_entry.focus_set()

    def save_data(self):
        self.root.config(cursor="watch")
        self.root.update()
        try:
            data = {
                "employees": self.employees,
                "holidays": [d.strftime("%d.%m.%Y") for d in self.holidays],
                "workdays": [d.strftime("%d.%m.%Y") for d in self.workdays],
                "weekends": [d.strftime("%d.%m.%Y") for d in self.weekends]
            }
            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            self.data_modified = False
            messagebox.showinfo("Информация", "Данные успешно сохранены")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при сохранении данных: {str(e)}")
        finally:
        self.root.config(cursor="")            

    # def on_window_focus(self, event):
    #     print("Окно получило фокус")

    def on_window_restore(self, event):
        """Обработчик восстановления окна после минимизации"""
        # print("Окно восстановлено из свернутого состояния")
        self.root.deiconify()  # Убеждаемся, что окно видимо
        self.root.focus_force()  # Принудительно возвращаем фокус
        if hasattr(self, 'search_entry'):
            self.search_entry.focus_set()  # Возвращаем фокус на поле поиска

    def on_closing(self):
        if self.data_modified:
            if messagebox.askyesno("Сохранение данных", "Сохранить изменения перед выходом?"):
                self.save_data()
        self.root.destroy()

def on_minimize(self, event):
    if self.data_modified:
        if messagebox.askyesno("Сохранение данных", "Сохранить изменения перед минимизацией?"):
            self.save_data()

    def filter_employees(self, *args):
        for child in self.employee_list.get_children():
            self.employee_list.delete(child)
        search_text = self.search_var.get().lower() if hasattr(self, 'search_var') else ""
        for emp in self.employees:
            if search_text and search_text not in emp["fio"].lower() and search_text not in emp["position"].lower():
                continue
            emp_id = self.employee_list.insert("", "end", text=emp["fio"], values=(emp["position"], "", ""), open=False)
            vacations = emp.get("vacations", [])
            for vac in vacations:
                try:
                    s_date = vac["start_date"]
                    e_date = vac["end_date"]
                    self.employee_list.insert(emp_id, "end", text="", values=("", s_date, e_date))
                except Exception:
                    continue