from __future__ import annotations

from pathlib import Path


def raster_a_xarray(path: str | Path):
    try:
        import rasterio
        import xarray as xr
    except ImportError as exc:
        raise RuntimeError("Instale dependencias locales con: python -m pip install -e \".[local]\"") from exc
    with rasterio.open(path) as src:
        arr = src.read().astype("float32")
        if src.nodata is not None:
            arr[arr == src.nodata] = float("nan")
        nombres = [src.descriptions[i] or f"banda_{i+1}" for i in range(src.count)]
        da = xr.DataArray(
            arr,
            dims=("banda", "y", "x"),
            coords={"banda": nombres},
            attrs={"crs": str(src.crs), "transform": tuple(src.transform)},
            name="sentinel1",
        )
    return da


def resumen_xarray(path: str | Path) -> dict:
    da = raster_a_xarray(path)
    return {
        "dimensiones": dict(da.sizes),
        "bandas": [str(x) for x in da.coords["banda"].values.tolist()],
        "min": float(da.min(skipna=True).values),
        "max": float(da.max(skipna=True).values),
        "media": float(da.mean(skipna=True).values),
    }
