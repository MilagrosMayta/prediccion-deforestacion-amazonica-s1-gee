# Instalación y uso

## 1. Preparar Python

```cmd
python --version
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -e ".[local,ml,dev]"
```

## 2. Registrar y habilitar Earth Engine

El usuario debe disponer de acceso a Google Earth Engine y un `project_id` válido de Google Cloud asociado al uso de Earth Engine.

## 3. Autenticación

```cmd
deforest-gee autenticar --proyecto TU_PROJECT_ID
```

## 4. Diagnóstico

```cmd
deforest-gee diagnostico --proyecto TU_PROJECT_ID
```

## 5. Buscar Sentinel-1

```cmd
deforest-gee buscar --proyecto TU_PROJECT_ID --config config\busqueda.ejemplo.json
```

## 6. Exportar una escena

```cmd
deforest-gee exportar --proyecto TU_PROJECT_ID --manifiesto outputs\busqueda_sentinel1_XXXX.json --seleccionar 1 --carpeta-drive Sentinel1_Deforestacion
```

## 7. Revisar estado

```cmd
deforest-gee tareas --proyecto TU_PROJECT_ID
```

## 8. Procesamiento local opcional

```cmd
deforest-gee inspeccionar-raster --archivo ruta\imagen.tif
```

```cmd
deforest-gee crear-features --entrada ruta\imagen.tif --salida data\processed\imagen_features.tif
```
