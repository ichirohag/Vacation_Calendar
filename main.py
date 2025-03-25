# main.py
import tkinter as tk
from tkinter import messagebox
from app import VacationCalendarApp

def main():
    try:
        root = tk.Tk()
        app = VacationCalendarApp(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("Критическая ошибка", f"Произошла непредвиденная ошибка: {str(e)}")
        raise

if __name__ == "__main__":
    main()