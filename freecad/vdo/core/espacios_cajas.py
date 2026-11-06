# =====================================================================
# espacios_cajas.py
# Modelo de caja y clave de pieza para las divisiones internas del COCO.
# Extraido de coco_spaces.py (D-48). Codigo sin cambios.
# Axioma 2: logica geometrica pura, sin dependencias de UI ni de FreeCAD.
# =====================================================================


from typing import Any

from freecad.vdo.core.layout_resuelto import PanelPiece


def _clave_pieza(pieza: PanelPiece) -> str:
    if pieza.axis == "X":
        return f"division_x:{pieza.path}"
    return f"division_y:{pieza.path}"


def _caja_pieza(pieza: PanelPiece, fondo: float, espesor: float, x0: float,
                z0: float) -> dict[str, Any]:
    if pieza.axis == "X":
        return {
            "nombre": pieza.nombre,
            "x": x0 + pieza.x, "y": 0.0, "z": z0 + pieza.z,
            "w": espesor, "h": fondo, "d": pieza.h,
        }
    return {
        "nombre": pieza.nombre,
        "x": x0 + pieza.x, "y": 0.0, "z": z0 + pieza.z,
        "w": pieza.w, "h": fondo, "d": espesor,
    }


def _ejes_pieza(pieza: PanelPiece) -> dict[str, str]:
    if pieza.axis == "X":
        return {"largo": "z", "ancho": "y", "espesor": "x"}
    return {"largo": "x", "ancho": "y", "espesor": "z"}


def _caja_dict(caja: dict[str, Any]) -> dict[str, Any]:
    return {
        "x": float(caja.get("x", 0.0)),
        "y": float(caja.get("y", 0.0)),
        "z": float(caja.get("z", 0.0)),
        "w": float(caja.get("w", 0.0)),
        "h": float(caja.get("h", 0.0)),
        "d": float(caja.get("d", 0.0)),
    }


def _fusionar_caja(base: dict[str, Any], cambios: dict[str, Any]) -> dict[str, Any]:
    nueva = dict(base)
    nueva.update(_caja_dict(cambios))
    return nueva


def _modo_obstaculo(obstaculo: dict[str, Any]) -> str:
    return (
        obstaculo.get("modo_choque")
        or obstaculo.get("comportamiento_choque_nucleo")
        or obstaculo.get("politica")
        or "retroceso"
    )


def _corte_expandido(corte: dict[str, Any], es_vertical: bool) -> dict[str, Any]:
    corte = dict(corte)
    if es_vertical:
        corte["x"] -= 0.5
        corte["w"] += 1.0
    else:
        corte["z"] -= 0.5
        corte["d"] += 1.0
    return corte


def _huella_caja(caja: dict[str, Any]) -> tuple[float, ...]:
    return tuple(round(float(caja.get(clave, 0.0)), 4)
                 for clave in ("x", "y", "z", "w", "h", "d"))


def _agregar_interrupcion(obstaculo: dict[str, Any], caja: dict[str, Any]) -> None:
    interrupciones = obstaculo.setdefault("_interrupciones", [])
    huella = _huella_caja(caja)
    for existente in interrupciones:
        if _huella_caja(existente) == huella:
            return
    interrupciones.append(_caja_dict(caja))


def _modo_efectivo(obstaculo: dict[str, Any], es_vertical: bool) -> str:
    """Modo de choque contextual.

    En montantes verticales, una tira horizontal (techo/base/repisa) debe
    mochear localmente la esquina por defecto, no retranquear toda la
    division. Si el taller eligio explicitamente ``retroceso``, se respeta.
    """
    modo = _modo_obstaculo(obstaculo)
    if (es_vertical and modo == "retroceso"
            and obstaculo.get("orientacion_tira") == "horizontal"
            and not obstaculo.get("modo_explicito", False)):
        return "mocheo"
    return modo
