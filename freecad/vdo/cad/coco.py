# =====================================================================
# coco.py
# Capa cad: make_coco (crea el COCO FeaturePython). La clase CocoFeature
# vive en coco_feature.py. El cálculo de piezas vive en core/vdo_coco_core.py.
# =====================================================================

import json

from freecad.vdo.cad.geometria import forma_ref
from freecad.vdo.cad.coco_feature import CocoFeature
from freecad.vdo.cad.propiedades import add_common_props
from freecad.vdo.core import vdo_defaults as VDO_D
from freecad.vdo.core import vdo_finish as VDO_FINISH
from freecad.vdo.core import vdo_frames as VDO_FR
from freecad.vdo.core import vdo_module_props as VDO_MOD
from freecad.vdo.core import vdo_reengrose_encuentros as VDO_RE_ENCUENTROS
from freecad.vdo.core import vdo_reengrose_geometria as VDO_RE_GEOMETRIA
from freecad.vdo.core import vdo_reengrose_modelo as VDO_RE_MODELO
from freecad.vdo.core import vdo_reengrose_modificador as VDO_RE_MODIFICADOR
from freecad.vdo.core.vdo_helpers import _get_app, _get_part, rotacion_z
from freecad.vdo.datos.valores import MELAMINA_ESTANDAR
from freecad.vdo.core.vdo_coco_core import (
    _expandir_reengrose,
    _modificador_mapa,
)



def make_coco(doc, configuracion):
    """
    Crea un COCO FeaturePython con propiedades configurables.

    Args:
        doc: Documento de FreeCAD activo (proporcionado por app/cad, no
             buscado desde core).
        configuracion (dict): Parámetros del cofre.

    Returns:
        _get_app().DocumentObject: El objeto FeaturePython creado.
    """
    if doc is None:
        _get_app().Console.PrintError("[VDO] No hay documento activo.\n")
        return None

    nombre = configuracion.get("nombre", "COCO_4C")

    obj = doc.addObject("Part::FeaturePython", nombre)
    CocoFeature(obj)

    if _get_app().GuiUp:
        # La vista se adjunta desde app/ (F5/F6), no desde core.
        pass

    # Aplicar configuración (valores por defecto desde vdo_manifest.json)
    obj.Alto = configuracion.get("alto", VDO_D.ALTO_DEFAULT)
    obj.Ancho = configuracion.get("ancho", VDO_D.ANCHO_DEFAULT)
    obj.FondoModulo = configuracion.get("fondo_modulo", VDO_D.FONDO_DEFAULT)
    obj.Espesor = configuracion.get("espesor", VDO_D.ESPESOR_DEFAULT)
    obj.TieneFondo = configuracion.get("tiene_fondo", VDO_D.FONDO_HABILITADO)
    obj.CalibreFondo = configuracion.get("calibre_fondo", VDO_D.FONDO_CALIBRE)
    obj.ProfundidadRanura = configuracion.get("profundidad_ranura", VDO_D.FONDO_PROFUNDIDAD_RANURA)
    obj.DistanciaBorde = configuracion.get("distancia_borde", VDO_D.FONDO_DISTANCIA_BORDE)
    obj.Tapa = configuracion.get("tapa", VDO_D.TAPA_POSICION)
    obj.Base = configuracion.get("base", VDO_D.BASE_POSICION)
    obj.VDO_Divisiones = configuracion.get("divisiones", "")
    reengroses = configuracion.get("reengroses", {})
    if not isinstance(reengroses, str):
        reengroses = json.dumps(reengroses or {}, ensure_ascii=False)
    obj.VDO_Reengrose_JSON = reengroses or "{}"
    rotacion = float(configuracion.get("rotacion", 0.0))
    obj.VDO_RotacionZ = rotacion
    obj.VDO_Anclaje = configuracion.get(
        "anclaje", VDO_MOD.ANCLAJE_DEFAULT)
    VDO_FR.guardar_exposicion(
        obj,
        configuracion.get("lados_vistos", [VDO_FR.FRENTE]),
        configuracion.get("lados_apoyados", [VDO_FR.FONDO]))
    if rotacion:
        obj.Placement = _get_app().Placement(
            obj.Placement.Base, rotacion_z(rotacion))

    doc.recompute()
    _get_app().Console.PrintMessage(
        f"[VDO] COCO '{nombre}' creado con FeaturePython.\n")
    return obj
