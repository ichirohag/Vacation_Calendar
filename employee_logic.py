#employee_logic.py
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from tkcalendar import Calendar
from calendar_logic import recalc_employee_vacations, update_calendar
from shared import cache_vacations, update_employee_list
from utils import center_window, validate_date, on_date_input, show_calendar

def create_date_entry(dialog, row, label_text, show_calendar_cmd):
    """Создает поле ввода даты с валидацией, подсказкой и кнопкой календаря"""
    ttk.Label(dialog, text=label_text).grid(row=row, column=0, padx=5, pady=5, sticky="e")
    entry = ttk.Entry(dialog, validate="key", validatecommand=(dialog.register(validate_date), "%S", "%P", "%d"))
    entry.grid(row=row, column=1, padx=5, pady=5, sticky="we")
    
    # Устанавливаем подсказку
    placeholder_text = "ДД.ММ.ГГГГ"
    entry.config(validate="none")  # Отключаем валидацию для вставки
    entry.insert(0, placeholder_text)
    entry.config(validate="key")   # Включаем валидацию обратно
    entry.config(foreground="grey")
    
    # Обработчик получения фокуса
    def on_focus_in(event):
        if entry.get() == placeholder_text:
            entry.delete(0, tk.END)
            entry.config(foreground="black")
    
    # Обработчик потери фокуса
    def on_focus_out(event):
        if not entry.get():
            entry.insert(0, placeholder_text)
            entry.config(foreground="grey")
    
    # Обработчик нажатия клавиши
    def on_key_press(event):
        if entry.get() != placeholder_text and entry.cget("foreground") != "black":
            entry.config(foreground="black")
    
    entry.bind("<FocusIn>", on_focus_in)
    entry.bind("<FocusOut>", on_focus_out)
    entry.bind("<KeyPress>", on_key_press)
    entry.bind("<KeyRelease>", on_date_input)
    
    ttk.Button(dialog, text="Выбрать", command=show_calendar_cmd).grid(row=row, column=2, padx=5)
    return entry

def add_employee_dialog(app):
    dialog = tk.Toplevel(app.root)
    dialog.transient(app.root)
    dialog.grab_set()
    dialog.title("Добавить сотрудника")
    dialog.geometry("300x150")

    # Настройка веса строк и столбцов для центрирования
    dialog.grid_rowconfigure(0, weight=1)  # Пустое пространство сверху
    dialog.grid_rowconfigure(1, weight=0)  # ФИО
    dialog.grid_rowconfigure(2, weight=0)  # Должность
    dialog.grid_rowconfigure(3, weight=0)  # Кнопка
    dialog.grid_rowconfigure(4, weight=1)  # Пустое пространство снизу
    dialog.grid_columnconfigure(0, weight=1)  # Левый отступ
    dialog.grid_columnconfigure(1, weight=1)  # Основной контент
    dialog.grid_columnconfigure(2, weight=1)  # Правый отступ

    # ФИО
    ttk.Label(dialog, text="ФИО:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
    fio_entry = ttk.Entry(dialog)
    fio_entry.grid(row=1, column=1, padx=5, pady=5, sticky="we")
    fio_error = ttk.Label(dialog, text="", foreground="red")
    fio_error.grid(row=1, column=2, padx=5, sticky="w")

    # Должность
    ttk.Label(dialog, text="Должность:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
    pos_entry = ttk.Entry(dialog)
    pos_entry.grid(row=2, column=1, padx=5, pady=5, sticky="we")

    # Кнопка "Сохранить" в отдельном фрейме
    btn_frame = ttk.Frame(dialog)
    btn_frame.grid(row=3, column=0, columnspan=3, pady=10)  # columnspan=3 для центрирования
    ttk.Button(btn_frame, text="Сохранить", command=lambda: save_emp(), width=10).pack()

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

    center_window(dialog, app.root)

def add_vacation_to_selected(app):
    sel = app.employee_list.selection()
    if sel:
        item = app.employee_list.item(sel)
        if item["text"]:
            fio = item["text"]
            add_vacation_dialog(app, fio)

def add_vacation_dialog(app, employee_fio=None):
    dialog = tk.Toplevel(app.root)
    dialog.transient(app.root)
    dialog.grab_set()
    dialog.title("Добавить отпуск")
    dialog.geometry("320x150")

    # Настраиваем вес строк и столбцов
    dialog.grid_rowconfigure(0, weight=1)  # Пустое пространство сверху
    dialog.grid_rowconfigure(1, weight=0)  # Сотрудник
    dialog.grid_rowconfigure(2, weight=0)  # Отпуск с
    dialog.grid_rowconfigure(3, weight=0)  # Отпуск по
    dialog.grid_rowconfigure(4, weight=0)  # Кнопка
    dialog.grid_rowconfigure(5, weight=1)  # Пустое пространство снизу
    dialog.grid_columnconfigure(0, weight=1)  # Левый отступ
    dialog.grid_columnconfigure(1, weight=1)  # Основной контент
    dialog.grid_columnconfigure(2, weight=1)  # Правый отступ

    # Сотрудник
    ttk.Label(dialog, text="Сотрудник:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
    emp_combobox = ttk.Combobox(dialog, values=[emp["fio"] for emp in app.employees])
    emp_combobox.grid(row=1, column=1, padx=5, pady=5, sticky="we")
    if employee_fio:
        emp_combobox.set(employee_fio)
        emp_combobox.config(state="readonly")

    # Поля ввода дат
    start_entry = create_date_entry(dialog, 2, "Отпуск с:", lambda: show_calendar(app, start_entry))
    end_entry = create_date_entry(dialog, 3, "Отпуск по:", lambda: show_calendar(app, end_entry))

    # Кнопка "Сохранить"
    btn_frame = ttk.Frame(dialog)
    btn_frame.grid(row=3, column=0, columnspan=3, pady=10)
    ttk.Button(btn_frame, text="Сохранить", command=save_vacation_wrapper, width=10).pack()

    def save_vacation_wrapper():
        validate_and_save_vacation(app, emp_combobox.get().strip(), start_entry.get().strip(), end_entry.get().strip(), dialog)

    center_window(dialog, app.root)
    dialog.after(100, dialog.focus_set)

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
            start_entry.config(foreground="red")
            end_entry.config(foreground="red")
            dialog.after(2000, lambda: [start_entry.config(foreground="black"), end_entry.config(foreground="black")])
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
            dialog.transient(app.root)
            dialog.grab_set()
            dialog.title("Редактировать отпуск")
            dialog.geometry("320x150")

            # Настройка веса строк и столбцов
            dialog.grid_rowconfigure(0, weight=1)  # Пустое пространство сверху
            dialog.grid_rowconfigure(1, weight=0)  # Сотрудник
            dialog.grid_rowconfigure(2, weight=0)  # Отпуск с
            dialog.grid_rowconfigure(3, weight=0)  # Отпуск по
            dialog.grid_rowconfigure(4, weight=0)  # Кнопка
            dialog.grid_rowconfigure(5, weight=1)  # Пустое пространство снизу
            dialog.grid_columnconfigure(0, weight=1)  # Левый отступ
            dialog.grid_columnconfigure(1, weight=1)  # Основной контент
            dialog.grid_columnconfigure(2, weight=1)  # Правый отступ

            # Сотрудник
            ttk.Label(dialog, text="Сотрудник:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
            emp_combobox = ttk.Combobox(dialog, values=[emp["fio"] for emp in app.employees])
            emp_combobox.set(fio)
            emp_combobox.config(state="readonly")
            emp_combobox.grid(row=1, column=1, padx=5, pady=5, sticky="we")

            # Поля дат
            start_entry = create_date_entry(dialog, 2, "Отпуск с:", lambda: show_calendar(app, start_entry))
            start_entry.delete(0, tk.END)
            start_entry.insert(0, old_start)
            start_entry.config(foreground="black")

            end_entry = create_date_entry(dialog, 3, "Отпуск по:", lambda: show_calendar(app, end_entry))
            end_entry.delete(0, tk.END)
            end_entry.insert(0, old_end)
            end_entry.config(foreground="black")

            # Кнопка "Сохранить" с фиксированной шириной
            btn_frame = ttk.Frame(dialog)
            btn_frame.grid(row=4, column=0, columnspan=3, pady=10)
            ttk.Button(btn_frame, text="Сохранить", command=lambda: save_edit(), width=10).pack()

            def save_edit():
                validate_and_save_vacation(app, emp_combobox.get().strip(), start_entry.get().strip(), end_entry.get().strip(), dialog, {"start_date": old_start, "end_date": old_end})

            center_window(dialog, app.root)
            dialog.after(100, dialog.focus_set)

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
            start_entry.config(foreground="red")  # Подсветка ошибки
            end_entry.config(foreground="red")
            dialog.after(2000, lambda: [start_entry.config(foreground="black"), end_entry.config(foreground="black")])  # Сброс через 2 секунды
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

def edit_employee_dialog(app):
    sel = app.employee_list.selection()
    if sel:
        item = app.employee_list.item(sel)
        if item["text"]:
            fio = item["text"]
            for emp in app.employees:
                if emp["fio"] == fio:
                    dialog = tk.Toplevel(app.root)
                    dialog.transient(app.root)
                    dialog.grab_set()
                    dialog.title("Редактировать сотрудника")
                    dialog.geometry("300x150")

                    # Настройка веса строк и столбцов для центрирования
                    dialog.grid_rowconfigure(0, weight=1)  # Пустое пространство сверху
                    dialog.grid_rowconfigure(1, weight=0)  # ФИО
                    dialog.grid_rowconfigure(2, weight=0)  # Должность
                    dialog.grid_rowconfigure(3, weight=0)  # Кнопка
                    dialog.grid_rowconfigure(4, weight=1)  # Пустое пространство снизу
                    dialog.grid_columnconfigure(0, weight=1)  # Левый отступ
                    dialog.grid_columnconfigure(1, weight=1)  # Основной контент
                    dialog.grid_columnconfigure(2, weight=1)  # Правый отступ

                    # ФИО
                    ttk.Label(dialog, text="ФИО:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
                    fio_entry = ttk.Entry(dialog)
                    fio_entry.insert(0, emp["fio"])
                    fio_entry.grid(row=1, column=1, padx=5, pady=5, sticky="we")

                    # Должность
                    ttk.Label(dialog, text="Должность:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
                    pos_entry = ttk.Entry(dialog)
                    pos_entry.insert(0, emp["position"])
                    pos_entry.grid(row=2, column=1, padx=5, pady=5, sticky="we")

                    # Кнопка "Сохранить" с фиксированной шириной
                    btn_frame = ttk.Frame(dialog)
                    btn_frame.grid(row=3, column=0, columnspan=3, pady=10)
                    ttk.Button(btn_frame, text="Сохранить", command=lambda: save_edit(), width=10).pack()

                    def save_edit():
                        # Логика сохранения остается прежней
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

                    center_window(dialog, app.root)
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

def validate_and_save_vacation(app, fio, start_date, end_date, dialog, old_vacation=None):
    try:
        if not fio:
            messagebox.showerror("Ошибка", "Выберите сотрудника")
            return False
        s_date = datetime.strptime(start_date, "%d.%m.%Y")
        e_date = datetime.strptime(end_date, "%d.%m.%Y")
        if s_date > e_date:
            messagebox.showerror("Ошибка", "Дата начала не может быть позже даты окончания")
            return False
        
        for emp in app.employees:
            if emp["fio"] == fio:
                for vac in emp.get("vacations", []):
                    vac_start = datetime.strptime(vac["start_date"], "%d.%m.%Y")
                    vac_end = datetime.strptime(vac["end_date"], "%d.%m.%Y")
                    if old_vacation and vac["start_date"] == old_vacation["start_date"] and vac["end_date"] == old_vacation["end_date"]:
                        continue  # Пропускаем старый отпуск при редактировании
                    if not (e_date < vac_start or s_date > vac_end):
                        messagebox.showerror("Ошибка", f"Отпуск для {fio} уже существует в периоде {vac['start_date']} - {vac['end_date']}")
                        return False
                if old_vacation:
                    for vac in emp["vacations"]:
                        if vac["start_date"] == old_vacation["start_date"] and vac["end_date"] == old_vacation["end_date"]:
                            vac["start_date"] = start_date
                            vac["end_date"] = end_date
                            break
                else:
                    emp["vacations"].append({"start_date": start_date, "end_date": end_date})
                break
        
        app.data_modified = True
        recalc_employee_vacations(app)
        cache_vacations(app)
        update_employee_list(app)
        update_calendar(app)
        dialog.destroy()
        return True
    except ValueError:
        messagebox.showerror("Ошибка", "Неверный формат даты! Используйте ДД.ММ.ГГГГ")
        return False
    except Exception as e:
        messagebox.showerror("Ошибка", f"Произошла ошибка: {str(e)}")
        return False