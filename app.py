import json
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from ui import setup_ui
from data import load_data, save_data
from calendar_logic import update_calendar, recalc_employee_vacations
from shared import update_employee_list, cache_vacations
from constants import DATA_FILE


class VacationCalendarApp:
    """Sets up app, UI, data, and events."""

    def __init__(self, root):
        self.root = root
        self.root.title("Календарь отпусков")
        self.root.geometry("1200x800")  
        self.root.minsize(800, 600)   

        self.holidays = {}
        self.workdays = {}
        self.weekends = {}
        self.current_year = datetime.now().year
        self.today = datetime.now().date()
        self.data_modified = False
        self.resize_timer = None
        self.last_width = self.root.winfo_width()
        self.last_height = self.root.winfo_height()
        self.vacation_cache = {}
        self.month_frames = []
        self.day_widgets = {}
        self.employees = []  

        setup_ui(self)
        load_data(self) 
        recalc_employee_vacations(self)
        update_employee_list(self)
        cache_vacations(self)
        update_calendar(self)

        if hasattr(self, 'search_entry'):
            self.root.after(500, lambda: [self.search_entry.focus_set(
            ), self.search_entry.select_range(0, tk.END)])

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.bind("<Map>", self.on_window_restore)

        self.root.update()
        self.root.focus_force()
        if hasattr(self, 'search_entry'):
            self.search_entry.focus_set()

    def update_after_change(self):
        """Updates data and UI after changes."""
        recalc_employee_vacations(self)
        cache_vacations(self)
        update_employee_list(self)
        update_calendar(self)

    def save_data(self):
        """Stores data in SQLite."""
        save_data(self) 

    def on_window_restore(self, event):
        """Restores window and focuses search."""
        self.root.deiconify()
        self.root.focus_force()
        if hasattr(self, 'search_entry'):
            self.search_entry.focus_set()

    def on_closing(self):
        """Prompts save, then closes window."""
        for date_key in list(self.day_widgets.keys()):
            day_frame, lbl = self.day_widgets.pop(date_key)
            day_frame.destroy()
            del day_frame, lbl
        self.day_widgets.clear()

        if self.data_modified:
            if messagebox.askyesno("Сохранение данных", "Сохранить изменения перед выходом?"):
                self.save_data()
        self.root.destroy()

    def filter_employees(self, *args):
        """Filters employees by search text."""
        for child in self.employee_list.get_children():
            self.employee_list.delete(child)
        search_text = self.search_var.get().lower() if hasattr(self, 'search_var') else ""
        for emp in self.employees:
            if search_text and search_text not in emp["fio"].lower() and search_text not in emp["position"].lower():
                continue
            emp_id = self.employee_list.insert(
                "", "end", text=emp["fio"], values=(emp["position"], "", ""), open=False)
            vacations = emp.get("vacations", [])
            for vac in vacations:
                try:
                    s_date = vac["start_date"]
                    e_date = vac["end_date"]
                    self.employee_list.insert(
                        emp_id, "end", text="", values=("", s_date, e_date))
                except Exception:
                    continue
