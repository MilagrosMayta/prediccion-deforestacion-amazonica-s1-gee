# Historial de cambios

## Sin publicar

- `descarga-masiva` cumple los requisitos del entrenamiento ConvLSTM: una carpeta de Drive por lugar, archivos `L001_01…` por fecha, solo ASCENDING + IW + GRD + VV con una única órbita relativa (se rechaza cualquier escena que no cumpla), y solo la banda VV.
- Todas las exportaciones son de 256×256 px con grilla UTM explícita (`crsTransform`); `lado_km` > 2,56 se rechaza.
- Nuevos `verificar-coregistro` y `exportar-png` (PNG gris sin ejes). Pillow pasa al extra `[local]`.
- Zonas renombradas a `L001…L004`. El catálogo cambia de formato (columna `nombre`): hay que empezar con uno nuevo.

## 0.3.0

- Nuevo `descarga-masiva`: varias zonas y años desde `config/zonas.json`, órbita relativa AUTO, carpetas de Drive por zona/año/órbita, lotes con reintentos, catálogo CSV reanudable y confirmación previa.
- Nuevo `estado`: actualiza el catálogo con el estado real de las tareas y permite reenviar las fallidas.
- Corregido: una escena compartida por dos zonas se exportaba solo para la primera.
- Corregido: la revisión de tareas existentes hacía una llamada de red por tarea.
- Corregido: `crear-features` y `resumen-xarray` trataban el nodata (-9999) como dato.
- `baseline`: opción `--grupo` para separar entrenamiento y prueba por zona; ya no falla con clases de un solo ejemplo.
- Eliminada la función `ejecutar_grafo` de SNAP, que nadie usaba.

## 0.2.0 — 2026-10-08

- Cambio de arquitectura principal a Google Earth Engine.
- Consulta de Sentinel-1 GRD con perfil homogéneo IW + VV/VH + 10 m.
- Autenticación e inicialización con proyecto de Google Cloud.
- Manifiestos JSON reproducibles.
- Exportación a Google Drive.
- Estado de tareas de Earth Engine.
- Procesamiento local opcional con rasterio.
- Baseline opcional con scikit-learn.
- Módulos experimentales para PyTorch y TensorFlow.
- Plantillas de GitHub y documentación completamente en español.
