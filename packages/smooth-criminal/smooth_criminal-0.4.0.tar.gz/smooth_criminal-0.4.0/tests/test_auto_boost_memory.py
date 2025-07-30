import os
import json
from pathlib import Path
from smooth_criminal.core import auto_boost
from smooth_criminal.memory import get_execution_history

LOG_PATH = Path.home() / ".smooth_criminal_log.json"

@auto_boost()
def boosted_function():
    return sum(i for i in range(1000))

def test_auto_boost_memory_logs():
    # Limpiar log antes del test si existe
    if LOG_PATH.exists():
        LOG_PATH.unlink()

    # Ejecutar función decorada
    boosted_function()

    # Comprobar si se ha creado el log
    assert LOG_PATH.exists()

    # Leer contenido
    history = get_execution_history("boosted_function")
    assert len(history) > 0

    entry = history[-1]
    assert entry["function"] == "boosted_function"
    assert entry["decorator"] in ("@smooth", "@jam", "none")  # depende del análisis
    assert isinstance(entry["duration"], float)
    assert entry["duration"] > 0
