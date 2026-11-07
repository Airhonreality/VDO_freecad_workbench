"""Base de los ViewProviders VDO (capa de interfaz).

Vive aparte de view_providers.py para que drag_handles.py y coco_unified_task.py
puedan usar la base sin cerrar un ciclo de imports (D-103, U-03).
"""

import logging
import os

import FreeCAD as App

from freecad.vdo.core.paths import ruta_icono

_LOG = logging.getLogger(__name__)


def _gui():
    """FreeCADGui si esta disponible; None si no hay GUI.

    Importacion perezosa: importar este modulo NO carga FreeCADGui (compuerta headless,
    Fase 2). En FreeCADCmd el import de FreeCADGui si tiene exito, por eso no basta con
    try/except al nivel de modulo.
    """
    try:
        import FreeCADGui
        return FreeCADGui
    except ImportError as exc:
        _LOG.debug("view_providers: FreeCADGui no disponible: %s", exc)
        return None


class VDOViewProviderBase:
    """Base para ViewProviders de módulos paramétricos VDO."""

    MENU_LABEL = "Propiedades del módulo"
    ICON = None

    def __init__(self, vobj):
        vobj.Proxy = self
        self.Object = vobj.Object
        self.vobj = vobj

    # -----------------------------------------------------------------
    # Ciclo de vida
    # -----------------------------------------------------------------
    def attach(self, vobj):
        self.Object = vobj.Object
        self.vobj = vobj
        return

    def getIcon(self):
        if self.ICON:
            icon_path = str(ruta_icono(self.ICON))
            if os.path.exists(icon_path):
                return icon_path
        return "Part_Box"

    # -----------------------------------------------------------------
    # Acceso al panel
    # -----------------------------------------------------------------
    def get_panel_class(self):
        raise NotImplementedError(
            "El ViewProvider VDO debe implementar get_panel_class()")

    def _crear_panel(self, obj):
        panel_cls = self.get_panel_class()
        return panel_cls(obj)

    def _abrir_panel(self, obj=None):
        obj = obj or self.Object
        if obj is None or _gui() is None:
            return False
        # Sincronizar y enfocar el Inspector Universal lateral
        enfocar_inspector_universal(obj)
        try:
            panel = self._crear_panel(obj)
            _gui().Control.showDialog(panel)
            return True
        except Exception as exc:
            App.Console.PrintError(
                f"[VDO] Error abriendo panel de propiedades: {exc}\n")
            import traceback
            App.Console.PrintError(traceback.format_exc())
            try:
                from freecad.vdo.qt_compat import QtGui, QtWidgets
                QtWidgets.QMessageBox.critical(
                    None, "VDO",
                    f"No se pudo abrir el panel de {obj.Name}:\n{exc}")
            except Exception:
                App.Console.PrintWarning(
                    "[VDO] No se pudo mostrar el diálogo de error")
            return False

    # -----------------------------------------------------------------
    # Clic derecho
    # -----------------------------------------------------------------
    def setupContextMenu(self, vobj, menu):
        try:
            action = menu.addAction(self.MENU_LABEL)
            action.triggered.connect(
                lambda checked=False, o=vobj.Object: self._abrir_panel(o))
            return False
        except Exception as exc:
            App.Console.PrintWarning(
                f"[VDO] No se pudo crear el menú contextual: {exc}\n")
            return False

    # -----------------------------------------------------------------
    # Doble clic / edición
    # -----------------------------------------------------------------
    def doubleClicked(self, vobj):
        # Si el Inspector Universal está activo, enfocarlo y retornar sin abrir dialogos secundarios
        if enfocar_inspector_universal(getattr(vobj, "Object", None)):
            return True
        return self._abrir_panel(vobj.Object)

    def setEdit(self, vobj, mode):
        if mode != 0:
            return False
        if _gui() is None:
            return False
        # Si el Inspector Universal está activo, enfocarlo y retornar sin abrir dialogos secundarios
        if enfocar_inspector_universal(getattr(vobj, "Object", None)):
            return True
        try:
            panel = self._crear_panel(vobj.Object)
            _gui().Control.showDialog(panel)
            return True
        except Exception as exc:
            App.Console.PrintError(
                f"[VDO] Error abriendo editor: {exc}\n")
            import traceback
            App.Console.PrintError(traceback.format_exc())
            return False

    def unsetEdit(self, vobj, mode):
        if _gui() is not None:
            try:
                _gui().Control.closeDialog()
            except Exception:
                App.Console.PrintWarning(
                    "[VDO] No se pudo cerrar el diálogo activo")
        return True

    # -----------------------------------------------------------------
    # Compatibilidad
    # -----------------------------------------------------------------
    def claimChildren(self):
        return []

    def dumps(self):
        return None

    def loads(self, state):
        return None


def enfocar_inspector_universal(obj):
    """
    Enfoca el QDockWidget del Inspector Universal y sincroniza la vista
    según el objeto seleccionado.
    """
    if obj is None or _gui() is None or not getattr(App, "GuiUp", False):
        return False
    try:
        from freecad.vdo.ui.inspector_dock import obtener_o_crear_dock_inspector
        dock = obtener_o_crear_dock_inspector()
        if dock is not None:
            dock.show()
            dock.raise_()
            inspector = dock.widget()
            if inspector is not None:
                from freecad.vdo.ui.selection_bridge import VDOSelectionBridge
                tipo = VDOSelectionBridge.classify_object(obj)
                if hasattr(inspector, "_on_selection_changed"):
                    inspector._on_selection_changed(obj, tipo)
                return True
    except Exception as exc:
        App.Console.PrintWarning(f"[VDO] Aviso al enfocar Inspector Universal: {exc}\n")
    return False


class ViewProviderCajon(VDOViewProviderBase):
    """ViewProvider del cajón FeaturePython (Trinidad v2)."""

    MENU_LABEL = "Propiedades del Cajón"
    ICON = "vdo_cajon.svg"

    def __init__(self, vobj):
        super().__init__(vobj)
        try:
            vobj.Visibility = True
        except Exception:
            App.Console.PrintWarning(
                "[VDO] No se pudo establecer la visibilidad del objeto")

    def get_panel_class(self):
        from freecad.vdo.ui.cajon_task import CajonTaskPanel
        return CajonTaskPanel


class ViewProviderPuerta(VDOViewProviderBase):
    MENU_LABEL = "Propiedades de la Puerta"
    ICON = "vdo_puerta.svg"

    def get_panel_class(self):
        from freecad.vdo.ui.puerta_task import PuertaTaskPanel
        return PuertaTaskPanel
