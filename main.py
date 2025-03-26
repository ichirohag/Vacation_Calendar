from app import VacationCalendarApp
import sys
import os
import tkinter as tk
from tkinter import messagebox


sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def center_root_window(root):
    """Centers main window."""
    root.withdraw()
    root.update_idletasks()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    window_width = 1610
    window_height = 900
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")
    root.deiconify()


def main():
    """Starts app, handles errors."""
    try:
        root = tk.Tk()
        root.geometry("1610x900")
        root.resizable(False, False)
        center_root_window(root)
        app = VacationCalendarApp(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("Критическая ошибка",
                             f"Произошла непредвиденная ошибка: {str(e)}")
        raise


if __name__ == "__main__":
    main()
