import flet as ft
from smooth_criminal.memory import get_execution_history
from smooth_criminal.flet_app.components import info_panel, function_table, action_buttons
from smooth_criminal.flet_app.utils import calcular_score, formatear_tiempo

def main_view(page: ft.Page):
    table = function_table()
    msg = ft.Text()

    def refresh(_=None):
        history = get_execution_history()
        summary = {}
        for entry in history:
            fn = entry["function"]
            if fn not in summary:
                summary[fn] = {"durations": [], "decorators": set()}
            summary[fn]["durations"].append(entry["duration"])
            summary[fn]["decorators"].add(entry["decorator"])

        table.rows.clear()
        for fn, data in summary.items():
            avg = sum(data["durations"]) / len(data["durations"])
            score = calcular_score(data["durations"], data["decorators"])
            table.rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(fn)),
                ft.DataCell(ft.Text(", ".join(sorted(data["decorators"])))),
                ft.DataCell(ft.Text(str(len(data["durations"])))),
                ft.DataCell(ft.Text(formatear_tiempo(avg))),
                ft.DataCell(ft.Text(f"{score}/100")),
            ]))
        page.update()

    btns = action_buttons(refresh, lambda e: None, lambda e: None, lambda e: None)

    page.add(
        ft.Text("🎩 Smooth Criminal Dashboard", size=28, weight="bold", color="purple"),
        btns,
        msg,
        table
    )

    refresh()
