# Decisiones técnicas

## Fuente principal

Se usa **Google Earth Engine** como plataforma de consulta y exportación.

## Colección Sentinel-1

El ID canónico de Earth Engine es `COPERNICUS/S1_GRD`. Esta cadena es obligatoria dentro de GEE. No se usa Copernicus Data Space Ecosystem.

## Perfil homogéneo

- modo: IW;
- polarizaciones: VV y VH;
- resolución: 10 m;
- producto: Sentinel-1 GRD disponible en GEE;
- órbita: configurable entre ascendente, descendente o ambas.

La colección `S1_GRD` de Earth Engine ya incluye preprocesamiento SAR realizado con Sentinel-1 Toolbox: eliminación de ruido térmico, calibración radiométrica, corrección de terreno y conversión a dB. Por ello SNAP no se ejecuta de nuevo por defecto sobre estos GeoTIFF, para evitar duplicar procesamiento.

## SNAP

SNAP se conserva como herramienta complementaria para validación técnica o para una ruta alternativa con productos crudos/SAFE si el equipo investigador decide incorporarla.
