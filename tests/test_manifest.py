from deforest_gee.config import SearchConfig
from deforest_gee.manifest import construir_manifiesto


def test_manifest_profile():
    cfg = SearchConfig(
        aoi={"tipo":"punto_radio","latitud":-12,"longitud":-69,"radio_km":5},
        fecha_inicio="2025-01-01", fecha_fin="2025-01-10"
    ).validate()
    m = construir_manifiesto(cfg, [{"ee_id":"x"}], "proyecto")
    assert m["perfil_sentinel1"]["mision"] == "Sentinel-1"
    assert m["cantidad_resultados"] == 1
