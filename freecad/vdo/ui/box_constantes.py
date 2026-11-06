"""Constantes, tablas e iconos. Parte de ui/box_controller.py (M7, D-44)."""

from freecad.vdo.core import reengrose_modelo as VDO_RE_MODELO
from freecad.vdo.ui.tema import LUCIDE_ICONS, get_svg_icon as _svg_icon


# ----------------------------------------------------------------------
# Iconos Vectoriales Lucide Embebidos (SVG)
# ----------------------------------------------------------------------

_ICON_CACHE = {}


def obtener_svg_icon(name, size=22):
    return _svg_icon(name, size, icons_map=LUCIDE_ICONS, cache=_ICON_CACHE)


# ----------------------------------------------------------------------
# Constantes de Geometría y Encuentros
# ----------------------------------------------------------------------
# Tablas de dominio: una sola definición en core (P-07, duplicados exactos).
TIPOS_ENCUENTRO = VDO_RE_MODELO.ESQUINAS

ENCUENTRO_TOOLTIPS = {
    "vertical_domina": "Tope lateral (Lateral pasa continuo punta a punta)",
    "horizontal_domina": "Tope frontal (Frente/Fondo pasa continuo punta a punta)",
    "inglete_45": "Inglete 45° (Corte diagonal a 45° en la esquina)",
    "marco_interior": "Marco interior (Ambos lados frenan antes de la esquina)",
}

ENCUENTRO_LABELS = {
    "vertical_domina": "Tope lateral",
    "horizontal_domina": "Tope frontal",
    "inglete_45": "Inglete 45°",
    "marco_interior": "Marco interior",
}

ESQUINAS = VDO_RE_MODELO.ESQUINAS_2D

BORDE_NOMBRES = {
    "frente": "Frente (Sur)",
    "fondo": "Fondo (Norte)",
    "izquierda": "Izquierda (Oeste)",
    "derecha": "Derecha (Este)",
}


# borde -> plantilla del texto del boton (w: ancho en mm, t: texto del offset)
_TEXTO_BOTON_BORDE = {
    "fondo": lambda w, t: f"▲ FONDO · {w:.0f}mm ({t})",
    "frente": lambda w, t: f"▼ FRENTE · {w:.0f}mm ({t})",
    "izquierda": lambda w, t: f"◄ IZQ\n{w:.0f}mm\n{t}",
    "derecha": lambda w, t: f"DER ►\n{w:.0f}mm\n{t}",
}


# margen seleccionado -> segmento (x1, y1, x2, y2) de la linea de resaltado
_SEGMENTO_MARGEN_SEL = {
    "fondo": lambda x0, y0, bw, bh: (x0, y0, x0 + bw, y0),
    "frente": lambda x0, y0, bw, bh: (x0, y0 + bh, x0 + bw, y0 + bh),
    "izquierda": lambda x0, y0, bw, bh: (x0, y0, x0, y0 + bh),
    "derecha": lambda x0, y0, bw, bh: (x0 + bw, y0, x0 + bw, y0 + bh),
}
