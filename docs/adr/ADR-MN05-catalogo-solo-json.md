# ADR-MN05: El catálogo de herrajes solo existe como JSON

**Estado:** aceptada (decisión delegada).
**Decisión de origen:** H-21 (ruta del catálogo única; corrige un defecto), y el commit `8b85ce3` de M2, que quita los `_FALLBACK_*` (ver `docs/PROGRESO_MINIMALISMO.md`).

## Contexto

Había dos fuentes del mismo hecho: `_FALLBACK_BISAGRA` (48 líneas) y `_FALLBACK_CORREDIZO` (34 líneas) en `core/vdo_hardware_hub.py`, mientras `core/vdo_hardware_catalog.json` ya contenía esos datos. Además, el gestor de herrajes calculaba una ruta de catálogo que no existe (H-21): mostraba un error al abrir y creaba un fichero que el hub nunca leía.

## Decisión

- Un único origen: el JSON del catálogo.
- Se eliminan los `_FALLBACK_*`.
- Si el archivo falta, la carga falla con un error claro (no hay valores por defecto en código).
- Una sola constante de ruta: `CATALOGO_PATH` en `core/hardware_hub.py`.

## Consecuencias

- Definiciones de `_FALLBACK_*` en el código final: 0 (grep, M10).
- Se corrige un defecto real: el gestor de herrajes leía y guardaba en la ruta correcta.
- **Por confirmar:** el texto exacto del error cuando falta el JSON. No se ha probado en esta fase.
- El JSON sigue en `core/`, no en `datos/` (ver ADR-MN04).

## Relacionado

ADR-MN04. Detalle en `docs/DECISIONES_DELEGADAS.md`, H-21.
