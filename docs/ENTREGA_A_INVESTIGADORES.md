# Entrega a investigadores principales

## Qué revisar primero

1. `README.md` — propósito y uso general.
2. `docs/DECISIONES_TECNICAS.md` — decisiones metodológicas.
3. `config/busqueda.ejemplo.json` — parámetros concretos de consulta.
4. `src/deforest_gee/sentinel1.py` — filtros Sentinel-1.
5. `src/deforest_gee/exporter.py` — exportación.
6. `VALIDACION.md` — qué se probó y qué requiere credenciales.

## Puntos que el equipo debe aprobar

- AOI definitivo.
- periodo histórico.
- uso conjunto o separado de órbitas ascendentes/descendentes.
- escala de exportación.
- estrategia de etiquetado de deforestación.
- definición científica del modelo de predicción y del componente de IA generativa.

## Qué no debe asumirse todavía

La presencia de módulos PyTorch/TensorFlow no significa que el modelo científico final esté definido. Son componentes experimentales para una fase posterior.
