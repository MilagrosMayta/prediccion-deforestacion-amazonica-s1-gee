from __future__ import annotations

from pathlib import Path

from .constants import LADO_PX
from .local_raster import _imports

VV_MIN_DB, VV_MAX_DB = -25.0, 0.0  # límites FIJOS para toda la serie: brillo comparable entre fechas


def verificar_coregistro(carpeta: str | Path) -> list[str]:
    """Problemas encontrados en los .tif de una carpeta (lista vacía = todos en la misma grilla exacta)."""
    _, rasterio = _imports()
    tifs = sorted(Path(carpeta).glob("*.tif"))
    if not tifs:
        raise ValueError(f"No hay .tif en {carpeta}.")
    problemas, ref = [], None
    for t in tifs:
        with rasterio.open(t) as src:
            firma = (str(src.crs), tuple(src.transform), src.width, src.height, src.count)
            if ref is None:
                ref = firma
            if firma != ref:
                problemas.append(f"{t.name}: grilla distinta a {tifs[0].name} ({firma} vs {ref})")
            if src.width > LADO_PX or src.height > LADO_PX:
                problemas.append(f"{t.name}: {src.width}x{src.height} supera {LADO_PX}x{LADO_PX}")
    return problemas


def exportar_png(carpeta: str | Path, salida: str | Path, vmin: float = VV_MIN_DB, vmax: float = VV_MAX_DB) -> list[Path]:
    """PNG de 1 canal (gris): solo la matriz, un píxel por píxel, sin ejes, títulos ni bordes.
    NoData sale negro (0), igual que el valor mínimo."""
    np, rasterio = _imports()
    try:
        from PIL import Image
    except ImportError as exc:
        raise RuntimeError('Falta Pillow. Instale: python -m pip install -e ".[local]"') from exc
    problemas = verificar_coregistro(carpeta)
    if problemas:
        raise ValueError("No se generan PNG: " + "; ".join(problemas))
    salida = Path(salida)
    salida.mkdir(parents=True, exist_ok=True)
    creados = []
    for t in sorted(Path(carpeta).glob("*.tif")):
        with rasterio.open(t) as src:
            vv = src.read(1).astype("float32")
            invalido = ~np.isfinite(vv) if src.nodata is None else (vv == src.nodata) | ~np.isfinite(vv)
        img = np.clip((vv - vmin) / (vmax - vmin), 0, 1) * 255
        img[invalido] = 0
        destino = salida / f"{t.stem}.png"
        Image.fromarray(img.round().astype("uint8"), mode="L").save(destino)
        creados.append(destino)
    return creados
