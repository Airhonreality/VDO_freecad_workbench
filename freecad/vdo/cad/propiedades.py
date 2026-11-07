"""cad/propiedades.py — Escritura de propiedades comunes en objetos FreeCAD.

Parte CAD del antiguo module_props.py. Escribe propiedades de
colocación (rotación, anclaje, exposición) en objetos FeaturePython.
No contiene lógica de dominio: solo adapta datos de core/ al documento.
"""

from __future__ import annotations

from typing import Any

import FreeCAD as App

from freecad.vdo.core import frames as VDO_FR
from freecad.vdo.core.module_props import ANCLAJE_DEFAULT, ANCLAJES


def add_common_props(obj: Any) -> None:
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


def rotacion_z(grados: float) -> Any:  # App.Rotation de FreeCAD sin tipo
    """Crea una rotación Z a partir de grados (única definición, D-97).

    En FreeCAD 1.1.4 el constructor `App.Rotation(axis, angle)` recibe el
    ángulo en GRADOS; `Rotation.Angle` sí devuelve radianes.
    """
    return App.Rotation(App.Vector(0.0, 0.0, 1.0), float(grados))




def ocultar_vista(obj: Any) -> None:
    """Oculta la vista del objeto mientras su panel de creación está abierto.

    Escritura de presentación sobre el objeto FreeCAD: vive en cad/ (D6).
    Sin GUI el objeto no tiene ViewObject y no hay nada que ocultar.
    """
    vista = getattr(obj, "ViewObject", None)
    if vista is not None:
        vista.Visibility = False


def anadir_propiedad_texto(obj: Any, nombre: str, grupo: str,  # objeto FreeCAD sin tipo
                            descripcion: str) -> Any:
    """Añade una propiedad de texto (App::PropertyString) a un objeto FreeCAD (D-31).

    Devuelve lo que devuelve ``addProperty`` (se conserva por compatibilidad).
    """
    return obj.addProperty("App::PropertyString", nombre, grupo, descripcion)


def asignar_propiedades(obj: Any, valores: dict[str, Any]) -> None:  # objeto FreeCAD sin tipo
    """Asigna propiedades a un objeto FreeCAD en el orden del dict (D-32).

    ``valores`` es un dict ``nombre -> valor``. Equivale a las asignaciones
    ``obj.nombre = valor`` en secuencia.
    """
    for nombre, valor in valores.items():
        setattr(obj, nombre, valor)


def asignar_placement_local(obj: Any, placement: Any) -> None:  # objeto/placement FreeCAD sin tipo
    """Asigna ``LocalPlacement`` a un objeto FreeCAD (D-32)."""
    obj.LocalPlacement = placement
