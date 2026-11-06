# =====================================================================
# espacios_cajas.py
# Modelo de caja y clave de pieza para las divisiones internas del COCO.
# Extraido de vdo_coco_spaces.py (D-48). Codigo sin cambios.
# Axioma 2: logica geometrica pura, sin dependencias de UI ni de FreeCAD.
# =====================================================================


from freecad.vdo.core import vdo_reengrose_modelo as VDO_RE_MODELO
from freecad.vdo.core import vdo_reengrose_modificador as VDO_RE_MODIFICADOR


def _clave_pieza(pieza):
    if pieza.axis == "X":
        return f"division_x:{pieza.path}"
    return f"division_y:{pieza.path}"


def _modificador(reengroses, pieza):
    datos = (reengroses or {}).get(_clave_pieza(pieza))
    if not datos:
        return VDO_RE_MODIFICADOR.ReengroseModifier()
    try:
        return VDO_RE_MODIFICADOR.ReengroseModifier(datos)
    except VDO_RE_MODELO.ReengroseError:
        return VDO_RE_MODIFICADOR.ReengroseModifier()


def _caja_pieza(pieza, fondo, espesor, x0, z0):
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


def _ejes_pieza(pieza):
    if pieza.axis == "X":
        return {"largo": "z", "ancho": "y", "espesor": "x"}
    return {"largo": "x", "ancho": "y", "espesor": "z"}


def _caja_dict(caja):
    return {
        "x": float(caja.get("x", 0.0)),
        "y": float(caja.get("y", 0.0)),
        "z": float(caja.get("z", 0.0)),
        "w": float(caja.get("w", 0.0)),
        "h": float(caja.get("h", 0.0)),
        "d": float(caja.get("d", 0.0)),
    }


def _fusionar_caja(base, cambios):
    nueva = dict(base)
    nueva.update(_caja_dict(cambios))
    return nueva


def _modo_obstaculo(obstaculo):
    return (
        obstaculo.get("modo_choque")
        or obstaculo.get("comportamiento_choque_nucleo")
        or obstaculo.get("politica")
        or "retroceso"
    )


def _corte_expandido(corte, es_vertical):
    corte = dict(corte)
    if es_vertical:
        corte["x"] -= 0.5
        corte["w"] += 1.0
    else:
        corte["z"] -= 0.5
        corte["d"] += 1.0
    return corte


def _huella_caja(caja):
    return tuple(round(float(caja.get(clave, 0.0)), 4)
                 for clave in ("x", "y", "z", "w", "h", "d"))


def _agregar_interrupcion(obstaculo, caja):
    interrupciones = obstaculo.setdefault("_interrupciones", [])
    huella = _huella_caja(caja)
    for existente in interrupciones:
        if _huella_caja(existente) == huella:
            return
    interrupciones.append(_caja_dict(caja))


def _modo_efectivo(obstaculo, es_vertical):
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
