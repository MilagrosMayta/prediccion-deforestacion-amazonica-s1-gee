import json
import pytest
from deforest_gee.config import cargar_config


def test_config_valida(tmp_path):
    p = tmp_path / "c.json"
    p.write_text(json.dumps({
        "aoi": {"tipo": "punto_radio", "latitud": -12, "longitud": -69, "radio_km": 5},
        "fecha_inicio": "2025-01-01", "fecha_fin": "2025-01-10", "orbita": "AMBAS"
    }), encoding="utf-8")
    c = cargar_config(p)
    assert c.max_resultados == 0


def test_fechas_invalidas(tmp_path):
    p = tmp_path / "c.json"
    p.write_text(json.dumps({
        "aoi": {"tipo": "punto_radio", "latitud": -12, "longitud": -69, "radio_km": 5},
        "fecha_inicio": "2025-02-01", "fecha_fin": "2025-01-01"
    }), encoding="utf-8")
    with pytest.raises(ValueError):
        cargar_config(p)
