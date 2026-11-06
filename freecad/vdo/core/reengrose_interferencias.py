"""Interferencias del reengrose con piezas vecinas: vano neto, choque tira-panel y mocheo de repisa."""

from freecad.vdo.core.helpers import DIMENSION_POR_EJE
from freecad.vdo.core.reengrose_encuentros import (
    _aabb,
    _aabb_dict,
    _eje_mayor,
    _eje_menor,
    _eje_restante,
    _interseccion_aabb,
    detectar_colision,
    recortar_tira_contra_tira,
)
from freecad.vdo.core.reengrose_modelo import (
    _EJES,
    POLITICAS_REPISA,
    _normalizar_modo_choque,
    _validar_enum,
)

#: Lado invadido -> (dimension que se reduce, desplazamiento que se aplica).
#: Un lado fuera de la tabla no cambia el vano.
_REDUCCION_VANO_POR_LADO = {
    "izquierda": ("ancho", "x"),
    "derecha": ("ancho", None),
    "inferior": ("alto", "z"),
    "superior": ("alto", None),
}


def calcular_vano_neto_con_reengrose(vano_original, division_con_reengrose):
    """Reduce el vano neto segun el lado invadido por el reengrose."""
    vano = dict(vano_original)
    division = dict(division_con_reengrose)
    ancho = float(vano.get("ancho", vano.get("w", 0.0)))
    alto = float(vano.get("alto", vano.get("h", 0.0)))
    extra = float(division.get("espesor_extra", division.get("extra", 0.0)))
    lado = str(division.get("lado_afectado", "")).lower()

    dx = 0.0
    dz = 0.0
    regla = _REDUCCION_VANO_POR_LADO.get(lado)
    if regla is not None:
        dimension, desplazamiento = regla
        if dimension == "ancho":
            ancho = max(0.0, ancho - extra)
        else:
            alto = max(0.0, alto - extra)
        if desplazamiento == "x":
            dx = extra
        elif desplazamiento == "z":
            dz = extra

    return {
        "ancho": ancho,
        "alto": alto,
        "desplazamiento_x": dx,
        "desplazamiento_z": dz,
        "lado_afectado": lado,
    }


def _retroceso_panel(panel_t, tira_t, eje_normal, eje_ancho):
    """Retroceso simetrico panel/tira en el eje de profundidad correcto.

    Si la tira cubre todo el ancho del panel, el panel se retira por su
    eje restante (por ejemplo una division baja para pasar bajo el techo).
    Si solo cubre una franja, el panel retrocede en profundidad hasta la
    cara de la tira. El resultado se expresa como AABB.
    """
    panel = {
        "x": panel_t[0], "y": panel_t[1], "z": panel_t[2],
        "w": panel_t[3], "h": panel_t[4], "d": panel_t[5],
    }
    tira = {
        "x": tira_t[0], "y": tira_t[1], "z": tira_t[2],
        "w": tira_t[3], "h": tira_t[4], "d": tira_t[5],
    }
    dims_p = {"x": panel["w"], "y": panel["h"], "z": panel["d"]}
    dims_t = {"x": tira["w"], "y": tira["h"], "z": tira["d"]}
    tol = 1e-6

    a = eje_ancho
    p0, p1 = panel[a], panel[a] + dims_p[a]
    t0, t1 = tira[a], tira[a] + dims_t[a]
    cubre_ancho = t0 <= p0 + tol and t1 >= p1 - tol

    if cubre_ancho:
        eje = next(
            e for e in _EJES if e not in (eje_normal, eje_ancho))
        p0h, p1h = panel[eje], panel[eje] + dims_p[eje]
        t0h, t1h = tira[eje], tira[eje] + dims_t[eje]
        corte0, corte1 = max(p0h, t0h), min(p1h, t1h)
        if corte1 <= corte0 + tol:
            return _aabb_dict(panel)
        if (t0h + t1h) / 2.0 < (p0h + p1h) / 2.0:
            panel[eje] = corte1
            panel[DIMENSION_POR_EJE[eje]] = max(0.0, p1h - corte1)
        else:
            panel[DIMENSION_POR_EJE[eje]] = max(0.0, corte0 - p0h)
        return _aabb_dict(panel)

    if t0 <= p0 + tol:
        # La tira invade desde el frente del panel: el panel nace detras
        # de su cara posterior y conserva la cota hasta el fondo.
        nuevo = max(p0, t1)
        panel[a] = nuevo
        panel[DIMENSION_POR_EJE[a]] = max(0.0, p1 - nuevo)
    else:
        # La tira esta delante del panel: retroceder el origen hasta su
        # cara posterior. Antes se asignaba la profundidad igual al offset,
        # lo que colapsaba la repisa a una tira flotante.
        nuevo = min(p1, t1)
        panel[a] = nuevo
        panel[DIMENSION_POR_EJE[a]] = max(0.0, p1 - nuevo)
    return _aabb_dict(panel)


def _caja_interseccion(inter):
    """Caja de la banda de invasion (tupla AABB de interseccion) como dict."""
    return _aabb_dict({
        "x": inter[0], "y": inter[1], "z": inter[2],
        "w": inter[3] - inter[0],
        "h": inter[4] - inter[1],
        "d": inter[5] - inter[2],
    })


def resolver_choque_tira_panel(tira, panel_perpendicular, modo="retroceso"):
    """Resuelve el choque entre una tira y un panel perpendicular.

    Es simetrico: sirve tanto para una repisa contra un montante como para
    un montante contra una tira de techo/base.

    Devuelve un plan con ``panel`` ajustado (retroceso recto), ``cortes_panel``
    (mocheo o cajeados) y ``tira_segmentos`` cuando se interrumpe la tira.
    """
    modo = _normalizar_modo_choque(modo)
    inter = _interseccion_aabb(tira, panel_perpendicular)
    if inter is None:
        return None

    tira_t = _aabb(tira)
    panel_t = _aabb(panel_perpendicular)
    eje_largo = _eje_mayor(tira_t)
    eje_corto = _eje_menor(tira_t)
    eje_ancho = _eje_restante(tira_t, {eje_largo, eje_corto})
    eje_normal_panel = _eje_menor(panel_t)
    plan = {
        "colision": True,
        "modo": modo,
        "panel": _aabb_dict(panel_perpendicular),
        "panel_original": _aabb_dict(panel_perpendicular),
        "tira": _aabb_dict(tira),
        "cortes_panel": [],
        "tira_segmentos": [],
        "eje_largo": eje_largo,
        "eje_corto": eje_corto,
        "eje_ancho": eje_ancho,
        "eje_normal_panel": eje_normal_panel,
    }

    if modo == "interrumpir_tira":
        plan["tira_segmentos"] = recortar_tira_contra_tira(
            tira, panel_perpendicular)
        return plan

    if modo == "mocheo":
        plan["cortes_panel"].append(_caja_interseccion(inter))
        return plan

    # Retroceso simetrico. La tira corre en el mismo eje que la normal del
    # panel (es perpendicular a su cara). El panel retrocede por el eje de
    # ancho de la tira o, si la tira cubre todo ese ancho, por el eje
    # restante. Cubre repisas contra montantes y montantes contra techo/base.
    if eje_largo == eje_normal_panel and eje_ancho != eje_normal_panel:
        plan["panel"] = _retroceso_panel(
            panel_t, tira_t, eje_normal_panel, eje_ancho)
        return plan

    # Paneles verticales (o encuentros no clasicos): cajeado recto en la
    # banda exacta de invasion. Esto evita partir la tira del techo.
    plan["cortes_panel"].append(_caja_interseccion(inter))
    return plan


def generar_mocheo_repisa(repisa, reengrose_vertical, politica=None):
    """Detecta colision repisa/reengrose y devuelve retroceso o mocheo."""
    if not detectar_colision(repisa, reengrose_vertical):
        return None

    mod = _validar_enum(
        politica or "retroceder", "politica_repisa", POLITICAS_REPISA)
    rx, ry, _rz, rw, rh, _rd = _aabb(repisa)
    gx, gy, _gz, gw, gh, _gd = _aabb(reengrose_vertical)

    x0 = max(rx, gx)
    x1 = min(rx + rw, gx + gw)
    y0 = max(ry, gy)
    y1 = min(ry + rh, gy + gh)
    recorte_x = max(0.0, x1 - x0)
    recorte_y = max(0.0, y1 - y0)

    if mod == "mochear":
        return {
            "modo": "mochear",
            "moche": {
                "x": x0 - rx,
                "y": y0 - ry,
                "w": recorte_x,
                "h": recorte_y,
            },
        }

    lado = "derecha" if (gx + gw / 2.0) >= (rx + rw / 2.0) else "izquierda"
    return {
        "modo": "retroceder",
        "lado": lado,
        "recorte_x": recorte_x,
        "recorte_y": recorte_y,
        "ancho_neto": max(0.0, rw - recorte_x),
    }
