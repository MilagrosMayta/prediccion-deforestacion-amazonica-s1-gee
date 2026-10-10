# Validación de la versión 0.2.0

## Validaciones locales incluidas

- compilación sintáctica del paquete Python;
- validación de configuraciones;
- construcción de especificaciones AOI;
- selección de índices y rangos;
- serialización de manifiestos;
- pruebas unitarias que no requieren conexión ni credenciales.

## Validaciones que requieren una cuenta real

Deben ejecutarse en una PC del proyecto:

```cmd
deforest-gee autenticar --proyecto TU_PROJECT_ID
deforest-gee diagnostico --proyecto TU_PROJECT_ID
deforest-gee buscar --proyecto TU_PROJECT_ID --config config\busqueda.ejemplo.json
deforest-gee exportar --proyecto TU_PROJECT_ID --manifiesto outputs\ARCHIVO.json --seleccionar 1 --carpeta-drive Sentinel1_Deforestacion
deforest-gee tareas --proyecto TU_PROJECT_ID
```

Una validación completa se considera aprobada cuando una escena Sentinel-1 se exporta correctamente como GeoTIFF a Google Drive y su tarea termina en estado `COMPLETED`.
