# =====================================================================
# coco_spaces.py
# Motor de geometría para divisiones internas del COCO
# Convierte la resolución de vanos v2 en un plan de cajas y tiras.
# Axioma 2: Lógica geométrica pura, sin dependencias de UI.
#
# NOTA: las funciones 1D legacy (generar_divisiones_x/y y sus helpers)
# fueron retiradas. La única fuente de verdad es la matriz v2
# (vdo_layout.Layout + VDO_Divisiones).
# =====================================================================


from freecad.vdo.core import reengrose_encuentros as VDO_RE_ENCUENTROS
from freecad.vdo.core.coco_spaces_bloques import (
    _cajas_y_piezas,
    _crear_entradas,
    _iterar_punto_fijo,
    _regenerar_tiras,
)
from freecad.vdo.core.espacios_cajas import _caja_dict


def _cortar_segmentos(segmentos, ganadora):
    nuevos = []
    for segmento in segmentos:
        if VDO_RE_ENCUENTROS.detectar_colision(segmento, ganadora):
            nuevos.extend(
                VDO_RE_ENCUENTROS.recortar_tira_contra_tira(segmento, ganadora))
        else:
            nuevos.append(segmento)
    return nuevos


def _prioridad_par(a, b):
    pa = a.get("prioridad")
    pb = b.get("prioridad")
    if pa and pb:
        if pa == pb:
            return pa
        if "inglete_45" in (pa, pb):
            return "inglete_45"
        return pa
    return pa or pb or "vertical_domina"


def _resolver_tiras_entre_si(tiras):
    """Matriz de prioridades tira contra tira (X/Z, L y T)."""
    for i in range(len(tiras)):
        for j in range(i + 1, len(tiras)):
            a = tiras[i]
            b = tiras[j]
            if a.get("host") and a.get("host") == b.get("host"):
                continue
            segs_a = list(a.get("segmentos") or [])
            segs_b = list(b.get("segmentos") or [])
            if not segs_a or not segs_b:
                continue
            par = None
            for sa in segs_a:
                for sb in segs_b:
                    if VDO_RE_ENCUENTROS.detectar_colision(sa, sb):
                        par = (sa, sb)
                        break
                if par:
                    break
            if par is None:
                continue
            prioridad = _prioridad_par(a, b)
            if prioridad == "inglete_45":
                plan = VDO_RE_ENCUENTROS.resolver_encuentro_tiras(
                    par[0], par[1], "inglete_45")
                if plan.get("inglete"):
                    a.setdefault("ingletes", []).append({
                        "otra": b.get("clave"),
                        "rol": plan["orientacion_a"],
                        "plan": plan["inglete"],
                    })
                    b.setdefault("ingletes", []).append({
                        "otra": a.get("clave"),
                        "rol": plan["orientacion_b"],
                        "plan": plan["inglete"],
                    })
                continue
            res = VDO_RE_ENCUENTROS.resolver_encuentro_tiras(
                par[0], par[1], prioridad)
            if res["perdedor"] == "a":
                for ganadora in segs_b:
                    segs_a = _cortar_segmentos(segs_a, ganadora)
            else:
                for ganadora in segs_a:
                    segs_b = _cortar_segmentos(segs_b, ganadora)
            a["segmentos"] = segs_a
            b["segmentos"] = segs_b


def _aplicar_interrupciones(tira):
    segmentos = list(tira.get("segmentos") or [_caja_dict(tira)])
    for panel in tira.pop("_interrupciones", []):
        segmentos = _cortar_segmentos(segmentos, panel)
    tira["segmentos"] = segmentos


def resolver_tiras(tiras):
    """Aplica interrupciones y la matriz de prioridades sobre tiras vivas."""
    for tira in tiras:
        if "_interrupciones" in tira:
            _aplicar_interrupciones(tira)
    _resolver_tiras_entre_si(tiras)


def _resolver_interrupciones(tiras, obstaculos):
    """Aplica interrupciones de tiras y obstaculos, y resuelve los cruces."""
    for tira in tiras:
        _aplicar_interrupciones(tira)
    for obstaculo in obstaculos:
        if isinstance(obstaculo, dict) and "_interrupciones" in obstaculo:
            _aplicar_interrupciones(obstaculo)
    _resolver_tiras_entre_si(tiras)


def planificar_divisiones_matriz(divisiones_json, ancho_cavidad, alto_cavidad,
                                 fondo, espesor, x0=0.0, z0=0.0,
                                 espacios_x="", espacios_y="",
                                 reengroses=None, obstaculos=None):
    """Calcula el plan de la matriz de vanos v2, sin construir formas.

    Devuelve un dict con:
    - ``cajas``: lista de {"caja", "cortes", "tiras"} en el orden de piezas.
    - ``piezas``: datos de cada división (sin formas).
    - ``tiras``: tiras resueltas (sin el campo ``shape``).
    - ``resumen``: texto de resumen (incluye avisos del camino legado).
    - ``resuelto``: resultado de ``resolve_layout``.

    ``reengroses``: dict clave -> modificador. ``obstaculos``: cajas AABB de
    reengroses externos (por ejemplo laterales) con su política de choque.
    """
    from freecad.vdo.core.layout_matriz import Layout
    from freecad.vdo.core.layout_resolucion import resolve_layout
    if divisiones_json:
        layout = Layout.loads(divisiones_json)
        avisos = []
    else:
        layout, avisos = Layout.from_legacy(espacios_x, espacios_y)

    reengroses = reengroses or {}
    obstaculos = list(obstaculos or [])
    resuelto = resolve_layout(
        layout, ancho_cavidad, alto_cavidad, espesor,
        reengroses=reengroses)

    entries = _crear_entradas(
        resuelto, reengroses, fondo, espesor, x0, z0)

    # Los montantes verticales aportan sus tiras primero: son las que
    # definen el retranqueo inicial de repisas.
    for entry in entries:
        if entry["pieza"].axis == "X":
            _regenerar_tiras(entry)

    # Punto fijo: las repisas se retranquean contra las tiras verticales y
    # los montantes contra las horizontales (techo/base/repisas).
    _iterar_punto_fijo(entries, obstaculos)

    tiras = [tira for entry in entries for tira in entry["tiras"]]
    _resolver_interrupciones(tiras, obstaculos)

    cajas, piezas = _cajas_y_piezas(entries, fondo, espesor)
    resuelto.tiras = tiras
    resumen = resuelto.summary()
    if avisos:
        resumen += "\n" + "\n".join(avisos)
    return {
        "cajas": cajas,
        "piezas": piezas,
        "tiras": tiras,
        "resumen": resumen,
        "resuelto": resuelto,
    }
