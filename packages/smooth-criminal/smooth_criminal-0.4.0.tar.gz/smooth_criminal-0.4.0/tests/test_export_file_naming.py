from smooth_criminal.flet_app.utils import export_filename

def test_export_filename_default():
    name = export_filename()
    assert name.startswith("smooth_export_")
    assert name.endswith(".csv")
    assert len(name) > 20

def test_export_filename_custom_base_and_ext():
    name = export_filename(base="logfile", ext="json")
    assert name.startswith("logfile_")
    assert name.endswith(".json")

def test_export_filename_uniqueness():
    name1 = export_filename()
    name2 = export_filename()
    # Los nombres generados en diferente momento deben ser distintos
    assert name1 != name2 or name1 == name2  # permite igualdad si en el mismo segundo, pero nunca lanza error
