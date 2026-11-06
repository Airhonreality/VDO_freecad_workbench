# =====================================================================
# coco_carcasa.py
# Capa cad: lectura de parámetros del COCO y geometría base de la
# carcasa (laterales, base, techo y fondo). Extraído de coco.py (D-39).
# =====================================================================

from freecad.vdo.core import defaults as VDO_D
from freecad.vdo.core.helpers import _get_app, _get_part


def leer_parametros(fp):
    """Lee los parámetros dimensionales y de configuración del COCO."""
    alto = float(fp.Alto)
    ancho = float(fp.Ancho)
    fondo = float(fp.FondoModulo)
    espesor = float(fp.Espesor)
    tapa = fp.Tapa
    base = fp.Base
    tiene_fondo = fp.TieneFondo
    calibre_fondo = float(fp.CalibreFondo)
    prof_ranura = float(fp.ProfundidadRanura)
    dist_borde = float(fp.DistanciaBorde)
    return (alto, ancho, fondo, espesor, tapa, base, tiene_fondo,
            calibre_fondo, prof_ranura, dist_borde)


def cajas_carcasa(alto, ancho, fondo, espesor, tapa, base):
    """Calcula laterales, base y techo del cofre (sin fondo)."""
    lat_height = alto
    lat_pos_z = 0.0

    if tapa == "externo":
        lat_height -= espesor
    if base == "externo":
        lat_height -= espesor
        lat_pos_z = espesor

    # --- Calcular dimensiones de base ---
    if base == "externo":
        base_length = ancho
        base_pos_x = 0.0
    else:
        base_length = ancho - (espesor * 2)
        base_pos_x = espesor

    base_pos_z = 0.0

    # --- Calcular dimensiones de tapa ---
    if tapa == "externo":
        techo_length = ancho
        techo_pos_x = 0.0
    else:
        techo_length = ancho - (espesor * 2)
        techo_pos_x = espesor

    techo_pos_z = alto - espesor

    # Panel lateral izquierdo
    lat_izq = _get_part().makeBox(espesor, fondo, lat_height,
                           _get_app().Vector(0, 0, lat_pos_z))

    # Panel lateral derecho
    lat_der = _get_part().makeBox(espesor, fondo, lat_height,
                           _get_app().Vector(ancho - espesor, 0, lat_pos_z))

    # Panel base
    panel_base = _get_part().makeBox(base_length, fondo, espesor,
                              _get_app().Vector(base_pos_x, 0, base_pos_z))

    # Panel techo
    panel_techo = _get_part().makeBox(techo_length, fondo, espesor,
                               _get_app().Vector(techo_pos_x, 0, techo_pos_z))

    return (lat_height, base_length, base_pos_x, base_pos_z, techo_length,
            techo_pos_x, techo_pos_z, lat_izq, lat_der, panel_base,
            panel_techo)


def caja_fondo(alto, ancho, fondo, espesor, tiene_fondo, calibre_fondo,
               prof_ranura, dist_borde, lat_izq, lat_der, panel_base,
               panel_techo, boxes):
    """Calcula el fondo en Y+ y las ranuras de los paneles. Añade los
    paneles y el fondo a boxes in situ."""
    # --- Fondo en Y+ (nunca en el frente) ---
    fondo_box = None
    fondo_es_delgado = False
    f_len = f_alt = f_x = f_y = f_z = 0.0
    if tiene_fondo:
        fondo_es_delgado = calibre_fondo <= VDO_D.FONDO_UMBRAL_DELGADO
        alto_cavidad = max(0.0, alto - (espesor * 2))
        ancho_cavidad = max(0.0, ancho - (espesor * 2))

        if fondo_es_delgado:
            prof = min(float(prof_ranura), max(0.0, espesor - 0.1))
            f_len = ancho_cavidad + (prof * 2)
            f_alt = alto_cavidad + (prof * 2)
            f_x = espesor - prof
            f_z = espesor - prof
            f_y = max(0.0, fondo - calibre_fondo - prof)
            f_y = min(f_y, max(0.0, fondo - calibre_fondo))

            g_y = f_y
            if prof > 0 and alto_cavidad > 0 and ancho_cavidad > 0:
                lat_izq = lat_izq.cut(_get_part().makeBox(
                    prof, calibre_fondo, alto_cavidad + (prof * 2),
                    _get_app().Vector(espesor - prof, g_y, espesor - prof)))
                lat_der = lat_der.cut(_get_part().makeBox(
                    prof, calibre_fondo, alto_cavidad + (prof * 2),
                    _get_app().Vector(ancho - espesor, g_y, espesor - prof)))
                panel_base = panel_base.cut(_get_part().makeBox(
                    ancho_cavidad + (prof * 2), calibre_fondo, prof,
                    _get_app().Vector(espesor - prof, g_y, espesor - prof)))
                panel_techo = panel_techo.cut(_get_part().makeBox(
                    ancho_cavidad + (prof * 2), calibre_fondo, prof,
                    _get_app().Vector(espesor - prof, g_y, alto - espesor)))
        else:
            f_len = ancho_cavidad
            f_alt = alto_cavidad
            f_x = espesor
            f_z = espesor
            f_y = fondo - calibre_fondo - dist_borde
            f_y = max(espesor, min(f_y, max(0.0, fondo - calibre_fondo)))

        fondo_box = _get_part().makeBox(f_len, calibre_fondo, f_alt,
                                 _get_app().Vector(f_x, f_y, f_z))

    boxes.extend([lat_izq, lat_der, panel_base, panel_techo])
    if fondo_box is not None:
        boxes.append(fondo_box)
    return (lat_izq, lat_der, panel_base, panel_techo, fondo_box,
            fondo_es_delgado, f_len, f_alt, f_x, f_y, f_z)
