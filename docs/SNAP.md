# SNAP / ESA Sentinel Toolbox

Google Earth Engine indica que su colección Sentinel-1 GRD ya se preprocesa usando Sentinel-1 Toolbox. Por ese motivo, SNAP no forma parte del camino obligatorio de exportación de esta versión.

El repositorio incluye `deforest_gee.snap` únicamente para:

- detectar si `gpt` de SNAP está instalado;
- ejecutar, en una ruta alternativa futura, un grafo XML de SNAP sobre productos crudos.

No se debe aplicar automáticamente una segunda calibración/corrección de terreno a los GeoTIFF ya derivados de `COPERNICUS/S1_GRD` sin una justificación metodológica.
