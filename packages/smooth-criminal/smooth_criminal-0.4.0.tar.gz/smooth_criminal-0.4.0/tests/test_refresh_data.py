from smooth_criminal.memory import get_execution_history
from smooth_criminal.flet_app.utils import calcular_score, formatear_tiempo

def test_refresh_logic(monkeypatch):
    # Simular historial con monkeypatch
    fake_history = [
        {"function": "foo", "duration": 0.001, "decorator": "@smooth"},
        {"function": "foo", "duration": 0.002, "decorator": "@smooth"},
        {"function": "bar", "duration": 0.01,  "decorator": "@jam"},
    ]

    monkeypatch.setattr("smooth_criminal.memory.get_execution_history", lambda: fake_history)

    # Procesar resumen
    resumen = {}
    for entry in get_execution_history():
        name = entry["function"]
        if name not in resumen:
            resumen[name] = {"durations": [], "decorators": set()}
        resumen[name]["durations"].append(entry["duration"])
        resumen[name]["decorators"].add(entry["decorator"])

    # Verificaciones
    assert "foo" in resumen
    assert len(resumen["foo"]["durations"]) == 2
    assert resumen["foo"]["decorators"] == {"@smooth"}

    avg = sum(resumen["foo"]["durations"]) / len(resumen["foo"]["durations"])
    score = calcular_score(resumen["foo"]["durations"], resumen["foo"]["decorators"])
    assert formatear_tiempo(avg).endswith("s")
    assert 80 <= score <= 100
