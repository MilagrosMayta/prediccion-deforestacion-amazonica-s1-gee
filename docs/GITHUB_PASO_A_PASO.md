# Preparar el repositorio en GitHub

## Nombre recomendado

```text
prediccion-deforestacion-amazonica-s1-gee
```

## Visibilidad inicial

Privado.

## Primer push

```cmd
git init
git branch -M main
git add .
git status
git commit -m "feat: versión inicial Sentinel-1 con Google Earth Engine"
git remote add origin https://github.com/USUARIO_O_ORG/prediccion-deforestacion-amazonica-s1-gee.git
git push -u origin main
```

Antes del commit, confirmar que `git status` no muestre credenciales, `.env`, GeoTIFF ni archivos pesados.
