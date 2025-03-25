# utils.py
import tkinter as tk

class Tooltip:
    def __init__(self, widget, text, delay=500):
        self.widget = widget
        self.text = text
        self.delay = delay
        self.after_id = None
        self.tooltip = None
        self.widget.bind("<Enter>", self.on_enter)
        self.widget.bind("<Leave>", self.on_leave)

    def on_enter(self, event):
        self.after_id = self.widget.after(self.delay, lambda: self.show_tooltip(event))

    def on_leave(self, event):
        if self.after_id:
            self.widget.after_cancel(self.after_id)
            self.after_id = None
        self.hide_tooltip()

    def show_tooltip(self, event):
        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
        tk.Label(self.tooltip, text=self.text, background="yellow", relief="solid", borderwidth=1).pack()

    def hide_tooltip(self):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

def attach_tooltip(widget, text, delay=500):
    return Tooltip(widget, text, delay)

def center_window(dialog, parent):
    dialog.update_idletasks()  # Обновляем размеры диалога
    parent.update_idletasks()  # Обновляем размеры родительского окна
    parent_x = parent.winfo_x()
    parent_y = parent.winfo_y()
    parent_width = parent.winfo_width()
    parent_height = parent.winfo_height()
    dialog_width = dialog.winfo_reqwidth()
    dialog_height = dialog.winfo_reqheight()
    x = parent_x + (parent_width - dialog_width) // 2
    y = parent_y + (parent_height - dialog_height) // 2
    dialog.geometry(f"+{x}+{y}")

def validate_date(char, entry_value, action):
    """Валидация ввода даты по шаблону ДД.ММ.ГГГГ"""
    if action == "0":  # Разрешаем удаление
        return True
    # Длина строки до вставки символа — это len(entry_value) минус длина текущего символа (1)
    current_len = len(entry_value) - 1 if action == "1" else len(entry_value)
    if current_len >= 10:  # Ограничиваем длину до 10 символов
        return False
    # Разрешаем цифры в нужных позициях
    if char.isdigit():
        if current_len in [0, 1, 3, 4, 6, 7, 8, 9]:  # Позиции до ввода: ДД.ММ.ГГГГ
            return True
    # Разрешаем точки в нужных позициях
    if char == "." and current_len in [2, 5]:
        return True
    return False

def on_date_input(event):
    """Добавление точек после ввода дня и месяца"""
    widget = event.widget
    value = widget.get()
    if len(value) in [2, 5] and value[-1].isdigit() and "." not in value[-1:]:
        widget.insert(tk.END, ".")

def show_calendar(app, entry):
    top = tk.Toplevel(app.root)
    top.transient(app.root)
    top.grab_set()
    top.title("Выбрать дату")
    top.geometry("300x300")
    frame = ttk.Frame(top)
    frame.pack(expand=True, padx=10, pady=10)
    cal = Calendar(frame, selectmode="day", year=app.current_year, month=1, day=1, date_pattern="dd.mm.yyyy")
    cal.pack()
    btn_frame = ttk.Frame(frame)
    btn_frame.pack(pady=10)
    ttk.Button(btn_frame, text="Выбрать", command=lambda: set_date(), width=10).pack()

    def set_date():
        entry.delete(0, tk.END)
        entry.insert(0, cal.get_date())
        top.destroy()

    center_window(top, app.root)