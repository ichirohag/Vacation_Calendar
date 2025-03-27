
from datetime import datetime, timedelta
from utils import is_holiday


def cache_vacations(app):
    """Caches vacation days excluding holidays."""
    app.vacation_cache.clear()
    for emp in app.employees:
        vacation_days = emp.get("vacation", [])
        for day_str in vacation_days:
            try:
                day_date = datetime.strptime(day_str, "%d.%m.%Y")
                if day_date.year == app.current_year:
                    date_key = day_date.strftime("%Y-%m-%d")
                    if date_key not in app.vacation_cache:
                        app.vacation_cache[date_key] = []
                    if emp["fio"] not in app.vacation_cache[date_key]:
                        app.vacation_cache[date_key].append(emp["fio"])
            except Exception as e:
                print(
                    f"Ошибка при кэшировании отпуска для {emp['fio']}: {str(e)}")


def update_employee_list(app):
    """Updates employee list UI."""
    for child in app.employee_list.get_children():
        app.employee_list.delete(child)
    search_text = app.search_var.get().lower() if hasattr(app, 'search_var') else ""
    for emp in app.employees:
        if search_text and search_text not in emp["fio"].lower() and search_text not in emp["position"].lower():
            continue
        emp_id = app.employee_list.insert(
            "", "end", text=emp["fio"], values=(emp["position"], "", ""), open=False)
        vacations = emp.get("vacations", {})
        if isinstance(vacations, list):
            for vac in vacations:
                try:
                    s_date = vac["start_date"]
                    e_date = vac["end_date"]
                    app.employee_list.insert(
                        emp_id, "end", text="", values=("", s_date, e_date))
                except Exception:
                    continue
        elif isinstance(vacations, dict):
            for year, vac_list in vacations.items():
                for vac in vac_list:
                    try:
                        s_date = vac["start_date"]
                        e_date = vac["end_date"]
                        adjusted_mark = " ⚠" if vac.get(
                            "adjusted", False) else ""
                        app.employee_list.insert(emp_id, "end", text="", values=(
                            "", s_date + adjusted_mark, e_date))
                    except Exception:
                        continue
