import tkinter as tk
from tkinter import ttk
from tkcalendar import Calendar
import datetime


class Tooltip:
    def __init__(self, widget, text, delay=500):
        """Sets up tooltip for widget."""
        self.widget = widget
        self.text = text
        self.delay = delay
        self.after_id = None
        self.tooltip = None
        self.widget.bind("<Enter>", self.on_enter)
        self.widget.bind("<Leave>", self.on_leave)

    def on_enter(self, event):
        """Schedules tooltip display."""
        self.after_id = self.widget.after(
            self.delay, lambda: self.show_tooltip(event))

    def on_leave(self, event):
        """Hides tooltip on leave."""
        if self.after_id:
            self.widget.after_cancel(self.after_id)
            self.after_id = None
        self.hide_tooltip()

    def show_tooltip(self, event):
        """Shows tooltip at cursor."""
        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
        tk.Label(self.tooltip, text=self.text, background="yellow",
                 relief="solid", borderwidth=1).pack()

    def hide_tooltip(self):
        """Hides and removes tooltip."""
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None


def attach_tooltip(widget, text, delay=500):
    """Attaches tooltip to widget."""
    return Tooltip(widget, text, delay)


def center_window(dialog, parent):
    """Centers dialog over parent."""
    dialog.update_idletasks()
    parent.update_idletasks()
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
    """Validates date input."""
    if action == "0":
        return True

    current_len = len(entry_value) - 1 if action == "1" else len(entry_value)
    if current_len >= 10:
        return False
    if char.isdigit():
        if current_len in [0, 1, 3, 4, 6, 7, 8, 9]:
            return True
    if char == "." and current_len in [2, 5]:
        return True
    return False


def on_date_input(event):
    """Adds dots to date."""
    widget = event.widget
    value = widget.get()
    if len(value) in [2, 5] and value[-1].isdigit() and "." not in value[-1:]:
        widget.insert(tk.END, ".")


def show_calendar(app, entry):
    top = tk.Toplevel(app.root)
    top.transient(app.root)
    top.grab_set()
    top.title("Выбрать дату")
    
    # Устанавливаем размер и центрируем до отображения
    top.geometry("300x300")
    center_window(top, app.root)
    top.update_idletasks()  # Обновляем геометрию перед отображением

    frame = ttk.Frame(top)
    frame.pack(expand=True, padx=10, pady=10)

    today = datetime.datetime.now()
    cal = Calendar(frame, selectmode="day", year=today.year,
                   month=today.month, day=today.day, date_pattern="dd.mm.yyyy")
    cal.pack()
    btn_frame = ttk.Frame(frame)
    btn_frame.pack(pady=10)
    ttk.Button(btn_frame, text="Выбрать",
               command=lambda: set_date(), width=10).pack()

    def set_date():
        selected_date = cal.get_date()
        entry.config(validate="none")
        entry.delete(0, tk.END)
        entry.insert(0, selected_date)
        entry.config(foreground="black")
        entry.config(validate="key")
        top.destroy()
        entry.focus_set()


def is_weekend(app, date):
    """Checks if date is weekend."""
    year = str(date.year)
    return date.weekday() >= 5 or (year in app.weekends and date in app.weekends[year])


def is_holiday(app, date):
    """Checks if date is holiday."""
    year = str(date.year)
    return year in app.holidays and date in app.holidays[year]


def is_workday(app, date):
    """Checks if date is workday."""
    year = str(date.year)
    if year in app.holidays and date in app.holidays[year]:
        return False
    if is_weekend(app, date):
        return year in app.workdays and date in app.workdays[year]
    return True
