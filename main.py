import sys
import os
import tkinter as tk
from tkinter import messagebox

# Устанавливаем путь к директории исполняемого файла
if getattr(sys, 'frozen', False):
    BASE_PATH = os.path.dirname(sys.executable)
else:
    BASE_PATH = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_PATH)

try:
    from app import VacationCalendarApp
except ModuleNotFoundError as e:
    messagebox.showerror("Ошибка", f"Не удалось найти модуль 'app': {str(e)}")
    sys.exit(1)

def center_root_window(root):
    """Centers main window."""
    root.withdraw()
    root.update_idletasks()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    window_width = 1200  # Обновите под текущий размер
    window_height = 800
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")
    root.deiconify()

def main():
    """Starts app, handles errors."""
    try:
        root = tk.Tk()
        root.geometry("1200x800")  # Используем размер из app.py
        center_root_window(root)
        app = VacationCalendarApp(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("Критическая ошибка", f"Произошла непредвиденная ошибка: {str(e)}")
        raise

if __name__ == "__main__":
    main()