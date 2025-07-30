import os
import json
import csv
from pathlib import Path
from smooth_criminal.core import auto_boost
from smooth_criminal.memory import export_execution_history, LOG_PATH

@auto_boost()
def export_test_func():
    return sum(i for i in range(1000))

def test_export_to_csv_and_json(tmp_path):
    # Ejecutar función varias veces para llenar historial
    for _ in range(2):
        export_test_func()

    # Rutas de exportación temporales
    csv_path = tmp_path / "export.csv"
    json_path = tmp_path / "export.json"

    # Exportar a CSV
    result_csv = export_execution_history(csv_path, format="csv")
    assert result_csv
    assert csv_path.exists()

    # Comprobar contenido del CSV
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        assert len(rows) >= 1
        assert "function" in rows[0]
        assert rows[0]["function"] == "export_test_func"

    # Exportar a JSON
    result_json = export_execution_history(json_path, format="json")
    assert result_json
    assert json_path.exists()

    # Comprobar contenido del JSON
    with open(json_path, encoding='utf-8') as f:
        data = json.load(f)
        assert isinstance(data, list)
        assert any(entry["function"] == "export_test_func" for entry in data)
