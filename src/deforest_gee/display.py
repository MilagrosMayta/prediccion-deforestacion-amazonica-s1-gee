from __future__ import annotations


def mostrar_resultados(resultados: list[dict]) -> None:
    print(f"\nEscenas encontradas: {len(resultados)}\n")
    if not resultados:
        return
    print(f"{'#':>3}  {'FECHA UTC':20}  {'ORBITA':11}  {'PLATAFORMA':10}  {'ID'}")
    print("-" * 100)
    for i, r in enumerate(resultados, 1):
        fecha = (r.get("fecha_hora_utc") or "N/D")[:20]
        orb = r.get("orbita") or "N/D"
        plat = r.get("plataforma") or "N/D"
        idx = r.get("system_index") or r.get("ee_id") or "N/D"
        print(f"{i:>3}  {fecha:20}  {orb:11}  {plat:10}  {idx}")


def mostrar_tareas(tareas: list[dict]) -> None:
    if not tareas:
        print("No se encontraron tareas.")
        return
    for t in tareas:
        print(f"{t.get('state') or 'N/D':12} | {t.get('description') or 'N/D'} | {t.get('id') or 'N/D'}")
        if t.get("error_message"):
            print(f"  ERROR: {t['error_message']}")
