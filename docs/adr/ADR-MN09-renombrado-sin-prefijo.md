# ADR-MN09: Renombrado de `vdo_*` a nombres sin prefijo

**Estado:** aceptada (decisión delegada). Cumplida para los `.py`; quedan dos JSON con el prefijo (ver Consecuencias).
**Decisión de origen:** D-77 (M8, renombrado masivo con `git mv`).

## Contexto

Todos los módulos empezaban por `vdo_` (`vdo_reengrose.py`, `vdo_cajon_core.py`, …). El paquete ya se llama `vdo`, así que el prefijo repetía el nombre.

## Decisión

Renombrar cada `freecad/vdo/**/vdo_<x>.py` a `<x>.py`, como último paso y de forma mecánica. Excluidos: ninguno por colisión, paquete existente o palabra reservada.

## Consecuencias

- 65 archivos renombrados con `git mv`. El mapeo completo está en `docs/archivo/mapeo_m8.md` (copia en `docs/mapeo_m8.md`).
- Imports, usos, rutas en cadenas, pruebas y `tools/` reescritos en el mismo commit.
- Quedan con prefijo: `core/vdo_hardware_catalog.json` y `core/vdo_manifest.json` (M8 renombró solo los `.py`).
- `tools/auditoria/verificar.py` (congelado) sigue buscando `vdo_<nombre>.py` en su regla de línea 241; no se toca.
- El golden de `module_specs` y `datos/modulos.json` no cambiaron.

## Relacionado

Ver `docs/ARQUITECTURA.md` §5 (mapa de archivos, con los nombres actuales).
