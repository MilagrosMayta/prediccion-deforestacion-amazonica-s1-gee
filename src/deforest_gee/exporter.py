from __future__ import annotations

import re
from typing import Any

from .aoi import aoi_to_ee, centro_aoi, epsg_utm
from .constants import BANDAS_EXPORTACION, NODATA, RESOLUCION_METROS
from .selection import parsear_seleccion

_ACTIVOS = {"READY", "RUNNING", "COMPLETED"}


def _nombre_seguro(texto: str) -> str:
    texto = re.sub(r"[^A-Za-z0-9_.-]+", "_", texto)
    return texto[:100]


def _descripciones_existentes(ee) -> set[str]:
    # Task.list() ya trae estado y descripción; .status() haría una llamada de red por tarea.
    return {(t.config or {}).get("description") for t in ee.batch.Task.list() if t.state in _ACTIVOS}


def iniciar_exportaciones(
    ee,
    manifiesto: dict[str, Any],
    seleccion: str,
    carpeta_drive: str,
    escala_m: int | None = None,
    max_pixels: float = 1e10,
    simular: bool = False,
    omitir_existentes: bool = True,
    prefijo: str = "",
) -> list[dict[str, Any]]:
    resultados = manifiesto.get("resultados", [])
    indices = parsear_seleccion(seleccion, len(resultados))
    consulta = manifiesto["consulta"]
    aoi_spec = consulta["aoi"]
    region = aoi_to_ee(aoi_spec, ee)
    escala = int(escala_m or consulta.get("escala_m", RESOLUCION_METROS))
    if escala < RESOLUCION_METROS:
        raise ValueError(f"La escala debe ser >= {RESOLUCION_METROS} m.")
    # Mismo CRS para todas las escenas: requisito para apilar series temporales.
    crs = consulta.get("crs") or epsg_utm(*centro_aoi(aoi_spec))
    existentes = _descripciones_existentes(ee) if omitir_existentes and not simular else set()

    tareas = []
    for idx in indices:
        escena = resultados[idx]
        ee_id = escena.get("ee_id")
        if not ee_id:
            raise ValueError(f"La escena {idx+1} no contiene ee_id.")
        nombre = _nombre_seguro(escena.get("system_index") or f"sentinel1_{idx+1}")
        # prefijo (zona): dos zonas con la misma escena no deben tomarse por duplicadas
        descripcion = (f"S1_{prefijo}_{nombre}" if prefijo else f"S1_{nombre}")[:100]
        info = {
            "indice": idx + 1,
            "ee_id": ee_id,
            "system_index": escena.get("system_index"),
            "carpeta_drive": carpeta_drive,
            "archivo": nombre,
            "crs": crs,
            "escala_m": escala,
        }
        if descripcion in existentes:
            tareas.append({**info, "task_id": None, "state": "OMITIDA_YA_EXPORTADA"})
            continue
        if simular:
            tareas.append({**info, "task_id": None, "state": "SIMULADA"})
            continue
        # unmask: fuera del AOI el píxel vale NODATA (declarado en el GeoTIFF), no un 0 ambiguo.
        image = ee.Image(ee_id).select(list(BANDAS_EXPORTACION)).toFloat().clip(region).unmask(NODATA, False)
        task = ee.batch.Export.image.toDrive(
            image=image,
            description=descripcion,
            folder=carpeta_drive,
            fileNamePrefix=nombre,
            region=region,
            scale=escala,
            crs=crs,
            maxPixels=max_pixels,
            fileFormat="GeoTIFF",
            formatOptions={"noData": NODATA},
        )
        task.start()
        status = task.status()
        tareas.append({**info, "task_id": status.get("id"), "state": status.get("state")})
    return tareas


def listar_tareas(ee, limite: int = 50) -> list[dict[str, Any]]:
    salida = []
    for task in ee.batch.Task.list()[:limite]:
        st = task.status()
        salida.append({
            "id": st.get("id"),
            "state": st.get("state"),
            "description": st.get("description"),
            "error_message": st.get("error_message"),
        })
    return salida
