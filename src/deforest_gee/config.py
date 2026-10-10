from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from .aoi import cargar_geojson, validar_aoi_spec
from .constants import ORBITAS_VALIDAS, RESOLUCION_METROS

_FECHA = re.compile(r"^\d{4}-\d{2}-\d{2}$")


@dataclass(frozen=True)
class SearchConfig:
    aoi: dict[str, Any]
    fecha_inicio: str
    fecha_fin: str
    orbita: str = "AMBAS"
    max_resultados: int = 0  # 0 = sin límite
    escala_m: int = RESOLUCION_METROS
    crs: str | None = None  # None = UTM automático según el AOI
    orbita_relativa: int | None = None  # fija la geometría de observación (recomendado para series)
    cobertura_completa: bool = False  # True = solo escenas cuyo footprint contiene todo el AOI

    def validate(self) -> "SearchConfig":
        for nombre, valor in (("fecha_inicio", self.fecha_inicio), ("fecha_fin", self.fecha_fin)):
            if not isinstance(valor, str) or not _FECHA.match(valor):
                raise ValueError(f"{nombre} debe tener formato YYYY-MM-DD, recibido {valor!r}.")
            datetime.strptime(valor, "%Y-%m-%d")
        if self.fecha_inicio > self.fecha_fin:
            raise ValueError("La fecha de inicio no puede ser posterior a la fecha final.")
        if self.orbita not in ORBITAS_VALIDAS:
            raise ValueError(f"Órbita inválida: {self.orbita}. Use {ORBITAS_VALIDAS}.")
        if self.max_resultados < 0:
            raise ValueError("max_resultados debe ser 0 (sin límite) o mayor.")
        if self.escala_m < RESOLUCION_METROS:
            raise ValueError(f"escala_m debe ser >= {RESOLUCION_METROS} (resolución nativa de S1 GRD IW).")
        if self.crs is not None and not re.match(r"^EPSG:\d+$", self.crs):
            raise ValueError(f"crs debe tener forma 'EPSG:xxxxx', recibido {self.crs!r}.")
        validar_aoi_spec(self.aoi)
        return self


def _entero(data: dict, clave: str, defecto: int | None) -> int | None:
    valor = data.get(clave, defecto)
    if valor is None:
        return None
    if isinstance(valor, bool) or (isinstance(valor, float) and not valor.is_integer()):
        raise ValueError(f"'{clave}' debe ser un entero, recibido {valor!r}.")
    try:
        return int(valor)
    except (TypeError, ValueError):
        raise ValueError(f"'{clave}' debe ser un entero, recibido {valor!r}.") from None


def cargar_config(path: str | Path) -> SearchConfig:
    path = Path(path)
    data = json.loads(path.read_text(encoding="utf-8"))
    for clave in ("aoi", "fecha_inicio", "fecha_fin"):
        if clave not in data:
            raise ValueError(f"Falta el campo obligatorio '{clave}' en {path.name}.")
    aoi = dict(data["aoi"])
    if str(aoi.get("tipo", "")).lower() == "geojson" and "archivo" in aoi:
        ap = Path(aoi.pop("archivo"))
        if not ap.is_absolute():
            ap = (path.parent / ap).resolve()
        # La geometría viaja dentro del manifiesto: reproducible y sin rutas locales.
        aoi["geometria"] = cargar_geojson(ap)
    cfg = SearchConfig(
        aoi=aoi,
        fecha_inicio=data["fecha_inicio"],
        fecha_fin=data["fecha_fin"],
        orbita=str(data.get("orbita", "AMBAS")).upper(),
        max_resultados=_entero(data, "max_resultados", 0),
        escala_m=_entero(data, "escala_m", RESOLUCION_METROS),
        crs=data.get("crs"),
        orbita_relativa=_entero(data, "orbita_relativa", None),
        cobertura_completa=bool(data.get("cobertura_completa", False)),
    )
    return cfg.validate()
