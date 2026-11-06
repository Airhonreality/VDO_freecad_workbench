# =====================================================================
# vdo_coco_spaces.py
# Motor de geometría para divisiones internas del COCO
# Convierte la resolución de vanos v2 en un plan de cajas y tiras.
# Axioma 2: Lógica geométrica pura, sin dependencias de UI.
#
# NOTA: las funciones 1D legacy (generar_divisiones_x/y y sus helpers)
# fueron retiradas. La única fuente de verdad es la matriz v2
# (vdo_layout.Layout + VDO_Divisiones).
# =====================================================================


from freecad.vdo.core import vdo_reengrose_encuentros as VDO_RE_ENCUENTROS
from freecad.vdo.core import vdo_reengrose_geometria as VDO_RE_GEOMETRIA
from freecad.vdo.core import vdo_reengrose_interferencias as VDO_RE_INTERFERENCIAS
from freecad.vdo.core import vdo_reengrose_modelo as VDO_RE_MODELO
from freecad.vdo.core.espacios_cajas import (
    _agregar_interrupcion,
    _caja_dict,
    _caja_pieza,
    _clave_pieza,
    _corte_expandido,
    _ejes_pieza,
    _fusionar_caja,
    _huella_caja,
    _modificador,
    _modo_efectivo,
)


def _aplicar_choques(caja, obstaculos, es_vertical):
    """Ajusta el núcleo de un panel contra tiras perpendiculares.

    Devuelve ``(caja_ajustada, cortes)``. El modo se toma de la tira
    invasora, de modo que el mismo helper sirve para repisas y montantes.
    """
    ajustada = dict(caja)
    cortes = []
    clave_host = caja.get("clave")
    for obstaculo in obstaculos:
        if clave_host and obstaculo.get("host") == clave_host:
            continue
        modo = _modo_efectivo(obstaculo, es_vertical)
        plan = VDO_RE_INTERFERENCIAS.resolver_choque_tira_panel(
            obstaculo, ajustada, modo)
        if not plan:
            continue
        if plan["modo"] == "interrumpir_tira":
            _agregar_interrupcion(obstaculo, ajustada)
            continue
        if plan.get("panel"):
            ajustada = _fusionar_caja(ajustada, plan["panel"])
        for corte in plan.get("cortes_panel") or []:
            cortes.append(_corte_expandido(corte, es_vertical))
    return ajustada, cortes


def _preparar_tira(refuerzo, entry, indice):
    pieza = entry["pieza"]
    tira = dict(refuerzo)
    tira["clave"] = (
        f"{_clave_pieza(pieza)}_tira{indice + 1:02d}")
    tira["host"] = _clave_pieza(pieza)
    tira["orientacion_tira"] = (
        "vertical" if pieza.axis == "X" else "horizontal")
    mod = entry["mod"]
    tira["modo_choque"] = mod.comportamiento_choque_nucleo
    tira["modo_explicito"] = entry.get("modo_explicito", False)
    prioridad = getattr(mod, "prioridad_encuentro_tiras", None)
    tira["prioridad"] = (
        None if prioridad == VDO_RE_MODELO.DEFAULTS["prioridad_encuentro_tiras"]
        else prioridad)
    segmento = _caja_dict(tira)
    if tira.get("poligono"):
        segmento["poligono"] = list(tira["poligono"])
        segmento["eje_extrusion"] = tira.get("eje_extrusion", "z")
    tira["segmentos"] = [segmento]
    return tira


def _crear_refuerzos(entry):
    mod = entry["mod"]
    if not mod.activo:
        return []
    try:
        geo = VDO_RE_GEOMETRIA.calcular_geometria_caja(
            entry["caja"], mod, entry["ejes"])
    except VDO_RE_MODELO.ReengroseError:
        return []
    return geo["refuerzos"]


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
    from freecad.vdo.core.vdo_layout_matriz import Layout
    from freecad.vdo.core.vdo_layout_resolucion import resolve_layout
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

    entries = []
    for pieza in resuelto.pieces:
        caja = _caja_pieza(pieza, fondo, espesor, x0, z0)
        clave = _clave_pieza(pieza)
        caja["clave"] = clave
        crudo = reengroses.get(clave) or {}
        entries.append({
            "pieza": pieza,
            "clave": clave,
            "caja": dict(caja),
            "caja_base": dict(caja),
            "ejes": _ejes_pieza(pieza),
            "mod": _modificador(reengroses, pieza),
            "modo_explicito": (
                "comportamiento_choque_nucleo" in crudo),
            "refuerzos": [],
            "tiras": [],
            "cortes": [],
        })

    def _regenerar_tiras(entry):
        """Recalcula refuerzos y anclaje desde la caja real de la pieza."""
        entry["refuerzos"] = _crear_refuerzos(entry)
        nuevas = []
        for i, ref in enumerate(entry["refuerzos"]):
            tira = _preparar_tira(ref, entry, i)
            tira["anclaje_y"] = VDO_RE_ENCUENTROS.vector_anclaje_y(entry["caja"])
            nuevas.append(tira)
        entry["tiras"] = nuevas
        return nuevas

    def _tiras_de(axis):
        return [
            tira for entry in entries if entry["pieza"].axis == axis
            for tira in entry.get("tiras", [])]

    def _frente_soportes(entry):
        """Frente maximo de los montantes que tocan los extremos de la repisa."""
        caja_base = entry["caja_base"]
        x0 = caja_base["x"]
        x1 = x0 + caja_base["w"]
        frente = caja_base["y"]
        for otro in entries:
            if otro["pieza"].axis != "X":
                continue
            vx0 = otro["caja"]["x"]
            vx1 = vx0 + otro["caja"]["w"]
            toca = any(
                abs(vertice - extremo) <= 1e-6
                for vertice in (vx0, vx1)
                for extremo in (x0, x1))
            if toca:
                frente = max(frente, otro["caja"]["y"])
        return frente

    # Los montantes verticales aportan sus tiras primero: son las que
    # definen el retranqueo inicial de repisas.
    for entry in entries:
        if entry["pieza"].axis == "X":
            _regenerar_tiras(entry)

    # Punto fijo: las repisas se retranquean contra las tiras verticales y
    # los montantes contra las horizontales (techo/base/repisas). Al mover
    # una pieza se regeneran sus tiras para que nunca queden flotando en
    # Y=0; se itera hasta estabilizar las cajas.
    for _ in range(4):
        antes = [_huella_caja(entry["caja"]) for entry in entries]

        verticales = _tiras_de("X")
        for entry in entries:
            if entry["pieza"].axis != "Y":
                continue
            ajustada, cortes = _aplicar_choques(
                entry["caja_base"], obstaculos + verticales,
                es_vertical=False)
            entry["caja"] = ajustada
            entry["cortes"] = list(cortes)
            _regenerar_tiras(entry)

        horizontales = _tiras_de("Y")
        for entry in entries:
            if entry["pieza"].axis != "X":
                continue
            ajustada, cortes = _aplicar_choques(
                entry["caja_base"], obstaculos + horizontales,
                es_vertical=True)
            entry["caja"] = ajustada
            entry["cortes"] = list(cortes)
            _regenerar_tiras(entry)

        # Contencion de limites: una repisa nunca puede nacer mas adelante
        # que los montantes que la sostienen. Conserva su cota hasta el fondo.
        for entry in entries:
            if entry["pieza"].axis != "Y":
                continue
            frente = _frente_soportes(entry)
            if frente <= entry["caja"]["y"] + 1e-6:
                continue
            caja_base = entry["caja_base"]
            fondo_caja = caja_base["y"] + caja_base["h"]
            entry["caja"]["y"] = frente
            entry["caja"]["h"] = max(0.0, fondo_caja - frente)
            _regenerar_tiras(entry)

        despues = [_huella_caja(entry["caja"]) for entry in entries]
        if antes == despues:
            break

    tiras = [tira for entry in entries for tira in entry["tiras"]]
    for tira in tiras:
        _aplicar_interrupciones(tira)
    for obstaculo in obstaculos:
        if isinstance(obstaculo, dict) and "_interrupciones" in obstaculo:
            _aplicar_interrupciones(obstaculo)
    _resolver_tiras_entre_si(tiras)

    cajas = []
    piezas = []
    for entry in entries:
        pieza = entry["pieza"]
        caja = entry["caja"]
        cajas.append({
            "caja": caja,
            "cortes": list(entry["cortes"]),
            "tiras": entry["tiras"],
        })

        if pieza.axis == "X":
            largo = fondo
            ancho = caja["d"]
        else:
            largo = caja["w"]
            ancho = caja["h"]

        datos = {
            "nombre": pieza.nombre,
            "tipo": "panel",
            "rol": "division_x" if pieza.axis == "X" else "division_y",
            "largo": largo,
            "ancho": ancho,
            "espesor": espesor,
            "orientacion": "vertical" if pieza.axis == "X" else "horizontal",
            "cantidad": 1,
        }
        datos["caja_geometrica"] = caja
        if entry["cortes"]:
            datos["mocheos"] = list(entry["cortes"])
        if entry["mod"].activo:
            datos["clave_reengrose"] = entry["clave"]
            datos["reengrose"] = entry["mod"].to_dict()
            datos["caja"] = caja
            datos["ejes"] = entry["ejes"]
            if entry["mod"].modo_fabricacion == "pacha":
                datos["grupo_pacha"] = f"Pacha_{pieza.nombre}"
        piezas.append(datos)

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
