"""cad/propiedades.py — Escritura de propiedades comunes en objetos FreeCAD.

Parte CAD del antiguo vdo_module_props.py. Escribe propiedades de
colocación (rotación, anclaje, exposición) en objetos FeaturePython.
No contiene lógica de dominio: solo adapta datos de core/ al documento.
"""

from __future__ import annotations

import FreeCAD as App

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


def add_common_props(obj):
    """Añade las propiedades de colocación si no existen (idempotente)."""
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


def rotacion_z(grados):
    """Crea una rotación Z a partir de grados.

    En FreeCAD 1.1.4 el constructor `App.Rotation(axis, angle)` recibe el
    ángulo en GRADOS; `Rotation.Angle` sí devuelve radianes.
    """
    return App.Rotation(App.Vector(0.0, 0.0, 1.0), float(grados))


def aplicar_rotacion(obj, grados):
    """Aplica rotación Z alrededor del anclaje, manteniéndolo fijo."""
    from freecad.vdo.cad.colocacion import ancla_local
    ancla = ancla_local(obj)
    p = obj.Placement
    ancla_global = p.multVec(ancla)
    rot = rotacion_z(grados)
    base = ancla_global - rot.multVec(ancla)
    obj.Placement = App.Placement(base, rot)
    if hasattr(obj, "VDO_RotacionZ"):
        obj.VDO_RotacionZ = float(grados)



def ocultar_vista(obj):
    """Oculta la vista del objeto mientras su panel de creación está abierto.

    Escritura de presentación sobre el objeto FreeCAD: vive en cad/ (D6).
    Sin GUI el objeto no tiene ViewObject y no hay nada que ocultar.
    """
    vista = getattr(obj, "ViewObject", None)
    if vista is not None:
        vista.Visibility = False
