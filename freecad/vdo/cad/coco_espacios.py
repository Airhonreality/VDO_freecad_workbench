# =====================================================================
# coco_espacios.py (cad)
# Construye las formas OCC de las divisiones internas del COCO a partir
# del plan calculado en core/coco_spaces.py (planificar_divisiones_matriz).
# =====================================================================

from __future__ import annotations

from freecad.vdo.cad.geometria import forma_ref
from freecad.vdo.core.coco_spaces import planificar_divisiones_matriz
from freecad.vdo.core.helpers import _get_app, _get_part


def _shape_caja(caja):
    if (caja["w"] <= 1e-9 or caja["h"] <= 1e-9
            or caja["d"] <= 1e-9):
        return None
    return _get_part().makeBox(
        caja["w"], caja["h"], caja["d"],
        _get_app().Vector(caja["x"], caja["y"], caja["z"]))


def _punto_inglete(plan, coord_v, coord_h, coord_e):
    coords = {"x": 0.0, "y": 0.0, "z": 0.0}
    coords[plan["eje_vertical"]] = float(coord_v)
    coords[plan["eje_horizontal"]] = float(coord_h)
    coords[plan["extrusion"]] = float(coord_e)
    return _get_app().Vector(coords["x"], coords["y"], coords["z"])


def _prisma_inglete(inglete):
    """Prisma triangular complementario para biselar una tira a 45 grados."""
    plan = inglete.get("plan") or {}
    try:
        v0, v1 = plan["rango_vertical"]
        h0, h1 = plan["rango_horizontal"]
        e0, e1 = plan["rango_extrusion"]
    except (KeyError, TypeError, ValueError):
        return None
    if v1 - v0 <= 1e-9 or h1 - h0 <= 1e-9:
        return None
    if inglete.get("rol") == "vertical":
        triangulo = [(v0, h1), (v1, h1), (v1, h0)]
    else:
        triangulo = [(v0, h0), (v1, h0), (v0, h1)]
    margen = 0.5
    puntos = [
        _punto_inglete(plan, cv, ch, e0 - margen)
        for cv, ch in triangulo
    ]
    wire = _get_part().makePolygon([*puntos, puntos[0]])
    cara = _get_part().Face(wire)
    vector = {"x": 0.0, "y": 0.0, "z": 0.0}
    vector[plan["extrusion"]] = (e1 - e0) + margen * 2.0
    return cara.extrude(_get_app().Vector(
        vector["x"], vector["y"], vector["z"]))


def _shape_tira(tira):
    piezas = []
    for segmento in tira.get("segmentos") or []:
        shape = forma_ref(segmento)
        if shape is not None:
            piezas.append(shape)
    for inglete in tira.get("ingletes") or []:
        prisma = _prisma_inglete(inglete)
        if prisma is None:
            continue
        nuevas = []
        for pieza in piezas:
            if not pieza.BoundBox.intersect(prisma.BoundBox):
                nuevas.append(pieza)
                continue
            try:
                corte = pieza.cut(prisma)
            except ValueError:
                nuevas.append(pieza)
                continue
            if corte.isNull() or corte.Volume <= 1e-9:
                continue
            nuevas.extend(
                solido for solido in corte.Solids
                if not solido.isNull() and solido.Volume > 1e-9)
        piezas = nuevas
    if not piezas:
        return None
    if len(piezas) == 1:
        return piezas[0]
    return _get_part().makeCompound(piezas)


def generar_divisiones_matriz(divisiones_json, ancho_cavidad, alto_cavidad,
                              fondo, espesor, x0=0.0, z0=0.0,
                              espacios_x="", espacios_y="",
                              reengroses=None, obstaculos=None):
    """Genera la matriz de vanos v2 como formas, con reengroses y colisiones.

    Misma firma y resultado que antes: ``(shapes, resumen, piezas, resuelto)``.
    ``reengroses``: dict clave -> modificador. ``obstaculos``: cajas AABB de
    reengroses externos (por ejemplo laterales) con su política de choque.
    """
    plan = planificar_divisiones_matriz(
        divisiones_json, ancho_cavidad, alto_cavidad, fondo, espesor,
        x0, z0, espacios_x, espacios_y, reengroses, obstaculos)

    shapes = []
    for bloque in plan["cajas"]:
        core_shape = _shape_caja(bloque["caja"])
        if core_shape is not None:
            for corte in bloque["cortes"]:
                if (corte["w"] <= 1e-9 or corte["h"] <= 1e-9
                        or corte["d"] <= 1e-9):
                    continue
                pieza_corte = _get_part().makeBox(
                    corte["w"], corte["h"], corte["d"],
                    _get_app().Vector(corte["x"], corte["y"], corte["z"]))
                core_shape = core_shape.cut(pieza_corte)
            shapes.append(core_shape)
        for tira in bloque["tiras"]:
            shape = _shape_tira(tira)
            tira["shape"] = shape
            if shape is not None:
                shapes.append(shape)

    return shapes, plan["resumen"], plan["piezas"], plan["resuelto"]
