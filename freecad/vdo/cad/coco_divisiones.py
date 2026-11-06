# =====================================================================
# coco_divisiones.py
# Capa cad: divisiones internas del COCO (matriz de vanos v2).
# Extraído de coco.py (D-39).
# =====================================================================


def aplicar_divisiones(fp, alto, ancho, espesor, fondo, tiene_fondo, f_y,
                       reengroses, obstaculos, boxes):
    """Genera las divisiones internas a partir de VDO_Divisiones.

    Añade las formas de las divisiones a boxes in situ y actualiza
    fp.ResumenEspacios. Devuelve (divs, divisiones_piezas, resuelto,
    indice_divs).
    """
    divisiones_json = getattr(fp, "VDO_Divisiones", "")
    divisiones_piezas = []

    from freecad.vdo.core.layout_modelo import cavidad_interior
    cavidad = cavidad_interior(alto, ancho, espesor)
    ancho_util = cavidad["ancho"]
    altura_util = cavidad["alto"]
    x_util = cavidad["x0"]
    z_util = cavidad["z0"]

    resuelto = None
    divs = []
    indice_divs = None
    fondo_divisiones = max(0.0, f_y) if tiene_fondo else fondo
    if divisiones_json:
        from freecad.vdo.cad.coco_espacios import generar_divisiones_matriz
        divs, resumen, piezas, resuelto = generar_divisiones_matriz(
            divisiones_json, ancho_util, altura_util,
            fondo_divisiones, espesor, x_util, z_util,
            reengroses=reengroses, obstaculos=obstaculos)
        indice_divs = len(boxes)
        boxes.extend(divs)
        divisiones_piezas.extend(piezas)
        fp.ResumenEspacios = resumen
    else:
        fp.ResumenEspacios = ""
    return divs, divisiones_piezas, resuelto, indice_divs
