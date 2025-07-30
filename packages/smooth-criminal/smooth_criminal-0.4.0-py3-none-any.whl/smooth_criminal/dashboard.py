from collections import defaultdict
from rich.table import Table
from rich.console import Console
from smooth_criminal.memory import get_execution_history

console = Console()

def render_dashboard():
    """
    Muestra un panel con el historial de funciones ejecutadas,
    decoradores aplicados y rendimiento medio.
    """
    all_logs = get_execution_history()
    if not all_logs:
        console.print("[yellow]No hay historial de ejecuciones todavía.[/yellow]")
        return

    stats = defaultdict(lambda: {"count": 0, "total_time": 0.0, "decorators": set()})

    for entry in all_logs:
        name = entry["function"]
        stats[name]["count"] += 1
        stats[name]["total_time"] += entry["duration"]
        stats[name]["decorators"].add(entry["decorator"])

    table = Table(title="🧠 Smooth Criminal — Function Dashboard", header_style="bold magenta")
    table.add_column("Function", style="cyan", no_wrap=True)
    table.add_column("Decorator(s)", style="green")
    table.add_column("Runs", justify="right")
    table.add_column("Avg Time (s)", justify="right")

    for name, info in stats.items():
        avg_time = info["total_time"] / info["count"]
        table.add_row(
            name,
            ", ".join(sorted(info["decorators"])),
            str(info["count"]),
            f"{avg_time:.6f}"
        )

    console.print(table)
