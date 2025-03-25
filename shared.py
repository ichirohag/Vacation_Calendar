# shared.py
from datetime import datetime

def cache_vacations(app):
    app.vacation_cache.clear()
    for emp in app.employees:
        for day_str in emp.get("vacation", []):
            day_date = datetime.strptime(day_str, "%d.%m.%Y")
            if day_date.year == app.current_year:
                date_key = day_date.strftime("%Y-%m-%d")
                if date_key not in app.vacation_cache:
                    app.vacation_cache[date_key] = []
                app.vacation_cache[date_key].append(emp["fio"])

def update_employee_list(app):
    for child in app.employee_list.get_children():
        app.employee_list.delete(child)
    search_text = app.search_var.get().lower() if hasattr(app, 'search_var') else ""
    for emp in app.employees:
        if search_text and search_text not in emp["fio"].lower() and search_text not in emp["position"].lower():
            continue
        emp_id = app.employee_list.insert("", "end", text=emp["fio"], values=(emp["position"], "", ""), open=False)
        vacations = emp.get("vacations", [])
        for vac in vacations:
            try:
                s_date = vac["start_date"]
                e_date = vac["end_date"]
                app.employee_list.insert(emp_id, "end", text="", values=("", s_date, e_date))
            except Exception:
                continue