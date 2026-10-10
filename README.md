# Predicción de la deforestación amazónica con Sentinel-1 y Google Earth Engine

Repositorio de investigación para la adquisición, filtrado, exportación y preparación inicial de datos **Sentinel-1 SAR** orientados al proyecto **“Predicción de la deforestación amazónica usando imágenes satelitales e IA generativa”**.

## Objetivo de esta versión

Esta versión prioriza un flujo reproducible por **línea de comandos** usando Python + Google Earth Engine (GEE). El programa permite:

- autenticarse e inicializar Earth Engine con un proyecto de Google Cloud;
- definir un área de interés por punto+radio, bounding box o GeoJSON;
- consultar escenas Sentinel-1 GRD;
- restringir la búsqueda a modo IW, polarización VV+VH, resolución de 10 m y órbita ascendente/descendente/ambas;
- guardar un manifiesto JSON reproducible de cada búsqueda;
- iniciar exportaciones GeoTIFF a Google Drive;
- revisar el estado de las tareas de exportación;
- inspeccionar GeoTIFF localmente y derivar una banda `VV_menos_VH`;
- preparar un baseline clásico con scikit-learn;
- dejar módulos experimentales separados para PyTorch y TensorFlow.

## Aclaración importante: Sentinel-1 y el identificador `COPERNICUS/S1_GRD`

El software **no usa Copernicus Data Space Ecosystem**. Google Earth Engine identifica su colección oficial de Sentinel-1 GRD con el nombre técnico:

```text
COPERNICUS/S1_GRD
```

Ese texto es el **ID obligatorio del catálogo de Earth Engine** para acceder a Sentinel-1 GRD; no significa que el programa esté usando la API o el portal Copernicus Data Space. Los datos siguen correspondiendo a la misión Sentinel-1.

## Arquitectura general

```text
Sentinel-1 SAR
      ↓
Google Earth Engine
      ↓
Filtro homogéneo: IW + VV/VH + 10 m + órbita
      ↓
Manifiesto JSON de búsqueda
      ↓
Exportación GeoTIFF a Google Drive
      ↓
Python local
      ↓
rasterio / xarray / geopandas
      ↓
scikit-learn (baseline)
      ↓
PyTorch o TensorFlow (etapas posteriores)
```

## Software contemplado

| Herramienta | Función en el proyecto |
|---|---|
| Python | Lenguaje principal y CLI |
| Google Earth Engine | Consulta, filtrado y exportación de Sentinel-1 |
| SNAP / ESA Sentinel Toolbox | Validación SAR y procesamiento alternativo de productos crudos, no duplicado sobre GEE por defecto |
| rasterio | Lectura/escritura de GeoTIFF |
| xarray | Manejo de arreglos y series multidimensionales |
| geopandas | Manejo de AOI y vectores locales |
| scikit-learn | Modelos base y comparación inicial |
| PyTorch | Modelos profundos/experimentales posteriores |
| TensorFlow | Alternativa de modelado profundo/experimental |

## Requisitos

- Windows 10/11, Linux o macOS.
- Python **3.11 o superior**.
- Una cuenta Google con acceso a Earth Engine.
- Un proyecto de Google Cloud habilitado para Earth Engine.
- Git, si se trabajará colaborativamente.

## Instalación rápida en Windows

```cmd
cd "C:\RUTA\prediccion-deforestacion-amazonica-s1-gee"
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -e .
```

Para instalar también herramientas locales de raster/vector y ML clásico:

```cmd
python -m pip install -e ".[local,ml]"
```

PyTorch y TensorFlow se mantienen como extras opcionales por su peso:

```cmd
python -m pip install -e ".[torch]"
```

o

```cmd
python -m pip install -e ".[tensorflow]"
```

## Primer uso

### 1. Autenticación

```cmd
deforest-gee autenticar --proyecto TU_PROJECT_ID
```

### 2. Diagnóstico

```cmd
deforest-gee diagnostico --proyecto TU_PROJECT_ID
```

### 3. Búsqueda de prueba

```cmd
deforest-gee buscar --proyecto TU_PROJECT_ID --config config\busqueda.ejemplo.json
```

El programa generará un archivo parecido a:

```text
outputs\busqueda_sentinel1_20261008_153000.json
```

### 4. Exportar la primera escena

```cmd
deforest-gee exportar --proyecto TU_PROJECT_ID --manifiesto outputs\busqueda_sentinel1_XXXXXXXX_XXXXXX.json --seleccionar 1 --carpeta-drive Sentinel1_Deforestacion
```

### 5. Revisar tareas

```cmd
deforest-gee tareas --proyecto TU_PROJECT_ID
```

### 6. Descarga masiva por zonas y años

Las zonas, el periodo y el tamaño del recuadro están en `config/zonas.json`. Cada colaborador usa **su propia cuenta y project ID**: los archivos se guardan en el Drive de quien ejecuta.

```cmd
deforest-gee descarga-masiva --proyecto TU_PROJECT_ID --limite 5 --simular
deforest-gee descarga-masiva --proyecto TU_PROJECT_ID --limite 5
deforest-gee descarga-masiva --proyecto TU_PROJECT_ID --zona UC_NR_01
deforest-gee estado --proyecto TU_PROJECT_ID --reintentar-fallidas
```

- Órbita relativa `AUTO`: se elige la más frecuente de cada zona y se conserva en las siguientes corridas.
- Carpetas de Drive (planas, Earth Engine no crea subcarpetas): `S1_<zona>_<año>_R<órbita>`.
- `outputs/catalogo.csv` registra cada escena enviada; repetir el comando no duplica. Para repartir el trabajo entre colaboradores, cada uno usa `--zona` con zonas distintas.
- `estado` copia al catálogo el estado real de las tareas; con `--reintentar-fallidas` las fallidas se reenvían en la siguiente corrida.

## Estructura del repositorio

```text
.
├── src/deforest_gee/             Código del programa
├── src/deforest_gee/ml/          Módulos experimentales de ML profundo
├── config/                       Configuraciones de ejemplo
├── tests/                        Pruebas unitarias sin credenciales GEE
├── docs/                         Documentación técnica
├── scripts/                      Automatizaciones de Windows
├── .github/                      Issues, Pull Requests y CI
├── outputs/                      Manifiestos generados (no versionados)
├── downloads/                    Descargas locales (no versionadas)
├── data/raw/                     Datos originales locales (no versionados)
└── data/processed/               Datos procesados locales (no versionados)
```

## Qué archivos son realmente “código”

El código ejecutable principal está en:

```text
src/deforest_gee/
```

Los archivos más importantes son:

- `cli.py`: comandos de consola.
- `gee_client.py`: autenticación e inicialización de Earth Engine.
- `sentinel1.py`: construcción de la colección Sentinel-1 y filtros.
- `aoi.py`: áreas de interés.
- `manifest.py`: manifiestos JSON.
- `exporter.py`: exportaciones a Google Drive.
- `local_raster.py`: procesamiento local con rasterio.
- `baseline.py`: baseline con scikit-learn.
- `vector_tools.py`: AOI y vectores con geopandas.
- `xarray_tools.py`: lectura analítica con xarray.

## Estado de validación

Esta entrega incluye pruebas unitarias locales y compilación sintáctica. La búsqueda/exportación real en Earth Engine requiere credenciales y `project_id` del equipo investigador, por lo que debe validarse en una máquina autenticada. Ver `VALIDACION.md`.

## Colaboración

Revisar:

- `docs/ENTREGA_A_INVESTIGADORES.md`
- `docs/ACCESOS_Y_ROLES_GITHUB.md`
- `CONTRIBUTING.md`
- `.github/ISSUE_TEMPLATE/`

## Seguridad

No subir al repositorio:

- claves de servicio;
- tokens;
- archivos `.env` reales;
- credenciales de Google;
- GeoTIFF masivos;
- datos sensibles del proyecto.

Consultar `SECURITY.md`.
