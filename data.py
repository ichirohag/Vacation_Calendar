import sqlite3
import os
import sys
from datetime import datetime
from tkinter import messagebox

if getattr(sys, 'frozen', False):
    # Если программа скомпилирована, используем путь к .exe
    BASE_PATH = os.path.dirname(sys.executable)
else:
    # Если запускаем исходный код, используем путь к data.py
    BASE_PATH = os.path.dirname(os.path.abspath(__file__))

DB_FILE = os.path.join(BASE_PATH, "vacation_calendar.db")


def init_db():
    """Инициализирует базу данных, если она не существует."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fio TEXT NOT NULL UNIQUE,
        position TEXT NOT NULL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS vacations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id INTEGER,
        start_date TEXT NOT NULL,
        end_date TEXT NOT NULL,
        original_end_date TEXT,
        year INTEGER NOT NULL,
        FOREIGN KEY (employee_id) REFERENCES employees(id))''')
    c.execute('''CREATE TABLE IF NOT EXISTS special_days (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        type TEXT NOT NULL,
        year INTEGER NOT NULL,
        UNIQUE(date, type))''')
    conn.commit()
    conn.close()


def load_data(app):
    """Загружает данные из SQLite."""
    try:
        if not os.path.exists(DB_FILE):
            init_db()
            app.employees = []
            app.holidays = {}
            app.workdays = {}
            app.weekends = {}
            messagebox.showinfo("Информация", "Создана новая база данных.")
            return

        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()

        c.execute("SELECT id, fio, position FROM employees")
        app.employees = [{"id": row[0], "fio": row[1],
                          "position": row[2], "vacations": {}} for row in c.fetchall()]

        c.execute("SELECT employee_id, start_date, end_date, original_end_date, year FROM vacations")
        for emp_id, start_date, end_date, orig_end_date, year in c.fetchall():
            for emp in app.employees:
                if emp["id"] == emp_id:
                    if str(year) not in emp["vacations"]:
                        emp["vacations"][str(year)] = []
                    vac_data = {"start_date": start_date, "end_date": end_date}
                    if orig_end_date:  # Добавляем original_end_date, если оно есть
                        vac_data["original_end_date"] = orig_end_date
                    emp["vacations"][str(year)].append(vac_data)

        app.holidays = {}
        app.workdays = {}
        app.weekends = {}
        c.execute("SELECT date, type, year FROM special_days")
        for date_str, day_type, year in c.fetchall():
            date = datetime.strptime(date_str, "%d.%m.%Y")
            year_str = str(year)
            if day_type == "holiday":
                if year_str not in app.holidays:
                    app.holidays[year_str] = set()
                app.holidays[year_str].add(date)
            elif day_type == "workday":
                if year_str not in app.workdays:
                    app.workdays[year_str] = set()
                app.workdays[year_str].add(date)
            elif day_type == "weekend":
                if year_str not in app.weekends:
                    app.weekends[year_str] = set()
                app.weekends[year_str].add(date)

        conn.close()
        messagebox.showinfo("Информация", "Данные успешно загружены из базы.")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Ошибка при загрузке данных: {str(e)}")
        app.employees = []
        app.holidays = {}
        app.workdays = {}
        app.weekends = {}

def save_data(app):
    """Сохраняет только изменённые данные в SQLite."""
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()

        for emp in app.employees:
            if "id" not in emp:
                c.execute("INSERT INTO employees (fio, position) VALUES (?, ?)",
                          (emp["fio"], emp["position"]))
                emp["id"] = c.lastrowid
            else:
                c.execute(
                    "SELECT fio, position FROM employees WHERE id = ?", (emp["id"],))
                row = c.fetchone()
                if row and (row[0] != emp["fio"] or row[1] != emp["position"]):
                    c.execute("UPDATE employees SET fio = ?, position = ? WHERE id = ?",
                              (emp["fio"], emp["position"], emp["id"]))

            for year, vac_list in emp.get("vacations", {}).items():
                c.execute(
                    "DELETE FROM vacations WHERE employee_id = ? AND year = ?", (emp["id"], int(year)))
                for vac in vac_list:
                    c.execute("INSERT INTO vacations (employee_id, start_date, end_date, original_end_date, year) VALUES (?, ?, ?, ?, ?)",
                              (emp["id"], vac["start_date"], vac["end_date"], vac.get("original_end_date"), int(year)))

        c.execute("DELETE FROM special_days")
        for year, dates in app.holidays.items():
            for date in dates:
                c.execute("INSERT OR IGNORE INTO special_days (date, type, year) VALUES (?, ?, ?)",
                          (date.strftime("%d.%m.%Y"), "holiday", int(year)))
        for year, dates in app.workdays.items():
            for date in dates:
                c.execute("INSERT OR IGNORE INTO special_days (date, type, year) VALUES (?, ?, ?)",
                          (date.strftime("%d.%m.%Y"), "workday", int(year)))
        for year, dates in app.weekends.items():
            for date in dates:
                c.execute("INSERT OR IGNORE INTO special_days (date, type, year) VALUES (?, ?, ?)",
                          (date.strftime("%d.%m.%Y"), "weekend", int(year)))

        conn.commit()
        conn.close()
        app.data_modified = False
        messagebox.showinfo("Успех", "Данные успешно сохранены в базу данных.")
        print("Данные успешно сохранены.")
    except Exception as e:
        print(f"Ошибка сохранения: {str(e)}")
        messagebox.showerror("Ошибка", f"Ошибка при сохранении данных: {str(e)}")