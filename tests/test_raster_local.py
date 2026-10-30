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


def _tif(p, w=256, origen=500000):
    from rasterio.transform import from_origin
    with rasterio.open(p, "w", driver="GTiff", width=w, height=256, count=1, dtype="float32", nodata=-9999,
                       crs="EPSG:32719", transform=from_origin(origen, 8800000, 10, 10)) as dst:
        dst.write(np.full((256, w), -12, dtype="float32"), 1)


def test_coregistro_detecta_desfase(tmp_path):
    from deforest_gee.imagenes import verificar_coregistro
    _tif(tmp_path / "L001_01.tif")
    _tif(tmp_path / "L001_02.tif")
    assert verificar_coregistro(tmp_path) == []
    _tif(tmp_path / "L001_03.tif", origen=500010)  # desplazado 1 px
    assert any("L001_03" in p for p in verificar_coregistro(tmp_path))


def test_png_gris_sin_adornos(tmp_path):
    Image = pytest.importorskip("PIL.Image")
    from deforest_gee.imagenes import exportar_png
    _tif(tmp_path / "L001_01.tif")
    (png,) = exportar_png(tmp_path, tmp_path / "png")
    im = Image.open(png)
    assert im.mode == "L" and im.size == (256, 256)  # sin márgenes ni ejes
