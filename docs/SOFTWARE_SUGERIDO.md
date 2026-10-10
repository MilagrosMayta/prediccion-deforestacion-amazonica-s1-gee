# Software sugerido y su uso real en el repositorio

## Python

Es el lenguaje central. Toda la CLI y la automatización están implementadas en Python.

## Google Earth Engine

Es la plataforma principal de búsqueda y exportación de Sentinel-1. La colección utilizada es `COPERNICUS/S1_GRD`, que es el identificador oficial dentro del catálogo de GEE.

## SNAP / ESA Sentinel Toolbox

Se mantiene como herramienta complementaria. GEE ya entrega `S1_GRD` con preprocesamiento realizado usando Sentinel-1 Toolbox, por lo que no se repite automáticamente sobre los productos exportados.

## rasterio

`local_raster.py` permite inspeccionar GeoTIFF y crear una característica VV−VH.

## xarray

`xarray_tools.py` convierte un GeoTIFF local en un `DataArray` para análisis multidimensional.

## geopandas

`vector_tools.py` normaliza áreas de interés vectoriales a EPSG:4326 y GeoJSON.

## scikit-learn

`baseline.py` implementa un Random Forest reproducible como línea base, una vez que existan datos etiquetados.

## PyTorch / TensorFlow

Se proporcionan autoencoders experimentales mínimos en `src/deforest_gee/ml/`. No representan todavía el modelo científico definitivo de IA generativa.
