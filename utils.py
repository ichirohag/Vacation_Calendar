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