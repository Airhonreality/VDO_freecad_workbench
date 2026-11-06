# =====================================================================
# coco_spaces_bloques.py
# Bloques de cálculo de la matriz de divisiones (D-55).
# Extraídos de coco_spaces.planificar_divisiones_matriz con el mismo
# orden de operaciones y los mismos valores. Sin dependencias de UI.
# =====================================================================


import logging

_LOG = logging.getLogger(__name__)

from freecad.vdo.core import reengrose_encuentros as VDO_RE_ENCUENTROS
from freecad.vdo.core import reengrose_geometria as VDO_RE_GEOMETRIA
from freecad.vdo.core import reengrose_interferencias as VDO_RE_INTERFERENCIAS
from freecad.vdo.core import reengrose_modelo as VDO_RE_MODELO
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
    except VDO_RE_MODELO.ReengroseError as exc:
        _LOG.warning("coco_spaces_bloques: reengrose invalido, sin refuerzos: %s", exc)
        return []
    return geo["refuerzos"]


def _crear_entradas(resuelto, reengroses, fondo, espesor, x0, z0):
    """Una entrada de trabajo por pieza resuelta, con su caja base."""
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
    return entries


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


def _tiras_de(entries, axis):
    return [
        tira for entry in entries if entry["pieza"].axis == axis
        for tira in entry.get("tiras", [])]


def _frente_soportes(entries, entry):
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


def _ajustar_repisas(entries, obstaculos):
    """Retranquea las repisas (eje Y) contra las tiras verticales."""
    verticales = _tiras_de(entries, "X")
    for entry in entries:
        if entry["pieza"].axis != "Y":
            continue
        ajustada, cortes = _aplicar_choques(
            entry["caja_base"], obstaculos + verticales, es_vertical=False)
        entry["caja"] = ajustada
        entry["cortes"] = list(cortes)
        _regenerar_tiras(entry)


def _ajustar_montantes(entries, obstaculos):
    """Retranquea los montantes (eje X) contra las tiras horizontales."""
    horizontales = _tiras_de(entries, "Y")
    for entry in entries:
        if entry["pieza"].axis != "X":
            continue
        ajustada, cortes = _aplicar_choques(
            entry["caja_base"], obstaculos + horizontales, es_vertical=True)
        entry["caja"] = ajustada
        entry["cortes"] = list(cortes)
        _regenerar_tiras(entry)


def _contener_repisas(entries):
    """Una repisa nunca nace mas adelante que sus montantes de apoyo."""
    for entry in entries:
        if entry["pieza"].axis != "Y":
            continue
        frente = _frente_soportes(entries, entry)
        if frente <= entry["caja"]["y"] + 1e-6:
            continue
        caja_base = entry["caja_base"]
        fondo_caja = caja_base["y"] + caja_base["h"]
        entry["caja"]["y"] = frente
        entry["caja"]["h"] = max(0.0, fondo_caja - frente)
        _regenerar_tiras(entry)


def _iterar_punto_fijo(entries, obstaculos):
    """Itera repisas, montantes y contencion hasta estabilizar las cajas."""
    for _ in range(4):
        antes = [_huella_caja(entry["caja"]) for entry in entries]
        _ajustar_repisas(entries, obstaculos)
        _ajustar_montantes(entries, obstaculos)
        _contener_repisas(entries)
        despues = [_huella_caja(entry["caja"]) for entry in entries]
        if antes == despues:
            break


def _cajas_y_piezas(entries, fondo, espesor):
    """Convierte las entradas resueltas en ``cajas`` y ``piezas``."""
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
    return cajas, piezas
