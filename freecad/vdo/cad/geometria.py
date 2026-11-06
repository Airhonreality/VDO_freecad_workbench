"""geometria.py — conversión de planes de dominio (números/tuplas) a formas FreeCAD.

Único módulo de cad/ que construye Part.Shape a partir de diccionarios de
dimensiones calculadas por core/. No hay lógica de dominio aquí: solo adaptación
de geometría.
"""

from __future__ import annotations

import FreeCAD as App
import Part

from freecad.vdo.core.helpers import DIMENSION_POR_EJE


def _extruir_poligono(puntos, eje, largo):
    """Extruye el polígono ``puntos`` a lo largo de ``eje`` una distancia ``largo``.

    Devuelve un sólido válido o None. No silencia errores: FreeCAD señala un
    polígono no extruible con ``Part.OCCError`` (p. ej. no planar), que se
    registra y se devuelve None para que el llamador use la caja de respaldo.
    Un polígono degenerado no lanza error: produce volumen nulo y se descarta
    por la comprobación de ``isNull()``/``Volume``.
    """
    vector = {"x": 0.0, "y": 0.0, "z": 0.0}
    vector[eje] = largo
    try:
        cara = Part.Face(Part.makePolygon([*puntos, puntos[0]]))
        solido = cara.extrude(App.Vector(vector["x"], vector["y"], vector["z"]))
    except Part.OCCError as exc:
        App.Console.PrintWarning(
            f"[VDO] forma_ref: polígono no extruible ({exc}); se usa caja\n")
        return None
    if not solido.isNull() and solido.Volume > 1e-9:
        return solido
    return None


def forma_ref(ref: dict) -> object | None:
    """Devuelve un Part.Shape para una tira/refuerzo descrito por ``ref``.

    ``ref`` contiene claves como x, y, z, w, h, d, espesor, largo, ancho,
    poligono (lista de (x,y,z) para inglete), eje_extrusion.
    Si hay polígono y su extrusión es válida, devuelve el sólido extruido; si
    no, usa la caja wxhxd. Devuelve None si faltan datos o si la construcción
    falla (datos no numéricos o caja inválida).
    """
    try:
        poly = ref.get("poligono")
        if poly and len(poly) >= 3:
            puntos = [App.Vector(float(p[0]), float(p[1]), float(p[2]))
                      for p in poly]
            eje = str(ref.get("eje_extrusion", "z")).lower()
            if eje not in DIMENSION_POR_EJE:
                eje = "z"
            dim = DIMENSION_POR_EJE[eje]
            largo = float(ref.get(dim, ref.get("espesor", 0.0)))
            if largo > 1e-9:
                solido = _extruir_poligono(puntos, eje, largo)
                if solido is not None:
                    return solido
        w = float(ref.get("w", ref.get("largo", 0.0)))
        h = float(ref.get("h", ref.get("ancho", 0.0)))
        d = float(ref.get("d", ref.get("espesor", 0.0)))
        if w <= 1e-9 or h <= 1e-9 or d <= 1e-9:
            return None
        return Part.makeBox(
            w, h, d,
            App.Vector(
                float(ref.get("x", 0.0)),
                float(ref.get("y", 0.0)),
                float(ref.get("z", 0.0))))
    except (TypeError, ValueError, Part.OCCError):
        return None
