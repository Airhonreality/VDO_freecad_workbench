# =====================================================================
# coco_core.py
# Cálculo puro de cofres COCO: modificadores de reengrose y expansión
# de piezas en subpiezas. La escritura FreeCAD vive en cad/coco.py.
# =====================================================================


import logging

from freecad.vdo.core import reengrose_despiece as VDO_RE_DESPIECE
from freecad.vdo.core import reengrose_modelo as VDO_RE_MODELO
from freecad.vdo.core import reengrose_modificador as VDO_RE_MODIFICADOR
from freecad.vdo.core.helpers import _get_app
from freecad.vdo.datos.valores import MELAMINA_ESTANDAR

_LOG = logging.getLogger(__name__)


def _modificador_mapa(mapa, clave):
    datos = (mapa or {}).get(clave)
    if not datos:
        return VDO_RE_MODIFICADOR.ReengroseModifier()
    try:
        return VDO_RE_MODIFICADOR.ReengroseModifier(datos)
    except VDO_RE_MODELO.ReengroseError as exc:
        _LOG.warning("coco_core: reengrose invalido, usa modificador vacio: %s", exc)
        return VDO_RE_MODIFICADOR.ReengroseModifier()



def _expandir_reengrose(pieza):
    mod = pieza.get("reengrose")
    caja = pieza.get("caja")
    ejes = pieza.get("ejes")
    if not mod or not caja or not ejes:
        return [pieza]
    caja = dict(caja)
    caja["nombre"] = pieza.get("nombre", "Pieza")
    cantos_bloque = (
        pieza.get("cantos")
        if mod.get("modo_fabricacion") == "pacha" else None)
    try:
        subpiezas = VDO_RE_DESPIECE.despiece_caja(
            caja, mod, ejes, cantos=pieza.get("cantos"),
            material_ref=pieza.get(
                "material_ref", MELAMINA_ESTANDAR),
            orientacion=pieza.get("orientacion", "vertical"),
            cantos_bloque=cantos_bloque)
    except VDO_RE_MODELO.ReengroseError as exc:
        _get_app().Console.PrintWarning(
            f"[VDO] Reengrose inválido en '{pieza.get('nombre')}': {exc}\n")
        return [pieza]
    for sub in subpiezas:
        sub["rol"] = pieza.get("rol", "")
        sub["rol_padre"] = pieza.get("rol", "")
        sub["clave_reengrose"] = pieza.get("clave_reengrose", "")
        if pieza.get("mocheos") and sub.get("rol_reengrose") == "base":
            sub["mocheos"] = pieza["mocheos"]
    return subpiezas
