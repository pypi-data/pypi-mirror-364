import flet as ft

def info_panel(text: str, color="blue") -> ft.Container:
    return ft.Container(
        content=ft.Text(text, color=color, size=16),
        padding=10,
        bgcolor=ft.colors.SURFACE_VARIANT,
        border_radius=10
    )

def function_table() -> ft.DataTable:
    return ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Function")),
            ft.DataColumn(ft.Text("Decorator(s)")),
            ft.DataColumn(ft.Text("Runs")),
            ft.DataColumn(ft.Text("Avg Time (s)")),
            ft.DataColumn(ft.Text("Score")),
        ],
        rows=[]
    )

def action_buttons(refresh_fn, clear_fn, export_fn, graph_fn) -> ft.Row:
    return ft.Row([
        ft.ElevatedButton("🔄 Refresh", on_click=refresh_fn, icon=ft.Icons.REFRESH),
        ft.ElevatedButton("🧼 Limpiar historial", on_click=clear_fn, icon=ft.Icons.DELETE),
        ft.ElevatedButton("💾 Exportar CSV", on_click=export_fn, icon=ft.Icons.DOWNLOAD),
        ft.ElevatedButton("📈 Ver gráfico", on_click=graph_fn, icon=ft.Icons.INSERT_CHART)
    ], spacing=15)
