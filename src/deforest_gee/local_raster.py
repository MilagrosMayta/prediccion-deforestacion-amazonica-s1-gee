from __future__ import annotations

from pathlib import Path


def _imports():
    try:
        import numpy as np
        import rasterio
    except ImportError as exc:
        raise RuntimeError(
            "Faltan dependencias locales. Instale: python -m pip install -e \".[local]\""
        ) from exc
    return np, rasterio


def inspeccionar_raster(path: str | Path) -> dict:
    _, rasterio = _imports()
    with rasterio.open(path) as src:
        return {
            "archivo": str(path),
            "crs": str(src.crs),
            "ancho": src.width,
            "alto": src.height,
            "bandas": src.count,
            "dtype": list(src.dtypes),
            "transform": tuple(src.transform),
            "bounds": tuple(src.bounds),
            "nodata": src.nodata,
        }


def crear_features_vv_vh(entrada: str | Path, salida: str | Path) -> Path:
    np, rasterio = _imports()
    entrada, salida = Path(entrada), Path(salida)
    salida.parent.mkdir(parents=True, exist_ok=True)
    with rasterio.open(entrada) as src:
        if src.count < 2:
            raise ValueError("El raster debe contener al menos las bandas VV y VH.")
        vv = src.read(1).astype("float32")
        vh = src.read(2).astype("float32")
        diferencia = vv - vh
        if src.nodata is not None:  # sin esto, nodata - nodata = 0 parecería un dato válido
            diferencia[(vv == src.nodata) | (vh == src.nodata)] = src.nodata
        profile = src.profile.copy()
        profile.update(count=3, dtype="float32", compress="deflate")
        with rasterio.open(salida, "w", **profile) as dst:
            dst.write(vv, 1)
            dst.set_band_description(1, "VV_dB")
            dst.write(vh, 2)
            dst.set_band_description(2, "VH_dB")
            dst.write(diferencia.astype(np.float32), 3)
            dst.set_band_description(3, "VV_menos_VH_dB")
    return salida
