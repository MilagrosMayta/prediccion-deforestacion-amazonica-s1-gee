import json
import pytest
from deforest_gee.aoi import epsg_utm, centro_aoi, validar_aoi_spec
from deforest_gee.config import cargar_config
from deforest_gee.exporter import iniciar_exportaciones
from deforest_gee.selection import parsear_seleccion
from deforest_gee.sentinel1 import _ventanas


def test_utm_madre_de_dios():
    assert epsg_utm(-69.2, -12.6) == "EPSG:32719"


def test_bbox_fuera_de_rango():
    with pytest.raises(ValueError):
        validar_aoi_spec({"tipo": "bbox", "oeste": -500, "sur": 0, "este": 500, "norte": 1})


def test_falta_clave_con_mensaje():
    with pytest.raises(ValueError, match="longitud"):
        validar_aoi_spec({"tipo": "punto_radio", "latitud": 1, "radio_km": 1})


def test_fecha_sin_ceros_rechazada(tmp_path):
    p = tmp_path / "c.json"
    p.write_text(json.dumps({"aoi": {"tipo": "punto_radio", "latitud": -12, "longitud": -69, "radio_km": 5},
                             "fecha_inicio": "2025-1-1", "fecha_fin": "2025-01-10"}), encoding="utf-8")
    with pytest.raises(ValueError, match="YYYY-MM-DD"):
        cargar_config(p)


def test_geojson_se_incrusta(tmp_path):
    (tmp_path / "a.geojson").write_text(json.dumps({"type": "Polygon", "coordinates": [[[-69, -12], [-68, -12], [-68, -11], [-69, -12]]]}), encoding="utf-8")
    p = tmp_path / "c.json"
    p.write_text(json.dumps({"aoi": {"tipo": "geojson", "archivo": "a.geojson"},
                             "fecha_inicio": "2025-01-01", "fecha_fin": "2025-01-10"}), encoding="utf-8")
    cfg = cargar_config(p)
    assert "archivo" not in cfg.aoi and cfg.aoi["geometria"]["type"] == "Polygon"
    assert centro_aoi(cfg.aoi) == (-68.5, -11.5)


def test_seleccion_negativa_mensaje():
    with pytest.raises(ValueError, match="Formato"):
        parsear_seleccion("-3", 5)


def test_ventanas_cubren_rango():
    v = _ventanas("2025-01-01", "2025-03-31")
    assert v[0][0] == "2025-01-01" and v[-1][1] == "2025-04-01"
    assert all(a[1] == b[0] for a, b in zip(v, v[1:]))


def test_existentes_se_leen_sin_llamar_status():
    from deforest_gee.exporter import _descripciones_existentes

    class T:
        def __init__(self, d, state):
            self.config, self.state = {"description": d}, state

        def status(self):
            raise AssertionError("status() hace una llamada de red por tarea")

    class EE:
        class batch:
            class Task:
                list = staticmethod(lambda: [T("A", "RUNNING"), T("B", "FAILED")])

    assert _descripciones_existentes(EE) == {"A"}


def test_exportar_simulado_no_llama_ee():
    class Boom:
        def __getattr__(self, n):
            raise AssertionError("no debe usarse en simulación: " + n)

    class EE:
        class Geometry:
            @staticmethod
            def Point(c):
                class P:
                    def buffer(self, m): return "region"
                return P()
        batch = Boom()
        Image = Boom()

    mani = {"consulta": {"aoi": {"tipo": "punto_radio", "latitud": -12.6, "longitud": -69.2, "radio_km": 1}},
            "resultados": [{"ee_id": "COPERNICUS/S1_GRD/X", "system_index": "X"}]}
    t = iniciar_exportaciones(EE, mani, "todos", "carpeta", simular=True)
    assert t[0]["state"] == "SIMULADA" and t[0]["crs"] == "EPSG:32719"
