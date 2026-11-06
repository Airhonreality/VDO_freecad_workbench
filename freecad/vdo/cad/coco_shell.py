# =====================================================================
# coco_shell.py
# Capa cad: tiras de reengrose de la carcasa (laterales, base, techo y
# fondo). Extraído de coco.py (D-39); el closure _aplicar_shell pasa a
# función de módulo con sus variables como argumentos.
# =====================================================================

from typing import Any

from freecad.vdo.cad.geometria import forma_ref
from freecad.vdo.core import reengrose_geometria as VDO_RE_GEOMETRIA
from freecad.vdo.core import reengrose_modelo as VDO_RE_MODELO
from freecad.vdo.core import reengrose_modificador as VDO_RE_MODIFICADOR
from freecad.vdo.core.coco_core import _modificador_mapa
from freecad.vdo.core.helpers import _get_app


def _aplicar_shell(boxes: list[Any], shell_info: dict[str, dict[str, Any]],
                   shell_tiras: list[dict[str, Any]],
                   shell_refs: list[dict[str, Any]], obstaculos: list[Any],
                   reengroses: dict[str, Any], clave: str, caja: dict[str, Any],
                   ejes: dict[str, str]) -> None:
    """Registra una caja de carcasa y, si tiene reengrose, añade sus tiras.
    Modifica boxes, shell_info, shell_tiras, shell_refs y obstaculos in situ."""
    mod = _modificador_mapa(reengroses, clave)
    shell_info[clave] = {
        "caja": caja,
        "ejes": ejes,
        "reengrose": mod.to_dict() if mod.activo else None,
    }
    if not mod.activo:
        return
    try:
        geo = VDO_RE_GEOMETRIA.calcular_geometria_caja(caja, mod, ejes)
    except VDO_RE_MODELO.ReengroseError as exc:
        _get_app().Console.PrintWarning(
            f"[VDO] Reengrose {clave} ignorado: {exc}\n")
        return
    for i, ref in enumerate(geo["refuerzos"]):
        forma = forma_ref(ref)
        if forma is None:
            continue
        indice = len(boxes)
        boxes.append(forma)
        tira = dict(ref)
        tira["clave"] = f"{clave}_tira{i + 1:02d}"
        tira["host"] = clave
        tira["orientacion_tira"] = (
            "vertical" if ejes.get("largo") == "z"
            else "horizontal")
        tira["modo_choque"] = (
            mod.comportamiento_choque_nucleo)
        crudo = reengroses.get(clave) or {}
        tira["modo_explicito"] = (
            "comportamiento_choque_nucleo" in crudo)
        prioridad = getattr(
            mod, "prioridad_encuentro_tiras", None)
        tira["prioridad"] = (
            None if prioridad
            == VDO_RE_MODELO.DEFAULTS["prioridad_encuentro_tiras"]
            else prioridad)
        segmento: dict[str, Any] = {
            "x": float(ref["x"]), "y": float(ref["y"]),
            "z": float(ref["z"]), "w": float(ref["w"]),
            "h": float(ref["h"]), "d": float(ref["d"]),
        }
        if ref.get("poligono"):
            segmento["poligono"] = list(ref["poligono"])
            segmento["eje_extrusion"] = ref.get(
                "eje_extrusion", "z")
        tira["segmentos"] = [segmento]
        tira["shape"] = forma
        shell_refs.append({
            "indice": indice,
            "clave": clave,
            "shape": forma,
            "tira": tira,
        })
        shell_tiras.append(tira)
        obstaculos.append(tira)


def preparar_carcasa(
    fp: Any, lat_izq: Any, lat_der: Any, panel_base: Any, panel_techo: Any,
    fondo_box: Any,
) -> tuple[Any, ...]:
    """Lee los reengroses de carcasa y prepara las listas y el mapa de
    núcleos de la carcasa."""
    reengroses = VDO_RE_MODIFICADOR.leer_reengroses(fp)
    obstaculos: list[Any] = []
    shell_tiras: list[dict[str, Any]] = []
    shell_info: dict[str, dict[str, Any]] = {}
    shell_refs: list[dict[str, Any]] = []
    shell_cores = {
        "lateral_izquierdo": lat_izq,
        "lateral_derecho": lat_der,
        "base": panel_base,
        "techo": panel_techo,
    }
    if fondo_box is not None:
        shell_cores["fondo"] = fondo_box
    return (reengroses, obstaculos, shell_tiras, shell_info, shell_refs,
            shell_cores)


def aplicar_carcasa(
    fp: Any, espesor: Any, ancho: Any, alto: Any, fondo: Any, base_pos_x: Any,
    base_length: Any, base_pos_z: Any, techo_pos_x: Any, techo_length: Any,
    techo_pos_z: Any, tiene_fondo: Any, f_x: Any, f_y: Any, f_z: Any, f_len: Any,
    calibre_fondo: Any, f_alt: Any, reengroses: Any, obstaculos: Any,
    shell_tiras: Any, shell_info: Any, shell_refs: Any, boxes: Any,
) -> None:
    """Aplica los reengroses a laterales, base, techo y fondo. Modifica
    las listas recibidas y boxes in situ."""
    _aplicar_shell(
        boxes, shell_info, shell_tiras, shell_refs, obstaculos, reengroses,
        "lateral_izquierdo",
        {"nombre": f"{fp.Label}_Lateral_Izq",
         "x": 0.0, "y": 0.0, "z": espesor,
         "w": espesor, "h": fondo,
         "d": max(0.0, alto - (espesor * 2))},
        {"largo": "z", "ancho": "y", "espesor": "x"})
    _aplicar_shell(
        boxes, shell_info, shell_tiras, shell_refs, obstaculos, reengroses,
        "lateral_derecho",
        {"nombre": f"{fp.Label}_Lateral_Der",
         "x": ancho - espesor, "y": 0.0, "z": espesor,
         "w": espesor, "h": fondo,
         "d": max(0.0, alto - (espesor * 2))},
        {"largo": "z", "ancho": "y", "espesor": "x"})
    _aplicar_shell(
        boxes, shell_info, shell_tiras, shell_refs, obstaculos, reengroses,
        "base",
        {"nombre": f"{fp.Label}_Base",
         "x": base_pos_x, "y": 0.0, "z": base_pos_z,
         "w": base_length, "h": fondo, "d": espesor},
        {"largo": "x", "ancho": "y", "espesor": "z"})
    _aplicar_shell(
        boxes, shell_info, shell_tiras, shell_refs, obstaculos, reengroses,
        "techo",
        {"nombre": f"{fp.Label}_Techo",
         "x": techo_pos_x, "y": 0.0, "z": techo_pos_z,
         "w": techo_length, "h": fondo, "d": espesor},
        {"largo": "x", "ancho": "y", "espesor": "z"})
    if tiene_fondo:
        _aplicar_shell(
            boxes, shell_info, shell_tiras, shell_refs, obstaculos,
            reengroses, "fondo",
            {"nombre": f"{fp.Label}_Fondo",
             "x": f_x, "y": f_y, "z": f_z,
             "w": f_len, "h": calibre_fondo, "d": f_alt},
            {"largo": "x", "ancho": "z", "espesor": "y"})
