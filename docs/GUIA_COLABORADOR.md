# Guía para el colaborador: descarga masiva de Sentinel-1

Con esta guía descargas las imágenes que te toquen a **tu propio Google Drive**. No necesitas escribir qué imágenes bajar: las zonas, el periodo y los filtros ya están en `config/zonas.json`.

## 1. Lo que necesitas antes de empezar

- Windows, Linux o macOS con **Python 3.11 o superior** y **Git**.
- Una **cuenta de Google** con espacio libre en Drive: unos **28 GB por zona** (cada imagen pesa ~110 MB).
- Un **proyecto de Google Cloud con Earth Engine habilitado** (registro para uso no comercial en https://earthengine.google.com). Anota el **ID del proyecto** (por ejemplo `mi-proyecto-123456`; no es lo mismo que el nombre).

## 2. Instalación (una sola vez)

```cmd
git clone URL_DEL_REPOSITORIO
cd prediccion-deforestacion-amazonica-s1-gee
python -m venv .venv
.venv\Scripts\activate
python -m pip install -e .
```

En Linux/macOS, el tercer paso es `source .venv/bin/activate`.

## 3. Conectar tu cuenta (una sola vez)

```cmd
deforest-gee autenticar
deforest-gee diagnostico --proyecto TU_PROJECT_ID
```

Se abre el navegador: entra con tu cuenta de Google y acepta. El diagnóstico debe mostrar `"earth_engine": "OK"`.

> Si sale `CERTIFICATE_VERIFY_FAILED`, tu red o tu antivirus intercepta las conexiones seguras. Prueba con otra red (datos del celular) o desactiva el análisis HTTPS del antivirus mientras dure la descarga.

## 4. Descargar

Primero una prueba pequeña, que no lanza nada:

```cmd
deforest-gee descarga-masiva --proyecto TU_PROJECT_ID --zona CODIGO_DE_ZONA --limite 5 --simular
```

Si se ve bien, la descarga real de las zonas que te asignaron (una por una):

```cmd
deforest-gee descarga-masiva --proyecto TU_PROJECT_ID --zona CODIGO_DE_ZONA
```

El programa busca las escenas, muestra el total y pregunta `¿Continuar? [s/N]`. Responde `s`. Las tareas se ejecutan en los servidores de Google: tu computadora puede apagarse.

Las imágenes aparecen en tu Drive, en carpetas `S1_<zona>_<año>_R<órbita>`, por ejemplo `S1_UC_NR_01_2018_R171`.

Zonas disponibles: `MD_IB_01`, `MD_IN_01`, `UC_NR_01`, `UC_MA_01`.

## 5. Revisar y reanudar

```cmd
deforest-gee tareas --proyecto TU_PROJECT_ID
deforest-gee estado --proyecto TU_PROJECT_ID --reintentar-fallidas
```

Si se cortó o hubo tareas fallidas, repite el comando de `descarga-masiva`: no duplica lo ya enviado (el avance está en `outputs/catalogo.csv`). Termina cuando `estado` solo muestre `COMPLETED`.

## 6. Al terminar

Comparte las carpetas `S1_*` de tu Drive con quien coordina el proyecto, o envía el archivo `outputs/catalogo.csv`.
