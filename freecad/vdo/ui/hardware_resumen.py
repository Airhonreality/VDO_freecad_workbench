"""Texto resumen de cotas de un herraje para la tabla del gestor (UI).

Movido sin cambios desde ui/hardware_manager.py (M7, D-52).
"""


def _resumen_cotas(sku, tecnicos):
    """Texto corto de cotas clave para la columna resumen de la tabla."""
    tipo = tecnicos.get("tipo_montaje")
    partes = []
    if tipo in ("parche", "semiparche", "embebida"):
        partes.append("Ø{}".format(tecnicos.get("diametro_cazoleta", 35)))
        if "cota_k_default" in tecnicos:
            partes.append("K={}".format(tecnicos["cota_k_default"]))
        if "solape_nominal" in tecnicos:
            partes.append("solape {}".format(tecnicos["solape_nominal"]))
        elif "holgura_perimetral_min" in tecnicos:
            partes.append("holgura {}".format(tecnicos["holgura_perimetral_min"]))
    else:
        if "descuento_altura_hoja" in tecnicos:
            partes.append("desc. {}".format(tecnicos["descuento_altura_hoja"]))
        if "traslape_minimo" in tecnicos:
            partes.append("traslape {}".format(tecnicos["traslape_minimo"]))
        if "ancho_piso_riel_doble" in tecnicos:
            partes.append("riel {}".format(tecnicos["ancho_piso_riel_doble"]))
    return " | ".join(partes) if partes else "-"
