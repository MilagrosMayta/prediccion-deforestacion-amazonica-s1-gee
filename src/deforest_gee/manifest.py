from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from . import __version__
from .aoi import centro_aoi, epsg_utm
from .constants import COLECCION_SENTINEL1, MODO_INSTRUMENTO, POLARIZACIONES, RESOLUCION_METROS
from .config import SearchConfig


def construir_manifiesto(cfg: SearchConfig, resultados: list[dict[str, Any]], project_id: str) -> dict[str, Any]:
    return {
        "version_manifiesto": 2,
        "version_software": __version__,
        "generado_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "project_id": project_id,
        "perfil_sentinel1": {
            "coleccion_gee": COLECCION_SENTINEL1,
            "mision": "Sentinel-1",
            "modo": MODO_INSTRUMENTO,
            "polarizaciones": list(POLARIZACIONES),
            "resolucion_m": RESOLUCION_METROS,
        },
        "consulta": {
            "aoi": cfg.aoi,
            "fecha_inicio": cfg.fecha_inicio,
            "fecha_fin": cfg.fecha_fin,
            "orbita": cfg.orbita,
            "orbita_relativa": cfg.orbita_relativa,
            "cobertura_completa": cfg.cobertura_completa,
            "max_resultados": cfg.max_resultados,
            "escala_m": cfg.escala_m,
            "crs": cfg.crs or epsg_utm(*centro_aoi(cfg.aoi)),
        },
        "cantidad_resultados": len(resultados),
        "resultados": resultados,
    }


def guardar_manifiesto(manifiesto: dict[str, Any], carpeta: str | Path = "outputs") -> Path:
    carpeta = Path(carpeta)
    carpeta.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S_%fZ")
    path = carpeta / f"busqueda_sentinel1_{stamp}.json"
    path.write_text(json.dumps(manifiesto, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def cargar_manifiesto(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))
