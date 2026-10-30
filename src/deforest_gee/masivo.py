from __future__ import annotations

import csv
import json
import math
import os
import re
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any, Callable

from .config import SearchConfig
from .constants import LADO_PX, MODO_INSTRUMENTO, PASADA, PRODUCTO, RESOLUCION_METROS
from .exporter import iniciar_exportaciones
from .sentinel1 import obtener_resultados

COLUMNAS = ["zona", "anio", "fecha_hora_utc", "system_index", "ee_id", "orbita", "orbita_relativa",
            "nombre", "carpeta_drive", "archivo", "task_id", "estado"]
REINTENTOS = 3
_CODIGO = re.compile(r"^[A-Za-z0-9_-]+$")
_FALLIDOS = {"FAILED", "CANCELLED", "CANCEL_REQUESTED"}


def bbox_km(lat: float, lon: float, lado_km: float) -> dict[str, Any]:
    h = lado_km / 2
    dlat = h / 110.574
    dlon = h / (111.320 * math.cos(math.radians(lat)))
    return {"tipo": "bbox", "oeste": round(lon - dlon, 5), "sur": round(lat - dlat, 5),
            "este": round(lon + dlon, 5), "norte": round(lat + dlat, 5)}


def cargar_zonas(path: str | Path) -> dict[str, Any]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    for k in ("fecha_inicio", "fecha_fin", "zonas"):
        if k not in data:
            raise ValueError(f"Falta '{k}' en {Path(path).name}.")
    if data.get("lado_km", 2.56) * 1000 / RESOLUCION_METROS > LADO_PX:
        raise ValueError(f"lado_km máximo: {LADO_PX * RESOLUCION_METROS / 1000} km ({LADO_PX} px a {RESOLUCION_METROS} m).")
    codigos = [z.get("codigo") for z in data["zonas"]]
    for c in codigos:
        if not isinstance(c, str) or not _CODIGO.match(c):
            raise ValueError(f"Código de zona inválido {c!r}: use solo letras, números, '_' o '-'.")
    if len(set(codigos)) != len(codigos):
        raise ValueError("Hay códigos de zona repetidos.")
    for z in data["zonas"]:
        for k, lim in (("latitud", 90), ("longitud", 180)):
            if not isinstance(z.get(k), (int, float)) or abs(z[k]) > lim:
                raise ValueError(f"Zona {z['codigo']}: '{k}' debe ser un número entre -{lim} y {lim}.")
    return data


def elegir_orbita(escenas: list[dict[str, Any]], pedida: Any, previa: int | None = None) -> int:
    """Un entero la fija; 'AUTO' reutiliza la ya usada en el catálogo o, si no hay, la más frecuente."""
    if pedida != "AUTO":
        return int(pedida)
    if previa is not None:  # misma órbita en todas las corridas: la serie no se mezcla
        return previa
    if not escenas:
        raise ValueError("Sin escenas: no se puede elegir la órbita relativa.")
    return Counter(e["orbita_relativa"] for e in escenas).most_common(1)[0][0]


def nombrar(escenas: list[dict[str, Any]], filas: dict, zona: str) -> dict[str, str]:
    """system_index -> L001_01. Lo ya catalogado conserva su nombre; lo nuevo toma su posición
    cronológica en la lista completa, o el siguiente número libre si esa posición ya está ocupada."""
    propios = {si: r["nombre"] for (z, si), r in filas.items() if z == zona}
    ocupados = set(propios.values())
    sig = max((int(n.rsplit("_", 1)[1]) for n in ocupados), default=0)
    nombres = {}
    for i, e in enumerate(escenas, 1):
        n = propios.get(e["system_index"]) or f"{zona}_{i:02d}"
        if e["system_index"] not in propios and n in ocupados:
            n = f"{zona}_{sig + 1:02d}"
        sig = max(sig, int(n.rsplit("_", 1)[1]))
        ocupados.add(n)
        nombres[e["system_index"]] = n
    return nombres


def exigir_homogeneas(escenas: list[dict[str, Any]]) -> None:
    malas = [e["system_index"] for e in escenas
             if (e["orbita"], e["modo"], e["producto"]) != (PASADA, MODO_INSTRUMENTO, PRODUCTO)
             or "VV" not in (e["polarizaciones"] or [])]
    if malas:
        raise ValueError(f"Escenas que no son {PASADA}/{MODO_INSTRUMENTO}/{PRODUCTO}/VV: {malas[:3]}")


def leer_catalogo(path: Path) -> dict[tuple[str, str], dict[str, str]]:
    """Clave (zona, system_index): la misma escena puede pertenecer a varias zonas."""
    if not path.exists():
        return {}
    with path.open(encoding="utf-8", newline="") as f:
        return {(r["zona"], r["system_index"]): r for r in csv.DictReader(f)}


def guardar_catalogo(path: Path, filas: dict[tuple[str, str], dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")  # escritura atómica: un corte no deja el CSV a medias
    with tmp.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNAS)
        w.writeheader()
        w.writerows(sorted(filas.values(), key=lambda r: (r["zona"], r["fecha_hora_utc"])))
    os.replace(tmp, path)


def _con_reintentos(fn):
    for intento in range(1, REINTENTOS + 1):
        try:
            return fn()
        except (ValueError, TypeError, KeyError):
            raise  # errores de datos/configuración: reintentar no los arregla
        except Exception as exc:
            if intento == REINTENTOS:
                raise
            espera = 5 * 2 ** intento
            print(f"  reintento {intento}/{REINTENTOS - 1} en {espera}s: {exc}", file=sys.stderr)
            time.sleep(espera)


def planificar(ee, data: dict[str, Any], catalogo: Path, zona: str | None = None, anio: str | None = None,
               lote: int = 50, limite: int = 0) -> list[dict[str, Any]]:
    """Busca escenas y devuelve los lotes pendientes (sin lanzar nada)."""
    filas = leer_catalogo(catalogo)
    plan: list[dict[str, Any]] = []
    total = 0
    for z in data["zonas"]:
        if zona and z["codigo"] != zona:
            continue
        aoi = bbox_km(z["latitud"], z["longitud"], data.get("lado_km", 2.56))
        # la pasada ASCENDENTE se fuerza aquí: no es configurable para este flujo
        cfg = SearchConfig(aoi=aoi, fecha_inicio=data["fecha_inicio"], fecha_fin=data["fecha_fin"],
                           orbita="ASCENDENTE", cobertura_completa=True).validate()
        escenas = _con_reintentos(lambda: obtener_resultados(ee, cfg))
        previas = {int(r["orbita_relativa"]) for (zc, _), r in filas.items() if zc == z["codigo"]}
        rel = elegir_orbita(escenas, data.get("orbita_relativa", "AUTO"), min(previas) if len(previas) == 1 else None)
        escenas = [e for e in escenas if e["orbita_relativa"] == rel]
        exigir_homogeneas(escenas)
        print(f"{z['codigo']}: órbita relativa {rel} ({PASADA}), {len(escenas)} escenas")
        nombres = nombrar(escenas, filas, z["codigo"])
        pend = [{**e, "nombre": nombres[e["system_index"]]} for e in escenas
                if (z["codigo"], e["system_index"]) not in filas and (not anio or e["fecha_hora_utc"][:4] == anio)]
        for i in range(0, len(pend), lote):
            trozo = pend[i:i + lote]
            if limite:
                trozo = trozo[:limite - total]
            if not trozo:
                break
            total += len(trozo)
            plan.append({"zona": z["codigo"], "rel": rel, "aoi": aoi, "escala_m": cfg.escala_m,
                         "carpeta": z["codigo"], "escenas": trozo})
        if limite and total >= limite:
            return plan
    return plan


def descarga_masiva(ee, data: dict[str, Any], catalogo: Path, zona: str | None = None, anio: str | None = None,
                    lote: int = 50, simular: bool = False, limite: int = 0,
                    confirmar: Callable[[int], bool] | None = None) -> int:
    plan = planificar(ee, data, catalogo, zona, anio, lote, limite)
    total = sum(len(p["escenas"]) for p in plan)
    if confirmar and not simular and total and not confirmar(total):
        print("Cancelado.")
        return 0
    filas = leer_catalogo(catalogo)
    for p in plan:
        mani = {"consulta": {"aoi": p["aoi"], "escala_m": p["escala_m"], "crs": None}, "resultados": p["escenas"]}
        tareas = _con_reintentos(lambda: iniciar_exportaciones(
            ee, mani, "todos", p["carpeta"], simular=simular, prefijo=p["zona"]))
        por_idx = {e["system_index"]: e for e in p["escenas"]}
        for t in tareas:
            e = por_idx[t["system_index"]]
            if not simular:  # una simulación no debe marcar escenas como enviadas
                filas[(p["zona"], e["system_index"])] = {
                    "zona": p["zona"], "anio": e["fecha_hora_utc"][:4], "fecha_hora_utc": e["fecha_hora_utc"],
                    "system_index": e["system_index"], "ee_id": e["ee_id"], "orbita": e["orbita"],
                    "orbita_relativa": p["rel"], "nombre": e["nombre"], "carpeta_drive": p["carpeta"], "archivo": t["archivo"],
                    "task_id": t["task_id"] or "", "estado": t["state"]}
        if not simular:
            guardar_catalogo(catalogo, filas)
        print(f"  {p['carpeta']}: {len(p['escenas'])} tareas ({'simuladas' if simular else 'lanzadas'})")
    return total


def actualizar_estados(ee, catalogo: Path, reintentar: bool = False) -> dict[str, int]:
    """Copia al catálogo el estado real de cada tarea. Con reintentar, las fallidas salen del
    catálogo para que la próxima descarga-masiva las vuelva a enviar."""
    filas = leer_catalogo(catalogo)
    vivas = {t.id: t.state for t in ee.batch.Task.list()}
    for k, r in list(filas.items()):
        estado = vivas.get(r["task_id"])
        if estado is None:
            continue
        if reintentar and estado in _FALLIDOS:
            del filas[k]
        else:
            r["estado"] = estado
    guardar_catalogo(catalogo, filas)
    return dict(Counter(r["estado"] for r in filas.values()))
