# Matriz de mapeo: Macro/ → estructura objetivo

> **Histórica.** Describe el estado de `Macro/` antes de la Fase 3, cuando el código aún estaba allí. `tools/matriz_mapeo.py` lee `Macro/`, que ya no existe; para regenerarla hace falta un checkout de `HEAD` anterior a la migración.

Generada por `tools/matriz_mapeo.py` (no editar a mano). Lee los imports reales con `ast`.

Capa: **CORE** = sin GUI a nivel de módulo (candidato a `freecad/vdo/core/`). **UI** = toca GUI/Qt a nivel de módulo o es un TaskPanel/widget (candidato a `freecad/vdo/ui/`).

| Módulo | Capa | GUI a nivel de módulo | Imports internos (nivel módulo + diferidos) | Imports GUI detectados |
|---|---|---|---|---|
| vdo_box_controller | UI | **sí** | vdo_qt, vdo_reengrose | PySide |
| vdo_cajon_core | CORE | no | vdo_cajon_despiece, vdo_cajon_task, vdo_defaults, vdo_facade_contract, vdo_guardian, vdo_hardware_hub, vdo_module_props, vdo_view_base | — |
| vdo_cajon_despiece | CORE | no | vdo_facade_contract, vdo_hardware_hub | — |
| vdo_cajon_task | UI | **sí** | vdo_cajon_despiece, vdo_facade_contract, vdo_hardware_hub, vdo_module_props, vdo_qt, vdo_task_base | FreeCADGui, PySide |
| vdo_chassis_widget | UI | **sí** | vdo_qt | PySide |
| vdo_clone | CORE | no | — | — |
| vdo_coco_core | CORE | no | vdo_coco_spaces, vdo_coco_unified_task, vdo_defaults, vdo_drag_handles, vdo_finish, vdo_frames, vdo_guardian, vdo_layout, vdo_module_props, vdo_reengrose, vdo_reengrose_solids, vdo_view_base | — |
| vdo_coco_divisions_task | UI | **sí** | vdo_box_controller, vdo_cajon_core, vdo_coco_preview2d, vdo_defaults, vdo_facade_contract, vdo_finish, vdo_frames, vdo_layout, vdo_puerta_core, vdo_reengrose | PySide |
| vdo_coco_preview2d | UI | **sí** | vdo_facade_contract, vdo_frames, vdo_reengrose | PySide |
| vdo_coco_spaces | CORE | no | vdo_layout, vdo_reengrose, vdo_reengrose_solids | — |
| vdo_coco_spaces_task | UI | **sí** | vdo_spaces | FreeCADGui, PySide |
| vdo_coco_task | UI | **sí** | — | FreeCADGui, PySide |
| vdo_coco_unified_task | UI | **sí** | vdo_cajon_core, vdo_cajon_despiece, vdo_chassis_widget, vdo_coco_divisions_task, vdo_facade_contract, vdo_frames, vdo_module_props, vdo_puerta_core, vdo_qt, vdo_spaces, vdo_task_base | FreeCADGui, PySide |
| vdo_creation_flow | CORE | no | vdo_guardian, vdo_module_props, vdo_module_specs, vdo_placement, vdo_view_base | FreeCADGui |
| vdo_cutting_list_preview | UI | **sí** | vdo_export_cutting_list, vdo_loader | FreeCADGui, PySide2 |
| vdo_defaults | CORE | no | — | — |
| vdo_detect_config | CORE | no | — | — |
| vdo_drag_handles | UI | **sí** | vdo_coco_unified_task, vdo_view_base | FreeCADGui |
| vdo_export_cutting_list | UI | **sí** | vdo_cutting_list_preview, vdo_loader, vdo_reengrose | FreeCADGui |
| vdo_facade_contract | CORE | no | — | — |
| vdo_finish | CORE | no | vdo_frames | — |
| vdo_frames | CORE | no | — | — |
| vdo_guardian | CORE | no | vdo_manifest | — |
| vdo_hardware_hub | CORE | no | — | — |
| vdo_hardware_manager | UI | **sí** | vdo_hardware_hub, vdo_qt | PySide |
| vdo_inspector_dock | UI | **sí** | vdo_universal_inspector | FreeCADGui, PySide6 |
| vdo_install | UI | **sí** | vdo_paths, vdo_toolbar_inject | FreeCADGui |
| vdo_layout | CORE | no | vdo_reengrose | — |
| vdo_loader | CORE | no | — | — |
| vdo_manifest | CORE | no | — | — |
| vdo_module_props | CORE | no | vdo_frames | — |
| vdo_module_specs | CORE | no | — | — |
| vdo_nesting_presets | CORE | no | — | — |
| vdo_nesting_workflow | UI | **sí** | vdo_nesting_presets | FreeCADGui, PySide2 |
| vdo_optimizer_core | CORE | no | vdo_defaults, vdo_optimizer_preview | — |
| vdo_optimizer_preview | UI | no | — | — |
| vdo_optimizer_view | UI | **sí** | vdo_optimizer_core | PySide2 |
| vdo_panel_core | CORE | no | vdo_defaults, vdo_guardian, vdo_module_props, vdo_panel_task, vdo_reengrose, vdo_reengrose_solids, vdo_view_base | — |
| vdo_panel_task | UI | **sí** | vdo_defaults, vdo_module_props, vdo_panel_core, vdo_qt, vdo_reengrose, vdo_reengrose_ui, vdo_task_base | PySide |
| vdo_paths | CORE | no | — | — |
| vdo_placement | UI | **sí** | vdo_module_props | FreeCADGui |
| vdo_publish | CORE | no | vdo_paths, vdo_toolbar_inject | — |
| vdo_puerta_core | CORE | no | vdo_facade_contract, vdo_module_props, vdo_puerta_despiece, vdo_puerta_task, vdo_view_base | — |
| vdo_puerta_despiece | CORE | no | vdo_facade_contract, vdo_hardware_hub | — |
| vdo_puerta_task | UI | **sí** | vdo_hardware_hub, vdo_module_props, vdo_puerta_despiece, vdo_qt, vdo_task_base | PySide |
| vdo_qt | UI | **sí** | — | PySide |
| vdo_reengrose | CORE | no | — | — |
| vdo_reengrose_solids | CORE | no | — | — |
| vdo_reengrose_ui | UI | **sí** | vdo_qt, vdo_reengrose | PySide |
| vdo_selection_bridge | UI | **sí** | — | FreeCADGui |
| vdo_spaces | CORE | no | — | — |
| vdo_sync | CORE | no | vdo_paths, vdo_toolbar_inject | — |
| vdo_sync_config | CORE | no | — | — |
| vdo_task_base | UI | **sí** | — | FreeCADGui, PySide |
| vdo_toolbar_inject | CORE | no | vdo_paths | FreeCADGui |
| vdo_toolbar_test | UI | **sí** | — | FreeCADGui |
| vdo_universal_inspector | UI | **sí** | vdo_box_controller, vdo_chassis_widget, vdo_coco_preview2d, vdo_hardware_hub, vdo_inspector_dock, vdo_layout, vdo_qt, vdo_selection_bridge | FreeCADGui, PySide6 |
| vdo_view_base | UI | **sí** | vdo_cajon_core, vdo_cajon_task, vdo_coco_unified_task, vdo_drag_handles, vdo_panel_core, vdo_panel_task, vdo_selection_bridge, vdo_universal_inspector, vdo_zocalo_core, vdo_zocalo_task | FreeCADGui |
| vdo_zocalo_core | CORE | no | vdo_defaults, vdo_guardian, vdo_layout, vdo_module_props, vdo_reengrose, vdo_view_base, vdo_zocalo_task | — |
| vdo_zocalo_task | UI | **sí** | vdo_coco_divisions_task, vdo_module_props, vdo_qt, vdo_task_base, vdo_zocalo_core | PySide |

**Totales:** 60 módulos; CORE: 32; UI: 28.

**Incumplimientos de headless en CORE (debe estar vacío):** ninguno
