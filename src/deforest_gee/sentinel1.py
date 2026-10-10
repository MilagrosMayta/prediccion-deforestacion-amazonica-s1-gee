from __future__ import annotations

import sys
from datetime import date, datetime, timezone, timedelta
from typing import Any

from .aoi import aoi_to_ee
from .constants import COLECCION_SENTINEL1, MODO_INSTRUMENTO, RESOLUCION_METROS
from .config import SearchConfig

VENTANA_DIAS = 31  # getInfo() falla con >5000 elementos; se consulta por ventanas


def _filtrar(ee, cfg: SearchConfig, region):
    col = (
        ee.ImageCollection(COLECCION_SENTINEL1)
        .filterBounds(region)
        .filter(ee.Filter.eq("instrumentMode", MODO_INSTRUMENTO))
        .filter(ee.Filter.eq("resolution_meters", RESOLUCION_METROS))
        .filter(ee.Filter.listContains("transmitterReceiverPolarisation", "VV"))
        .filter(ee.Filter.listContains("transmitterReceiverPolarisation", "VH"))
    )
    if cfg.orbita == "ASCENDENTE":
        col = col.filter(ee.Filter.eq("orbitProperties_pass", "ASCENDING"))
    elif cfg.orbita == "DESCENDENTE":
        col = col.filter(ee.Filter.eq("orbitProperties_pass", "DESCENDING"))
    if cfg.orbita_relativa is not None:
        col = col.filter(ee.Filter.eq("relativeOrbitNumber_start", cfg.orbita_relativa))
    if cfg.cobertura_completa:
        col = col.filter(ee.Filter.contains(leftField=".geo", rightValue=region))
    return col


def construir_coleccion(ee, cfg: SearchConfig, inicio: str | None = None, fin_exclusiva: str | None = None):
    region = aoi_to_ee(cfg.aoi, ee)
    if fin_exclusiva is None:
        fin_exclusiva = (datetime.strptime(cfg.fecha_fin, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")
    col = _filtrar(ee, cfg, region).filterDate(inicio or cfg.fecha_inicio, fin_exclusiva)
    return col.sort("system:time_start")


def _ventanas(fecha_inicio: str, fecha_fin: str) -> list[tuple[str, str]]:
    """Ventanas [inicio, fin) consecutivas que cubren fecha_inicio..fecha_fin inclusive."""
    ini = date.fromisoformat(fecha_inicio)
    fin = date.fromisoformat(fecha_fin) + timedelta(days=1)
    salida = []
    while ini < fin:
        sig = min(ini + timedelta(days=VENTANA_DIAS), fin)
        salida.append((ini.isoformat(), sig.isoformat()))
        ini = sig
    return salida


def _iso_utc(ms: int | float | None) -> str | None:
    if ms is None:
        return None
    return datetime.fromtimestamp(float(ms) / 1000, tz=timezone.utc).isoformat().replace("+00:00", "Z")


def _resumir(feature: dict[str, Any]) -> dict[str, Any]:
    props = feature.get("properties", {})
    return {
        "ee_id": feature.get("id"),
        "system_index": props.get("system:index"),
        "fecha_hora_utc": _iso_utc(props.get("system:time_start")),
        "plataforma": props.get("platform_number"),
        "modo": props.get("instrumentMode"),
        "producto": props.get("productType"),
        "resolucion_m": props.get("resolution_meters"),
        "polarizaciones": props.get("transmitterReceiverPolarisation"),
        "orbita": props.get("orbitProperties_pass"),
        "orbita_absoluta": props.get("orbitNumber_start"),
        "orbita_relativa": props.get("relativeOrbitNumber_start"),
        "mission_data_take_id": props.get("missionDataTakeID"),
    }


def obtener_resultados(ee, cfg: SearchConfig) -> list[dict[str, Any]]:
    """Todas las escenas del rango, en orden cronológico. Si max_resultados > 0
    y se supera, se conservan las MÁS RECIENTES y se avisa por stderr."""
    resultados: list[dict[str, Any]] = []
    for ini, fin in _ventanas(cfg.fecha_inicio, cfg.fecha_fin):
        info = construir_coleccion(ee, cfg, ini, fin).getInfo()
        resultados.extend(_resumir(f) for f in info.get("features", []))
    resultados.sort(key=lambda r: r["fecha_hora_utc"] or "")
    if cfg.max_resultados and len(resultados) > cfg.max_resultados:
        print(
            f"AVISO: {len(resultados)} escenas encontradas; se conservan las {cfg.max_resultados} más recientes "
            "(max_resultados). Use 0 para no limitar.",
            file=sys.stderr,
        )
        resultados = resultados[-cfg.max_resultados:]
    return resultados
