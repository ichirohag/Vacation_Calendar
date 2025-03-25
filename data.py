# data.py
import json
import os
from datetime import datetime
from tkinter import messagebox
from constants import DATA_FILE
from shared import update_employee_list
from calendar_logic import recalc_employee_vacations

def load_data(app):
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                app.employees = data.get("employees", [])
                app.holidays = {datetime.strptime(date_str, "%d.%m.%Y") for date_str in data.get("holidays", [])}
                app.workdays = {datetime.strptime(date_str, "%d.%m.%Y") for date_str in data.get("workdays", [])}
                app.weekends = {datetime.strptime(date_str, "%d.%m.%Y") for date_str in data.get("weekends", [])}
                recalc_employee_vacations(app)
                messagebox.showinfo("Информация", "Данные успешно загружены")
    except FileNotFoundError:
        messagebox.showwarning("Предупреждение", "Файл данных не найден, начнем с пустого календаря")
    except json.JSONDecodeError:
        messagebox.showerror("Ошибка", "Ошибка формата данных в файле")
    except ValueError:
        messagebox.showerror("Ошибка", "Ошибка формата даты в данных")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Неизвестная ошибка при загрузке данных: {str(e)}")