import json
import os
from datetime import datetime
from pathlib import Path
from collections import defaultdict
import csv
import statistics

# Ruta del archivo de log
LOG_PATH = Path.home() / ".smooth_criminal_log.json"


def log_execution_stats(func_name, input_type, decorator_used, duration):
    """
    Registra estadísticas de ejecución para aprendizaje futuro.
    """
    log_entry = {
        "function": func_name,
        "input_type": str(input_type),
        "decorator": decorator_used,
        "duration": duration,
        "timestamp": datetime.utcnow().isoformat()
    }

    logs = []
    if LOG_PATH.exists():
        with open(LOG_PATH, "r", encoding="utf-8") as f:
            try:
                logs = json.load(f)
            except json.JSONDecodeError:
                logs = []

    logs.append(log_entry)

    with open(LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(logs, f, indent=2)


_ORIGINAL_GET_HISTORY = None

def get_execution_history(func_name=None):
    """
    Devuelve el historial de ejecuciones guardadas.
    Si se pasa un nombre de función, filtra por ella.
    Permite ser parcheada sin afectar a importaciones previas.
    """
    current = globals().get("get_execution_history", _ORIGINAL_GET_HISTORY)
    if _ORIGINAL_GET_HISTORY is not None and current is not _ORIGINAL_GET_HISTORY:
        try:
            return current(func_name)
        except TypeError:
            return current()

    if not LOG_PATH.exists():
        return []

    with open(LOG_PATH, "r", encoding="utf-8") as f:
        try:
            logs = json.load(f)
        except json.JSONDecodeError:
            return []

    if func_name:
        logs = [entry for entry in logs if entry["function"] == func_name]

    return logs

_ORIGINAL_GET_HISTORY = get_execution_history


def suggest_boost(func_name):
    """
    Recomienda el mejor decorador según el historial registrado.
    """
    logs = get_execution_history(func_name)
    if not logs:
        return f"No data found for function '{func_name}'."

    decor_stats = defaultdict(list)
    for entry in logs:
        decor_stats[entry["decorator"]].append(entry["duration"])

    avg_times = {
        decor: sum(times) / len(times)
        for decor, times in decor_stats.items()
    }

    best_decor = min(avg_times, key=avg_times.get)
    return f"🧠 Suggestion for '{func_name}': use [bold green]{best_decor}[/bold green] (avg {avg_times[best_decor]:.6f}s)"

def clear_execution_history():
    """
    Elimina el archivo de log del historial de ejecuciones.
    """
    if LOG_PATH.exists():
        LOG_PATH.unlink()
        return True
    return False

def export_execution_history(filepath, format="csv"):
    """
    Exporta el historial de ejecuciones a CSV o JSON.
    """
    data = get_execution_history()
    if not data:
        return False

    # Ordenar por timestamp para que los registros más recientes aparezcan primero
    try:
        data.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    except Exception:
        pass

    format = format.lower()
    if format == "json":
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    elif format == "csv":
        keys = ["function", "input_type", "decorator", "duration", "timestamp"]
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(data)
    else:
        raise ValueError("Formato no soportado: usa 'csv' o 'json'.")

    return True

def score_function(func_name):
    """
    Calcula una puntuación de optimización para la función dada.
    Rango: 0 a 100
    """
    logs = get_execution_history(func_name)
    if not logs:
        return None, "No hay registros para esta función."

    times = [entry["duration"] for entry in logs]
    decorators = {entry["decorator"] for entry in logs}
    count = len(times)
    avg = statistics.mean(times)
    stddev = statistics.stdev(times) if count > 1 else 0.0

    # Heurística de puntuación
    score = 100
    if "@smooth" not in decorators and "@jam" not in decorators:
        score -= 20
    if avg > 0.01:
        score -= min((avg * 1000), 20)
    if stddev > 0.005:
        score -= 10

    score = max(0, round(score))

    summary = f"🧠 Function: {func_name}\n" \
              f"- Executions: {count}\n" \
              f"- Avg time: {avg:.6f}s\n" \
              f"- Std dev: {stddev:.6f}s\n" \
              f"- Decorators: {', '.join(sorted(decorators))}\n"

    return score, summary
