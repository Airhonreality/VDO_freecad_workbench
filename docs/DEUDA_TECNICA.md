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
| D-01 | ~~Golden de `module_props.rotacion_z`~~ | Resuelto: serializador de `App.Rotation` y golden con reubicación. Ver P-02. | ejecutor | 2026-11-02 |
| D-02 | Golden de `guardian` y `nesting_presets` | `guardian`: **resuelto**, golden de 9 entradas desde `b78de04`. `nesting_presets`: **N/A con motivo (P-10)**. No carga en `b78de04` (`NameError` al importar). Deuda: arreglar la carga en el código actual y generar golden "nuevo, no de origen". | ejecutor | antes de M5 |
| D-11 | Locale numérico del guardián | `guardian` escribe `"0.4"` como texto. Con `LC_NUMERIC=es_CO` (que Qt fija al crear `QApplication`), FreeCAD lo lee como `0`. Medido: el golden falla en nivel 2 tras los tests de UI. Riesgo real para usuarios con locale de coma. Fix propuesto: escribir números sin depender del locale; cambia el contenido de las celdas, así que necesita aprobación. | usuario (aprobar), ejecutor (implementar) | 2026-11-09 |
| D-12 | Ciclo dentro de `cad` | `cad.colocacion` ↔ `cad.propiedades`: el import diferido de `aplicar_rotacion` cierra el ciclo. P-08 no lo cubría. Decidir dónde vive `ancla_local` o `aplicar_rotacion`. Lo mide `tools/auditoria/ciclos.py`. | usuario (decidir), ejecutor (implementar) | M5 |
| D-13 | Aristas core→cad: 8 | Tras P-08 subieron de 4 a 8 (los llamadores de `add_common_props` ahora importan de `cad`). Es el coste aceptado hasta M5. Medido con `tools/auditoria/ciclos.py`. | ejecutor | M5 |
| D-14 | `test_single_dock_convergence.py` (otra sesión) | Usa `sys` sin importarlo (F821, línea 218). Su `__main__` falla con NameError. Es un cambio sin commitear de P-04: no lo toco. | usuario | 2026-11-09 |
| D-03 | Método de conteo del plan §1 | El plan dice 88 archivos y 23.920 líneas; `minimalismo.py` mide 85 y 23.608. Hay que fijar un solo método. | usuario | 2026-11-09 |
| D-04 | ~~`ruff check` = 288 con `.venv` (plan dice 259)~~ | **Resuelto en M0**: alcance y versión fijados en el plan §2 (D-04) y en `pyproject.toml`. Medido hoy con `ruff check .`: 299. `verificar.py` (`freecad/`+`tests/`+`tools/`) da 291; la cifra de 288 del registro no se reproduce. La diferencia de 1 incidencia en `test_single_dock_convergence.py` viene de los cambios sin commitear de P-04. | ejecutor | 2026-11-03 |
| D-05 | `test_arquitectura.py` en rojo (3 FALLO) | Violaciones reales de MN-03. Se corrigen en M5. Por eso el nivel 2 sale con código 1. | ejecutor | M5 |
| D-06 | Cambios de tests de otra sesión sin commitear | `os._exit` → `sys.exit` en `test_gui_wiring.py` y `test_single_dock_convergence.py`, sin verificar. Ver P-04. | usuario | 2026-11-09 |
| D-07 | Golden de `frames.interpretar_lados` con 1 entrada en error | Entrada JSON inválida. Comportamiento de `b78de04` y actual. Se conserva como caso de error. | ejecutor | M1 |
| D-08 | Planes anteriores sin archivar | MN-13 pide moverlos a `docs/archivo/`. Se hace en M11. | ejecutor | M11 |
| D-09 | `rotacion_z` duplicado | Dos definiciones actuales (`core/vdo_helpers.py` y `cad/propiedades.py`), misma lógica. El mensaje de `b2583a6` dice "un solo rotacion_z". Se elimina en M2. | ejecutor | M2 |
| D-10 | Cargador de anclajes duplicado | `ANCLAJES`, `ANCLAJE_LABELS`, `ANCLAJE_DEFAULT` y `ANCLAJE_IDS` se cargan desde `datos/anclajes.json` en `core/vdo_module_props.py` y `cad/propiedades.py`. Se duplican 5 líneas de carga porque `cad` no puede importar de `core` sin ciclo: `core/vdo_module_props.py` importa `add_common_props` de `cad`, y los módulos de `core` lo usan. Se elimina en M5. | ejecutor | M5 |
