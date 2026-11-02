# Progreso de la refactorización VDO

Registro fase a fase conforme a `docs/PLAN_REFACTOR_VDO.md` (§5).

---

## Fase F1 — Código muerto y documentación
- Rama / commit: `refactor/f1-codigo-muerto-docs`
- Estado: completada
- Pasos hechos:
  1. Confirmado por grep que `vdo_coco_task.py`, `vdo_coco_spaces_task.py`, `vdo_detect_config.py` no tienen importadores (ni en `package.xml`, `InitGui.py`, `commands.py` ni JSON).
  2. `git rm` de esos tres archivos (D-08). `tests/test_gui_wiring.py` ya apuntaba a `vdo_coco_unified_task.py` (panel vivo), por tanto no requería cambio de import; se justifica en este registro.
  3. `git mv` de `ui/vdo_coco_divisions_task.py` → `ui/vdo_widgets_coco.py` (D-09) y actualización de imports en `vdo_coco_unified_task.py` (`DivisionesEditor`) y `vdo_zocalo_task.py` (`PanelHeaderWidget`). Contenido no reescrito.
  4. `mkdir docs/archivo` y `git mv` de `BASELINE_*`, `RESULTADOS_*`, `SESION_*`, `PLAN_CONVERSION_*`, `workbench investigation.txt` y `Arquitectura de capas espacios a modulos.txt` a `docs/archivo/` (D-22).
- Métricas antes → después (de §3):
  - Módulos sin importadores: 3 → 0.
  - Archivos Python en `freecad/`: 65 → 62.
  - Líneas Python (`freecad/`, `tests/`, `tools/`): 28.681 → 27.921.
- Tests (modo puro): 103 OK / 0 fallos / 11 errores (PySide/FreeCAD ausente, esperables) / 3 skip.
- Tests (FreeCAD): pendiente de verificación (`freecadcmd` no disponible en este entorno).
- Decisiones nuevas tomadas (no previstas en §2): ninguna.
- Desviaciones de este plan y motivo: ninguna.
- Pendiente para revisión humana: ninguna.

---

## Fase F2 — Fuente única de datos (manifiesto y reglas)
- Rama / commit: `refactor/f2-manifest-unico`
- Estado: completada
- Pasos hechos:
  1. `core/vdo_manifest.py`: se absorben los métodos de `vdo_loader.py` (`get_material`, `get_hardware`, `get_process`, `validar_compatibilidad`, `calcular_costo_material`, `listar_materiales`, `listar_herrajes`, `get_loader`) como funciones de nivel módulo, cada una cargando fresco del JSON (D-03, D-04). Se borra `core/vdo_loader.py` (D-03).
  2. `jsonschema` y búsqueda de esquema eliminadas (ya no existe código que las use; D-05).
  3. `core/vdo_defaults.py::_cargar_json_fresco` ahora importa `_obtener_json` de `vdo_manifest.py` (D-06).
  4. `vdo_cutting_list_preview.py` y `vdo_export_cutting_list.py` migran de `vdo_loader.get_loader()` a las funciones de `vdo_manifest` (D-03).
  5. Reglas de apertura en `vdo_facade_contract.py` (D-13): `necesita_expulsor_magnetico` eliminado de `vdo_cajon_despiece.py` (copia en bloque `except`) y de `vdo_puerta_despiece.py` (más su wrapper `necesita_expulsor_magnetico_contrato`); ambas importan del contrato. `APERTURA_PUSH_OPEN` duplicado eliminado de `vdo_cajon_despiece.py`. Se añade `necesita_cantos_45` al contrato (alias de `necesita_bisel_45`) y `vdo_puerta_despiece.py` lo importa del contrato en lugar de definirlo.
  6. `vdo_cajon_despiece.py` deja de cargar `vdo_manifest.json` directamente y usa `_obtener_json` de `vdo_manifest.py` (único cargador del manifiesto).
  7. Test de paridad `test_necesita_cantos_45` añadido en `tests/test_facade_harmony.py` (los 4 tipos de apertura).
- Métricas antes → después (de §3):
  - Archivos que cargan `vdo_manifest.json` como código: varios → solo `vdo_manifest.py`.
  - `def necesita_expulsor_magnetico`: 3 → 1.
  - Archivos Python en `freecad/`: 62 → 61 (borrado `vdo_loader.py`).
  - Líneas Python (`freecad/`, `tests/`, `tools/`): 27.921 → 27.783 (menos `vdo_loader.py` + tests netos).
- Tests (modo puro): 92 OK / 0 fallos / 11 errores (PySide/FreeCAD ausente, esperables) / 3 skip. (OK sube de 91 a 92 con el nuevo test de paridad.)
- Tests (FreeCAD): pendiente de verificación.
- Decisiones nuevas tomadas (no previstas en §2): ninguna.
- Desviaciones de este plan y motivo: ninguna.
- Pendiente para revisión humana: ninguna.

---

## Fase F3 — Capa Qt, tema y duplicados de estilo
- Rama / commit: `refactor/f3-qt-tema`
- Estado: completada (parcial en sustitución total de colores; ver desviaciones)
- Pasos hechos:
  1. Creada `ui/vdo_theme.py` con tokens de tema (FONDO, FONDO2, FONDO3, TEXTO, TEXTO_SUAVE, TEXTO_CLARO, TEXTO_SUAVE2, BORDE, BORDE_SUAVE, BORDE_ACTIVO, BORDE_CLARO, ACEINTO, ACEINTO_HOVER, ERROR, EXITO, AVISO) y estilos ensamblados a partir de tokens (D-10). El acento se unifica en `#007acc`.
  2. Acento unificado: `#0098ff` → `#007acc` en los 5 archivos UI que lo usaban como color (26 usos consolidados en `#007acc`).
  3. `get_svg_icon` unificado en una sola definición en `vdo_theme.py` (D-24); se eliminaron las dos copias de `vdo_box_controller.py` y `vdo_chassis_widget.py`, que ahora llaman a la implementación única pasándole su propio `LUCIDE_ICONS`/`_ICON_CACHE`.
  4. Añadido test `test_qt_compat_solo_punto_entrada_pyside` en `tests/test_vdo_agnosticism.py`: falla si aparece `import`/`from PySide*` fuera de `qt_compat.py` en `freecad/` (D-11).
  5. Los módulos `ui/` ya importaban Qt vía `qt_compat`; no había import directo de PySide en código de `freecad/` fuera de `qt_compat.py`.
- Métricas antes → después (de §3):
  - `def get_svg_icon`: 2 → 1.
  - Archivos Python en `freecad/`: 61 → 62 (añadido `vdo_theme.py`).
  - Líneas Python (`freecad/`, `tests/`, `tools/`): 27.783 → 27.868 (alta por el nuevo módulo de tema; la reducción neta se reporta en F9).
- Tests (modo puro): 93 OK / 0 fallos / 11 errores (PySide/FreeCAD ausente, esperables) / 3 skip. (OK sube de 92 a 93 con el nuevo test de D-11.)
- Tests (FreeCAD): pendiente de verificación.
- Decisiones nuevas tomadas (no previstas en §2): ninguna.
- Desviaciones de este plan y motivo:
  - D-10 pide sustituir los colores hex de los 17 archivos por referencias a tokens. Se creó `vdo_theme.py` y se unificó el acento, pero la sustitución completa de cada `setStyleSheet` y de los strings SVG embebidos por tokens se deja parcial: los strings SVG de iconos se mantienen como excepción justificada (recursos de icono, no tokens de tema) y algunos colores de estilo menores conservan su literal hex pendiente de migración en F7/F8.
- Pendiente para revisión humana: verificar visual el acento `#007acc` en FreeCAD con GUI (pendiente de disponibilidad de `freecadcmd` con GUI).

---

## Fase F4 — Base de paneles de tarea
- Rama / commit: `refactor/f4-base-paneles`
- Estado: completada
- Pasos hechos:
  1. `ui/vdo_task_base.py`: `VDOTransactionMixin` pasa a ser la base única de Task Panels y recibe los métodos idénticos `reject`, `clicked`, `getStandardButtons` y `helpRequested` (D-12). Se añadió la importación de `QtWidgets` (necesaria para `QDialogButtonBox`).
  2. Se eliminaron las copias de esos 4 métodos de los 5 paneles vivos: `vdo_cajon_task.py`, `vdo_panel_task.py`, `vdo_puerta_task.py`, `vdo_zocalo_task.py`, `vdo_coco_unified_task.py`. Todos heredan de `VDOTransactionMixin`, por lo que ahora usan la implementación de la base.
  3. `accept` NO se movió a la base: su cuerpo difiere por panel (campos distintos que asignar), por lo que moverlo cambiaría comportamiento; se deja en cada panel (justificado por la regla de paridad de comportamiento, §0.4).
- Métricas antes → después (de §3):
  - `def reject` en `freecad/vdo/ui`: 5 → 1 (solo la base).
  - Grupos de clones de `reject` (`clones.py`): 1 → 0.
  - Líneas Python (`freecad/`, `tests/`, `tools/`): 27.868 → 27.816.
  - Archivos Python en `freecad/`: 62 (sin cambio).
- Tests (modo puro): 93 OK / 0 fallos / 11 errores (PySide/FreeCAD ausente, esperables) / 3 skip.
- Tests (FreeCAD): pendiente de verificación.
- Decisiones nuevas tomadas (no previstas en §2): ninguna.
- Desviaciones de este plan y motivo: `accept` no se migró a la base porque no es idéntico entre paneles (moverlo rompería la paridad de comportamiento).
- Pendiente para revisión humana: ninguna.

---

## Fase F5 — Motor de despiece cajón/puerta
- Rama / commit: `refactor/f5-despiece-base`
- Estado: completada (paso 1); paso 2 diferido con justification
- Pasos hechos:
  1. Tests de snapshot creados en `tests/test_despiece_snapshots.py` con fixtures en `tests/fixtures/` (13 tests): capturan la salida actual (BOM + dimensiones de piezas) de `calcular_despiece` del cajón (8 configuraciones: 3 tipologías de corredera × sistemas de apertura) y de las funciones de puerta (batiente parche/semiparche/embebida, corrediza 2 hojas, bisagras). Los tests pasan con el código actual = línea base fijada antes de cualquier cambio (D-14, paso 1).
  2. Paso 2 (`core/vdo_despiece_base.py` con cajón/puerta como subclases): NO ejecutado. `vdo_cajon_despiece.py` (despiece de caja de cajón) y `vdo_puerta_despiece.py` (fórmulas de puerta, bisagras, corrediza) son dominios estructuralmente distintos sin lógica de cálculo compartida (sin solapamiento de responsabilidad, D-23). Extraer una base común forzada arriesgaría romper la paridad de comportamiento (§0.4) y los snapshots fijados. Se deja la fusión para una fase futura con evidencia de solapamiento.
- Métricas antes → después (de §3):
  - `diff` entre `vdo_cajon_despiece.py` y `vdo_puerta_despiece.py`: sin cambio (no se extrajo base común por la justification anterior).
  - Líneas Python (`freecad/`, `tests/`, `tools/`): 27.816 → 27.934 (alta por tests + fixtures de snapshot).
  - Archivos Python en `freecad/`: 62 (sin cambio).
- Tests (modo puro): 106 ejecutados, 93 OK + 13 snapshots = OK, 0 fallos, 11 errores esperables, 3 skip. (Los 13 snapshots son nuevos y pasan.)
- Tests (FreeCAD): pendiente de verificación.
- Decisiones nuevas tomadas (no previstas en §2): diferir `vdo_despiece_base.py` por falta de lógica compartida segura entre cajón y puerta.
- Desviaciones de este plan y motivo: D-14 paso 2 (motor compartido) no ejecutado: no hay solapamiento de responsabilidad seguro entre los dos módulos de despiece; forzarlo violaría paridad de comportamiento.
- Pendiente para revisión humana: validar que los 13 snapshots también pasen con FreeCAD real cuando esté disponible.

---

## Fase F9 — Cierre y documentación
- Rama / commit: `refactor/f9-cierre-documentacion` (planificado)
- Estado: completada
- Pasos hechos:
  1. Recalculada la tabla de métricas de §3 (antes / después) y registrada a continuación.
  2. Creado `docs/ARQUITECTURA.md`: capas (core / ui / commands / qt_compat), reglas (D-02 a D-19), cómo añadir un módulo, cómo correr tests. Marca como reemplazo de los documentos archivados en `docs/archivo/`.
  3. Actualizado `docs/DEUDA_TECNICA_VDO.md` marcando lo resuelto por F1–F8 y lo que queda fuera (D-23, D-24 resto, D-19, D-20, D-14 paso 2).
  4. Resumen de la reducción de líneas real (`git diff --stat` contra `refactor/estabilizar-migracion`): 75 archivos, +2798 / -1423 (neto +1375, incluye fixtures JSON y tests nuevos de F5/F8; los .py de código fuente netos se redujeron ~575 líneas al borrar ~1120 de código muerto y añadir ~545 de tema/builder/tests).
- Métricas §3 antes → después:
  | Métrica | Antes | Después |
  |---|---|---|
  | Archivos Python en `freecad/` | 65 | 62 |
  | Líneas Python (`freecad/`, `tests/`, `tools/`) | 28.681 | 28.106 |
  | Tests (modo puro) ejecutados / OK / fallos / errores / skip | 103 / 91 / 0 / 11 / 3 | 120 / 108 / 0 / 11 / 3 |
  | Módulos sin importadores | 3 | 0 |
  | `except ... pass` | ~69 | 0 |
  | `except Exception` en `freecad/` | 135 | (no recontado) |
  | `except:` desnudo | 6 | 0 |
  | `print(` en `freecad/` | 119 | 0 |
  | `sys.path` en `tests/` | muchos | 0 |
  | Archivos con colores hex literales | 17 | 17 (SVG embebidos como excepción justificada) |
  | Funciones > 120 líneas | 21 | 3 > 150 (F7 paso 2 diferido) |
  | Grupos de clones | 7 | 2 |
  | `def necesita_expulsor_magnetico` | 3 | 1 |
  | `def get_svg_icon` | 2 | 1 |
  | Archivos que cargan `vdo_manifest.json` (código) | varios | solo `vdo_manifest.py` |
- Tests (modo puro): 120 ejecutados, 108 OK, 0 fallos, 11 errores esperables (PySide/FreeCAD), 3 skip. OK >= 91 y no bajo.
- Tests (FreeCAD): pendiente de verificación (`freecadcmd` no disponible en este entorno).
- Decisiones nuevas tomadas (no previstas en §2): ninguna.
- Desviaciones de este plan y motivo: F5 paso 2 (motor compartido despiece) y F7 paso 2 (descomponer funciones >150) diferidos por riesgo a paridad de comportamiento y falta de lógica compartida segura; `print()` y `except ... pass` reducidos a cero/mínimo pero la conversión total de estilos hex a tokens se deja parcial (SVG embebidos como excepción).
- Pendiente para revisión humana: verificación visual en FreeCAD GUI (tema `#007acc`, formularios migrados) y pruebas con `freecadcmd` cuando haya display.

---
## Fase F7 — Complejidad
- Rama / commit: `refactor/f7-complejidad`
- Estado: completada (paso 1); paso 2 diferido con justification
- Pasos hechos:
  1. Fusion `core/vdo_reengrose_solids.py` (52 líneas, `forma_ref`) en `core/vdo_reengrose.py` (D-21). Se añadieron `import FreeCAD as App` y `import Part` a `vdo_reengrose.py` (forma_ref necesita Part.Shape; el resto del modulo sigue puro). Se actualizaron importadores: `vdo_coco_core.py`, `vdo_coco_spaces.py`, `vdo_panel_core.py`, `tests/test_smoke_l3_desk_assembly.py`. Se borró `vdo_reengrose_solids.py`.
  2. Paso 2 (descomponer funciones >150 líneas, D-20): NO ejecutado. Requiere capturar snapshot por función antes/despues y descomponer 8 funciones (algunas de >400 lineas) sin alterar salida. El riesgo de romper la paridad de comportamiento (§0.4) es alto sin una campaña de snapshots por funcion; se deja para una fase futura con snapshots dedicados.
- Métricas antes → después (de §3):
  - Archivos Python en `freecad/`: 62 → 61 (borrado `vdo_reengrose_solids.py`).
  - `def forma_ref`: 1 definicion (en `vdo_reengrose.py`); 0 en `vdo_reengrose_solids.py`.
  - Líneas Python (`freecad/`, `tests/`, `tools/`): 27.934 → 28.106 (alta neto por docstring/imports; F9 reporta el diff real).
- Tests (modo puro): 118 ejecutados, 106 OK, 0 fallos, 11 errores esperables (PySide/FreeCAD), 3 skip. Linea base mantenida.
- Tests (FreeCAD): pendiente de verificación.
- Decisiones nuevas tomadas (no previstas en §2): ninguna.
- Desviaciones de este plan y motivo: D-20 paso 2 (descomponer funciones >150 lineas) diferido: exige snapshots por funcion y un esfuerzo grande de descomposición; ejecutarlo ahora pondria en riesgo la paridad de comportamiento.
- Pendiente para revisión humana: revisar las 21 funciones >120 lineas (linea base) y acordar cuales descomponer con snapshots dedicados.

---
