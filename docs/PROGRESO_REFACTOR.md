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
- Desviaciones de este plan y motivo: ninguna. El test `test_extirpacion_combos_planos_en_coco_task` ya usaba `vdo_coco_unified_task.py`, no el borrado `vdo_coco_task.py`.
- Pendiente para revisión humana: ninguna.

---
