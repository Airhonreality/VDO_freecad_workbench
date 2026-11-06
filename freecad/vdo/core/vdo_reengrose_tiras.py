"""Tiras perimetrales 2D de reengrose: recorte de esquinas, inglete 45 grados y generacion de tiras por borde."""

import operator

from freecad.vdo.core.vdo_reengrose_modelo import (
    BORDES_2D, ENCUENTRO_ESQUINAS_DEFAULT, ESQUINAS_2D, SUFIJOS_BORDE)

from freecad.vdo.core.vdo_reengrose_modificador import (
    _normalizar_borde_config, _normalizar_encuentro, normalizar_modificador)


def _poligono_rect(x0, y0, x1, y1):
    if x1 - x0 <= 1e-9 or y1 - y0 <= 1e-9:
        return []
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def _clip_poligono(poligono, a, b, c, sentido=1.0, tolerancia=1e-9):
    """Recorta un poligono contra la semirrecta a*x+b*y=c.

    ``sentido=1`` conserva a*x+b*y >= c; ``sentido=-1`` conserva <=.
    """
    if not poligono:
        return []
    salida = []
    total = len(poligono)
    for i, punto in enumerate(poligono):
        siguiente = poligono[(i + 1) % total]
        f0 = sentido * (a * punto[0] + b * punto[1] - c)
        f1 = sentido * (a * siguiente[0] + b * siguiente[1] - c)
        dentro0 = f0 >= -tolerancia
        dentro1 = f1 >= -tolerancia
        if dentro0:
            salida.append(punto)
        if dentro0 != dentro1:
            den = f0 - f1
            if abs(den) <= 1e-15:
                continue
            t = f0 / den
            salida.append((
                punto[0] + t * (siguiente[0] - punto[0]),
                punto[1] + t * (siguiente[1] - punto[1])))
    limpio = []
    for punto in salida:
        if not limpio or (
                abs(punto[0] - limpio[-1][0]) > 1e-9
                or abs(punto[1] - limpio[-1][1]) > 1e-9):
            limpio.append(punto)
    if len(limpio) > 1 and (
            abs(limpio[0][0] - limpio[-1][0]) <= 1e-9
            and abs(limpio[0][1] - limpio[-1][1]) <= 1e-9):
        limpio.pop()
    return limpio


def _esquina_bordes(esquina):
    """Devuelve el par de bordes (horizontal, vertical) que se unen en la esquina."""
    return {
        "frente_izquierda": ("frente", "izquierda"),
        "frente_derecha": ("frente", "derecha"),
        "fondo_izquierda": ("fondo", "izquierda"),
        "fondo_derecha": ("fondo", "derecha"),
    }[esquina]


#: Esquina -> funcion(h0, h1, v0, v1) que devuelve los argumentos de recorte
#: (a, b, c, sentido) del borde horizontal y del vertical.
_RECORTE_INGLETE_POR_ESQUINA = {
    "frente_izquierda": lambda h0, h1, v0, v1: (
        (-1.0, 1.0, h0 - v0, -1.0),
        (1.0, -1.0, v0 - h0, -1.0)),
    "frente_derecha": lambda h0, h1, v0, v1: (
        (1.0, 1.0, v1 + h0, -1.0),
        (1.0, 1.0, v1 + h0, 1.0)),
    "fondo_izquierda": lambda h0, h1, v0, v1: (
        (1.0, 1.0, v0 + h1, 1.0),
        (1.0, 1.0, v0 + h1, -1.0)),
    "fondo_derecha": lambda h0, h1, v0, v1: (
        (-1.0, 1.0, h1 - v1, 1.0),
        (-1.0, 1.0, h1 - v1, -1.0)),
}


def _inglete_clip(poligonos, rects, esquina, borde_h, borde_v, largo, ancho):
    """Aplica corte a 45° (miter) en una esquina entre dos bordes activos."""
    h0, h1 = rects[borde_h][1], rects[borde_h][3]  # rango Y del borde horizontal
    v0, v1 = rects[borde_v][0], rects[borde_v][2]  # rango X del borde vertical
    recorte = _RECORTE_INGLETE_POR_ESQUINA.get(esquina)
    if recorte is None:
        return
    args_h, args_v = recorte(h0, h1, v0, v1)
    poligonos[borde_h] = _clip_poligono(poligonos[borde_h], *args_h)
    poligonos[borde_v] = _clip_poligono(poligonos[borde_v], *args_v)


#: Borde -> eje del rango largo ("x" o "y").
_EJE_RANGO_LARGO = {
    "frente": "x",
    "fondo": "x",
    "izquierda": "y",
    "derecha": "y",
}

#: Borde -> funcion(off, w, largo, ancho) que devuelve el rango corto (inicio, fin).
_RANGO_CORTO_POR_BORDE = {
    "frente": lambda off, w, largo, ancho: (off, off + w),
    "fondo": lambda off, w, largo, ancho: (ancho - off - w, ancho - off),
    "izquierda": lambda off, w, largo, ancho: (off, off + w),
    "derecha": lambda off, w, largo, ancho: (largo - off - w, largo - off),
}

#: Tope de extremo de un borde contra el borde vecino de una esquina.
#: Cada regla: (borde que se topa, extremo 0=inicio 1=fin, limite, clave de
#: la caja, operador de la distancia, borde cuyo ancho se aplica).
_TOPE_VERTICAL_POR_ESQUINA = {
    "frente_izquierda": (("frente", 0, max, "x0", operator.add, "izquierda"),),
    "frente_derecha": (("frente", 1, min, "x1", operator.sub, "derecha"),),
    "fondo_izquierda": (("fondo", 0, max, "x0", operator.add, "izquierda"),),
    "fondo_derecha": (("fondo", 1, min, "x1", operator.sub, "derecha"),),
}
_TOPE_HORIZONTAL_POR_ESQUINA = {
    "frente_izquierda": (("izquierda", 0, max, "y0", operator.add, "frente"),),
    "frente_derecha": (("derecha", 0, max, "y0", operator.add, "frente"),),
    "fondo_izquierda": (("izquierda", 1, min, "y1", operator.sub, "fondo"),),
    "fondo_derecha": (("derecha", 1, min, "y1", operator.sub, "fondo"),),
}

#: Esquina -> tipo de encuentro -> reglas de tope que aplica.
_REGLAS_ESQUINA = {
    esquina: {
        "vertical_domina": _TOPE_VERTICAL_POR_ESQUINA[esquina],
        "horizontal_domina": _TOPE_HORIZONTAL_POR_ESQUINA[esquina],
        "marco_interior": (_TOPE_VERTICAL_POR_ESQUINA[esquina]
                           + _TOPE_HORIZONTAL_POR_ESQUINA[esquina]),
    }
    for esquina in ESQUINAS_2D
}


def generar_tiras_perimetrales(largo_tablero, ancho_tablero, bordes,
                               espesor_madre,
                               encuentro_esquinas=ENCUENTRO_ESQUINAS_DEFAULT):
    """Primitiva perimetral 2D con lenguaje limpio de taller.

    Coordenadas del tablero: x = largo (0..largo_tablero),
    y = ancho/profundidad (0..ancho_tablero).

    Cada borde acepta:
      - ``distancia_al_canto``: separacion desde el canto hacia adentro.
      - ``largo_tira``: ``marco_interior`` o ``punta_a_punta``.
      - ``encuentro_esquinas``: ``vertical_domina``,
        ``horizontal_domina``, ``inglete_45`` o ``marco_interior``.
        Puede ser un str (aplica a las 4 esquinas) o un dict por esquina.

    Reglas de esquina (el tipo de esquina manda sobre el recorte final):
      - vertical_domina: el borde vertical (izq/der) llega al canto; el
        horizontal hace tope.
      - horizontal_domina: el borde horizontal (frente/fondo) llega al
        canto; el vertical hace tope.
      - marco_interior: ninguno llega al canto exterior; hueco en la esquina.
      - inglete_45: ambos llegan al canto con corte a 45° (miter).
    """
    largo = float(largo_tablero)
    ancho = float(ancho_tablero)
    if largo <= 0 or ancho <= 0:
        return []
    encuentro_por_esquina = _normalizar_encuentro(encuentro_esquinas)

    cfgs = {}
    for borde in BORDES_2D:
        cfg = _normalizar_borde_config(
            (bordes or {}).get(borde),
            ancho_defecto=espesor_madre,
            espesor_defecto=espesor_madre)
        esp = cfg["espesor"]
        if esp is None:
            esp = float(espesor_madre)
        cfgs[borde] = {
            "activo": bool(cfg["activo"]),
            "ancho": min(
                float(cfg["ancho"]),
                largo if borde in ("izquierda", "derecha") else ancho),
            "distancia": float(cfg["distancia_al_canto"]),
            "largo_tira": cfg["largo_tira"],
            "espesor": float(esp),
        }

    activos = {b for b in BORDES_2D if cfgs[b]["activo"]}
    if not activos:
        return []

    # Caja interior definida por los bordes y su distancia al canto.
    x0_box = cfgs["izquierda"]["distancia"] if "izquierda" in cfgs else 0.0
    x1_box = largo - (cfgs["derecha"]["distancia"] if "derecha" in cfgs else 0.0)
    y0_box = cfgs["frente"]["distancia"] if "frente" in cfgs else 0.0
    y1_box = ancho - (cfgs["fondo"]["distancia"] if "fondo" in cfgs else 0.0)

    caja = {"x0": x0_box, "x1": x1_box, "y0": y0_box, "y1": y1_box}
    dimension = {"x": largo, "y": ancho}

    def wd(borde):
        return max(0.0, cfgs[borde]["ancho"])

    # Rango largo base por borde segun largo_tira: [inicio, fin].
    largos = {}
    for borde in BORDES_2D:
        es_punta = cfgs[borde]["largo_tira"] == "punta_a_punta"
        eje = _EJE_RANGO_LARGO[borde]
        largos[borde] = [
            0.0 if es_punta else caja[eje + "0"],
            dimension[eje] if es_punta else caja[eje + "1"]]

    # Recorte por esquina: el tipo de esquina manda sobre el recorte final.
    for esquina in ESQUINAS_2D:
        borde_h, borde_v = _esquina_bordes(esquina)
        if borde_h not in activos or borde_v not in activos:
            continue
        reglas = _REGLAS_ESQUINA[esquina].get(
            encuentro_por_esquina[esquina], ())
        for borde, extremo, limite, clave, operar, borde_ancho in reglas:
            valor = operar(caja[clave], wd(borde_ancho))
            largos[borde][extremo] = limite(largos[borde][extremo], valor)

    def sane(x0, x1):
        if x1 < x0:
            x1 = x0
        return x0, x1

    rects = {}
    for borde in BORDES_2D:
        largo0, largo1 = sane(*largos[borde])
        corto0, corto1 = _RANGO_CORTO_POR_BORDE[borde](
            cfgs[borde]["distancia"], wd(borde), largo, ancho)
        if _EJE_RANGO_LARGO[borde] == "x":
            rects[borde] = [largo0, corto0, largo1, corto1]
        else:
            rects[borde] = [corto0, largo0, corto1, largo1]

    poligonos = {}
    for borde in activos:
        x0, y0, x1, y1 = rects[borde]
        x0, x1 = sorted((x0, x1))
        y0, y1 = sorted((y0, y1))
        poligonos[borde] = _poligono_rect(x0, y0, x1, y1)

    # Inglete 45° por esquina (sobre parejas activas en esa esquina).
    for esquina in ESQUINAS_2D:
        if encuentro_por_esquina[esquina] != "inglete_45":
            continue
        borde_h, borde_v = _esquina_bordes(esquina)
        if borde_h not in activos or borde_v not in activos:
            continue
        _inglete_clip(poligonos, rects, esquina, borde_h, borde_v, largo, ancho)

    tiras = []
    for borde in BORDES_2D:
        if borde not in activos:
            continue
        poly = poligonos.get(borde) or []
        if len(poly) < 3:
            continue
        xs = [p[0] for p in poly]
        ys = [p[1] for p in poly]
        x0, x1 = min(xs), max(xs)
        y0, y1 = min(ys), max(ys)
        if x1 - x0 <= 1e-9 or y1 - y0 <= 1e-9:
            continue
        ancho_borde = float(x1 - x0)
        largo_borde = float(y1 - y0)
        tiene_inglete = any(
            encuentro_por_esquina[e] == "inglete_45"
            for e in ESQUINAS_2D
            if borde in _esquina_bordes(e))
        tira = {
            "borde": borde,
            "nombre_sufijo": SUFIJOS_BORDE[borde],
            "x": float(x0),
            "y": float(y0),
            "w": ancho_borde,
            "h": largo_borde,
            "largo": max(ancho_borde, largo_borde),
            "ancho": min(ancho_borde, largo_borde),
            "d": float(cfgs[borde]["espesor"]),
            "espesor": float(cfgs[borde]["espesor"]),
            "distancia_al_canto": float(cfgs[borde]["distancia"]),
            "largo_tira": cfgs[borde]["largo_tira"],
            "encuentro_esquinas": dict(encuentro_por_esquina),
            "offset_borde": float(cfgs[borde]["distancia"]),
        }
        if tiene_inglete:
            tira["poligono"] = [
                (float(px), float(py)) for px, py in poly]
            tira["esquinas"] = "inglete_45"
        tiras.append(tira)
    return tiras


def generar_geometria_tiras_perimetrales(ancho_tablero, largo_tablero,
                                         reengrose_dto, espesor_madre):
    """Compatibilidad: tiras perimetrales desde un ReengroseDTO.

    x = largo (0..largo_tablero), y = ancho/profundidad (0..ancho_tablero).
    Devuelve una lista de tiras con x/y/w/h/d y, para inglete, ``poligono``.
    """
    mod = normalizar_modificador(reengrose_dto)
    if not mod["activo"]:
        return []
    return generar_tiras_perimetrales(
        float(largo_tablero), float(ancho_tablero),
        mod["bordes"], espesor_madre, mod["esquinas"])
