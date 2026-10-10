from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _num(spec: dict[str, Any], clave: str) -> float:
    if clave not in spec:
        raise ValueError(f"AOI '{spec.get('tipo')}': falta el campo '{clave}'.")
    try:
        return float(spec[clave])
    except (TypeError, ValueError):
        raise ValueError(f"AOI: '{clave}' debe ser numérico, recibido {spec[clave]!r}.") from None


def _rango(valor: float, minimo: float, maximo: float, nombre: str) -> None:
    if not minimo <= valor <= maximo:
        raise ValueError(f"{nombre} fuera de rango ({minimo}..{maximo}): {valor}.")


def validar_aoi_spec(spec: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(spec, dict):
        raise ValueError("El AOI debe ser un objeto JSON con el campo 'tipo'.")
    tipo = str(spec.get("tipo", "")).lower()
    if tipo == "punto_radio":
        _rango(_num(spec, "latitud"), -90, 90, "Latitud")
        _rango(_num(spec, "longitud"), -180, 180, "Longitud")
        if _num(spec, "radio_km") <= 0:
            raise ValueError("radio_km debe ser mayor que 0.")
    elif tipo == "bbox":
        oeste, sur, este, norte = (_num(spec, k) for k in ("oeste", "sur", "este", "norte"))
        _rango(oeste, -180, 180, "oeste")
        _rango(este, -180, 180, "este")
        _rango(sur, -90, 90, "sur")
        _rango(norte, -90, 90, "norte")
        if oeste >= este or sur >= norte:
            raise ValueError("Bounding box inválido (oeste<este y sur<norte).")
    elif tipo == "geojson":
        if "geometria" in spec:
            _validar_geometria(spec["geometria"])
        elif "archivo" in spec:
            archivo = Path(spec["archivo"])
            if not archivo.exists():
                raise FileNotFoundError(f"No existe el GeoJSON: {archivo}")
        else:
            raise ValueError("AOI geojson: indique 'archivo' o 'geometria'.")
    else:
        raise ValueError("AOI no soportado. Use punto_radio, bbox o geojson.")
    return spec


def _validar_geometria(geom: Any) -> None:
    if not isinstance(geom, dict) or not geom.get("type") or not geom.get("coordinates"):
        raise ValueError("GeoJSON sin geometría válida (se espera 'type' y 'coordinates').")


def cargar_geojson(path: str | Path) -> dict[str, Any]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if data.get("type") == "Feature":
        geom = data.get("geometry")
    elif data.get("type") == "FeatureCollection":
        features = data.get("features") or []
        if len(features) != 1:
            raise ValueError("Para esta versión, un FeatureCollection debe contener exactamente 1 geometría.")
        geom = features[0].get("geometry")
    else:
        geom = data
    _validar_geometria(geom)
    return geom


def _pares(coords: Any):
    if coords and isinstance(coords[0], (int, float)):
        yield coords[0], coords[1]
    else:
        for c in coords:
            yield from _pares(c)


def centro_aoi(spec: dict[str, Any]) -> tuple[float, float]:
    """(longitud, latitud) del centro del AOI; sirve para elegir la zona UTM."""
    tipo = spec["tipo"].lower()
    if tipo == "punto_radio":
        return float(spec["longitud"]), float(spec["latitud"])
    if tipo == "bbox":
        return (float(spec["oeste"]) + float(spec["este"])) / 2, (float(spec["sur"]) + float(spec["norte"])) / 2
    geom = spec.get("geometria") or cargar_geojson(spec["archivo"])
    pts = list(_pares(geom["coordinates"]))
    lons, lats = [p[0] for p in pts], [p[1] for p in pts]
    return (min(lons) + max(lons)) / 2, (min(lats) + max(lats)) / 2


def epsg_utm(lon: float, lat: float) -> str:
    zona = int((lon + 180) // 6) + 1
    return f"EPSG:{(32600 if lat >= 0 else 32700) + zona}"


def aoi_to_ee(spec: dict[str, Any], ee):
    validar_aoi_spec(spec)
    tipo = spec["tipo"].lower()
    if tipo == "punto_radio":
        punto = ee.Geometry.Point([float(spec["longitud"]), float(spec["latitud"])])
        return punto.buffer(float(spec["radio_km"]) * 1000)
    if tipo == "bbox":
        return ee.Geometry.Rectangle([
            float(spec["oeste"]), float(spec["sur"]),
            float(spec["este"]), float(spec["norte"]),
        ])
    return ee.Geometry(spec.get("geometria") or cargar_geojson(spec["archivo"]))
