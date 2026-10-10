# Arquitectura técnica

## Capa 1 — Adquisición en la nube

`gee_client.py` inicializa Google Earth Engine. `sentinel1.py` construye una colección homogénea Sentinel-1 y `aoi.py` define el área espacial.

## Capa 2 — Reproducibilidad

Cada consulta se materializa como un manifiesto JSON. El manifiesto conserva la configuración de búsqueda y los identificadores exactos de las escenas retornadas.

## Capa 3 — Exportación

`exporter.py` inicia tareas `Export.image.toDrive`. Cada escena se exporta con las bandas VV, VH y `angle`, recortada al AOI y a la escala configurada.

## Capa 4 — Procesamiento local

`local_raster.py` usa rasterio para inspección y para generar una tercera característica VV−VH en dB.

## Capa 5 — Modelado

`baseline.py` permite una línea base con Random Forest. Los módulos bajo `ml/` son experimentales y no deben confundirse con el modelo científico definitivo de IA generativa.
