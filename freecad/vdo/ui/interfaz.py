"""ui/interfaz.py — adaptador de interfaz para el caso de uso de creación.

app/vdo_creacion.crear_modulo_interactivo recibe dos funciones por parámetro:
abrir_panel y colocar. Este módulo las implementa con los paneles TaskPanel
y la colocación con clic de ui/. commands.py lo pasa al caso de uso.

No importa core/ ni cad/: la spec llega desde app/ y el panel se resuelve
aquí por su referencia textual (panel.<tipo>), igual que en b78de04.
"""

from __future__ import annotations

import importlib

# Referencia de panel de core/module_specs -> (módulo ui, clase TaskPanel).
_PANELES = {
    "panel.coco": ("freecad.vdo.ui.coco_unified_task", "CocoUnifiedTaskPanel"),
    "panel.cajon": ("freecad.vdo.ui.cajon_task", "CajonTaskPanel"),
    "panel.panel": ("freecad.vdo.ui.panel_task", "PanelTaskPanel"),
    "panel.puerta": ("freecad.vdo.ui.puerta_task", "PuertaTaskPanel"),
    "panel.zocalo": ("freecad.vdo.ui.zocalo_task", "ZocaloTaskPanel"),
}


def _clase_panel(referencia: str):
    if referencia not in _PANELES:
        raise KeyError(f"Panel desconocido: {referencia}")
    modulo, clase = _PANELES[referencia]
    return getattr(importlib.import_module(modulo), clase)


def abrir_panel(spec, obj, on_accept, on_cancel):
    """Muestra el TaskPanel del módulo. Cierra antes el panel activo."""
    import FreeCADGui as Gui

    clase = _clase_panel(spec["panel_ref"])
    if Gui.Control.activeDialog():
        Gui.Control.closeDialog()
    panel = clase(obj, on_accept=on_accept, on_cancel=on_cancel,
                  auto_transaction=False)
    Gui.Control.showDialog(panel)


def colocar(obj, on_done, on_cancel):
    """Inicia la colocación con clic (ui/placement)."""
    from freecad.vdo.ui.placement import iniciar_colocacion

    return iniciar_colocacion(obj, on_done=on_done, on_cancel=on_cancel)
