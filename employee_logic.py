import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import Calendar
from datetime import datetime, timedelta
from utils import center_window, validate_date, on_date_input, show_calendar
from shared import update_employee_list, cache_vacations
from calendar_logic import recalc_employee_vacations, update_calendar
from dialogs import add_vacation_dialog, validate_and_save_vacation


def apply_employee_filter(app, search_text):
    """Filters employees by text."""
    for emp in app.employees:
        try:
            if search_text and search_text not in emp["fio"].lower() and search_text not in emp["position"].lower():
                continue
            show_employee = False
            vacation_periods = []
            if "vacations" in emp and isinstance(emp["vacations"], list) and emp["vacations"]:
                for vac in emp["vacations"]:
                    try:
                        s_date = datetime.strptime(
                            vac["start_date"], "%d.%m.%Y")
                        e_date = datetime.strptime(vac["end_date"], "%d.%m.%Y")
                        if s_date.year <= app.current_year <= e_date.year:
                            show_employee = True
                            vacation_periods.append(
                                f"{vac['start_date']} - {vac['end_date']}")
                    except Exception:
                        continue
            elif "start_date" in emp and "end_date" in emp:
                s_date = datetime.strptime(emp["start_date"], "%d.%m.%Y")
                e_date = datetime.strptime(emp["end_date"], "%d.%m.%Y")
                if s_date.year <= app.current_year <= e_date.year:
                    show_employee = True
                    vacation_periods.append(
                        f"{emp['start_date']} - {emp['end_date']}")
            if any(datetime.strptime(day, "%d.%m.%Y").year == app.current_year for day in emp.get("vacation", [])):
                show_employee = True
            if show_employee:
                start_date = emp.get("start_date", "")
                end_date = emp.get("end_date", "")
                app.employee_list.insert("", "end", values=(
                    emp["fio"], emp["position"], start_date, end_date))
        except Exception as e:
            print(f"Ошибка при фильтрации сотрудников: {str(e)}")
            continue
