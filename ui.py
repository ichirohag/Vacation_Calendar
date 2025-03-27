from calendar_logic import export_to_csv, show_about, apply_changes
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import Calendar
from datetime import datetime
from shared import cache_vacations, update_employee_list
from utils import center_window, validate_date, on_date_input, show_calendar
from dialogs import add_employee_dialog, add_vacation_dialog, edit_employee_dialog, delete_employee, edit_vacation_dialog, delete_vacation


def setup_top_panel(app):
    """Sets up top controls."""
    app.top_panel = ttk.Frame(app.main_frame)
    app.top_panel.grid(row=0, column=0, columnspan=2,
                       sticky="ew", padx=5, pady=5)
    ttk.Label(app.top_panel, text="Год:").pack(side="left", padx=(0, 5))
    app.year_spinbox = ttk.Spinbox(
        app.top_panel, from_=2000, to=2100, width=6, command=lambda: apply_changes(app))
    app.year_spinbox.set(app.current_year)
    app.year_spinbox.pack(side="left")
    app.apply_btn = ttk.Button(
        app.top_panel, text="Применить", command=lambda: safe_apply_changes(app))
    app.apply_btn.pack(side="left", padx=5)
    ttk.Separator(app.top_panel, orient='vertical').pack(
        side="left", padx=10, fill='y')
    app.save_btn = ttk.Button(
        app.top_panel, text="Сохранить", command=lambda: safe_save_data(app))
    app.save_btn.pack(side="left", padx=5)
    app.about_btn = ttk.Button(
        app.top_panel, text="О программе", command=lambda: show_about(app))
    app.about_btn.pack(side="right", padx=5)

def safe_apply_changes(app):
    try:
        apply_changes(app)
    except Exception as e:
        messagebox.showerror("Ошибка", f"Ошибка при применении изменений: {str(e)}")

def safe_save_data(app):
    try:
        app.save_data()
    except Exception as e:
        messagebox.showerror("Ошибка", f"Ошибка при сохранении: {str(e)}")

def setup_calendar_frame(app):
    app.calendar_frame = ttk.Frame(app.content_frame)
    app.calendar_frame.grid(row=0, column=0, sticky="nsew")
    app.content_frame.grid_columnconfigure(0, weight=3)
    app.content_frame.grid_rowconfigure(0, weight=1)
    app.month_frames = []
    for i in range(12):
        m_frame = ttk.Frame(app.calendar_frame)
        m_frame.grid(row=i//3, column=i % 3, sticky="nsew", padx=5, pady=5)
        app.calendar_frame.grid_rowconfigure(i//3, weight=1)
        app.calendar_frame.grid_columnconfigure(i % 3, weight=1)
        app.month_frames.append(m_frame)
    print("Фреймы месяцев созданы")


def setup_employee_frame(app):
    """Sets up employee list."""
    app.employee_frame = ttk.Frame(
        app.content_frame, relief="ridge", borderwidth=2, width=600)
    app.employee_frame.grid(row=0, column=1, sticky="ns")
    app.employee_frame.grid_propagate(False)
    app.content_frame.grid_columnconfigure(1, weight=1)

    employee_scroll_frame = ttk.Frame(app.employee_frame)
    employee_scroll_frame.pack(fill="both", expand=True, padx=5, pady=5)
    employee_scroll_frame.grid_rowconfigure(0, weight=1)
    employee_scroll_frame.grid_columnconfigure(0, weight=1)

    app.employee_list = ttk.Treeview(employee_scroll_frame,
                                     columns=("Должность", "Отпуск с",
                                              "Отпуск по"),
                                     show="tree headings", height=20)
    app.employee_list.heading("#0", text="ФИО")
    app.employee_list.heading("Должность", text="Должность")
    app.employee_list.heading("Отпуск с", text="Отпуск с")
    app.employee_list.heading("Отпуск по", text="Отпуск по")
    app.employee_list.column("#0", width=200, stretch=False)
    app.employee_list.column("Должность", width=150, stretch=False)
    app.employee_list.column("Отпуск с", width=120, stretch=False)
    app.employee_list.column("Отпуск по", width=120, stretch=False)

    vsb = ttk.Scrollbar(employee_scroll_frame,
                        orient="vertical", command=app.employee_list.yview)
    app.employee_list.configure(yscrollcommand=vsb.set)
    hsb = ttk.Scrollbar(employee_scroll_frame,
                        orient="horizontal", command=app.employee_list.xview)
    app.employee_list.configure(xscrollcommand=hsb.set)

    app.employee_list.grid(row=0, column=0, sticky="nsew")
    vsb.grid(row=0, column=1, sticky="ns")
    hsb.grid(row=1, column=0, sticky="ew")
    employee_scroll_frame.grid_rowconfigure(0, weight=1)
    employee_scroll_frame.grid_columnconfigure(0, weight=1)


def setup_search_and_buttons(app):
    """Sets up search and buttons."""
    search_frame = ttk.Frame(app.employee_frame)
    search_frame.pack(fill="x", padx=5, pady=5)
    ttk.Label(search_frame, text="Поиск:").pack(side="left")
    app.search_var = tk.StringVar()
    app.search_var.trace("w", lambda *args: app.filter_employees())
    app.search_entry = ttk.Entry(search_frame, textvariable=app.search_var)
    app.search_entry.pack(side="left", fill="x", expand=True, padx=5)
    app.search_entry.bind(
        "<Button-1>", lambda event: app.search_entry.focus_set())
    clear_btn = ttk.Button(search_frame, text="X", width=2,
                           command=lambda: app.search_var.set(""))
    clear_btn.pack(side="right")

    app.add_button = ttk.Button(
        app.employee_frame, text="Добавить сотрудника", command=lambda: add_employee_dialog(app))
    app.add_button.pack(pady=5, fill="x", padx=5)

    export_frame = ttk.Frame(app.employee_frame)
    export_frame.pack(pady=5, fill="x", padx=5)
    app.export_csv_btn = ttk.Button(
        export_frame, text="Экспорт в HTML", command=lambda: export_to_csv(app))
    app.export_csv_btn.pack(pady=2, fill="x")


def setup_context_menu(app):
    """Sets up right-click menu."""
    app.employee_menu = tk.Menu(app.root, tearoff=0)
    app.employee_list.bind(
        "<Button-3>", lambda event: show_employee_menu(app, event))


def setup_ui(app):
    """Sets up full UI."""
    app.main_frame = ttk.Frame(app.root)
    app.main_frame.grid(row=0, column=0, sticky="nsew")
    app.root.grid_rowconfigure(0, weight=1)
    app.root.grid_columnconfigure(0, weight=1)

    setup_top_panel(app)

    app.content_frame = ttk.Frame(app.main_frame)
    app.content_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
    app.main_frame.grid_rowconfigure(1, weight=1)
    app.main_frame.grid_columnconfigure(0, weight=1)

    setup_calendar_frame(app)
    setup_employee_frame(app)
    setup_search_and_buttons(app)
    setup_context_menu(app)

    app.employee_list.bind(
        "<Button-3>", lambda event: show_employee_menu(app, event))


def show_employee_menu(app, event):
    """Shows employee context menu."""
    sel = app.employee_list.identify_row(event.y)
    app.employee_menu.delete(0, tk.END)

    if sel:
        app.employee_list.selection_set(sel)
        item = app.employee_list.item(sel)
        if item["text"]:
            app.employee_menu.add_command(
                label="Добавить отпуск", command=lambda: add_vacation_to_selected(app))
            app.employee_menu.add_command(
                label="Редактировать сотрудника", command=lambda: edit_employee_dialog(app))
            app.employee_menu.add_command(
                label="Удалить сотрудника", command=lambda: delete_employee(app))
        elif item["values"] and not item["text"]:
            app.employee_menu.add_command(
                label="Редактировать отпуск", command=lambda: edit_vacation_dialog(app))
            app.employee_menu.add_command(
                label="Удалить отпуск", command=lambda: delete_vacation(app))
    else:
        app.employee_menu.add_command(
            label="Добавить сотрудника", command=lambda: add_employee_dialog(app))

    app.employee_menu.post(event.x_root, event.y_root)


def add_vacation_to_selected(app):
    """Adds vacation for selected employee."""
    sel = app.employee_list.selection()
    if sel:
        item = app.employee_list.item(sel)
        if item["text"]:
            fio = item["text"]
            add_vacation_dialog(app, fio)
