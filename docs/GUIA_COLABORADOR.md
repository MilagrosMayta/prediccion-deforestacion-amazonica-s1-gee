# Guía para el colaborador: descarga masiva de imágenes Sentinel-1

Esta guía está pensada para que puedas hacer la tarea **sin conocer el proyecto de antemano**. Léela completa una vez antes de empezar.

## 1. Qué estamos haciendo y por qué

El proyecto busca **predecir la deforestación de la Amazonía peruana** usando imágenes de satélite e inteligencia artificial. Para eso hace falta una base de datos grande de imágenes **Sentinel-1** (un satélite de radar de la Agencia Espacial Europea, que ve a través de las nubes) de **4 zonas**, entre **2018 y 2025**.

Tu tarea es **descargar esas imágenes**. El programa de este repositorio hace casi todo solo:

1. Busca en Google Earth Engine todas las imágenes de cada zona.
2. Elige automáticamente la órbita del satélite que más veces pasó por la zona (así todas las imágenes son comparables).
3. Pide a Google que **guarde cada imagen en tu Google Drive**, en carpetas ordenadas.
4. Anota lo enviado en un archivo `outputs/catalogo.csv`, para poder retomar sin repetir.

**No tienes que escribir qué imágenes bajar ni editar nada.** Todo está definido en `config/zonas.json`. No lo cambies.

> El trabajo pesado lo hacen los servidores de Google, no tu computadora. Tu laptop solo envía las órdenes; puede apagarse después.

## 2. Las 4 zonas

| Código | Zona | Departamento |
|---|---|---|
| `MD_IB_01` | Iberia, frente Tahuamanu | Madre de Dios |
| `MD_IN_01` | Inambari / entorno de La Pampa | Madre de Dios |
| `UC_NR_01` | Nueva Requena | Ucayali |
| `UC_MA_01` | Masisea | Ucayali |

Cada zona es un cuadrado de **30 × 30 km** y se descarga de 2018-01-01 a 2025-12-31.

## 3. Cuánto pesa y cuánto tarda (importante)

- Cada imagen pesa unos **110 MB** (son 3 bandas: VV, VH y ángulo de incidencia, a 10 metros de resolución).
- Cada zona tiene unas **250 imágenes** (por ejemplo, Nueva Requena tiene 246), o sea unos **28 GB por zona**.
- Las 4 zonas son unos **110 GB** en total.
- Un Google Drive gratuito tiene **15 GB**. **No alcanza ni para una zona.** Necesitas una de estas opciones:
  - Comprar **Google One de 200 GB** (alcanza para unas 6 zonas-lote, o todo con margen) o de 2 TB. Cuesta pocos dólares al mes y puedes cancelarlo al terminar.
  - O bajar **una zona a la vez**: cuando una zona termine, la descargas a un disco externo y borras esa carpeta de Drive para liberar espacio. Es más lento y manual.
- **Tiempo:** cada imagen es una tarea que Google procesa en cola. Una zona completa puede tardar **varias horas**, y las 4 zonas puede ser **más de un día**. No es un error: Google las procesa a su ritmo. Puedes dejar la computadora apagada.

## 4. Lo que necesitas antes de empezar

1. Una computadora con **Windows** (los comandos de esta guía son para Windows) y conexión a internet.
2. Una **cuenta de Google** (Gmail) con el espacio de Drive explicado arriba.
3. Una **cuenta de GitHub**, y que Milagros te haya invitado al repositorio (te llega un correo: acéptalo).
4. Unos 30 minutos para la instalación inicial.

## 5. Instalación (una sola vez)

### 5.1 Instalar Python
1. Entra a https://www.python.org/downloads/ y descarga la versión **3.11 o superior**.
2. Al abrir el instalador, **marca la casilla "Add python.exe to PATH"** (abajo) y luego **Install Now**.
3. Comprueba: abre el menú Inicio, escribe `cmd`, abre **Símbolo del sistema** y escribe `python --version`. Debe mostrar `Python 3.11` o mayor.

### 5.2 Instalar Git
1. Descarga https://git-scm.com/download/win e instálalo dejando todas las opciones por defecto.
2. Comprueba en `cmd`: `git --version`.

### 5.3 Descargar el proyecto
En `cmd`, ve a una carpeta donde quieras guardarlo (por ejemplo, Documentos) y ejecuta:

```cmd
cd %USERPROFILE%\Documents
git clone https://github.com/MilagrosMayta/prediccion-deforestacion-amazonica-s1-gee.git
cd prediccion-deforestacion-amazonica-s1-gee
```

La primera vez se abrirá una ventana para iniciar sesión en GitHub. Si dice que el repositorio no existe, es que aún no aceptaste la invitación de Milagros.

### 5.4 Instalar el programa
Sigue en `cmd`, dentro de la carpeta del proyecto:

```cmd
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -e .
```

Después de `activate`, al inicio de la línea debe aparecer `(.venv)`. **Cada vez que abras una ventana nueva de `cmd` para trabajar, repite `cd` a la carpeta del proyecto y `.venv\Scripts\activate`.**

Comprueba que quedó bien:

```cmd
deforest-gee --version
```

## 6. Crear tu proyecto de Google Earth Engine (una sola vez)

Earth Engine es el servicio de Google que entrega las imágenes. Necesita un "proyecto" a tu nombre.

1. Entra a https://console.cloud.google.com con tu cuenta de Google y acepta los términos.
2. Arriba a la izquierda, clic en el selector de proyectos y luego **Proyecto nuevo**. Ponle un nombre (por ejemplo `imagenes-satelitales`) y **Crear**.
3. Anota el **ID del proyecto**: aparece en el mismo selector, columna **ID**. Es algo como `imagenes-satelitales-123456`. **No es igual al nombre.** Lo vas a usar en todos los comandos.
4. Entra a https://code.earthengine.google.com/register . Elige **Uso no comercial** (investigación académica), selecciona tu proyecto y completa el registro. Cuando termine, ya tienes Earth Engine habilitado.

## 7. Conectar tu cuenta (una sola vez)

En `cmd`, con el entorno activo:

```cmd
deforest-gee autenticar
```

Se abre el navegador: elige tu cuenta de Google y acepta los permisos. Al terminar dice "Autenticación completada".

Luego comprueba que todo funciona (cambia `TU_PROJECT_ID` por el ID del paso 6):

```cmd
deforest-gee diagnostico --proyecto TU_PROJECT_ID
```

Debe mostrar `"earth_engine": "OK"` y `"sentinel1_accesible": true`. Si no, revisa la sección de problemas más abajo.

## 8. Descargar las imágenes

Haz **una zona a la vez**, empezando por `UC_NR_01`. Cambia `TU_PROJECT_ID` y el código de zona.

### 8.1 Simulación (no descarga nada)

```cmd
deforest-gee descarga-masiva --proyecto TU_PROJECT_ID --zona UC_NR_01 --limite 5 --simular
```

La búsqueda de 8 años tarda unos minutos. Debe mostrar algo así:

```
UC_NR_01: órbita relativa 171, 246 escenas
  S1_UC_NR_01_2018_R171: 5 tareas (simuladas)
```

### 8.2 Prueba real con 5 imágenes

```cmd
deforest-gee descarga-masiva --proyecto TU_PROJECT_ID --zona UC_NR_01 --limite 5
```

Pregunta `¿Continuar? [s/N]`: escribe `s` y Enter. Espera unos minutos y revisa tu Drive: debe aparecer la carpeta `S1_UC_NR_01_2018_R171` con 5 archivos `.tif` de ~110 MB. Comprueba también:

```cmd
deforest-gee estado --proyecto TU_PROJECT_ID
```

Cuando las 5 digan `COMPLETED`, la prueba salió bien.

### 8.3 Descarga completa de la zona

```cmd
deforest-gee descarga-masiva --proyecto TU_PROJECT_ID --zona UC_NR_01
```

Responde `s` a la pregunta. Muestra cuántas escenas va a enviar (unas 240 menos las 5 ya enviadas). Las imágenes se crean en Drive en carpetas `S1_UC_NR_01_<año>_R171`, una por año.

### 8.4 Repite con las otras zonas

Cuando una zona esté completa, repite el comando 8.3 cambiando el código: `UC_MA_01`, `MD_IB_01`, `MD_IN_01`. Si no tienes espacio para todo a la vez, lanza la siguiente zona solo cuando hayas liberado Drive.

## 9. Cómo saber si va bien

```cmd
deforest-gee estado --proyecto TU_PROJECT_ID
```

Muestra cuántas tareas hay en cada estado:

- `READY`: en cola.
- `RUNNING`: Google la está procesando.
- `COMPLETED`: lista; el archivo ya está en tu Drive.
- `FAILED`: falló. Se corrige con el paso siguiente.

**Si hay tareas fallidas o se cortó el proceso:**

```cmd
deforest-gee estado --proyecto TU_PROJECT_ID --reintentar-fallidas
deforest-gee descarga-masiva --proyecto TU_PROJECT_ID --zona UC_NR_01
```

El segundo comando solo reenvía lo que falta. **Es seguro repetirlo**: nunca duplica lo ya enviado, porque el avance está en `outputs/catalogo.csv`.

**Cuándo terminó una zona:** `estado` no muestra `READY`, `RUNNING` ni `FAILED`, y el número de archivos `.tif` en sus carpetas de Drive coincide con la cantidad de filas de esa zona en `outputs/catalogo.csv` (ábrelo con Excel).

## 10. Qué NO debes hacer

- No edites `config/zonas.json` ni el código.
- No lances la misma zona en dos ventanas a la vez.
- No borres archivos de Drive hasta confirmar que `estado` muestra `COMPLETED` y que ya los respaldaste.
- No compartas tu ID de proyecto ni el archivo `outputs/catalogo.csv` en lugares públicos.
- No ejecutes los comandos con `--reexportar` (volvería a descargar todo).

## 11. Problemas frecuentes

| Qué ves | Qué hacer |
|---|---|
| `CERTIFICATE_VERIFY_FAILED` o `SSLError` | Tu red o tu antivirus intercepta las conexiones seguras. Prueba con los datos del celular (hotspot) o desactiva el análisis HTTPS del antivirus mientras dura la descarga. Vuelve a activarlo al terminar. |
| `deforest-gee` no se reconoce como comando | Falta activar el entorno: `.venv\Scripts\activate` desde la carpeta del proyecto. |
| `Debe indicar --proyecto` | Olvidaste `--proyecto TU_PROJECT_ID`. |
| `Not signed up for Earth Engine` o permisos | No terminaste el registro del paso 6.4, o usaste otro proyecto. |
| La descarga se detiene sin error | Repite el comando de descarga; continúa donde se quedó. |
| Drive lleno | Las tareas fallan. Libera espacio, ejecuta el paso de reintento de la sección 9 y repite. |

## 12. Al terminar, entrega a Milagros

1. Comparte las carpetas `S1_*` de tu Drive con ella (clic derecho en la carpeta, **Compartir**).
2. Envíale el archivo `outputs/catalogo.csv`.
3. Avísale cuando cada zona esté completa, para que sepa en qué punto está el proyecto.
