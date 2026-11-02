# -*- coding: utf-8 -*-
"""ViewProviders VDO y acceso a paneles/Inspector (capa de interfaz).

Movido desde core/ (D24): un ViewProvider es código de GUI de FreeCAD. El motor lo pide
por el registro (core/vdo_ui_registry.py) y no lo importa.
"""

import os

import FreeCAD as App

from freecad.vdo.app.vdo_api import ruta_icono
from freecad.vdo.app.vdo_api import _es_coco, _es_cajon, _es_zocalo, _es_panel


def _gui():
    """FreeCADGui si esta disponible; None si no hay GUI.

    Importacion perezosa: importar este modulo NO carga FreeCADGui (compuerta headless,
    Fase 2). En FreeCADCmd el import de FreeCADGui si tiene exito, por eso no basta con
    try/except al nivel de modulo.
    """
    try:
        import FreeCADGui
        return FreeCADGui
    except ImportError:
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


def reparar_viewprovider(obj):
    """Reinstala el ViewProvider VDO si el objeto perdió su proxy."""
    if obj is None or _gui() is None:
        return None
    try:
        vp = obj.ViewObject
    except Exception:
        return None
    if vp is None:
        return None
    proxy = getattr(vp, "Proxy", None)
    if hasattr(proxy, "_abrir_panel") and hasattr(proxy, "get_panel_class"):
        return proxy

    try:
        if _es_coco(obj):
            try:
                from freecad.vdo.ui.vdo_drag_handles import DragableViewProvider
                return DragableViewProvider(vp)
            except Exception:
                return ViewProviderCoco(vp)
        if _es_cajon(obj):
            return ViewProviderCajon(vp)
        if _es_zocalo(obj):
            return ViewProviderZocalo(vp)
        if _es_panel(obj):
            return ViewProviderPanel(vp)
    except Exception as exc:
        App.Console.PrintError(
            f"[VDO] No se pudo reparar ViewProvider de {obj.Name}: {exc}\n")
    return None


def enfocar_inspector_universal(obj):
    """
    Enfoca el QDockWidget del Inspector Universal y sincroniza la vista
    según el objeto seleccionado.
    """
    if obj is None or _gui() is None or not getattr(App, "GuiUp", False):
        return False
    try:
        from freecad.vdo.ui.vdo_inspector_dock import obtener_o_crear_dock_inspector
        dock = obtener_o_crear_dock_inspector()
        if dock is not None:
            dock.show()
            dock.raise_()
            inspector = dock.widget()
            if inspector is not None:
                from freecad.vdo.ui.vdo_selection_bridge import VDOSelectionBridge
                tipo = VDOSelectionBridge.classify_object(obj)
                if hasattr(inspector, "_on_selection_changed"):
                    inspector._on_selection_changed(obj, tipo)
                return True
    except Exception as exc:
        App.Console.PrintWarning(f"[VDO] Aviso al enfocar Inspector Universal: {exc}\n")
    return False


def abrir_panel_objeto(obj):
    """Abre el panel de cualquier módulo VDO, reparando el proxy si hace falta."""
    if obj is None:
        return False
    # Si el Inspector Universal está disponible, enfocarlo y no abrir diálogos secundarios flotantes
    if enfocar_inspector_universal(obj):
        return True
    proxy = getattr(getattr(obj, "ViewObject", None), "Proxy", None)
    if not hasattr(proxy, "_abrir_panel"):
        proxy = reparar_viewprovider(obj)
    if proxy is not None and hasattr(proxy, "_abrir_panel"):
        return proxy._abrir_panel(obj)

    # Último recurso: panel directo según las propiedades del objeto.
    try:
        if _es_coco(obj):
            from freecad.vdo.ui.vdo_coco_unified_task import CocoUnifiedTaskPanel
            panel = CocoUnifiedTaskPanel(obj)
        elif _es_cajon(obj):
            from freecad.vdo.ui.vdo_cajon_task import CajonTaskPanel
            panel = CajonTaskPanel(obj)
        elif _es_zocalo(obj):
            from freecad.vdo.ui.vdo_zocalo_task import ZocaloTaskPanel
            panel = ZocaloTaskPanel(obj)
        elif _es_panel(obj):
            from freecad.vdo.ui.vdo_panel_task import PanelTaskPanel
            panel = PanelTaskPanel(obj)
        else:
            App.Console.PrintWarning(
                f"[VDO] {obj.Name} no parece un módulo VDO.\n")
            return False
        _gui().Control.showDialog(panel)
        return True
    except Exception as exc:
        App.Console.PrintError(
            f"[VDO] No se pudo abrir el panel de {obj.Name}: {exc}\n")
        import traceback
        App.Console.PrintError(traceback.format_exc())
        return False


class ViewProviderCoco(VDOViewProviderBase):
    """ViewProvider de respaldo para el COCO FeaturePython."""

    MENU_LABEL = "Propiedades del COCO"
    ICON = "vdo_coco.svg"

    def get_panel_class(self):
        from freecad.vdo.ui.vdo_coco_unified_task import CocoUnifiedTaskPanel
        return CocoUnifiedTaskPanel

    def setEdit(self, vobj, mode):
        enfocar_inspector_universal(getattr(vobj, "Object", None))
        return super().setEdit(vobj, mode)

    def doubleClicked(self, vobj):
        enfocar_inspector_universal(getattr(vobj, "Object", None))
        return super().doubleClicked(vobj)


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
        from freecad.vdo.ui.vdo_cajon_task import CajonTaskPanel
        return CajonTaskPanel


class ViewProviderZocalo(VDOViewProviderBase):
    """ViewProvider del zócalo FeaturePython."""

    MENU_LABEL = "Propiedades del Zócalo"
    ICON = "vdo_zocalo.svg"

    def get_panel_class(self):
        from freecad.vdo.ui.vdo_zocalo_task import ZocaloTaskPanel
        return ZocaloTaskPanel


class ViewProviderPanel(VDOViewProviderBase):
    """ViewProvider del panel VDO."""

    MENU_LABEL = "Propiedades del Panel"
    ICON = "vdo_panel.svg"

    def get_panel_class(self):
        from freecad.vdo.ui.vdo_panel_task import PanelTaskPanel
        return PanelTaskPanel


class ViewProviderPuerta(VDOViewProviderBase):
    MENU_LABEL = "Propiedades de la Puerta"
    ICON = "vdo_puerta.svg"

    def get_panel_class(self):
        from freecad.vdo.ui.vdo_puerta_task import PuertaTaskPanel
        return PuertaTaskPanel
