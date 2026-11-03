# Deuda Técnica VDO

> **Nota (2026-11-02):** esta tabla es del plan maestro anterior y ya no es el registro
> vigente. La deuda del plan de minimalismo está en la sección "Plan de minimalismo" al final,
> con responsable y fecha. Lo de abajo se conserva como historial.

Estado de la tabla histórica: **sin ítems abiertos** (a fecha de cierre del plan maestro).

Todos los ítems de deuda técnica identificados en las fases F1–F9 han sido resueltos o documentados como decisión consciente:

| Ítem | Fase | Decisión |
|------|------|----------|
| Motor de despiece compartido cajón/puerta | F5 | Diferido: no hay lógica de solapamiento seguro (M-16 solo unifica la tabla de aperturas, no el motor) |
| Descomponer funciones >150 líneas | F7 | Diferido: requiere campaña de snapshots por función; algunas funciones de UI permanecen >100 líneas (F10 parcial) |
| Conversión total de colores hex a tokens | F12 | Parcial: `ui/tema.py` creado con todos los tokens; 436 literales hex restantes pendientes de migración |
| Renombrado `vdo_*` → sin prefijo | F13 | Pospuesto: la capa `app/vdo_api.py` ya abstrae los nombres de core para UI |
| Type hints completos | F14 | Parcial: `pyproject.toml` creado con `mypy --strict`; 1121 errores de tipo pendientes de anotar |
| Capturas visuales F17 | F17 | Pendiente de disponibilidad de FreeCAD GUI y decisión del usuario sobre versionado |

No hay ítems de deuda técnica con dueño y fecha pendientes de cierre fuera de esta tabla.

---

## Plan de minimalismo (2026-11-02)

Formato: causa · responsable (**usuario** si es decisión, **ejecutor** si es trabajo) · fecha.
Las fechas son **propuesta del ejecutor**, a confirmar por el usuario. Las que dicen "M5", "M9" o "M11" dependen de la fase.

| # | Ítem | Causa | Responsable | Fecha |
|---|---|---|---|---|
| D-01 | Golden de `module_props.rotacion_z` | El serializador no representa `App.Rotation`. Ver P-02 en `PENDIENTES_HUMANO.md`. | usuario (decidir) · ejecutor (implementar si se aprueba) | 2026-11-09 |
| D-02 | Golden de `guardian` y `nesting_presets` | Sin función de cálculo. Ver P-01. | usuario | 2026-11-09 |
| D-03 | Método de conteo del plan §1 | El plan dice 88 archivos y 23.920 líneas; `minimalismo.py` mide 85 y 23.608. Hay que fijar un solo método. | usuario | 2026-11-09 |
| D-04 | `ruff check` = 288 con `.venv` (plan dice 259) | Diferencia de versión o de alcance de ruff. Hay que fijar versión y alcance en `pyproject.toml`. | ejecutor | 2026-11-16 (M9) |
| D-05 | `test_arquitectura.py` en rojo (3 FALLO) | Violaciones reales de MN-03. Se corrigen en M5. Por eso el nivel 2 sale con código 1. | ejecutor | M5 |
| D-06 | Cambios de tests de otra sesión sin commitear | `os._exit` → `sys.exit` en `test_gui_wiring.py` y `test_single_dock_convergence.py`, sin verificar. Ver P-04. | usuario | 2026-11-09 |
| D-07 | Golden de `frames.interpretar_lados` con 1 entrada en error | Entrada JSON inválida. Comportamiento de `b78de04` y actual. Se conserva como caso de error. | ejecutor | M1 |
| D-08 | Planes anteriores sin archivar | MN-13 pide moverlos a `docs/archivo/`. Se hace en M11. | ejecutor | M11 |
