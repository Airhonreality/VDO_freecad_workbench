"""app/casos_uso/colocar_modulo.py — Caso de uso: colocar módulo en el documento."""

from __future__ import annotations

from typing import Any

from freecad.vdo.core.dto import ColocarModuloDTO, ColocarModuloResultado
from freecad.vdo.cad.colocacion import PlanColocacion
from freecad.vdo.cad.colocacion import aplicar_colocacion as _cad_aplicar
from freecad.vdo.cad.colocacion import preparar_colocacion as _cad_preparar


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


# ---------------------------------------------------------------------
# Colocación interactiva (la UI llama a estas dos funciones; no importa cad/).
# ---------------------------------------------------------------------

def preparar_colocacion(obj: Any, anclaje: str | None = None) -> PlanColocacion:
    """Fija la rotación y el anclaje del módulo antes de colocarlo con clic."""
    return _cad_preparar(obj, anclaje)


def colocar_en_punto(obj: Any, punto: Any, plan: PlanColocacion) -> None:
    """Sitúa el módulo para que su anclaje quede en ``punto``."""
    _cad_aplicar(obj, punto, plan)
