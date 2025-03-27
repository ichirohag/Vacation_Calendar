
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from calendar import monthcalendar
from datetime import datetime, timedelta
from utils import attach_tooltip, center_window, validate_date, on_date_input, is_weekend, is_holiday, is_workday
from shared import update_employee_list, cache_vacations


def get_next_available_day(app, date):
    """Finds next valid day (not holiday)."""
    next_day = date + timedelta(days=1)
    while is_holiday(app, next_day):
        next_day += timedelta(days=1)
    return next_day


def recalc_employee_vacations(app):
    for emp in app.employees:
        all_vac_days = set()
        vacations = emp.get("vacations", {})
        for year, vac_list in vacations.items():
            for vac_period in vac_list:
                print(f"Обработка отпуска для {emp['fio']}: {vac_period}")
                try:
                    if "start_date" not in vac_period or "end_date" not in vac_period:
                        raise KeyError("Отсутствуют обязательные ключи start_date или end_date")
                    s_date = datetime.strptime(vac_period["start_date"], "%d.%m.%Y")
                    end_date_value = vac_period.get("original_end_date", vac_period["end_date"])
                    if not isinstance(end_date_value, str):
                        raise ValueError(f"end_date_value не строка: {end_date_value}")
                    orig_e_date = datetime.strptime(end_date_value, "%d.%m.%Y")
                    curr_e_date = datetime.strptime(vac_period["end_date"], "%d.%m.%Y")
                    
                    original_days = (orig_e_date - s_date).days + 1
                    
                    current_days = (curr_e_date - s_date).days + 1
                    period_vac_days = [s_date + timedelta(days=i) for i in range(current_days)]
                    non_holiday_days = [d for d in period_vac_days if not is_holiday(app, d)]

                    if len(non_holiday_days) < original_days:
                        new_end_date = curr_e_date
                        while len(non_holiday_days) < original_days:
                            new_end_date = get_next_available_day(app, new_end_date)
                            period_vac_days.append(new_end_date)
                            non_holiday_days = [d for d in period_vac_days if not is_holiday(app, d)]
                        vac_period["end_date"] = new_end_date.strftime("%d.%m.%Y")
                        vac_period["adjusted"] = True
                    else:
                        holiday_count = sum(1 for d in period_vac_days if is_holiday(app, d))
                        if holiday_count == 0:
                            vac_period["end_date"] = orig_e_date.strftime("%d.%m.%Y")
                            vac_period.pop("adjusted", None)
                        else:
                            if len(non_holiday_days) > original_days:
                                new_end_date = s_date
                                non_holiday_days = []
                                while len(non_holiday_days) < original_days:
                                    if not is_holiday(app, new_end_date):
                                        non_holiday_days.append(new_end_date)
                                    new_end_date += timedelta(days=1)
                                vac_period["end_date"] = non_holiday_days[-1].strftime("%d.%m.%Y")
                                vac_period["adjusted"] = True if non_holiday_days[-1] != orig_e_date else False

                    all_vac_days.update(non_holiday_days)
                except Exception as e:
                    messagebox.showwarning("Предупреждение", f"Ошибка обработки отпуска для {emp['fio']}: {str(e)}")
                    continue
        emp["vacation"] = [d.strftime("%d.%m.%Y") for d in sorted(all_vac_days)]
    cache_vacations(app)

def make_holiday(app, date):
    year = str(date.year)
    if is_holiday(app, date):
        return
    if year not in app.holidays:
        app.holidays[year] = set()
    app.holidays[year].add(date)
    if year in app.workdays:
        app.workdays[year].discard(date)
    if year in app.weekends:
        app.weekends[year].discard(date)
    app.data_modified = True
    recalc_employee_vacations(app) 
    app.update_after_change()

def make_workday(app, date):
    year = str(date.year)
    if is_workday(app, date) and not is_holiday(app, date) and not is_weekend(app, date):
        return
    if year not in app.workdays:
        app.workdays[year] = set()
    if year in app.holidays:
        app.holidays[year].discard(date)
    if year in app.weekends:
        app.weekends[year].discard(date)
    app.workdays[year].add(date)
    app.data_modified = True
    recalc_employee_vacations(app) 
    app.update_after_change()

def make_weekend(app, date):
    year = str(date.year)
    if is_weekend(app, date) and not is_holiday(app, date):
        return
    if year not in app.weekends:
        app.weekends[year] = set()
    if year in app.holidays:
        app.holidays[year].discard(date)
    if year in app.workdays:
        app.workdays[year].discard(date)
    app.weekends[year].add(date)
    app.data_modified = True
    recalc_employee_vacations(app) 
    app.update_after_change()


def update_calendar(app):
    """Updates the calendar based on the vacation cache."""
    app.root.config(cursor="watch")
    app.root.update_idletasks()

    for date_key in list(app.day_widgets.keys()):
        day_frame, lbl = app.day_widgets.pop(date_key)
        day_frame.destroy()
        del day_frame, lbl 

    for i, m_frame in enumerate(app.month_frames):
        month_num = i + 1
        month_name = datetime(app.current_year, month_num, 1).strftime("%B %Y")
        month_label = tk.Label(m_frame, text=month_name,
                               font=("Arial", 10, "bold"))
        month_label.grid(row=0, column=0, columnspan=7, pady=5)

        days_of_week = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
        for d_idx, day_name in enumerate(days_of_week):
            day_label = tk.Label(m_frame, text=day_name,
                                 width=4, anchor="center")
            day_label.grid(row=1, column=d_idx, sticky="nsew")

        calendar_days = monthcalendar(app.current_year, month_num)
        for w_idx, week in enumerate(calendar_days):
            for d_idx, day in enumerate(week):
                r = w_idx + 2
                if day != 0:
                    date = datetime(app.current_year, month_num, day)
                    date_key = date.strftime("%Y-%m-%d")

                    day_frame = tk.Frame(
                        m_frame, borderwidth=1, relief="flat", padx=2, pady=2)
                    day_frame.grid(row=r, column=d_idx,
                                   sticky="nsew", padx=1, pady=1)
                    m_frame.grid_rowconfigure(r, weight=1)
                    m_frame.grid_columnconfigure(d_idx, weight=1)

                    lbl = tk.Label(day_frame, text=str(
                        day), width=4, anchor="center")
                    lbl.pack(fill="both", expand=True)
                    app.day_widgets[date_key] = (day_frame, lbl)

                    vacation_employees = app.vacation_cache.get(date_key, [])
                    has_vacation = len(vacation_employees) > 0
                    vacation_overlap = len(vacation_employees) > 1

                    if vacation_overlap:
                        bg_color = "#FFCC99"
                    elif has_vacation:
                        bg_color = "#CCFFCC"
                    else:
                        bg_color = "#FFFFFF"
                    day_frame.config(bg=bg_color)
                    lbl.config(bg=bg_color)

                    if date.date() == app.today:
                        lbl.config(foreground="#3366CC")
                    elif is_holiday(app, date):
                        lbl.config(foreground="red")
                    elif is_workday(app, date):
                        lbl.config(foreground="black")
                    elif is_weekend(app, date):
                        lbl.config(foreground="gray")

                    if has_vacation:
                        tooltip_text = "Отпуск:\n" + \
                            "\n".join(
                                f"{name} ({get_employee_position(app, name)})" for name in vacation_employees)
                        attach_tooltip(day_frame, tooltip_text)

                    d_menu = tk.Menu(app.root, tearoff=0)
                    d_menu.add_command(
                        label="Сделать праздничным", command=lambda d=date: make_holiday(app, d))
                    d_menu.add_command(
                        label="Сделать рабочим", command=lambda d=date: make_workday(app, d))
                    d_menu.add_command(
                        label="Сделать выходным", command=lambda d=date: make_weekend(app, d))
                    day_frame.bind("<Button-3>", lambda e,
                                   m=d_menu: m.post(e.x_root, e.y_root))
                    lbl.bind("<Button-3>", lambda e,
                             m=d_menu: m.post(e.x_root, e.y_root))

    app.root.config(cursor="")


def apply_changes(app):
    """Applies year change."""
    try:
        new_year = int(app.year_spinbox.get())
        if 2000 <= new_year <= 2100:
            app.current_year = new_year
            recalc_employee_vacations(app)
            cache_vacations(app)
            update_employee_list(app)
            update_calendar(app)
        else:
            messagebox.showerror(
                "Ошибка", "Год должен быть в диапазоне от 2000 до 2100")
    except ValueError:
        messagebox.showerror("Ошибка", "Введите корректный год")


def get_employee_position(app, fio):
    """Gets employee position by FIO."""
    for emp in app.employees:
        if emp["fio"] == fio:
            return emp["position"]
    return ""


def export_to_csv(app):
    """Exports calendar and employee list to separate HTML files."""
    try:
        calendar_file_path = filedialog.asksaveasfilename(
            defaultextension=".html",
            filetypes=[("HTML файлы", "*.html"), ("Все файлы", "*.*")],
            title="Сохранить календарь как HTML",
            initialfile=f"calendar_{app.current_year}"
        )
        if not calendar_file_path:
            return

        employees_file_path = filedialog.asksaveasfilename(
            defaultextension=".html",
            filetypes=[("HTML файлы", "*.html"), ("Все файлы", "*.*")],
            title="Сохранить список сотрудников как HTML",
            initialfile=f"employees_{app.current_year}"
        )
        if not employees_file_path:
            return

        calendar_css = """
        <style>
            table, th, td { border: 1px solid black; border-collapse: collapse; padding: 5px; text-align: center; }
            .month-table { display: inline-block; vertical-align: top; margin: 10px; }
            .vacation { background-color: #90EE90; }
            .vacation-overlap { background-color: #FFA500; }
            .holiday { color: #FF0000; }
            .weekend { color: #808080; }
            .today { color: #0000FF; }
            .employee-id { font-size: 10px; vertical-align: super; color: blue; }
        </style>
        """

        employees_css = """
        <style>
            table, th, td { border: 1px solid black; border-collapse: collapse; padding: 5px; text-align: center; }
            th { background-color: #f2f2f2; }
        </style>
        """

        employee_indices = {emp["fio"]: idx + 1 for idx, emp in enumerate(sorted(app.employees, key=lambda x: x["fio"]))}
        vacation_dict = {}
        for emp in app.employees:
            vacation_days = emp.get("vacation", [])
            for day_str in vacation_days:
                try:
                    day_date = datetime.strptime(day_str, "%d.%m.%Y")
                    if day_date.year == app.current_year:
                        date_key = day_date.strftime("%Y-%m-%d")
                        if date_key not in vacation_dict:
                            vacation_dict[date_key] = []
                        vacation_dict[date_key].append(emp["fio"])
                except (ValueError, TypeError):
                    continue

        with open(employees_file_path, 'w', encoding='utf-8') as emp_file:
            emp_file.write('<!DOCTYPE html>\n<html>\n<head>\n<meta charset="utf-8">\n')
            emp_file.write(f'<title>Список сотрудников с отпусками на {app.current_year} год</title>\n')
            emp_file.write(employees_css)
            emp_file.write('</head>\n<body>\n')
            emp_file.write(f'<h2>Список сотрудников с отпусками на {app.current_year} год</h2>\n')
            emp_file.write('<table style="width:100%">\n')
            emp_file.write('<tr><th>ID</th><th>ФИО</th><th>Должность</th><th>Период отпуска</th></tr>\n')

            for emp in sorted(app.employees, key=lambda x: x["fio"]):
                this_year_vacations = emp.get("vacations", {}).get(str(app.current_year), [])
                if this_year_vacations:
                    vacation_periods = []
                    for vac in this_year_vacations:
                        try:
                            start = vac["start_date"]
                            end = vac["end_date"]
                            vacation_periods.append(f"{start} - {end}")
                        except (ValueError, KeyError):
                            continue
                    emp_id = employee_indices[emp["fio"]]
                    emp_file.write(f'<tr><td>{emp_id}</td><td>{emp["fio"]}</td><td>{emp["position"]}</td><td>{vacation_periods[0]}</td></tr>\n')
                    for period in vacation_periods[1:]:
                        emp_file.write(f'<tr><td></td><td></td><td></td><td>{period}</td></tr>\n')
                else:
                    emp_id = employee_indices[emp["fio"]]
                    emp_file.write(f'<tr><td>{emp_id}</td><td>{emp["fio"]}</td><td>{emp["position"]}</td><td>-</td></tr>\n')

            emp_file.write('</table>\n</body>\n</html>')

        with open(calendar_file_path, 'w', encoding='utf-8') as html_file:
            html_file.write('<!DOCTYPE html>\n<html>\n<head>\n<meta charset="utf-8">\n')
            html_file.write(f'<title>Календарь отпусков на {app.current_year} год</title>\n')
            html_file.write(calendar_css)
            html_file.write('</head>\n<body>\n')
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
                                
                                emp_ids = []
                                for emp in app.employees:
                                    emp_id = employee_indices[emp["fio"]]
                                    for vac in emp.get("vacations", {}).get(str(app.current_year), []):
                                        start_date = datetime.strptime(vac["start_date"], "%d.%m.%Y").date()
                                        if start_date == date:
                                            emp_ids.append(str(emp_id))
                                emp_ids_str = '<span class="employee-id">' + ','.join(emp_ids) + '</span>' if emp_ids else ""
                                tooltip = f' title="Отпуск: {", ".join(vacation_employees)}"' if vacation_employees else ""
                                html_file.write(f'<td class="{cell_class}"{tooltip}>{day}{emp_ids_str}</td>\n')
                        html_file.write('</tr>\n')
                    html_file.write('</table>\n')
                html_file.write('</div>\n')

            html_file.write('</body>\n</html>')

        messagebox.showinfo("Готово", f"Экспорт завершен.\nКалендарь: {calendar_file_path}\nСписок сотрудников: {employees_file_path}")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Ошибка при экспорте в HTML: {str(e)}")

def show_about(app):
    """Shows about dialog."""
    from constants import VERSION
    about_dialog = tk.Toplevel(app.root)
    about_dialog.title("О программе")
    about_dialog.geometry("400x300")
    about_dialog.resizable(True, True)

    ttk.Label(about_dialog, text="Календарь отпусков",
              font=("Arial", 14, "bold")).pack(pady=10)
    ttk.Label(about_dialog, text=f"Версия: {VERSION}").pack(pady=5)
    ttk.Label(about_dialog, text="Описание:").pack(anchor="w", padx=20, pady=5)
    ttk.Label(about_dialog, text="Программа для учета и отображения отпусков сотрудников.",
              wraplength=350).pack(padx=20)
    ttk.Label(about_dialog, text="Возможности:").pack(
        anchor="w", padx=20, pady=5)

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

    ttk.Button(about_dialog, text="Закрыть",
               command=about_dialog.destroy).pack(pady=20)
