from __future__ import annotations

from pathlib import Path


def normalizar_aoi(entrada: str | Path, salida: str | Path) -> Path:
    try:
        import geopandas as gpd
    except ImportError as exc:
        raise RuntimeError("Instale dependencias locales con: python -m pip install -e \".[local]\"") from exc
    gdf = gpd.read_file(entrada)
    if gdf.empty:
        raise ValueError("El archivo vectorial no contiene geometrías.")
    if gdf.crs is None:
        raise ValueError("El archivo vectorial no tiene CRS definido.")
    gdf = gdf.to_crs("EPSG:4326")
    salida = Path(salida)
    salida.parent.mkdir(parents=True, exist_ok=True)
    gdf.to_file(salida, driver="GeoJSON")
    return salida
