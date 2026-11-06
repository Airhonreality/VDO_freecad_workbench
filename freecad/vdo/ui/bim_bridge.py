"""Puente VDO → BIM (integración opcional, "Opción C" de la investigación).

VDO sigue siendo un workbench autónomo. Además, cuando BIM está activo, añade al menú
Archivo la entrada «Nuevo proyecto VDO» (comando VDO_AbrirVDO).

Mecanismo: Gui.addWorkbenchManipulator (la API que usa BIM en BIM/InitGui.py).
Problema: el manipulador se consulta al montar los menús, y no sabemos si el workbench
activo ya ha cambiado en ese momento. Solución: un estado propio que se actualiza con la
señal workbenchActivated de la ventana principal (la señal se emite con el workbench ya
activo; así lo usa Tux/PersistentToolbarsGui.py). Si el estado cambia, se recarga el
workbench activo para que sus menús se reconstruyan con el estado correcto.

Si la API no existe, no se añade nada y se avisa en consola; VDO sigue funcionando.
"""

import FreeCAD as App

from freecad.vdo.qt_compat import QtCore

_NOMBRE_BIM = "BIMWorkbench"  # nombre de clase de BIM/InitGui.py


class EstadoBim:
    """Estado de la integración BIM (encapsulado, no es variable suelta de módulo)."""

    def __init__(self):
        self.bim = False
        self.conexiones = []


ESTADO_BIM = EstadoBim()


def _nombre_workbench_activo():
    import FreeCADGui as Gui
    wb = Gui.activeWorkbench()
    return type(wb).__name__ if wb is not None else ""


class ManipuladorBIM:
    """Manipulador de workbench: añade la entrada VDO en el menú Archivo de BIM."""

    def modifyMenuBar(self):
        if not ESTADO_BIM.bim:
            return []
        # Misma forma que usa BIM en BIM/InitGui.py (BIM_WBManipulator.modifyMenuBar).
        return [{"insert": "VDO_AbrirVDO", "menuItem": "Std_New", "after": ""}]


def _al_cambiar_workbench(*_args):
    """Actualiza el estado y, si cambia, recarga el workbench activo en el siguiente ciclo."""
    try:
        nuevo = _nombre_workbench_activo() == _NOMBRE_BIM
    except Exception as exc:
        App.Console.PrintWarning(f"[VDO] bim_bridge: estado BIM no leido, sin cambio: {exc}\n")
        return
    if nuevo == ESTADO_BIM.bim:
        return
    ESTADO_BIM.bim = nuevo
    QtCore.QTimer.singleShot(0, _recargar_activo)


def _recargar_activo():
    try:
        import FreeCADGui as Gui
        wb = Gui.activeWorkbench()
        if wb is not None and hasattr(wb, "reloadActive"):
            wb.reloadActive()
    except Exception as exc:
        App.Console.PrintWarning(f"[VDO] No se pudo recargar menús tras cambiar a BIM: {exc}\n")


def registrar_integracion_bim():
    """Registra el manipulador y la señal. Llamar desde InitGui.py, tras register_all()."""
    try:
        import FreeCADGui as Gui
        if getattr(Gui, "VDO_BIMManipulator", None) is None:
            Gui.VDO_BIMManipulator = ManipuladorBIM()
        Gui.addWorkbenchManipulator(Gui.VDO_BIMManipulator)
        mw = Gui.getMainWindow()
        if mw is not None and not ESTADO_BIM.conexiones:
            mw.workbenchActivated.connect(_al_cambiar_workbench)
            ESTADO_BIM.conexiones.append(_al_cambiar_workbench)
        ESTADO_BIM.bim = _nombre_workbench_activo() == _NOMBRE_BIM
        return True
    except Exception as exc:  # no bloquear la carga de VDO por la integración
        App.Console.PrintWarning(f"[VDO] Integración con BIM no disponible: {exc}\n")
        return False
