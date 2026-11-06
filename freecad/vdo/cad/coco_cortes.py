# =====================================================================
# coco_cortes.py
# Capa cad: resta robusta de formas y resolución de tiras de carcasa
# frente a divisiones y núcleos del COCO. Extraído de coco.py (D-39).
# =====================================================================

import logging
from typing import Any

from freecad.vdo.core import reengrose_encuentros as VDO_RE_ENCUENTROS
from freecad.vdo.core.helpers import _get_part

_LOG = logging.getLogger(__name__)


def _cortar_shape(forma, recorte):
    """Resta robusta: OCC falla al cortar compounds multi-solido."""
    if forma is None or forma.isNull():
        return None
    if forma.ShapeType != "Compound":
        try:
            resultado = forma.cut(recorte)
        except ValueError as exc:
            _LOG.warning("coco_cortes: valor de corte no valido: %s", exc)
            return None
        if resultado.isNull() or resultado.Volume <= 1e-9:
            return None
        return resultado
    solidos = []
    for solido in forma.Solids:
        try:
            resultado = solido.cut(recorte)
        except ValueError as exc:
            _LOG.debug("coco_cortes: fila de corte malformada, se omite: %s", exc)
            continue
        if resultado.isNull():
            continue
        solidos.extend(
            s for s in resultado.Solids if not s.isNull() and s.Volume > 1e-9)
    if not solidos:
        return None
    return _get_part().makeCompound(solidos)


def resolver_tiras_divisiones(
    resuelto: Any, shell_tiras: Any, divisiones_piezas: Any,
    divs: Any, boxes: Any, indice_divs: Any,
) -> Any:
    """Segmenta las tiras de carcasa alrededor de las divisiones y resuelve
    tiras contra tiras. Modifica divs y boxes in situ.

    Devuelve division_tiras (tiras que aportan las divisiones).
    """
    division_tiras = list(getattr(resuelto, "tiras", []) or [])
    from freecad.vdo.cad.coco_espacios import _shape_tira
    from freecad.vdo.core.coco_spaces import resolver_tiras

    # Las tiras de carcasa con "interrumpir_tira" se segmentan
    # de forma controlada alrededor de las divisiones.
    for tira in shell_tiras:
        if tira.get("modo_choque") != "interrumpir_tira":
            continue
        for pz in divisiones_piezas:
            caja = pz.get("caja_geometrica")
            if not caja:
                continue
            nuevos = []
            for segmento in tira.get("segmentos") or []:
                if VDO_RE_ENCUENTROS.detectar_colision(segmento, caja):
                    nuevos.extend(
                        VDO_RE_ENCUENTROS.recortar_tira_contra_tira(
                            segmento, caja))
                else:
                    nuevos.append(segmento)
            tira["segmentos"] = nuevos

    resolver_tiras(shell_tiras + division_tiras)

    mapa_divs = {id(shape): i for i, shape in enumerate(divs)}
    for tira in division_tiras:
        viejo = tira.get("shape")
        nuevo = _shape_tira(tira)
        tira["shape"] = nuevo
        idx = mapa_divs.get(id(viejo))
        if idx is not None:
            divs[idx] = nuevo if nuevo is not None else _get_part().Shape()
            boxes[indice_divs + idx] = divs[idx]
    return division_tiras


def cortar_shells_contra_nucleos(
    division_tiras: Any, shell_refs: Any, shell_cores: Any,
    divs: Any, boxes: Any,
) -> None:
    """Recorta cada tira de carcasa contra los núcleos y las divisiones.
    Modifica boxes in situ."""
    from freecad.vdo.cad.coco_espacios import _shape_tira

    strip_shape_ids = {
        id(tira.get("shape")) for tira in division_tiras
        if tira.get("shape") is not None}

    for entry in shell_refs:
        tira = entry["tira"]
        forma = _shape_tira(tira)
        if forma is None:
            boxes[entry["indice"]] = _get_part().Shape()
            continue
        for clave, nucleo in shell_cores.items():
            if clave == entry["clave"]:
                continue
            if (forma.BoundBox.intersect(nucleo.BoundBox)
                    and forma.common(nucleo).Volume > 1e-6):
                forma = _cortar_shape(forma, nucleo)
                if forma is None:
                    break
        if forma is not None:
            for division in divs:
                if (division.isNull()
                        or id(division) in strip_shape_ids):
                    continue
                if (forma.BoundBox.intersect(division.BoundBox)
                        and forma.common(division).Volume > 1e-6):
                    forma = _cortar_shape(forma, division)
                    if forma is None:
                        break
        boxes[entry["indice"]] = (
            forma if forma is not None else _get_part().Shape())
        tira["shape"] = forma
