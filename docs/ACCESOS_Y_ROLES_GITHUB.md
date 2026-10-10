# Accesos y roles en GitHub

## Recomendación

Para un equipo de investigación con varios niveles de responsabilidad, preferir una **organización de GitHub** en lugar de un repositorio privado dentro de una cuenta personal.

## Distribución sugerida

| Perfil | Rol sugerido |
|---|---|
| Responsable técnico | Admin |
| Investigador principal que supervisa | Maintain |
| Ingeniero/desarrollador | Write |
| Revisor metodológico | Read |
| Persona que clasifica Issues | Triage |

## Protección de `main`

Se recomienda:

- exigir Pull Request;
- al menos una aprobación;
- exigir pruebas automáticas aprobadas;
- impedir `force push`;
- impedir borrado de rama protegida.

## Información sensible

Las credenciales de Google nunca deben almacenarse como archivos normales del repositorio. Si en el futuro GitHub Actions necesita autenticación, se deben usar GitHub Secrets y una identidad de servicio aprobada por el equipo.
