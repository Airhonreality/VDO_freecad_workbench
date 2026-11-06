"""Geometria AABB 3D y encuentro de tiras: colision, orientacion, recorte en T/L y bisel."""

from collections.abc import Collection
from typing import Any, TypedDict

from freecad.vdo.core.helpers import DIMENSION_POR_EJE
from freecad.vdo.core.reengrose_modelo import (
    _EJES,
    PRIORIDADES_ENCUENTRO,
    ReengroseError,
    _validar_enum,
)


class _Anclaje(TypedDict):
    frente: float
    fondo: float
    centro: float
    origen: tuple[float, float, float]


class _PlanInglete(TypedDict):
    plano: str
    eje_vertical: str
    eje_horizontal: str
    extrusion: str
    rango_vertical: tuple[float, float]
    rango_horizontal: tuple[float, float]
    rango_extrusion: tuple[float, float]
    interseccion: dict[str, float]


class _ResultadoEncuentro(TypedDict):
    colision: bool
    modo: str
    prioridad: str
    orientacion_a: str
    orientacion_b: str
    ganador: str | None
    perdedor: str | None
    tira_a: list[dict[str, float]]
    tira_b: list[dict[str, float]]
    recortes: list[dict[str, float]]
    inglete: _PlanInglete | None


# Any: valor es un dict de JSON o una tupla de 6, sin tipo fijo.
def _aabb(valor: Any) -> tuple[float, ...]:
    if isinstance(valor, dict):
        datos: dict[str, Any] = valor
        return (
            float(datos.get("x", 0.0)),
            float(datos.get("y", 0.0)),
            float(datos.get("z", 0.0)),
            float(datos.get("w", datos.get("largo", 0.0))),
            float(datos.get("h", datos.get("ancho", 0.0))),
            float(datos.get("d", datos.get("espesor", 0.0))),
        )
    if isinstance(valor, (list, tuple)) and len(valor) == 6:
        return tuple(float(v) for v in valor)
    raise ReengroseError("AABB invalido: se esperaba dict o tupla de 6.")


def detectar_colision(a: Any, b: Any, tolerancia: float = 1e-6) -> bool:
    ax, ay, az, aw, ah, ad = _aabb(a)
    bx, by, bz, bw, bh, bd = _aabb(b)
    return not (
        ax + aw <= bx + tolerancia or bx + bw <= ax + tolerancia
        or ay + ah <= by + tolerancia or by + bh <= ay + tolerancia
        or az + ad <= bz + tolerancia or bz + bd <= az + tolerancia
    )


def _aabb_dict(caja: Any) -> dict[str, float]:
    x, y, z, w, h, d = _aabb(caja)
    return {"x": x, "y": y, "z": z, "w": w, "h": h, "d": d}


def _dimensiones(aabb: tuple[float, ...]) -> dict[str, float]:
    return {"x": aabb[3], "y": aabb[4], "z": aabb[5]}


def _eje_mayor(aabb: tuple[float, ...]) -> str:
    dims = _dimensiones(aabb)
    return max(_EJES, key=lambda eje: dims[eje])


def _eje_menor(aabb: tuple[float, ...]) -> str:
    dims = _dimensiones(aabb)
    return min(_EJES, key=lambda eje: dims[eje])


def _eje_restante(aabb: tuple[float, ...], usados: Collection[str]) -> str:
    dims = _dimensiones(aabb)
    restantes = [eje for eje in _EJES if eje not in usados]
    if not restantes:
        return "y"
    return max(restantes, key=lambda eje: dims[eje])


def _interseccion_aabb(a: Any, b: Any,
                       tolerancia: float = 1e-6) -> tuple[float, ...] | None:
    ax, ay, az, aw, ah, ad = _aabb(a)
    bx, by, bz, bw, bh, bd = _aabb(b)
    x0 = max(ax, bx)
    x1 = min(ax + aw, bx + bw)
    y0 = max(ay, by)
    y1 = min(ay + ah, by + bh)
    z0 = max(az, bz)
    z1 = min(az + ad, bz + bd)
    if (x1 - x0 <= tolerancia or y1 - y0 <= tolerancia
            or z1 - z0 <= tolerancia):
        return None
    return (x0, y0, z0, x1, y1, z1)


def orientacion_tira(tira: Any) -> str:
    """Devuelve 'vertical' u 'horizontal' para una tira AABB."""
    if isinstance(tira, dict):
        pista = str(
            tira.get("orientacion_tira")
            or tira.get("orientacion")
            or tira.get("eje_largo")
            or "").strip().lower()
        if pista in ("vertical", "horizontal"):
            return pista
        if pista == "z":
            return "vertical"
        if pista in ("x", "y"):
            return "horizontal"
    eje = _eje_mayor(_aabb(tira))
    return "vertical" if eje == "z" else "horizontal"


def vector_anclaje_y(panel_real: Any) -> _Anclaje:
    """Vector de anclaje relativo en Y de la cara real del panel.

    El frente funcional VDO es Y-. El resultado nunca usa coordenadas
    absolutas del mueble: nace del BoundingBox real del panel huesped.
    """
    x, y, z, _w, h, _d = _aabb(panel_real)
    return {
        "frente": y,
        "fondo": y + h,
        "centro": y + h / 2.0,
        "origen": (x, y, z),
    }


def recortar_tira_contra_tira(perdedora: Any, ganadora: Any,
                              tolerancia: float = 1e-6) -> list[dict[str, float]]:
    """Parte la tira perdedora fuera del volumen de la tira ganadora.

    Devuelve una lista de AABB. En un cruce en T produce dos tramos; en
    una esquina en L deja un solo tramo. No modifica la ganadora.
    """
    inter = _interseccion_aabb(perdedora, ganadora, tolerancia)
    if inter is None:
        return [_aabb_dict(perdedora)]

    base = _aabb_dict(perdedora)
    eje = _eje_mayor(_aabb(perdedora))
    dim = DIMENSION_POR_EJE[eje]
    idx = _EJES.index(eje)
    inicio = base[eje]
    fin = inicio + base[dim]
    corte_ini = inter[idx]
    corte_fin = inter[idx + 3]
    tramos: list[dict[str, float]] = []
    if corte_ini > inicio + tolerancia:
        tramo = dict(base)
        tramo[dim] = corte_ini - inicio
        tramos.append(tramo)
    if corte_fin < fin - tolerancia:
        tramo = dict(base)
        tramo[eje] = corte_fin
        tramo[dim] = fin - corte_fin
        tramos.append(tramo)
    return tramos


def _plan_inglete(a: Any, b: Any) -> _PlanInglete | None:
    """Datos minimos para construir un bisel a 45 grados en Capa 2."""
    inter = _interseccion_aabb(a, b)
    if inter is None:
        return None
    oa = orientacion_tira(a)
    ob = orientacion_tira(b)
    if oa == ob:
        return None
    vertical = a if oa == "vertical" else b
    horizontal = a if oa == "horizontal" else b
    eje_v = _eje_menor(_aabb(vertical))
    eje_h = _eje_menor(_aabb(horizontal))
    if eje_v == eje_h:
        return None
    extrusion = next(
        eje for eje in _EJES if eje not in (eje_v, eje_h))
    idx_v = _EJES.index(eje_v)
    idx_h = _EJES.index(eje_h)
    idx_e = _EJES.index(extrusion)
    return {
        "plano": "".join(sorted({eje_v.upper(), eje_h.upper()})),
        "eje_vertical": eje_v,
        "eje_horizontal": eje_h,
        "extrusion": extrusion,
        "rango_vertical": (inter[idx_v], inter[idx_v + 3]),
        "rango_horizontal": (inter[idx_h], inter[idx_h + 3]),
        "rango_extrusion": (inter[idx_e], inter[idx_e + 3]),
        "interseccion": _aabb_dict({
            "x": inter[0], "y": inter[1], "z": inter[2],
            "w": inter[3] - inter[0],
            "h": inter[4] - inter[1],
            "d": inter[5] - inter[2],
        }),
    }


def _ganador_perdedor(prioridad: str, oa: str, ob: str) -> tuple[str, str]:
    """Tira ganadora y perdedora del encuentro segun prioridad y orientaciones."""
    if prioridad == "vertical_domina":
        if ob == "vertical" and oa != "vertical":
            return "b", "a"
        return "a", "b"
    if ob == "horizontal" and oa != "horizontal":
        return "b", "a"
    return "a", "b"


def _recortes_interseccion(tira_a: Any, tira_b: Any) -> list[dict[str, float]]:
    """Caja de interseccion de las dos tiras como lista de un recorte, o []."""
    inter = _interseccion_aabb(tira_a, tira_b)
    if inter is None:
        return []
    return [_aabb_dict({
        "x": inter[0], "y": inter[1], "z": inter[2],
        "w": inter[3] - inter[0],
        "h": inter[4] - inter[1],
        "d": inter[5] - inter[2],
    })]


def resolver_encuentro_tiras(tira_a: Any, tira_b: Any,
                             prioridad: str = "vertical_domina") -> _ResultadoEncuentro:
    """Resuelve el encuentro entre dos tiras sin solape booleano.

    Devuelve las tiras resultantes ya segmentadas. En ``inglete_45``
    devuelve las cajas originales mas un plan de bisel para Capa 2.
    """
    prioridad = _validar_enum(
        prioridad or "vertical_domina", "prioridad_encuentro_tiras",
        PRIORIDADES_ENCUENTRO)
    resultado: _ResultadoEncuentro = {
        "colision": False,
        "modo": prioridad,
        "prioridad": prioridad,
        "orientacion_a": orientacion_tira(tira_a),
        "orientacion_b": orientacion_tira(tira_b),
        "ganador": None,
        "perdedor": None,
        "tira_a": [_aabb_dict(tira_a)],
        "tira_b": [_aabb_dict(tira_b)],
        "recortes": [],
        "inglete": None,
    }
    if not detectar_colision(tira_a, tira_b):
        return resultado

    resultado["colision"] = True
    if prioridad == "inglete_45":
        plan = _plan_inglete(tira_a, tira_b)
        if plan is None:
            prioridad = "vertical_domina"
            resultado["modo"] = prioridad
        else:
            resultado["inglete"] = plan
            return resultado

    ganador, perdedor = _ganador_perdedor(
        prioridad, resultado["orientacion_a"], resultado["orientacion_b"])
    g = tira_a if ganador == "a" else tira_b
    p = tira_b if perdedor == "b" else tira_a
    segmentos = recortar_tira_contra_tira(p, g)
    resultado["ganador"] = ganador
    resultado["perdedor"] = perdedor
    if perdedor == "a":
        resultado["tira_a"] = segmentos
    else:
        resultado["tira_b"] = segmentos
    resultado["recortes"] = _recortes_interseccion(tira_a, tira_b)
    return resultado
