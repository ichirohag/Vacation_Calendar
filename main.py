import tkinter as tk
from tkinter import messagebox
from app import VacationCalendarApp

def center_root_window(root):
    # Скрываем окно перед настройкой позиции
    root.withdraw()
    
    # Обновляем размеры окна, чтобы получить корректные значения ширины и высоты
    root.update_idletasks()
    
    # Получаем размеры экрана
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    
    # Задаём размеры окна (они уже есть в VacationCalendarApp, но подтверждаем здесь)
    window_width = 1610
    window_height = 900
    
    # Вычисляем координаты для центрирования
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    
    # Устанавливаем позицию и размеры окна
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")
    
    # Показываем окно после настройки
    root.deiconify()

def main():
    try:
        root = tk.Tk()
        
        # Задаём начальные размеры и фиксируем их
        root.geometry("1610x900")
        root.resizable(False, False)
        
        # Центрируем окно перед инициализацией приложения
        center_root_window(root)
        
        app = VacationCalendarApp(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("Критическая ошибка", f"Произошла непредвиденная ошибка: {str(e)}")
        raise

if __name__ == "__main__":
    main()