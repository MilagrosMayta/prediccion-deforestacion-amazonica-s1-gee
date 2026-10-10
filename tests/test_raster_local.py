import pytest

np = pytest.importorskip("numpy")
rasterio = pytest.importorskip("rasterio")

from deforest_gee.local_raster import crear_features_vv_vh
from deforest_gee.xarray_tools import resumen_xarray


@pytest.fixture
def tif(tmp_path):
    vv = np.array([[-10, -9999], [-12, -8]], dtype="float32")
    vh = np.array([[-15, -9999], [-9999, -14]], dtype="float32")
    p = tmp_path / "e.tif"
    with rasterio.open(p, "w", driver="GTiff", width=2, height=2, count=2, dtype="float32", nodata=-9999) as dst:
        dst.write(vv, 1)
        dst.write(vh, 2)
    return p


def test_diferencia_conserva_nodata(tif, tmp_path):
    salida = crear_features_vv_vh(tif, tmp_path / "f.tif")
    with rasterio.open(salida) as src:
        assert src.read(3).tolist() == [[5, -9999], [-9999, 6]]


def test_resumen_ignora_nodata(tif):
    r = resumen_xarray(tif)
    assert r["min"] == -15 and r["max"] == -8
