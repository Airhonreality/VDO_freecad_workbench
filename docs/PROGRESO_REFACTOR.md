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


---
