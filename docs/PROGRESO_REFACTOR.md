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
