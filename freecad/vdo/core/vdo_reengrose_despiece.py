"""Despiece de paneles y cajas con reengrose: politica de cantos y subpiezas fisicas."""

from freecad.vdo.core.vdo_finish import BORDES, CANTOS_VALIDOS

from freecad.vdo.datos.valores import MELAMINA_ESTANDAR

from freecad.vdo.core.vdo_reengrose_geometria import (
    calcular_geometria_caja, calcular_geometria_reengrose)

from freecad.vdo.core.vdo_reengrose_modelo import CANTO_OCULTO, CANTO_VISTO

from freecad.vdo.core.vdo_reengrose_modificador import normalizar_modificador


def _cantos_completos(tipo=CANTO_VISTO):
    return {borde: tipo for borde in BORDES}


def resolver_politica_cantos(panel_base, modifier):
    """Traduce el modo de fabricacion en un plan de cantos por pieza."""
    mod = normalizar_modificador(modifier)
    cantos_base = dict(panel_base.get("cantos") or {})
    for borde in BORDES:
        valor = str(cantos_base.get(borde, CANTO_OCULTO)).upper()
        cantos_base[borde] = valor if valor in CANTOS_VALIDOS else CANTO_OCULTO

    if not mod["activo"]:
        return {"base": cantos_base, "tira": {}, "bloque": {}}
    if mod["modo_fabricacion"] == "independiente":
        return {
            "base": cantos_base,
            "tira": _cantos_completos(CANTO_VISTO),
            "bloque": {},
        }
    return {
        "base": _cantos_completos(CANTO_OCULTO),
        "tira": _cantos_completos(CANTO_OCULTO),
        "bloque": _cantos_completos(CANTO_VISTO),
    }


def despiece_panel(nombre, largo, ancho, espesor, modifier,
                   cantos=None, material_ref=MELAMINA_ESTANDAR,
                   orientacion="vertical"):
    """Devuelve las subpiezas fisicas de un panel con reengrose."""
    panel = {
        "nombre": nombre,
        "largo": float(largo),
        "ancho": float(ancho),
        "espesor": float(espesor),
        "cantos": dict(cantos or {}),
        "material_ref": material_ref,
    }
    mod = normalizar_modificador(modifier)
    geo = calcular_geometria_reengrose(panel, mod)
    plan = resolver_politica_cantos(panel, mod)
    grupo = geo["grupo_pacha"]
    modo = mod["modo_fabricacion"] if mod["activo"] else ""

    piezas = []
    base = geo["base"]
    base.update({
        "tipo": "panel",
        "orientacion": orientacion,
        "cantidad": 1,
        "material_ref": material_ref,
        "cantos": plan["base"],
        "grupo": grupo,
        "grupo_pacha": grupo,
        "operacion": (
            "Encolar + canto de bloque unificado" if grupo
            else ("Cantear por separado" if modo else "")),
        "rol_reengrose": "base",
    })
    piezas.append(base)

    for refuerzo in geo["refuerzos"]:
        refuerzo.update({
            "tipo": "panel",
            "orientacion": orientacion,
            "cantidad": 1,
            "material_ref": material_ref,
            "cantos": plan["tira"],
            "grupo": grupo,
            "grupo_pacha": grupo,
            "operacion": (
                "Encolar + canto de bloque unificado" if grupo
                else "Cantear por separado"),
            "rol_reengrose": "refuerzo",
        })
        if plan["bloque"]:
            refuerzo["cantos_bloque"] = dict(plan["bloque"])
        piezas.append(refuerzo)

    if plan["bloque"] and piezas:
        piezas[0]["cantos_bloque"] = dict(plan["bloque"])
    return piezas


def _pieza_panel(nombre, medidas, orientacion, material_ref, cantos,
                 grupo, operacion, rol):
    """Dict de una pieza de tablero del despiece de caja."""
    largo, ancho, espesor = medidas
    return {
        "nombre": nombre,
        "tipo": "panel",
        "orientacion": orientacion,
        "largo": largo,
        "ancho": ancho,
        "espesor": espesor,
        "cantidad": 1,
        "material_ref": material_ref,
        "cantos": dict(cantos),
        "grupo": grupo,
        "grupo_pacha": grupo,
        "operacion": operacion,
        "rol_reengrose": rol,
    }


def despiece_caja(caja, modifier, ejes, cantos=None,
                  material_ref=MELAMINA_ESTANDAR,
                  orientacion="vertical", cantos_bloque=None):
    """Despiece de una pieza de modulo con reengrose.

    ``caja`` usa x/y/z + w/h/d y ``ejes`` define largo/ancho/espesor.
    Devuelve subpiezas con dimensiones de tablero y grupo de pacha.
    """
    mod = normalizar_modificador(modifier)
    geo = calcular_geometria_caja(caja, mod, ejes)
    plan = resolver_politica_cantos({"cantos": cantos or {}}, mod)
    if cantos_bloque is not None:
        plan["bloque"] = dict(cantos_bloque)
    grupo = geo["grupo_pacha"]
    modo = mod["modo_fabricacion"] if mod["activo"] else ""
    dim_key = {"x": "w", "y": "h", "z": "d"}
    ejes = dict(ejes)
    base = geo["base"]

    def medidas(caja_pieza):
        return (
            float(caja_pieza[dim_key[ejes["largo"]]]),
            float(caja_pieza[dim_key[ejes["ancho"]]]),
            float(caja_pieza[dim_key[ejes["espesor"]]]),
        )

    operacion_base = (
        "Encolar + canto de bloque unificado" if grupo
        else ("Cantear por separado" if modo else ""))
    piezas = [_pieza_panel(
        caja.get("nombre", "Pieza"), medidas(base), orientacion, material_ref,
        plan["base"], grupo, operacion_base, "base")]
    operacion_refuerzo = (
        "Encolar + canto de bloque unificado" if grupo
        else "Cantear por separado")
    for ref in geo["refuerzos"]:
        pieza = _pieza_panel(
            ref["nombre"], medidas(ref), orientacion, material_ref,
            plan["tira"], grupo, operacion_refuerzo, "refuerzo")
        if plan["bloque"]:
            pieza["cantos_bloque"] = dict(plan["bloque"])
        piezas.append(pieza)

    if plan["bloque"] and piezas:
        piezas[0]["cantos_bloque"] = dict(plan["bloque"])
    return piezas
