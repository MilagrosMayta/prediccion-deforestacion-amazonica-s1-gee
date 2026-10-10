import json
import pytest
from deforest_gee.aoi import validar_aoi_spec, cargar_geojson


def test_punto_radio():
    spec = {"tipo": "punto_radio", "latitud": -12.6, "longitud": -69.2, "radio_km": 10}
    assert validar_aoi_spec(spec) == spec


def test_bbox_invalido():
    with pytest.raises(ValueError):
        validar_aoi_spec({"tipo": "bbox", "oeste": 1, "sur": 0, "este": 0, "norte": 2})


def test_geojson_feature(tmp_path):
    p = tmp_path / "a.geojson"
    p.write_text(json.dumps({"type":"Feature","properties":{},"geometry":{"type":"Point","coordinates":[-69,-12]}}), encoding="utf-8")
    assert cargar_geojson(p)["type"] == "Point"
