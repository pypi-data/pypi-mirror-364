import statistics

def calcular_score(durations: list, decorators: set) -> int:
    """
    Calcula una puntuación de optimización basada en duración y decoradores.
    """
    if not durations:
        return 0

    avg = statistics.mean(durations)
    stddev = statistics.stdev(durations) if len(durations) > 1 else 0.0

    score = 100
    if "@smooth" not in decorators and "@jam" not in decorators:
        score -= 20
    if avg > 0.01:
        score -= min((avg * 1000), 20)
    if stddev > 0.005:
        score -= 10

    return max(0, round(score))

def formatear_tiempo(segundos: float) -> str:
    """
    Devuelve el tiempo con 6 decimales y 's' al final.
    Usa truncamiento para evitar redondeo.
    """
    trunc = int(segundos * 1_000_000) / 1_000_000
    return f"{trunc:.6f}s"

def export_filename(base: str = "smooth_export", ext: str = "csv") -> str:
    """
    Genera un nombre de archivo con timestamp.
    """
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{base}_{timestamp}.{ext}"
