# -*- coding: utf-8 -*-
# =====================================================================
# vdo_module_props.py
# Constantes y lecturas puras de propiedades de colocación VDO.
#
# add_common_props escribe atributos en objetos FreeCAD recibidos como
# parametro (no importa FreeCAD a nivel de modulo). Este modulo es puro:
# no importa FreeCAD ni Qt a nivel de modulo.
# =====================================================================

from freecad.vdo.core import vdo_frames as VDO_FR

ANCLAJES = [
    "inferior_izquierda_frente",
    "inferior_derecha_frente",
    "inferior_izquierda_fondo",
    "inferior_derecha_fondo",
    "superior_izquierda_frente",
    "superior_derecha_frente",
    "superior_izquierda_fondo",
    "superior_derecha_fondo",
    "centro_inferior",
]

ANCLAJE_DEFAULT = "inferior_izquierda_frente"

ANCLAJE_LABELS = {
    "inferior_izquierda_frente": "Inferior izquierda (frente)",
    "inferior_derecha_frente": "Inferior derecha (frente)",
    "inferior_izquierda_fondo": "Inferior izquierda (fondo)",
    "inferior_derecha_fondo": "Inferior derecha (fondo)",
    "superior_izquierda_frente": "Superior izquierda (frente)",
    "superior_derecha_frente": "Superior derecha (frente)",
    "superior_izquierda_fondo": "Superior izquierda (fondo)",
    "superior_derecha_fondo": "Superior derecha (fondo)",
    "centro_inferior": "Centro inferior",
}

ANCLAJE_IDS = {label: idx for idx, label in ANCLAJE_LABELS.items()}


def leer_rotacion(obj):
    """Devuelve la rotación en grados (lee el atributo del objeto)."""
    try:
        return float(getattr(obj, "VDO_RotacionZ", 0.0))
    except (TypeError, ValueError):
        return 0.0


def ancla_local(obj, anclaje=None):
    """Devuelve el punto local (Vector) de la esquina de anclaje.

    Convención de ejes:
      X: izquierda (min) / derecha (max)
      Y: frente (min) / fondo (max)
      Z: inferior (min) / superior (max)
    """
    anclaje = anclaje or getattr(obj, "VDO_Anclaje", ANCLAJE_DEFAULT)
    try:
        bb = obj.Shape.BoundBox
    except Exception:
        bb = None
    if bb is None:
        xmin = xmax = ymin = ymax = zmin = zmax = 0.0
    else:
        xmin, xmax = bb.XMin, bb.XMax
        ymin, ymax = bb.YMin, bb.YMax
        zmin, zmax = bb.ZMin, bb.ZMax

    izquierda = str(anclaje).startswith("inferior_izquierda") or str(anclaje).startswith("superior_izquierda")
    derecha = str(anclaje).startswith("inferior_derecha") or str(anclaje).startswith("superior_derecha")
    frente = str(anclaje).endswith("_frente")
    fondo = str(anclaje).endswith("_fondo")
    superior = str(anclaje).startswith("superior_")
    centro_inferior = str(anclaje) == "centro_inferior"

    if centro_inferior:
        from freecad.vdo.cad.propiedades import _get_app
        App = _get_app()
        return App.Vector((xmin + xmax) / 2.0, (ymin + ymax) / 2.0, zmin)
    return App.Vector(
        xmin if izquierda else (xmax if derecha else (xmin + xmax) / 2.0),
        ymin if frente else (ymax if fondo else (ymin + ymax) / 2.0),
        zmax if superior else zmin,
    )


def add_common_props(obj):
    """Añade las propiedades de colocación si no existen (idempotente).

    Funcion pura: recibe un objeto de FreeCAD y escribe atributos en el.
    No importa FreeCAD a nivel de modulo (las cadenas "App::Property*"
    son solo identificadores de tipo de FreeCAD).
    """
    if not hasattr(obj, "VDO_RotacionZ"):
        obj.addProperty(
            "App::PropertyAngle", "VDO_RotacionZ", "Colocación",
            "Rotación del módulo alrededor del eje Z (pose, no geometría)"
        ).VDO_RotacionZ = 0.0

    if not hasattr(obj, "VDO_Anclaje"):
        prop = obj.addProperty(
            "App::PropertyEnumeration", "VDO_Anclaje", "Colocación",
            "Esquina del módulo que se alinea con el punto de colocación"
        )
        prop.VDO_Anclaje = ANCLAJES
        obj.VDO_Anclaje = ANCLAJE_DEFAULT

    if not hasattr(obj, "VDO_Lados_Vistos"):
        obj.addProperty(
            "App::PropertyString", "VDO_Lados_Vistos", "Exposición",
            "Lados del módulo visibles desde el espacio (JSON)"
        ).VDO_Lados_Vistos = VDO_FR.serializar_lados([VDO_FR.FRENTE])

    if not hasattr(obj, "VDO_Lados_Apoyados"):
        obj.addProperty(
            "App::PropertyString", "VDO_Lados_Apoyados", "Exposición",
            "Lados del módulo apoyados contra muro/piso (JSON)"
        ).VDO_Lados_Apoyados = VDO_FR.serializar_lados([VDO_FR.FONDO])
