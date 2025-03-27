
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import Calendar
from datetime import datetime
from utils import center_window, validate_date, on_date_input, show_calendar

def add_context_menu(entry):
    """Adds a context menu for copy/paste."""
    menu = tk.Menu(entry, tearoff=0)
    menu.add_command(label="Вырезать", command=lambda: entry.event_generate("<<Cut>>"))
    menu.add_command(label="Копировать", command=lambda: entry.event_generate("<<Copy>>"))
    menu.add_command(label="Вставить", command=lambda: entry.event_generate("<<Paste>>"))
    entry.bind("<Button-3>", lambda event: menu.post(event.x_root, event.y_root))

    entry.bind("<Control-c>", lambda event: entry.event_generate("<<Copy>>"))
    entry.bind("<Control-v>", lambda event: entry.event_generate("<<Paste>>"))
    entry.bind("<Control-x>", lambda event: entry.event_generate("<<Cut>>"))

def create_date_entry(dialog, row, label_text, show_calendar_cmd):
    """Creates validated date entry."""
    ttk.Label(dialog, text=label_text).grid(
        row=row, column=0, padx=5, pady=5, sticky="e")
    entry = ttk.Entry(dialog, validate="key", validatecommand=(
        dialog.register(validate_date), "%S", "%P", "%d"))
    entry.grid(row=row, column=1, padx=5, pady=5, sticky="we")

    placeholder_text = "ДД.ММ.ГГГГ"
    entry.config(validate="none")
    entry.insert(0, placeholder_text)
    entry.config(validate="key")
    entry.config(foreground="grey")

    def on_focus_in(event):
        if entry.get() == placeholder_text:
            entry.delete(0, tk.END)
            entry.config(foreground="black")

    def on_focus_out(event):
        if not entry.get():
            entry.insert(0, placeholder_text)
            entry.config(foreground="grey")

    def on_key_press(event):
        if entry.get() != placeholder_text and entry.cget("foreground") != "black":
            entry.config(foreground="black")

    entry.bind("<FocusIn>", on_focus_in)
    entry.bind("<FocusOut>", on_focus_out)
    entry.bind("<KeyPress>", on_key_press)
    entry.bind("<KeyRelease>", on_date_input)

    ttk.Button(dialog, text="Выбрать", command=show_calendar_cmd).grid(
        row=row, column=2, padx=5)
    return entry


def add_employee_dialog(app):
    """Opens add employee dialog."""
    dialog = tk.Toplevel(app.root)
    dialog.transient(app.root)
    dialog.grab_set()
    dialog.title("Добавить сотрудника")
    dialog.geometry("300x150")

    dialog.grid_rowconfigure(0, weight=1)
    dialog.grid_rowconfigure(1, weight=0)
    dialog.grid_rowconfigure(2, weight=0)
    dialog.grid_rowconfigure(3, weight=0)
    dialog.grid_rowconfigure(4, weight=1)
    dialog.grid_columnconfigure(0, weight=1)
    dialog.grid_columnconfigure(1, weight=1)
    dialog.grid_columnconfigure(2, weight=1)

    ttk.Label(dialog, text="ФИО:").grid(
        row=1, column=0, padx=5, pady=5, sticky="e")
    fio_entry = ttk.Entry(dialog)
    fio_entry.grid(row=1, column=1, padx=5, pady=5, sticky="we")
    add_context_menu(fio_entry)   
    fio_error = ttk.Label(dialog, text="", foreground="red")
    fio_error.grid(row=1, column=2, padx=5, sticky="w")

    ttk.Label(dialog, text="Должность:").grid(
        row=2, column=0, padx=5, pady=5, sticky="e")
    pos_entry = ttk.Entry(dialog)
    pos_entry.grid(row=2, column=1, padx=5, pady=5, sticky="we")
    add_context_menu(pos_entry)   

    btn_frame = ttk.Frame(dialog)
    btn_frame.grid(row=3, column=0, columnspan=3, pady=10)
    ttk.Button(btn_frame, text="Сохранить",
               command=lambda: save_emp(), width=10).pack()

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
            if not fio or any(emp["fio"] == fio for emp in app.employees):
                messagebox.showerror(
                    "Ошибка", "ФИО не может быть пустым или уже существует")
                return
            if not pos:
                messagebox.showerror("Ошибка", "Должность не может быть пустой")
                return
            if any(emp["fio"] == fio for emp in app.employees):
                messagebox.showerror("Ошибка", "Сотрудник с таким ФИО уже существует")
                return
            app.employees.append({"fio": fio, "position": pos, "vacations": {}})
            app.data_modified = True
            app.update_after_change()
            dialog.destroy()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {str(e)}")

    btn_frame = ttk.Frame(dialog)
    btn_frame.grid(row=3, column=0, columnspan=3, pady=10)
    save_btn = ttk.Button(btn_frame, text="Сохранить", command=save_emp, width=10)
    save_btn.pack()
    
      
    dialog.bind("<Return>", lambda event: save_emp())

    center_window(dialog, app.root)


def add_vacation_dialog(app, employee_fio=None):
    """Opens add vacation dialog."""
    dialog = tk.Toplevel(app.root)
    dialog.transient(app.root)
    dialog.grab_set()
    dialog.title("Добавить отпуск")
    dialog.geometry("320x150")

    dialog.grid_rowconfigure(0, weight=1)
    dialog.grid_rowconfigure(1, weight=0)
    dialog.grid_rowconfigure(2, weight=0)
    dialog.grid_rowconfigure(3, weight=0)
    dialog.grid_rowconfigure(4, weight=0)
    dialog.grid_rowconfigure(5, weight=1)
    dialog.grid_columnconfigure(0, weight=1)
    dialog.grid_columnconfigure(1, weight=1)
    dialog.grid_columnconfigure(2, weight=1)

    ttk.Label(dialog, text="Сотрудник:").grid(
        row=1, column=0, padx=5, pady=5, sticky="e")
    emp_combobox = ttk.Combobox(
        dialog, values=[emp["fio"] for emp in app.employees])
    emp_combobox.grid(row=1, column=1, padx=5, pady=5, sticky="we")
    if employee_fio:
        emp_combobox.set(employee_fio)
        emp_combobox.config(state="readonly")

    start_entry = create_date_entry(
        dialog, 2, "Отпуск с:", lambda: show_calendar(app, start_entry))
    end_entry = create_date_entry(
        dialog, 3, "Отпуск по:", lambda: show_calendar(app, end_entry))

    def save_vacation_wrapper():
        fio = emp_combobox.get().strip()
        start = start_entry.get().strip()
        end = end_entry.get().strip()
        if not fio:
            messagebox.showerror("Ошибка", "Выберите сотрудника")
            return
        if not start or start == "ДД.ММ.ГГГГ":
            messagebox.showerror("Ошибка", "Поле 'Отпуск с' не может быть пустым")
            return
        if not end or end == "ДД.ММ.ГГГГ":
            messagebox.showerror("Ошибка", "Поле 'Отпуск по' не может быть пустым")
            return
        validate_and_save_vacation(app, fio, start, end, dialog)
    
    btn_frame = ttk.Frame(dialog)
    btn_frame.grid(row=4, column=0, columnspan=3, pady=10)
    save_btn = ttk.Button(btn_frame, text="Сохранить", command=save_vacation_wrapper, width=10)
    save_btn.pack()

      
    dialog.bind("<Return>", lambda event: save_vacation_wrapper())

    center_window(dialog, app.root)
    dialog.after(100, dialog.focus_set)


def edit_employee_dialog(app):
    """Opens edit employee dialog."""
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

                    dialog.grid_rowconfigure(0, weight=1)
                    dialog.grid_rowconfigure(1, weight=0)
                    dialog.grid_rowconfigure(2, weight=0)
                    dialog.grid_rowconfigure(3, weight=0)
                    dialog.grid_rowconfigure(4, weight=1)
                    dialog.grid_columnconfigure(0, weight=1)
                    dialog.grid_columnconfigure(1, weight=1)
                    dialog.grid_columnconfigure(2, weight=1)

                    ttk.Label(dialog, text="ФИО:").grid(
                        row=1, column=0, padx=5, pady=5, sticky="e")
                    fio_entry = ttk.Entry(dialog)
                    fio_entry.insert(0, emp["fio"])
                    fio_entry.grid(row=1, column=1, padx=5,
                                   pady=5, sticky="we")
                    add_context_menu(fio_entry)   

                    ttk.Label(dialog, text="Должность:").grid(
                        row=2, column=0, padx=5, pady=5, sticky="e")
                    pos_entry = ttk.Entry(dialog)
                    pos_entry.insert(0, emp["position"])
                    pos_entry.grid(row=2, column=1, padx=5,
                                   pady=5, sticky="we")
                    add_context_menu(pos_entry)   

                    btn_frame = ttk.Frame(dialog)
                    btn_frame.grid(row=3, column=0, columnspan=3, pady=10)
                    ttk.Button(btn_frame, text="Сохранить",
                               command=lambda: save_edit(), width=10).pack()

                    def save_edit():
                        new_fio = fio_entry.get().strip()
                        new_pos = pos_entry.get().strip()
                        if not new_fio:
                            messagebox.showerror("Ошибка", "ФИО не может быть пустым")
                            return
                        if not new_pos:
                            messagebox.showerror("Ошибка", "Должность не может быть пустой")
                            return
                        if new_fio != fio and any(e["fio"] == new_fio for e in app.employees):
                            messagebox.showerror("Ошибка", "Сотрудник с таким ФИО уже существует")
                            return
                        emp["fio"] = new_fio
                        emp["position"] = new_pos
                        app.data_modified = True
                        app.update_after_change()
                        dialog.destroy()

                    btn_frame = ttk.Frame(dialog)
                    btn_frame.grid(row=3, column=0, columnspan=3, pady=10)
                    save_btn = ttk.Button(btn_frame, text="Сохранить", command=save_edit, width=10)
                    save_btn.pack()
                    
                      
                    dialog.bind("<Return>", lambda event: save_edit())

                    center_window(dialog, app.root)
                    break


def edit_vacation_dialog(app):
    """Opens edit vacation dialog."""
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

            dialog.grid_rowconfigure(0, weight=1)
            dialog.grid_rowconfigure(1, weight=0)
            dialog.grid_rowconfigure(2, weight=0)
            dialog.grid_rowconfigure(3, weight=0)
            dialog.grid_rowconfigure(4, weight=0)
            dialog.grid_rowconfigure(5, weight=1)
            dialog.grid_columnconfigure(0, weight=1)
            dialog.grid_columnconfigure(1, weight=1)
            dialog.grid_columnconfigure(2, weight=1)

            ttk.Label(dialog, text="Сотрудник:").grid(
                row=1, column=0, padx=5, pady=5, sticky="e")
            emp_combobox = ttk.Combobox(
                dialog, values=[emp["fio"] for emp in app.employees])
            emp_combobox.set(fio)
            emp_combobox.config(state="readonly")
            emp_combobox.grid(row=1, column=1, padx=5, pady=5, sticky="we")

            start_entry = create_date_entry(
                dialog, 2, "Отпуск с:", lambda: show_calendar(app, start_entry))
            start_entry.delete(0, tk.END)
            start_entry.insert(0, old_start)
            start_entry.config(foreground="black")

            end_entry = create_date_entry(
                dialog, 3, "Отпуск по:", lambda: show_calendar(app, end_entry))
            end_entry.delete(0, tk.END)
            end_entry.insert(0, old_end)
            end_entry.config(foreground="black")

            btn_frame = ttk.Frame(dialog)
            btn_frame.grid(row=4, column=0, columnspan=3, pady=10)
            ttk.Button(btn_frame, text="Сохранить",
                       command=lambda: save_edit(), width=10).pack()

            def save_edit():
                fio = emp_combobox.get().strip()
                start = start_entry.get().strip()
                end = end_entry.get().strip()
                if not fio:
                    messagebox.showerror("Ошибка", "Выберите сотрудника")
                    return
                if not start or start == "ДД.ММ.ГГГГ":
                    messagebox.showerror("Ошибка", "Поле 'Отпуск с' не может быть пустым")
                    return
                if not end or end == "ДД.ММ.ГГГГ":
                    messagebox.showerror("Ошибка", "Поле 'Отпуск по' не может быть пустым")
                    return
                validate_and_save_vacation(app, fio, start, end, dialog, {"start_date": old_start, "end_date": old_end})

            btn_frame = ttk.Frame(dialog)
            btn_frame.grid(row=4, column=0, columnspan=3, pady=10)
            save_btn = ttk.Button(btn_frame, text="Сохранить", command=save_edit, width=10)
            save_btn.pack()
            
              
            dialog.bind("<Return>", lambda event: save_edit())

            center_window(dialog, app.root)
            dialog.after(100, dialog.focus_set)


def delete_employee(app):
    """Deletes selected employee."""
    sel = app.employee_list.selection()
    if sel:
        item = app.employee_list.item(sel)
        if item["text"]:
            fio = item["text"]
            if messagebox.askyesno("Подтверждение", f"Удалить сотрудника {fio} и все его отпуска? Данные будут потеряны безвозвратно."):
                app.employees = [
                    emp for emp in app.employees if emp["fio"] != fio]
                app.data_modified = True
                app.update_after_change()


def delete_vacation(app):
    """Deletes selected vacation."""
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
                        for year, vac_list in emp.get("vacations", {}).items():
                            emp["vacations"][year] = [vac for vac in vac_list if not (
                                vac["start_date"] == start_date and vac["end_date"] == end_date)]
                        break
                app.data_modified = True
                app.update_after_change()


def validate_and_save_vacation(app, fio, start_date, end_date, dialog, old_vacation=None):
    try:
        if not fio:
            messagebox.showerror("Ошибка", "Выберите сотрудника")
            return False
        s_date = datetime.strptime(start_date, "%d.%m.%Y")
        e_date = datetime.strptime(end_date, "%d.%m.%Y")
        if s_date > e_date:
            messagebox.showerror(
                "Ошибка", "Дата начала не может быть позже даты окончания")
            return False

        year = str(s_date.year)
        for emp in app.employees:
            if emp["fio"] == fio:
                if "vacations" not in emp:
                    emp["vacations"] = {}
                if year not in emp["vacations"]:
                    emp["vacations"][year] = []

                for vac in emp["vacations"][year]:
                    vac_start = datetime.strptime(
                        vac["start_date"], "%d.%m.%Y")
                    vac_end = datetime.strptime(vac["end_date"], "%d.%m.%Y")
                    if old_vacation and vac["start_date"] == old_vacation["start_date"] and vac["end_date"] == old_vacation["end_date"]:
                        continue
                    if not (e_date < vac_start or s_date > vac_end):
                        messagebox.showerror(
                            "Ошибка", f"Отпуск для {fio} уже существует в периоде {vac['start_date']} - {vac['end_date']}")
                        return False
                if old_vacation:
                    for vac in emp["vacations"][year]:
                        if vac["start_date"] == old_vacation["start_date"] and vac["end_date"] == old_vacation["end_date"]:
                            vac["start_date"] = start_date
                            vac["end_date"] = end_date
                            break
                else:

                    emp["vacations"][year].append({
                        "start_date": start_date,
                        "end_date": end_date,
                        "original_end_date": end_date
                    })
                break

        app.data_modified = True
        app.update_after_change()
        dialog.destroy()
        return True
    except ValueError:
        messagebox.showerror(
            "Ошибка", "Неверный формат даты! Используйте ДД.ММ.ГГГГ")
        return False
    except Exception as e:
        messagebox.showerror("Ошибка", f"Произошла ошибка: {str(e)}")
        return False
