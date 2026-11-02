# -*- coding: utf-8 -*-
"""Rellena el registro del motor con las piezas de interfaz (D24).

Lo llama InitGui.py al cargar la GUI. Las entradas son cargadores perezosos: el módulo de
cada panel o ViewProvider se importa la primera vez que el motor lo pide.

Claves (las usa core/):
  panel.<tipo>      clase TaskPanel del módulo <tipo>
  vista.<tipo>      fábrica del ViewProvider (recibe ViewObject)
  colocacion.iniciar  función que inicia la colocación con clic
  dialogo.cerrar_activo / dialogo.mostrar  control de TaskPanels de FreeCAD
"""

from freecad.vdo.core.vdo_ui_registry import registrar


def _perezoso(modulo, atributo):
    def cargar():
        import importlib
        return getattr(importlib.import_module(modulo), atributo)
    return cargar


def _vista_coco(vobj):
    """ViewProvider del COCO: arrastre de caras si está disponible; si no, el básico."""
    import FreeCAD as App
    from freecad.vdo.ui.vdo_view_providers import ViewProviderCoco
    try:
        from freecad.vdo.ui.vdo_drag_handles import DragableViewProvider
    except ImportError:
        App.Console.PrintWarning(
            "[VDO] vdo_drag_handles no disponible, usando ViewProvider básico.\n")
        return ViewProviderCoco(vobj)
    return DragableViewProvider(vobj)


def _cerrar_dialogo_activo():
    """Cierra el TaskPanel activo antes de abrir otro (guarda del antiguo macro)."""
    import FreeCADGui as Gui
    try:
        if hasattr(Gui.Control, "activeDialog") and Gui.Control.activeDialog():
            Gui.Control.closeDialog()
    except Exception:
        pass


def _mostrar_dialogo(panel):
    import FreeCADGui as Gui
    Gui.Control.showDialog(panel)


def _cargar_vista(nombre):
    def cargar():
        import importlib
        return getattr(importlib.import_module("freecad.vdo.ui.vdo_view_providers"), nombre)
    return cargar


_registrado = {"hecho": False}


def registrar_piezas():
    """Registra todas las piezas de interfaz. Idempotente."""
    if _registrado["hecho"]:
        return
    registrar("panel.coco", _perezoso("freecad.vdo.ui.vdo_coco_unified_task", "CocoUnifiedTaskPanel"))
    registrar("panel.cajon", _perezoso("freecad.vdo.ui.vdo_cajon_task", "CajonTaskPanel"))
    registrar("panel.panel", _perezoso("freecad.vdo.ui.vdo_panel_task", "PanelTaskPanel"))
    registrar("panel.puerta", _perezoso("freecad.vdo.ui.vdo_puerta_task", "PuertaTaskPanel"))
    registrar("panel.zocalo", _perezoso("freecad.vdo.ui.vdo_zocalo_task", "ZocaloTaskPanel"))

    registrar("vista.coco", lambda: _vista_coco)
    registrar("vista.cajon", _cargar_vista("ViewProviderCajon"))
    registrar("vista.zocalo", _cargar_vista("ViewProviderZocalo"))
    registrar("vista.panel", _cargar_vista("ViewProviderPanel"))
    registrar("vista.puerta", _cargar_vista("ViewProviderPuerta"))

    registrar("colocacion.iniciar", _perezoso("freecad.vdo.ui.vdo_placement", "iniciar_colocacion"))
    registrar("dialogo.cerrar_activo", lambda: _cerrar_dialogo_activo)
    registrar("dialogo.mostrar", lambda: _mostrar_dialogo)
    _registrado["hecho"] = True
