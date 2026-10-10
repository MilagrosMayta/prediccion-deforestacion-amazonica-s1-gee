from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from . import __version__
from .baseline import entrenar_random_forest
from .config import cargar_config
from .display import mostrar_resultados, mostrar_tareas
from .exporter import iniciar_exportaciones, listar_tareas
from .gee_client import autenticar, diagnostico, inicializar
from .local_raster import crear_features_vv_vh, inspeccionar_raster
from .masivo import actualizar_estados, cargar_zonas, descarga_masiva
from .manifest import construir_manifiesto, cargar_manifiesto, guardar_manifiesto
from .selection import parsear_seleccion
from .sentinel1 import obtener_resultados
from .snap import detectar_gpt
from .vector_tools import normalizar_aoi
from .xarray_tools import resumen_xarray

LIMITE_CONFIRMACION = 10


def cmd_autenticar(args):
    autenticar()
    print("Autenticación completada. Ahora ejecute 'diagnostico' con su project_id.")


def cmd_diagnostico(args):
    info = diagnostico(args.proyecto)
    print(json.dumps(info, ensure_ascii=False, indent=2))
    print(f"SNAP GPT detectado: {detectar_gpt() or 'NO (opcional)'}")


def cmd_buscar(args):
    cfg = cargar_config(args.config)
    ee = inicializar(args.proyecto)
    resultados = obtener_resultados(ee, cfg)
    mostrar_resultados(resultados)
    if cfg.orbita == "AMBAS" or cfg.orbita_relativa is None:
        print("AVISO: para series temporales homogéneas fije 'orbita' (ASCENDENTE/DESCENDENTE) y 'orbita_relativa'.", file=sys.stderr)
    manifiesto = construir_manifiesto(cfg, resultados, args.proyecto or os.getenv("GEE_PROJECT_ID", ""))
    path = guardar_manifiesto(manifiesto, args.salida)
    print(f"\nManifiesto guardado en: {path}")


def cmd_exportar(args):
    ee = inicializar(args.proyecto)
    mani = cargar_manifiesto(args.manifiesto)
    n = len(parsear_seleccion(args.seleccionar, len(mani.get("resultados", []))))
    if n > LIMITE_CONFIRMACION and not (args.simular or args.si):
        if input(f"Se exportarán {n} escenas a Drive. ¿Continuar? [s/N] ").strip().lower() not in {"s", "si", "sí", "y"}:
            print("Cancelado.")
            return
    tareas = iniciar_exportaciones(
        ee, mani, args.seleccionar, args.carpeta_drive, escala_m=args.escala,
        simular=args.simular, omitir_existentes=not args.reexportar,
    )
    print(json.dumps(tareas, ensure_ascii=False, indent=2))
    if args.simular:
        print("\nSimulación: no se lanzó ninguna tarea.")
    else:
        print("\nLas exportaciones se ejecutan como tareas de Earth Engine. Use 'deforest-gee tareas'.")


def cmd_descarga_masiva(args):
    ee = inicializar(args.proyecto)
    def confirmar(n):
        return args.si or input(f"Se exportarán {n} escenas a Drive. ¿Continuar? [s/N] ").strip().lower() in {"s", "si", "sí", "y"}

    n = descarga_masiva(ee, cargar_zonas(args.zonas), Path(args.catalogo), zona=args.zona, anio=args.anio,
                        lote=args.lote, simular=args.simular, limite=args.limite, confirmar=confirmar)
    print(f"\n{n} escenas {'simuladas' if args.simular else 'enviadas'}. Catálogo: {args.catalogo}")


def cmd_estado(args):
    ee = inicializar(args.proyecto)
    print(json.dumps(actualizar_estados(ee, Path(args.catalogo), args.reintentar_fallidas), indent=2))
    if args.reintentar_fallidas:
        print("Las fallidas se quitaron del catálogo: ejecute descarga-masiva para reenviarlas.")


def cmd_tareas(args):
    ee = inicializar(args.proyecto)
    mostrar_tareas(listar_tareas(ee, args.limite))


def cmd_inspeccionar(args):
    print(json.dumps(inspeccionar_raster(args.archivo), ensure_ascii=False, indent=2))


def cmd_features(args):
    path = crear_features_vv_vh(args.entrada, args.salida)
    print(f"Raster de características creado: {path}")


def cmd_baseline(args):
    reporte = entrenar_random_forest(args.csv, args.etiqueta, args.modelo, args.grupo)
    print(reporte)
    print(f"Modelo guardado en: {args.modelo}")


def cmd_normalizar_aoi(args):
    path = normalizar_aoi(args.entrada, args.salida)
    print(f"AOI normalizado a EPSG:4326: {path}")


def cmd_resumen_xarray(args):
    print(json.dumps(resumen_xarray(args.archivo), ensure_ascii=False, indent=2))


def construir_parser():
    p = argparse.ArgumentParser(
        prog="deforest-gee",
        description="Sentinel-1 + Google Earth Engine para investigación de deforestación amazónica.",
    )
    p.add_argument("--verbose", action="store_true", help="Mostrar el traceback completo en errores.")
    p.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = p.add_subparsers(dest="comando", required=True)

    s = sub.add_parser("autenticar", help="Abrir el flujo de autenticación de Google Earth Engine.")
    s.add_argument("--proyecto", required=False, help="Se conserva por claridad; la autenticación se asocia a su cuenta Google.")
    s.set_defaults(func=cmd_autenticar)

    s = sub.add_parser("diagnostico", help="Comprobar inicialización y acceso a Sentinel-1 en Earth Engine.")
    s.add_argument("--proyecto", default=None, help="Project ID de Google Cloud (o variable GEE_PROJECT_ID).")
    s.set_defaults(func=cmd_diagnostico)

    s = sub.add_parser("buscar", help="Buscar Sentinel-1 según un archivo JSON de configuración.")
    s.add_argument("--proyecto", default=None, help="Project ID de Google Cloud (o variable GEE_PROJECT_ID).")
    s.add_argument("--config", required=True)
    s.add_argument("--salida", default="outputs")
    s.set_defaults(func=cmd_buscar)

    s = sub.add_parser("exportar", help="Exportar escenas de un manifiesto a Google Drive.")
    s.add_argument("--proyecto", default=None, help="Project ID de Google Cloud (o variable GEE_PROJECT_ID).")
    s.add_argument("--manifiesto", required=True)
    s.add_argument("--seleccionar", default="1", help="Ej.: 1, 1,3,5, 1-5 o todos")
    s.add_argument("--carpeta-drive", default="Sentinel1_Deforestacion")
    s.add_argument("--escala", type=int, default=None)
    s.add_argument("--simular", action="store_true", help="Mostrar qué se exportaría sin lanzar tareas.")
    s.add_argument("--si", action="store_true", help="No pedir confirmación en exportaciones grandes.")
    s.add_argument("--reexportar", action="store_true", help="No omitir escenas ya exportadas.")
    s.set_defaults(func=cmd_exportar)

    s = sub.add_parser("descarga-masiva", help="Buscar y exportar varias zonas/años, con carpetas de Drive por zona/año/órbita.")
    s.add_argument("--proyecto", default=None, help="Project ID de Google Cloud (o variable GEE_PROJECT_ID).")
    s.add_argument("--zonas", default="config/zonas.json")
    s.add_argument("--catalogo", default="outputs/catalogo.csv", help="CSV de avance; permite retomar sin repetir.")
    s.add_argument("--zona", default=None, help="Solo este código de zona.")
    s.add_argument("--anio", default=None, help="Solo este año.")
    s.add_argument("--lote", type=int, default=50, help="Escenas por lote (reintentos por lote).")
    s.add_argument("--limite", type=int, default=0, help="Máximo de escenas en esta corrida (0 = sin límite); útil para probar con 5.")
    s.add_argument("--simular", action="store_true")
    s.add_argument("--si", action="store_true", help="No pedir confirmación.")
    s.set_defaults(func=cmd_descarga_masiva)

    s = sub.add_parser("estado", help="Actualizar el catálogo con el estado real de las tareas de Earth Engine.")
    s.add_argument("--proyecto", default=None, help="Project ID de Google Cloud (o variable GEE_PROJECT_ID).")
    s.add_argument("--catalogo", default="outputs/catalogo.csv")
    s.add_argument("--reintentar-fallidas", action="store_true")
    s.set_defaults(func=cmd_estado)

    s = sub.add_parser("tareas", help="Mostrar tareas recientes de Earth Engine.")
    s.add_argument("--proyecto", default=None, help="Project ID de Google Cloud (o variable GEE_PROJECT_ID).")
    s.add_argument("--limite", type=int, default=50)
    s.set_defaults(func=cmd_tareas)

    s = sub.add_parser("inspeccionar-raster", help="Inspeccionar un GeoTIFF exportado.")
    s.add_argument("--archivo", required=True)
    s.set_defaults(func=cmd_inspeccionar)

    s = sub.add_parser("crear-features", help="Crear VV, VH y VV-VH en un nuevo GeoTIFF.")
    s.add_argument("--entrada", required=True)
    s.add_argument("--salida", required=True)
    s.set_defaults(func=cmd_features)

    s = sub.add_parser("normalizar-aoi", help="Normalizar un vector a GeoJSON EPSG:4326 con geopandas.")
    s.add_argument("--entrada", required=True)
    s.add_argument("--salida", required=True)
    s.set_defaults(func=cmd_normalizar_aoi)

    s = sub.add_parser("resumen-xarray", help="Cargar un raster como xarray y mostrar un resumen.")
    s.add_argument("--archivo", required=True)
    s.set_defaults(func=cmd_resumen_xarray)

    s = sub.add_parser("baseline", help="Entrenar un Random Forest desde un CSV etiquetado.")
    s.add_argument("--csv", required=True)
    s.add_argument("--etiqueta", required=True)
    s.add_argument("--modelo", default="outputs/random_forest.joblib")
    s.add_argument("--grupo", default=None, help="Columna (zona/bloque) para separar entrenamiento y prueba sin fuga espacial.")
    s.set_defaults(func=cmd_baseline)

    return p


def main():
    parser = construir_parser()
    args = parser.parse_args()
    try:
        args.func(args)
    except KeyboardInterrupt:
        print("\nOperación cancelada.")
        sys.exit(130)
    except Exception as exc:
        if args.verbose:
            raise
        print(f"\nERROR: {exc}", file=sys.stderr)
        sys.exit(1)
