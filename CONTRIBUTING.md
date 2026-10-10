# Contribución al proyecto

## Flujo recomendado

1. Crear un Issue antes de un cambio relevante.
2. Crear una rama desde `main`.
3. Implementar el cambio.
4. Ejecutar las pruebas.
5. Crear un Pull Request.
6. Solicitar revisión de un investigador o responsable técnico.

## Convención de ramas

```text
feature/nombre-corto
fix/nombre-corto
docs/nombre-corto
experiment/nombre-corto
```

## Convención de commits

Ejemplos:

```text
feat: agrega exportación por manifiesto
fix: corrige validación del rango de fechas
docs: aclara autenticación de Earth Engine
test: agrega prueba de selección de escenas
```

## Regla científica

No modificar silenciosamente el perfil de datos Sentinel-1 (modo, polarización, resolución, órbita o preprocesamiento). Todo cambio metodológico debe documentarse y ser revisado por el equipo investigador.
