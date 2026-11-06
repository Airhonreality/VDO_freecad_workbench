"""cad/colocacion.py — geometría de colocación de módulos (adaptador FreeCAD).

Lee el anclaje y la rotación de un objeto y calcula su Placement a partir de
un punto del espacio. Vive en cad/ porque lee Shape.BoundBox y escribe
Placement. Movido desde core/vdo_module_props.py (F19.2-ter, regresión de
colocación): core/ no debe conocer objetos FreeCAD.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import FreeCAD as App

from freecad.vdo.cad.propiedades import rotacion_z
from freecad.vdo.core.dto import ColocarModuloDTO, ColocarModuloResultado
from freecad.vdo.core.vdo_module_props import ANCLAJE_DEFAULT


def leer_rotacion(obj: Any) -> float:
    """Devuelve la rotación en grados (lee el atributo del objeto)."""
    try:
        return float(getattr(obj, "VDO_RotacionZ", 0.0))
    except (TypeError, ValueError):
        return 0.0


def ancla_local(obj: Any, anclaje: str | None = None) -> Any:
    """Devuelve el punto local (Vector) de la esquina de anclaje.

    Convención de ejes:
      X: izquierda (min) / derecha (max)
      Y: frente (min) / fondo (max)
      Z: inferior (min) / superior (max)
    """
    anclaje = anclaje or getattr(obj, "VDO_Anclaje", ANCLAJE_DEFAULT)
    bb = obj.Shape.BoundBox
    if bb is None:
        xmin = xmax = ymin = ymax = zmin = zmax = 0.0
    else:
        xmin, xmax = bb.XMin, bb.XMax
        ymin, ymax = bb.YMin, bb.YMax
        zmin, zmax = bb.ZMin, bb.ZMax

    izquierda = str(anclaje).startswith(("inferior_izquierda", "superior_izquierda"))
    derecha = str(anclaje).startswith(("inferior_derecha", "superior_derecha"))
    frente = str(anclaje).endswith("_frente")
    fondo = str(anclaje).endswith("_fondo")
    superior = str(anclaje).startswith("superior_")
    centro_inferior = str(anclaje) == "centro_inferior"

    from freecad.vdo.core.vdo_helpers import _get_app
    App = _get_app()
    if centro_inferior:
        return App.Vector((xmin + xmax) / 2.0, (ymin + ymax) / 2.0, zmin)
    return App.Vector(
        xmin if izquierda else (xmax if derecha else (xmin + xmax) / 2.0),
        ymin if frente else (ymax if fondo else (ymin + ymax) / 2.0),
        zmax if superior else zmin,
    )


def aplicar_rotacion(obj: Any, grados: float) -> None:
    """Aplica rotación Z alrededor del anclaje, manteniéndolo fijo.

    Vive aquí y no en cad/propiedades.py: necesita ancla_local, y propiedades
    no puede importar colocacion sin crear un ciclo (D-12).
    """
    ancla = ancla_local(obj)
    p = obj.Placement
    ancla_global = p.multVec(ancla)
    rot = rotacion_z(grados)
    base = ancla_global - rot.multVec(ancla)
    obj.Placement = App.Placement(base, rot)
    if hasattr(obj, "VDO_RotacionZ"):
        obj.VDO_RotacionZ = float(grados)


@dataclass(frozen=True)
class PlanColocacion:
    """Rotación y anclaje de un módulo fijados antes de empezar a colocarlo."""

    rot: Any  # App.Rotation
    ancla: Any  # App.Vector, punto local del anclaje


def preparar_colocacion(obj: Any, anclaje: str | None = None) -> PlanColocacion:
    """Lee la rotación del objeto y calcula su punto de anclaje local."""
    rot = rotacion_z(leer_rotacion(obj))
    ancla = ancla_local(
        obj, anclaje or getattr(obj, "VDO_Anclaje", ANCLAJE_DEFAULT))
    return PlanColocacion(rot=rot, ancla=ancla)


def aplicar_colocacion(obj: Any, punto: Any, plan: PlanColocacion) -> None:
    """Sitúa el objeto para que su anclaje quede en ``punto``."""
    base = punto - plan.rot.multVec(plan.ancla)
    obj.Placement = App.Placement(base, plan.rot)


def colocar_modulo(doc, dto: ColocarModuloDTO) -> ColocarModuloResultado:
    """Coloca un módulo en el documento estableciendo su Placement."""
    if doc is None:
        raise ValueError("Documento requerido para colocar el módulo.")
    obj = doc.getObject(dto.nombre)
    if obj is None:
        return ColocarModuloResultado(nombre=dto.nombre, colocado=False)
    import FreeCAD as App
    obj.Placement = App.Placement(
        App.Vector(dto.x, dto.y, dto.z),
        App.Rotation(App.Vector(0, 0, 1), dto.rotacion),
    )
    doc.recompute()
    return ColocarModuloResultado(nombre=dto.nombre, colocado=True)
