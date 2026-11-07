"""ViewProviders VDO y acceso a paneles/Inspector (capa de interfaz).

Movido desde core/ (D24): un ViewProvider es código de GUI de FreeCAD. El motor lo pide
por el registro (core/vdo_ui_registry.py) y no lo importa.
"""

import FreeCAD as App

from freecad.vdo.core.view_base import _es_cajon, _es_coco, _es_panel, _es_zocalo
from freecad.vdo.ui.view_provider_base import (
    VDOViewProviderBase,
    ViewProviderCajon,
    _gui,
    enfocar_inspector_universal,
)


def reparar_viewprovider(obj):
    """Reinstala el ViewProvider VDO si el objeto perdió su proxy."""
    if obj is None or _gui() is None:
        return None
    try:
        vp = obj.ViewObject
    except Exception as exc:
        App.Console.PrintWarning(f"[VDO] view_providers: ViewProvider no creado, devuelve None: {exc}\n")
        return None
    if vp is None:
        return None
    proxy = getattr(vp, "Proxy", None)
    if hasattr(proxy, "_abrir_panel") and hasattr(proxy, "get_panel_class"):
        return proxy

    try:
        if _es_coco(obj):
            try:
                from freecad.vdo.ui.drag_handles import DragableViewProvider
                return DragableViewProvider(vp)
            except Exception as exc:
                App.Console.PrintWarning(f"[VDO] view_providers: DragableViewProvider fallido, usa ViewProviderCoco: {exc}\n")
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
            from freecad.vdo.ui.coco_unified_task import CocoUnifiedTaskPanel
            panel = CocoUnifiedTaskPanel(obj)
        elif _es_cajon(obj):
            from freecad.vdo.ui.cajon_task import CajonTaskPanel
            panel = CajonTaskPanel(obj)
        elif _es_zocalo(obj):
            from freecad.vdo.ui.zocalo_task import ZocaloTaskPanel
            panel = ZocaloTaskPanel(obj)
        elif _es_panel(obj):
            from freecad.vdo.ui.panel_task import PanelTaskPanel
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


def panel_coco_unificado():
    """Panel de edición del COCO (fuente única para ViewProviders y handles 3D)."""
    from freecad.vdo.ui.coco_unified_task import CocoUnifiedTaskPanel
    return CocoUnifiedTaskPanel


class ViewProviderCoco(VDOViewProviderBase):
    """ViewProvider de respaldo para el COCO FeaturePython."""

    MENU_LABEL = "Propiedades del COCO"
    ICON = "vdo_coco.svg"

    def get_panel_class(self):
        return panel_coco_unificado()

    def setEdit(self, vobj, mode):
        enfocar_inspector_universal(getattr(vobj, "Object", None))
        return super().setEdit(vobj, mode)

    def doubleClicked(self, vobj):
        enfocar_inspector_universal(getattr(vobj, "Object", None))
        return super().doubleClicked(vobj)


class ViewProviderZocalo(VDOViewProviderBase):
    """ViewProvider del zócalo FeaturePython."""

    MENU_LABEL = "Propiedades del Zócalo"
    ICON = "vdo_zocalo.svg"

    def get_panel_class(self):
        from freecad.vdo.ui.zocalo_task import ZocaloTaskPanel
        return ZocaloTaskPanel


class ViewProviderPanel(VDOViewProviderBase):
    """ViewProvider del panel VDO."""

    MENU_LABEL = "Propiedades del Panel"
    ICON = "vdo_panel.svg"

    def get_panel_class(self):
        from freecad.vdo.ui.panel_task import PanelTaskPanel
        return PanelTaskPanel
