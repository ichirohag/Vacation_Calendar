# calendar_logic.py
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from calendar import monthcalendar
from datetime import datetime, timedelta
from utils import attach_tooltip
from shared import update_employee_list
from shared import cache_vacations

def is_weekend(app, date):
    return date.weekday() >= 5 or date in app.weekends

def is_holiday(app, date):
    return date in app.holidays

def is_workday(app, date):
    if date in app.holidays:
        return False
    if is_weekend(app, date):
        return date in app.workdays
    return True

def get_next_available_day(app, date):
    next_day = date + timedelta(days=1)
    while True:
        if is_workday(app, next_day) or is_weekend(app, next_day):
            return next_day
        next_day += timedelta(days=1)

def recalc_employee_vacations(app):
    for emp in app.employees:
        all_vac_days = []
        if "vacations" in emp and isinstance(emp["vacations"], list):
            for vac_period in emp["vacations"]:
                try:
                    s_date = datetime.strptime(vac_period["start_date"], "%d.%m.%Y")
                    e_date = datetime.strptime(vac_period["end_date"], "%d.%m.%Y")
                    days = (e_date - s_date).days + 1
                    period_vac_days = [s_date + timedelta(days=i) for i in range(days)]
                    count_holidays = sum(1 for d in period_vac_days if is_holiday(app, d))
                    period_vac_days = [d for d in period_vac_days if not is_holiday(app, d)]
                    if count_holidays > 0:
                        last_day = period_vac_days[-1] if period_vac_days else e_date
                        for _ in range(count_holidays):
                            nw = get_next_available_day(app, last_day)
                            period_vac_days.append(nw)
                            last_day = nw
                    all_vac_days.extend(period_vac_days)
                except Exception as e:
                    messagebox.showwarning("Предупреждение", f"Ошибка обработки отпуска для {emp['fio']}: {str(e)}")
                    continue
        emp["vacation"] = [d.strftime("%d.%m.%Y") for d in sorted(all_vac_days)]
    cache_vacations(app)

def make_holiday(app, date):
    app.holidays.add(date)
    app.workdays.discard(date)
    app.weekends.discard(date)
    app.data_modified = True
    recalc_employee_vacations(app)
    update_calendar(app)

def make_workday(app, date):
    app.holidays.discard(date)
    app.weekends.discard(date)
    app.workdays.add(date)
    app.data_modified = True
    recalc_employee_vacations(app)
    update_calendar(app)

def make_weekend(app, date):
    app.holidays.discard(date)
    app.workdays.discard(date)
    app.weekends.add(date)
    app.data_modified = True
    recalc_employee_vacations(app)
    update_calendar(app)

def update_calendar(app):
    print("Обновление календаря началось...")
    app.root.config(cursor="watch")
    app.root.update_idletasks()

    if not app.month_frames:
        for w in app.calendar_frame.winfo_children():
            w.destroy()

        months = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
                  "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"]
        weekdays = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]

        for i in range(3):
            app.calendar_frame.grid_rowconfigure(i, weight=1)
        for i in range(4):
            app.calendar_frame.grid_columnconfigure(i, weight=1)

        for i, month in enumerate(months):
            row = i // 4
            col = i % 4
            m_frame = ttk.Frame(app.calendar_frame, borderwidth=1, relief="solid")
            m_frame.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
            m_frame.grid_propagate(False)
            for c in range(7):
                m_frame.grid_columnconfigure(c, weight=1)
            ttk.Label(m_frame, text=month, font=("Arial", 12)).grid(row=0, column=0, columnspan=7, sticky="nsew")
            for c, d in enumerate(weekdays):
                ttk.Label(m_frame, text=d).grid(row=1, column=c, sticky="nsew")
            app.month_frames.append(m_frame)

    for i, m_frame in enumerate(app.month_frames):
        month_num = i + 1
        calendar_days = monthcalendar(app.current_year, month_num)
        for r in range(2, m_frame.grid_size()[1]):
            for w in m_frame.grid_slaves(row=r):
                w.destroy()
        for w_idx, week in enumerate(calendar_days):
            for d_idx, day in enumerate(week):
                r = w_idx + 2
                if day != 0:
                    date = datetime(app.current_year, month_num, day)
                    date_key = date.strftime("%Y-%m-%d")
                    vacation_employees = app.vacation_cache.get(date_key, [])
                    has_vacation = len(vacation_employees) > 0
                    vacation_overlap = len(vacation_employees) > 1
                    bg_color = "#FFCC99" if vacation_overlap else "#CCFFCC" if has_vacation else "#FFFFFF"
                    day_frame = tk.Frame(m_frame, bg=bg_color, borderwidth=1, relief="flat", padx=2, pady=2)
                    day_frame.grid(row=r, column=d_idx, sticky="nsew", padx=1, pady=1)
                    lbl = tk.Label(day_frame, text=str(day), width=4, anchor="center", bg=bg_color)
                    lbl.pack(fill="both", expand=True)
                    is_today = date.date() == app.today
                    if is_today:
                        lbl.config(foreground="#3366CC")
                        day_canvas = tk.Canvas(day_frame, bg=bg_color, highlightthickness=0)
                        day_canvas.place(relx=0.5, rely=0.5, anchor="center", width=20, height=20)
                        day_canvas.create_oval(2, 2, 18, 18, outline="#3366CC", width=2)
                        lbl.lift()
                    elif is_holiday(app, date):
                        lbl.config(foreground="red")
                    elif is_weekend(app, date):
                        lbl.config(foreground="gray")
                    else:
                        lbl.config(foreground="black")
                    if has_vacation:
                        tooltip_text = "Отпуск:\n" + "\n".join(f"{name} ({get_employee_position(app, name)})" for name in vacation_employees)
                        attach_tooltip(day_frame, tooltip_text)
                    d_menu = tk.Menu(app.root, tearoff=0)
                    d_menu.add_command(label="Сделать праздничным", command=lambda d=date: make_holiday(app, d))
                    d_menu.add_command(label="Сделать рабочим", command=lambda d=date: make_workday(app, d))
                    d_menu.add_command(label="Сделать выходным", command=lambda d=date: make_weekend(app, d))
                    day_frame.bind("<Button-3>", lambda e, m=d_menu: m.post(e.x_root, e.y_root))
                    lbl.bind("<Button-3>", lambda e, m=d_menu: m.post(e.x_root, e.y_root))

    app.root.config(cursor="")
    print("Обновление календаря завершено")

def apply_changes(app):
    try:
        new_year = int(app.year_spinbox.get())
        if 2000 <= new_year <= 2100:
            app.current_year = new_year
            recalc_employee_vacations(app)
            cache_vacations(app)
            update_employee_list(app)
            update_calendar(app)
        else:
            messagebox.showerror("Ошибка", "Год должен быть в диапазоне от 2000 до 2100")
    except ValueError:
        messagebox.showerror("Ошибка", "Введите корректный год")

def get_employee_position(app, fio):
    for emp in app.employees:
        if emp["fio"] == fio:
            return emp["position"]
    return ""

def add_holiday_dialog(app):
    dialog = tk.Toplevel(app.root)
    dialog.title("Добавить праздник")
    dialog.geometry("300x150")
    dialog.resizable(True, True)
    dialog.grid_columnconfigure(0, weight=1)
    dialog.grid_columnconfigure(1, weight=1)

    ttk.Label(dialog, text="Дата праздника (ДД.ММ.ГГГГ):").grid(row=0, column=0, padx=5, pady=5, sticky="e")
    date_entry = ttk.Entry(dialog)
    date_entry.grid(row=0, column=1, padx=5, pady=5, sticky="we")

    def save_holiday():
        try:
            date_str = date_entry.get().strip()
            holiday_date = datetime.strptime(date_str, "%d.%m.%Y")
            app.holidays.add(holiday_date)
            app.data_modified = True
            recalc_employee_vacations(app)
            update_calendar(app)
            dialog.destroy()
            messagebox.showinfo("Информация", f"Праздник {date_str} добавлен")
        except ValueError:
            messagebox.showerror("Ошибка", "Неверный формат даты! Используйте ДД.ММ.ГГГГ")

    ttk.Button(dialog, text="Сохранить", command=save_holiday).grid(row=1, column=0, columnspan=2, pady=10, sticky="we")

def add_workday_dialog(app):
    dialog = tk.Toplevel(app.root)
    dialog.title("Добавить рабочий выходной")
    dialog.geometry("300x150")
    dialog.resizable(True, True)
    dialog.grid_columnconfigure(0, weight=1)
    dialog.grid_columnconfigure(1, weight=1)

    ttk.Label(dialog, text="Дата рабочего дня (ДД.ММ.ГГГГ):").grid(row=0, column=0, padx=5, pady=5, sticky="e")
    date_entry = ttk.Entry(dialog)
    date_entry.grid(row=0, column=1, padx=5, pady=5, sticky="we")

    def save_workday():
        try:
            date_str = date_entry.get().strip()
            workday_date = datetime.strptime(date_str, "%d.%m.%Y")
            if workday_date.weekday() < 5 and workday_date not in app.weekends:
                messagebox.showwarning("Предупреждение", "Выбранный день не является выходным")
                return
            app.workdays.add(workday_date)
            app.data_modified = True
            recalc_employee_vacations(app)
            update_calendar(app)
            dialog.destroy()
            messagebox.showinfo("Информация", f"Рабочий выходной {date_str} добавлен")
        except ValueError:
            messagebox.showerror("Ошибка", "Неверный формат даты! Используйте ДД.ММ.ГГГГ")

    ttk.Button(dialog, text="Сохранить", command=save_workday).grid(row=1, column=0, columnspan=2, pady=10, sticky="we")

def export_to_csv(app):
    try:
        file_path = filedialog.asksaveasfilename(
            defaultextension=".html",
            filetypes=[("HTML файлы", "*.html"), ("Все файлы", "*.*")],
            title="Сохранить календарь как HTML"
        )
        if not file_path:
            return

        css = """
        <style>
            table, th, td {
                border: 1px solid black;
                border-collapse: collapse;
                padding: 5px;
                text-align: center;
            }
            th {
                background-color: #f2f2f2;
            }
            .month-table {
                display: inline-block;
                vertical-align: top;
                margin: 10px;
            }
            .vacation {
                background-color: #90EE90;
            }
            .vacation-overlap {
                background-color: #FFA500;
            }
            .holiday {
                color: #FF0000;
            }
            .weekend {
                color: #808080;
            }
            .today {
                color: #0000FF;
                font-weight: bold;
            }
        </style>
        """

        with open(file_path, 'w', encoding='utf-8') as html_file:
            html_file.write('<!DOCTYPE html>\n<html>\n<head>\n<meta charset="utf-8">\n')
            html_file.write(f'<title>Календарь отпусков на {app.current_year} год</title>\n')
            html_file.write(css)
            html_file.write('</head>\n<body>\n')

            html_file.write(f'<h2>Список сотрудников с отпусками на {app.current_year} год</h2>\n')
            html_file.write('<table style="width:100%">\n')
            html_file.write('<tr><th>ФИО</th><th>Должность</th><th>Период отпуска</th></tr>\n')

            vacation_dict = {}
            for emp in sorted(app.employees, key=lambda x: x["fio"]):
                for day_str in emp.get("vacation", []):
                    day_date = datetime.strptime(day_str, "%d.%m.%Y")
                    if day_date.year == app.current_year:
                        date_key = day_date.strftime("%Y-%m-%d")
                        if date_key not in vacation_dict:
                            vacation_dict[date_key] = []
                        vacation_dict[date_key].append(emp["fio"])
                this_year_vacations = emp.get("vacations", []) if "vacations" in emp else []
                if not this_year_vacations and "start_date" in emp:
                    this_year_vacations = [{"start_date": emp["start_date"], "end_date": emp["end_date"]}]
                if this_year_vacations:
                    vacation_periods = [f"{vac['start_date']} - {vac['end_date']}" for vac in this_year_vacations
                                      if datetime.strptime(vac["start_date"], "%d.%m.%Y").year == app.current_year or
                                      datetime.strptime(vac["end_date"], "%d.%m.%Y").year == app.current_year]
                    if vacation_periods:
                        html_file.write(f'<tr><td>{emp["fio"]}</td><td>{emp["position"]}</td><td>{vacation_periods[0]}</td></tr>\n')
                        for period in vacation_periods[1:]:
                            html_file.write(f'<tr><td></td><td></td><td>{period}</td></tr>\n')

            html_file.write('</table>\n<br><br>\n')

            html_file.write(f'<h2>Календарь отпусков на {app.current_year} год</h2>\n')
            months = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
                      "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"]
            weekdays = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]

            for row in range(4):
                html_file.write('<div style="display: flex; justify-content: space-around;">\n')
                for col in range(3):
                    month_idx = row * 3 + col
                    if month_idx >= len(months):
                        break
                    month_name = months[month_idx]
                    html_file.write('<table class="month-table">\n')
                    html_file.write(f'<tr><th colspan="7">{month_name}</th></tr>\n')
                    html_file.write('<tr>' + ''.join(f'<th>{wd}</th>' for wd in weekdays) + '</tr>\n')

                    cal = monthcalendar(app.current_year, month_idx + 1)
                    today = datetime.now().date()

                    for week in cal:
                        html_file.write('<tr>\n')
                        for day in week:
                            if day == 0:
                                html_file.write('<td></td>\n')
                            else:
                                date = datetime(app.current_year, month_idx + 1, day).date()
                                date_key = date.strftime("%Y-%m-%d")
                                vacation_employees = vacation_dict.get(date_key, [])
                                cell_class = "vacation-overlap" if len(vacation_employees) > 1 else "vacation" if vacation_employees else ""
                                if is_holiday(app, date):
                                    cell_class += " holiday" if cell_class else "holiday"
                                elif is_weekend(app, date):
                                    cell_class += " weekend" if cell_class else "weekend"
                                if date == today:
                                    cell_class += " today" if cell_class else "today"
                                tooltip = f' title="Отпуск: {", ".join(vacation_employees)}"' if vacation_employees else ""
                                html_file.write(f'<td class="{cell_class}"{tooltip}>{day}</td>\n')
                        html_file.write('</tr>\n')
                    html_file.write('</table>\n')
                html_file.write('</div>\n')

            html_file.write('</body>\n</html>')

        messagebox.showinfo("Готово", f"Экспорт в HTML завершен. Файл сохранен: {file_path}")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Ошибка при экспорте в HTML: {str(e)}")

def show_about(app):
    from .constants import VERSION
    about_dialog = tk.Toplevel(app.root)
    about_dialog.title("О программе")
    about_dialog.geometry("400x300")
    about_dialog.resizable(True, True)

    ttk.Label(about_dialog, text="Календарь отпусков", font=("Arial", 14, "bold")).pack(pady=10)
    ttk.Label(about_dialog, text=f"Версия: {VERSION}").pack(pady=5)
    ttk.Label(about_dialog, text="Описание:").pack(anchor="w", padx=20, pady=5)
    ttk.Label(about_dialog, text="Программа для учета и отображения отпусков сотрудников.", wraplength=350).pack(padx=20)
    ttk.Label(about_dialog, text="Возможности:").pack(anchor="w", padx=20, pady=5)

    features = [
        "• Добавление и редактирование сотрудников",
        "• Поиск сотрудников по имени и должности",
        "• Визуализация отпусков в календаре",
        "• Учет праздничных и рабочих дней",
        "• Экспорт календаря в HTML с визуальным форматированием",
        "• Отображение текущей даты в календаре"
    ]

    for feature in features:
        ttk.Label(about_dialog, text=feature).pack(anchor="w", padx=40)

    ttk.Button(about_dialog, text="Закрыть", command=about_dialog.destroy).pack(pady=20)