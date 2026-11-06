# =====================================================================
# view_base.py
# Utilidades de clasificación de objetos VDO para el motor (sin GUI).
#
# Los ViewProviders y el acceso a paneles/Inspector viven en
# freecad/vdo/ui/view_providers.py (D24): el motor los pide por
# core/vdo_ui_registry.py y no los importa.
#
# Nota: este modulo es puro (no importa FreeCAD). diagnostico_viewprovider
# accede a atributos del objeto pasado por el llamador (UI/comandos),
# no importa FreeCAD a nivel de modulo.
# =====================================================================

from typing import Any

# obj: objeto FreeCAD con atributos dinamicos, sin tipo estatico (Any)


def _es_coco(obj: Any) -> bool:
    return (hasattr(obj, "VDO_Divisiones")
            or hasattr(obj, "EspaciosX")
            or hasattr(obj, "EspaciosY"))


def _es_cajon(obj: Any) -> bool:
    return hasattr(obj, "AnchoLibre") and hasattr(obj, "MarcaCorredera")


def _es_zocalo(obj: Any) -> bool:
    return hasattr(obj, "AltoZocalo") and hasattr(obj, "DistanciaFrente")


def _es_panel(obj: Any) -> bool:
    return hasattr(obj, "VDO_Orientacion") and hasattr(obj, "Largo")


def diagnostico_viewprovider(obj: Any) -> str:
    """Texto de diagnóstico para depurar el proxy de un módulo VDO."""
    if obj is None:
        return "Sin objeto."
    vp = obj.ViewObject
    proxy = getattr(vp, "Proxy", None)
    metodos = [m for m in ("_abrir_panel", "setupContextMenu",
                           "doubleClicked", "setEdit", "get_panel_class")
               if hasattr(proxy, m)]
    return (f"{obj.Name}: TypeId={obj.TypeId} "
            f"Proxy={type(proxy).__name__} metodos={metodos}")
