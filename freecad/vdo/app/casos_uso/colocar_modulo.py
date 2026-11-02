"""app/casos_uso/colocar_modulo.py — Caso de uso: colocar módulo en el documento."""

from __future__ import annotations

from freecad.vdo.app.dto import ColocarModuloDTO, ColocarModuloResultado


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
