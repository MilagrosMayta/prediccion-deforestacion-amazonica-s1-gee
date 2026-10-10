from __future__ import annotations

import os


def importar_ee():
    try:
        import ee
    except ImportError as exc:
        raise RuntimeError(
            "No está instalada la API de Google Earth Engine. Ejecute: python -m pip install -e ."
        ) from exc
    return ee


def autenticar():
    ee = importar_ee()
    ee.Authenticate()


def inicializar(project_id: str | None = None):
    ee = importar_ee()
    project_id = project_id or os.getenv("GEE_PROJECT_ID")
    if not project_id:
        raise ValueError(
            "Debe indicar --proyecto o definir la variable de entorno GEE_PROJECT_ID."
        )
    ee.Initialize(project=project_id)
    return ee


def diagnostico(project_id: str | None = None) -> dict:
    ee = inicializar(project_id)
    # Lectura real de una escena de Sentinel-1; si falla, el proyecto no tiene acceso.
    col = (
        ee.ImageCollection("COPERNICUS/S1_GRD")
        .filterBounds(ee.Geometry.Point([-69.2, -12.6]))
        .filterDate("2025-01-01", "2026-01-01")
        .filter(ee.Filter.eq("instrumentMode", "IW"))
        .filter(ee.Filter.listContains("transmitterReceiverPolarisation", "VV"))
        .filter(ee.Filter.listContains("transmitterReceiverPolarisation", "VH"))
        .limit(1)
    )
    n = col.size().getInfo()
    if n < 1:
        raise RuntimeError("Earth Engine inicializó pero no devolvió escenas Sentinel-1 de prueba.")
    col.first().select("VV").getInfo()
    return {"project_id": project_id or os.getenv("GEE_PROJECT_ID"), "earth_engine": "OK", "sentinel1_accesible": True}
