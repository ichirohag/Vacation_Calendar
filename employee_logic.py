# employee_logic.py
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from tkcalendar import Calendar
from calendar_logic import recalc_employee_vacations
from calendar_logic import update_calendar
from shared import cache_vacations
from shared import update_employee_list

def add_employee_dialog(app):
    dialog = tk.Toplevel(app.root)
    dialog.title("Добавить сотрудника")
    dialog.geometry("400x150")

    ttk.Label(dialog, text="ФИО:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
    fio_entry = ttk.Entry(dialog)
    fio_entry.grid(row=0, column=1, padx=5, pady=5, sticky="we")
    fio_error = ttk.Label(dialog, text="", foreground="red")
    fio_error.grid(row=0, column=2, padx=5)

    def validate_fio(*args):
        fio = fio_entry.get().strip()
        if not fio:
            fio_error.config(text="ФИО не может быть пустым")
        elif any(emp["fio"] == fio for emp in app.employees):
            fio_error.config(text="Сотрудник уже существует")
        else:
            fio_error.config(text="")

    fio_var = tk.StringVar()
    fio_entry.config(textvariable=fio_var)
    fio_var.trace("w", validate_fio)

    ttk.Label(dialog, text="Должность:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
    pos_entry = ttk.Entry(dialog)
    pos_entry.grid(row=1, column=1, padx=5, pady=5, sticky="we")

    def save_emp():
        try:
            fio = fio_entry.get().strip()
            pos = pos_entry.get().strip()
            if not fio:
                messagebox.showerror("Ошибка", "ФИО не может быть пустым")
                return
            for emp in app.employees:
                if emp["fio"] == fio:
                    messagebox.showerror("Ошибка", "Сотрудник с таким ФИО уже существует")
                    return
            app.employees.append({"fio": fio, "position": pos, "vacations": []})
            app.data_modified = True
            update_employee_list(app)
            dialog.destroy()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {str(e)}")

    ttk.Button(dialog, text="Сохранить", command=save_emp).grid(row=2, column=0, columnspan=2, pady=10, sticky="we")

def add_vacation_to_selected(app):
    sel = app.employee_list.selection()
    if sel:
        item = app.employee_list.item(sel)
        if item["text"]:
            fio = item["text"]
            add_vacation_dialog(app, fio)

def add_vacation_dialog(app, employee_fio=None):
    dialog = tk.Toplevel(app.root)
    dialog.title("Добавить отпуск")
    dialog.geometry("400x300")

    ttk.Label(dialog, text="Сотрудник:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
    emp_combobox = ttk.Combobox(dialog, values=[emp["fio"] for emp in app.employees])
    emp_combobox.grid(row=0, column=1, padx=5, pady=5, sticky="we")
    if employee_fio:
        emp_combobox.set(employee_fio)
        emp_combobox.config(state="readonly")

    ttk.Label(dialog, text="Отпуск с:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
    start_entry = ttk.Entry(dialog)
    start_entry.grid(row=1, column=1, padx=5, pady=5, sticky="we")
    ttk.Button(dialog, text="Выбрать", command=lambda: show_calendar(app, start_entry)).grid(row=1, column=2, padx=5)

    ttk.Label(dialog, text="Отпуск по:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
    end_entry = ttk.Entry(dialog)
    end_entry.grid(row=2, column=1, padx=5, pady=5, sticky="we")
    ttk.Button(dialog, text="Выбрать", command=lambda: show_calendar(app, end_entry)).grid(row=2, column=2, padx=5)

    def save_vacation_wrapper():
        save_vacation(app, emp_combobox, start_entry, end_entry, dialog)

    ttk.Button(dialog, text="Сохранить", command=save_vacation_wrapper).grid(row=3, column=0, columnspan=3, pady=10, sticky="we")

def show_calendar(app, entry):
    top = tk.Toplevel(app.root)
    cal = Calendar(top, selectmode="day", year=app.current_year, month=1, day=1, date_pattern="dd.mm.yyyy")
    cal.pack(pady=10)

    def set_date():
        entry.delete(0, tk.END)
        entry.insert(0, cal.get_date())
        top.destroy()

    ttk.Button(top, text="Выбрать", command=set_date).pack(pady=5)

def save_vacation(app, emp_combobox, start_entry, end_entry, dialog):
    try:
        fio = emp_combobox.get().strip()
        start_date = start_entry.get().strip()
        end_date = end_entry.get().strip()
        if not fio:
            messagebox.showerror("Ошибка", "Выберите сотрудника")
            return
        try:
            s_date = datetime.strptime(start_date, "%d.%m.%Y")
            e_date = datetime.strptime(end_date, "%d.%m.%Y")
            if s_date > e_date:
                messagebox.showerror("Ошибка", "Дата начала не может быть позже даты окончания")
                return
        except ValueError:
            messagebox.showerror("Ошибка", "Неверный формат даты! Используйте ДД.ММ.ГГГГ")
            return

        for emp in app.employees:
            if emp["fio"] == fio:
                for vac in emp.get("vacations", []):
                    vac_start = datetime.strptime(vac["start_date"], "%d.%m.%Y")
                    vac_end = datetime.strptime(vac["end_date"], "%d.%m.%Y")
                    if not (e_date < vac_start or s_date > vac_end):
                        messagebox.showerror("Ошибка", f"Отпуск для {fio} уже существует в периоде {vac['start_date']} - {vac['end_date']}")
                        return
                emp["vacations"].append({"start_date": start_date, "end_date": end_date})
                break

        app.data_modified = True
        recalc_employee_vacations(app)
        cache_vacations(app)
        update_employee_list(app)
        update_calendar(app)
        dialog.destroy()
    except Exception as e:
        messagebox.showerror("Ошибка", f"Произошла ошибка: {str(e)}")

def edit_vacation_dialog(app):
    sel = app.employee_list.selection()
    if sel:
        item = app.employee_list.item(sel)
        if not item["text"] and item["values"]:
            parent_id = app.employee_list.parent(sel)
            parent_item = app.employee_list.item(parent_id)
            fio = parent_item["text"]
            old_start = item["values"][1]
            old_end = item["values"][2]

            dialog = tk.Toplevel(app.root)
            dialog.title("Редактировать отпуск")
            dialog.geometry("400x150")

            ttk.Label(dialog, text="Отпуск с:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
            start_entry = ttk.Entry(dialog)
            start_entry.insert(0, old_start)
            start_entry.grid(row=0, column=1, padx=5, pady=5, sticky="we")

            ttk.Label(dialog, text="Отпуск по:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
            end_entry = ttk.Entry(dialog)
            end_entry.insert(0, old_end)
            end_entry.grid(row=1, column=1, padx=5, pady=5, sticky="we")

            def save_edit():
                try:
                    new_start = start_entry.get().strip()
                    new_end = end_entry.get().strip()
                    try:
                        s_date = datetime.strptime(new_start, "%d.%m.%Y")
                        e_date = datetime.strptime(new_end, "%d.%m.%Y")
                        if s_date > e_date:
                            messagebox.showerror("Ошибка", "Дата начала не может быть позже даты окончания")
                            return
                    except ValueError:
                        messagebox.showerror("Ошибка", "Неверный формат даты! Используйте ДД.ММ.ГГГГ")
                        return
                    for emp in app.employees:
                        if emp["fio"] == fio:
                            for vac in emp["vacations"]:
                                if vac["start_date"] == old_start and vac["end_date"] == old_end:
                                    vac["start_date"] = new_start
                                    vac["end_date"] = new_end
                                    break
                            break
                    app.data_modified = True
                    recalc_employee_vacations(app)
                    update_employee_list(app)
                    update_calendar(app)
                    dialog.destroy()
                except Exception as e:
                    messagebox.showerror("Ошибка", f"Произошла ошибка: {str(e)}")

            ttk.Button(dialog, text="Сохранить", command=save_edit).grid(row=2, column=0, columnspan=2, pady=10, sticky="we")

def edit_employee_dialog(app):
    sel = app.employee_list.selection()
    if sel:
        item = app.employee_list.item(sel)
        if item["text"]:
            fio = item["text"]
            for emp in app.employees:
                if emp["fio"] == fio:
                    dialog = tk.Toplevel(app.root)
                    dialog.title("Редактировать сотрудника")
                    dialog.geometry("400x150")

                    ttk.Label(dialog, text="ФИО:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
                    fio_entry = ttk.Entry(dialog)
                    fio_entry.insert(0, emp["fio"])
                    fio_entry.grid(row=0, column=1, padx=5, pady=5, sticky="we")

                    ttk.Label(dialog, text="Должность:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
                    pos_entry = ttk.Entry(dialog)
                    pos_entry.insert(0, emp["position"])
                    pos_entry.grid(row=1, column=1, padx=5, pady=5, sticky="we")

                    def save_edit():
                        try:
                            new_fio = fio_entry.get().strip()
                            new_pos = pos_entry.get().strip()
                            if not new_fio:
                                messagebox.showerror("Ошибка", "ФИО не может быть пустым")
                                return
                            if new_fio != fio and any(e["fio"] == new_fio for e in app.employees):
                                messagebox.showerror("Ошибка", "Сотрудник с таким ФИО уже существует")
                                return
                            emp["fio"] = new_fio
                            emp["position"] = new_pos
                            app.data_modified = True
                            update_employee_list(app)
                            dialog.destroy()
                        except Exception as e:
                            messagebox.showerror("Ошибка", f"Произошла ошибка: {str(e)}")

                    ttk.Button(dialog, text="Сохранить", command=save_edit).grid(row=2, column=0, columnspan=2, pady=10, sticky="we")
                    break

def delete_vacation(app):
    sel = app.employee_list.selection()
    if sel:
        item = app.employee_list.item(sel)
        if not item["text"] and item["values"]:
            parent_id = app.employee_list.parent(sel)
            parent_item = app.employee_list.item(parent_id)
            fio = parent_item["text"]
            start_date = item["values"][1]
            end_date = item["values"][2]
            if messagebox.askyesno("Подтверждение", f"Удалить отпуск {start_date} - {end_date} у {fio}?"):
                for emp in app.employees:
                    if emp["fio"] == fio:
                        emp["vacations"] = [vac for vac in emp["vacations"] if not (vac["start_date"] == start_date and vac["end_date"] == end_date)]
                        break
                app.data_modified = True
                recalc_employee_vacations(app)
                cache_vacations(app)
                update_employee_list(app)
                update_calendar(app)

def delete_employee(app):
    sel = app.employee_list.selection()
    if sel:
        item = app.employee_list.item(sel)
        if item["text"]:
            fio = item["text"]
            if messagebox.askyesno("Подтверждение", f"Удалить сотрудника {fio} и все его отпуска?"):
                app.employees = [emp for emp in app.employees if emp["fio"] != fio]
                app.data_modified = True
                update_employee_list(app)
                update_calendar(app)

def filter_employees(app, *args):
    for child in app.employee_list.get_children():
        app.employee_list.delete(child)
    search_text = app.search_var.get().lower() if hasattr(app, 'search_var') else ""
    apply_employee_filter(app, search_text)

def apply_employee_filter(app, search_text):
    for emp in app.employees:
        try:
            if search_text and search_text not in emp["fio"].lower() and search_text not in emp["position"].lower():
                continue
            show_employee = False
            vacation_periods = []
            if "vacations" in emp and isinstance(emp["vacations"], list) and emp["vacations"]:
                for vac in emp["vacations"]:
                    try:
                        s_date = datetime.strptime(vac["start_date"], "%d.%m.%Y")
                        e_date = datetime.strptime(vac["end_date"], "%d.%m.%Y")
                        if s_date.year <= app.current_year <= e_date.year:
                            show_employee = True
                            vacation_periods.append(f"{vac['start_date']} - {vac['end_date']}")
                    except Exception:
                        continue
            elif "start_date" in emp and "end_date" in emp:
                s_date = datetime.strptime(emp["start_date"], "%d.%m.%Y")
                e_date = datetime.strptime(emp["end_date"], "%d.%m.%Y")
                if s_date.year <= app.current_year <= e_date.year:
                    show_employee = True
                    vacation_periods.append(f"{emp['start_date']} - {emp['end_date']}")
            if any(datetime.strptime(day, "%d.%m.%Y").year == app.current_year for day in emp.get("vacation", [])):
                show_employee = True
            if show_employee:
                start_date = emp.get("start_date", "")
                end_date = emp.get("end_date", "")
                app.employee_list.insert("", "end", values=(emp["fio"], emp["position"], start_date, end_date))
        except Exception as e:
            print(f"Ошибка при фильтрации сотрудников: {str(e)}")
            continue

def show_employee_menu(app, event):
    sel = app.employee_list.identify_row(event.y)
    if sel:
        app.employee_list.selection_set(sel)
        app.employee_menu.post(event.x_root, event.y_root)