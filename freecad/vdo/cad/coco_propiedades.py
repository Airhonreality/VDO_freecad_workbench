# =====================================================================
# coco_propiedades.py
# Capa cad: propiedades exportadas del COCO (paneles para cutting list),
# forma final y propagación de Placement a insertos. Extraído de
# coco.py (D-39).
# =====================================================================

import json
from typing import Any

from freecad.vdo.core import finish as VDO_FINISH
from freecad.vdo.core import frames as VDO_FR
from freecad.vdo.core.coco_core import _expandir_reengrose
from freecad.vdo.core.helpers import _get_part


def paneles_carcasa(
    fp: Any, fondo: Any, lat_height: Any, espesor: Any, base_length: Any,
    techo_length: Any,
) -> Any:
    """Crea los paneles de carcasa (laterales, base y techo) para exportar.

    Devuelve (lados_vistos, lados_apoyados, paneles_data).
    """
    # === GUARDAR DATOS DE LOS PANELES PARA EXPORTACIÓN ===
    # Convención: largo/ancho = caras del tablero, espesor = grosor.
    lados_vistos, lados_apoyados = VDO_FR.cargar_exposicion(fp)
    paneles_data = [
        {
            "nombre": f"{fp.Label}_Lateral_Izq",
            "tipo": "panel",
            "rol": "lateral_izquierdo",
            "largo": fondo,
            "ancho": lat_height,
            "espesor": espesor,
            "orientacion": "vertical",
            "cantidad": 1,
            "material_ref": fp.VDO_Material_Ref
        },
        {
            "nombre": f"{fp.Label}_Lateral_Der",
            "tipo": "panel",
            "rol": "lateral_derecho",
            "largo": fondo,
            "ancho": lat_height,
            "espesor": espesor,
            "orientacion": "vertical",
            "cantidad": 1,
            "material_ref": fp.VDO_Material_Ref
        },
        {
            "nombre": f"{fp.Label}_Base",
            "tipo": "panel",
            "rol": "base",
            "largo": base_length,
            "ancho": fondo,
            "espesor": espesor,
            "orientacion": "horizontal",
            "cantidad": 1,
            "material_ref": fp.VDO_Material_Ref
        },
        {
            "nombre": f"{fp.Label}_Techo",
            "tipo": "panel",
            "rol": "techo",
            "largo": techo_length,
            "ancho": fondo,
            "espesor": espesor,
            "orientacion": "horizontal",
            "cantidad": 1,
            "material_ref": fp.VDO_Material_Ref
        }
    ]
    return lados_vistos, lados_apoyados, paneles_data


def anadir_fondo_y_divisiones(
    fp: Any, tiene_fondo: Any, fondo_es_delgado: Any, f_len: Any,
    f_alt: Any, calibre_fondo: Any, paneles_data: Any,
    divisiones_piezas: Any,
) -> None:
    """Añade a paneles_data el panel de fondo (si lo hay) y las piezas de
    divisiones. Modifica paneles_data in situ."""
    if tiene_fondo:
        paneles_data.append({
            "nombre": f"{fp.Label}_Fondo",
            "tipo": "panel",
            "rol": "fondo",
            "largo": f_len,
            "ancho": f_alt,
            "espesor": calibre_fondo,
            "orientacion": "vertical",
            "cantidad": 1,
            "material_ref": fp.VDO_Material_Ref,
            "fondo_delgado": fondo_es_delgado
        })

    for pz in divisiones_piezas:
        pz["nombre"] = f"{fp.Label}_{pz['nombre']}"
        pz["material_ref"] = fp.VDO_Material_Ref
        paneles_data.append(pz)


def exportar_paneles(
    fp: Any, shell_info: Any, tapa: Any, base: Any, lados_vistos: Any,
    lados_apoyados: Any, paneles_data: Any,
) -> None:
    """Aplica reengroses, cantos y expansión a los paneles y escribe
    fp.VDO_Paneles_JSON."""
    for pz in paneles_data:
        info = shell_info.get(pz.get("rol"))
        if info and info.get("reengrose"):
            pz["reengrose"] = info["reengrose"]
            pz["caja"] = info["caja"]
            pz["ejes"] = info["ejes"]
            pz["clave_reengrose"] = pz.get("rol", "")

    paneles_data = VDO_FINISH.aplicar_cantos(
        paneles_data, lados_vistos, lados_apoyados,
        tapa=tapa, base=base)

    paneles_expandidos: list[dict[str, Any]] = []
    for pz in paneles_data:
        paneles_expandidos.extend(_expandir_reengrose(pz))
    paneles_data = paneles_expandidos

    fp.VDO_Paneles_JSON = json.dumps(paneles_data, ensure_ascii=False)


def ensamblar_forma(fp: Any, boxes: Any) -> None:
    """Une las formas de boxes en un compound y lo asigna a fp.Shape."""
    solidos: list[Any] = []  # formas FreeCAD sin tipo
    for forma in boxes:
        if forma is None or forma.isNull():
            continue
        if forma.ShapeType == "Compound":
            solidos.extend(
                solido for solido in forma.Solids
                if solido.Volume > 1e-9)
        elif forma.Volume > 1e-9:
            solidos.append(forma)
    fp.Shape = _get_part().makeCompound(solidos)


def propagar_placement(fp: Any) -> None:
    """Mueve los insertos (hijos) rígidamente con el Placement del COCO."""
    # Cuando el COCO se mueve o rota (su Placement cambia),
    # todos sus hijos se mueven rígidamente con él.
    hijos = list(fp.Hijos or [])
    for hijo in hijos:
        if hijo is not None and hasattr(hijo, "LocalPlacement"):
            hijo.Placement = fp.Placement.multiply(
                hijo.LocalPlacement)
