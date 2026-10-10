import pytest

from deforest_gee import masivo
from deforest_gee.config import SearchConfig
from deforest_gee.masivo import (bbox_km, carpeta_drive, cargar_zonas, descarga_masiva, elegir_orbita,
                                 guardar_catalogo, leer_catalogo)


def test_bbox_30km_valido():
    aoi = bbox_km(-11.4351, -69.6793, 30)
    SearchConfig(aoi=aoi, fecha_inicio="2018-01-01", fecha_fin="2025-12-31").validate()
    assert 0.26 < aoi["norte"] - aoi["sur"] < 0.28


def test_auto_elige_la_mas_frecuente_y_respeta_la_previa():
    esc = [{"orbita_relativa": r} for r in (135, 135, 33)]
    assert elegir_orbita(esc, "AUTO") == 135
    assert elegir_orbita(esc, "AUTO", previa=33) == 33
    assert elegir_orbita(esc, 33) == 33
    with pytest.raises(ValueError):
        elegir_orbita([], "AUTO")


def test_carpeta_y_catalogo_atomico(tmp_path):
    assert carpeta_drive("MD_IB_01", "2019", 3) == "S1_MD_IB_01_2019_R003"
    fila = {"zona": "A", "anio": "2019", "fecha_hora_utc": "x", "system_index": "s1", "ee_id": "e", "orbita": "ASC",
            "orbita_relativa": 3, "carpeta_drive": "c", "archivo": "s1", "task_id": "t", "estado": "READY"}
    guardar_catalogo(tmp_path / "c.csv", {("A", "s1"): fila})
    assert set(leer_catalogo(tmp_path / "c.csv")) == {("A", "s1")}
    assert not (tmp_path / "c.csv.tmp").exists()


def test_zonas_ejemplo_cargan():
    assert len(cargar_zonas("config/zonas.json")["zonas"]) == 4


@pytest.mark.parametrize("zona", [{"codigo": "mal codigo", "latitud": 0, "longitud": 0},
                                  {"codigo": "OK", "latitud": 99, "longitud": 0}])
def test_zona_invalida(tmp_path, zona):
    p = tmp_path / "z.json"
    p.write_text('{"fecha_inicio":"2018-01-01","fecha_fin":"2018-02-01","zonas":[%s]}' % __import__("json").dumps(zona))
    with pytest.raises(ValueError):
        cargar_zonas(p)


def _escena(i, anio="2019", rel=3):
    return {"ee_id": f"COPERNICUS/S1_GRD/{i}", "system_index": i, "fecha_hora_utc": f"{anio}-01-{i[-2:]}T00:00:00Z",
            "orbita": "ASCENDING", "orbita_relativa": rel}


@pytest.fixture
def falso_ee(monkeypatch):
    """Dos zonas que ven las MISMAS escenas (misma pasada de satélite) + una de otra órbita."""
    escenas = [_escena("S_01"), _escena("S_02"), _escena("S_03"), _escena("O_04", rel=9)]
    llamadas = []
    monkeypatch.setattr(masivo, "obtener_resultados", lambda ee, cfg: list(escenas))

    def exportar(ee, mani, sel, carpeta, simular=False, prefijo="", **kw):
        llamadas.append((prefijo, carpeta, [e["system_index"] for e in mani["resultados"]]))
        return [{"system_index": e["system_index"], "archivo": e["system_index"], "task_id": "t", "state": "READY"}
                for e in mani["resultados"]]

    monkeypatch.setattr(masivo, "iniciar_exportaciones", exportar)
    return llamadas


DATA = {"fecha_inicio": "2019-01-01", "fecha_fin": "2019-12-31", "orbita_relativa": "AUTO", "zonas": [
    {"codigo": "A", "latitud": -8.3, "longitud": -74.8}, {"codigo": "B", "latitud": -8.6, "longitud": -74.3}]}


def test_dos_zonas_con_la_misma_escena_se_exportan_ambas(falso_ee, tmp_path):
    cat = tmp_path / "c.csv"
    assert descarga_masiva(None, DATA, cat) == 6  # 3 escenas x 2 zonas; la de otra órbita no entra
    assert {(p, c) for p, c, _ in falso_ee} == {("A", "S1_A_2019_R003"), ("B", "S1_B_2019_R003")}
    assert len(leer_catalogo(cat)) == 6


def test_reanudar_no_repite_y_limite_corta(falso_ee, tmp_path):
    cat = tmp_path / "c.csv"
    assert descarga_masiva(None, DATA, cat, limite=2) == 2
    assert descarga_masiva(None, DATA, cat) == 4
    assert descarga_masiva(None, DATA, cat) == 0


def test_simular_y_cancelar_no_escriben_catalogo(falso_ee, tmp_path):
    cat = tmp_path / "c.csv"
    assert descarga_masiva(None, DATA, cat, simular=True) == 6
    assert descarga_masiva(None, DATA, cat, confirmar=lambda n: False) == 0
    assert not cat.exists()
