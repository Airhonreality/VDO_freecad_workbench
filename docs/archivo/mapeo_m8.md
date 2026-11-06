# Mapeo M8: renombrado de módulos vdo_* (MN-09, D-77)

Archivos renombrados con `git mv`: 65. Excluidos por colisión, paquete existente o palabra reservada: ninguno.

Fuera del renombrado:
- `tools/auditoria/verificar.py`: congelado (referencia). Contiene `f"vdo_{nombre}.py"` en la línea 241 y dejará de encontrar los archivos.
- `freecad/vdo/datos/modulos.json` y `tests/golden/module_specs.json`: sin cambios, porque ninguna ruta `factory` usa un módulo `vdo_*`.
- Archivos de documentación histórica (`docs/archivo`, `docs/adr`, registros de decisiones y planes): sin reescritura.
- Nombres de datos y recursos que no son módulos (`vdo_manifest.json`, `vdo_hardware_catalog.json`, iconos `vdo_*.svg`, CSV) y atributos `_vdo_*`: sin cambio.

| Antes | Después |
|---|---|
| `freecad/vdo/core/vdo_cajon_autotest.py` | `freecad/vdo/core/cajon_autotest.py` |
| `freecad/vdo/core/vdo_cajon_calculo.py` | `freecad/vdo/core/cajon_calculo.py` |
| `freecad/vdo/core/vdo_cajon_correderas.py` | `freecad/vdo/core/cajon_correderas.py` |
| `freecad/vdo/core/vdo_coco_core.py` | `freecad/vdo/core/coco_core.py` |
| `freecad/vdo/core/vdo_coco_spaces.py` | `freecad/vdo/core/coco_spaces.py` |
| `freecad/vdo/core/vdo_coco_spaces_bloques.py` | `freecad/vdo/core/coco_spaces_bloques.py` |
| `freecad/vdo/core/vdo_defaults.py` | `freecad/vdo/core/defaults.py` |
| `freecad/vdo/core/vdo_facade_contract.py` | `freecad/vdo/core/facade_contract.py` |
| `freecad/vdo/core/vdo_finish.py` | `freecad/vdo/core/finish.py` |
| `freecad/vdo/core/vdo_frames.py` | `freecad/vdo/core/frames.py` |
| `freecad/vdo/core/vdo_hardware_hub.py` | `freecad/vdo/core/hardware_hub.py` |
| `freecad/vdo/core/vdo_helpers.py` | `freecad/vdo/core/helpers.py` |
| `freecad/vdo/core/vdo_layout_matriz.py` | `freecad/vdo/core/layout_matriz.py` |
| `freecad/vdo/core/vdo_layout_modelo.py` | `freecad/vdo/core/layout_modelo.py` |
| `freecad/vdo/core/vdo_layout_resolucion.py` | `freecad/vdo/core/layout_resolucion.py` |
| `freecad/vdo/core/vdo_layout_resuelto.py` | `freecad/vdo/core/layout_resuelto.py` |
| `freecad/vdo/core/vdo_manifest.py` | `freecad/vdo/core/manifest.py` |
| `freecad/vdo/core/vdo_module_props.py` | `freecad/vdo/core/module_props.py` |
| `freecad/vdo/core/vdo_module_specs.py` | `freecad/vdo/core/module_specs.py` |
| `freecad/vdo/core/vdo_nesting_presets.py` | `freecad/vdo/core/nesting_presets.py` |
| `freecad/vdo/core/vdo_optimizer_core.py` | `freecad/vdo/core/optimizer_core.py` |
| `freecad/vdo/core/vdo_panel_core.py` | `freecad/vdo/core/panel_core.py` |
| `freecad/vdo/core/vdo_paths.py` | `freecad/vdo/core/paths.py` |
| `freecad/vdo/core/vdo_puerta_despiece.py` | `freecad/vdo/core/puerta_despiece.py` |
| `freecad/vdo/core/vdo_reengrose_despiece.py` | `freecad/vdo/core/reengrose_despiece.py` |
| `freecad/vdo/core/vdo_reengrose_encuentros.py` | `freecad/vdo/core/reengrose_encuentros.py` |
| `freecad/vdo/core/vdo_reengrose_geometria.py` | `freecad/vdo/core/reengrose_geometria.py` |
| `freecad/vdo/core/vdo_reengrose_interferencias.py` | `freecad/vdo/core/reengrose_interferencias.py` |
| `freecad/vdo/core/vdo_reengrose_modelo.py` | `freecad/vdo/core/reengrose_modelo.py` |
| `freecad/vdo/core/vdo_reengrose_modificador.py` | `freecad/vdo/core/reengrose_modificador.py` |
| `freecad/vdo/core/vdo_reengrose_tiras.py` | `freecad/vdo/core/reengrose_tiras.py` |
| `freecad/vdo/core/vdo_spaces.py` | `freecad/vdo/core/spaces.py` |
| `freecad/vdo/core/vdo_view_base.py` | `freecad/vdo/core/view_base.py` |
| `freecad/vdo/core/vdo_zocalo_core.py` | `freecad/vdo/core/zocalo_core.py` |
| `freecad/vdo/ui/vdo_bim_bridge.py` | `freecad/vdo/ui/bim_bridge.py` |
| `freecad/vdo/ui/vdo_box_controller.py` | `freecad/vdo/ui/box_controller.py` |
| `freecad/vdo/ui/vdo_cajon_task.py` | `freecad/vdo/ui/cajon_task.py` |
| `freecad/vdo/ui/vdo_chassis_widget.py` | `freecad/vdo/ui/chassis_widget.py` |
| `freecad/vdo/ui/vdo_coco_preview2d.py` | `freecad/vdo/ui/coco_preview2d.py` |
| `freecad/vdo/ui/vdo_coco_unified_task.py` | `freecad/vdo/ui/coco_unified_task.py` |
| `freecad/vdo/ui/vdo_cutting_list_menu.py` | `freecad/vdo/ui/cutting_list_menu.py` |
| `freecad/vdo/ui/vdo_cutting_list_preview.py` | `freecad/vdo/ui/cutting_list_preview.py` |
| `freecad/vdo/ui/vdo_drag_handles.py` | `freecad/vdo/ui/drag_handles.py` |
| `freecad/vdo/ui/vdo_export_cutting_list.py` | `freecad/vdo/ui/export_cutting_list.py` |
| `freecad/vdo/ui/vdo_form_builder.py` | `freecad/vdo/ui/form_builder.py` |
| `freecad/vdo/ui/vdo_hardware_manager.py` | `freecad/vdo/ui/hardware_manager.py` |
| `freecad/vdo/ui/vdo_inspector_dock.py` | `freecad/vdo/ui/inspector_dock.py` |
| `freecad/vdo/ui/vdo_interfaz.py` | `freecad/vdo/ui/interfaz.py` |
| `freecad/vdo/ui/vdo_nesting_workflow.py` | `freecad/vdo/ui/nesting_workflow.py` |
| `freecad/vdo/ui/vdo_optimizer_dialog.py` | `freecad/vdo/ui/optimizer_dialog.py` |
| `freecad/vdo/ui/vdo_optimizer_preview.py` | `freecad/vdo/ui/optimizer_preview.py` |
| `freecad/vdo/ui/vdo_optimizer_view.py` | `freecad/vdo/ui/optimizer_view.py` |
| `freecad/vdo/ui/vdo_panel_task.py` | `freecad/vdo/ui/panel_task.py` |
| `freecad/vdo/ui/vdo_placement.py` | `freecad/vdo/ui/placement.py` |
| `freecad/vdo/ui/vdo_plano_cero.py` | `freecad/vdo/ui/plano_cero.py` |
| `freecad/vdo/ui/vdo_puerta_task.py` | `freecad/vdo/ui/puerta_task.py` |
| `freecad/vdo/ui/vdo_qt.py` | `freecad/vdo/ui/qt.py` |
| `freecad/vdo/ui/vdo_reengrose_ui.py` | `freecad/vdo/ui/reengrose_ui.py` |
| `freecad/vdo/ui/vdo_registro.py` | `freecad/vdo/ui/registro.py` |
| `freecad/vdo/ui/vdo_selection_bridge.py` | `freecad/vdo/ui/selection_bridge.py` |
| `freecad/vdo/ui/vdo_task_base.py` | `freecad/vdo/ui/task_base.py` |
| `freecad/vdo/ui/vdo_universal_inspector.py` | `freecad/vdo/ui/universal_inspector.py` |
| `freecad/vdo/ui/vdo_view_providers.py` | `freecad/vdo/ui/view_providers.py` |
| `freecad/vdo/ui/vdo_zocalo_task.py` | `freecad/vdo/ui/zocalo_task.py` |
| `freecad/vdo/cad/vdo_guardian.py` | `freecad/vdo/cad/guardian.py` |
