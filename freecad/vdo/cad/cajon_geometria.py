# =====================================================================
# cajon_geometria.py
# Capa cad: helpers geométricos puros del cajón (sustracciones con
# prismas y cilindros en coordenadas calculadas). Extraído de cajon.py (D-49).
# =====================================================================

from freecad.vdo.core.vdo_helpers import _get_app, _get_part


def _box(pos):
    """Crea un sólido Box desde un dict de posición/dimensiones."""
    return _get_part().makeBox(
        pos["largo_x"], pos["largo_y"], pos["largo_z"],
        _get_app().Vector(pos["x"], pos["y"], pos["z"]))


def _cilindro(radio, alto, base, direccion):
    """Crea un cilindro para operaciones booleanas."""
    return _get_part().makeCylinder(radio, alto, base, direccion)


def _aplicar_corte(solido, herramienta):
    """Aplica una sustracción booleana segura."""
    if solido is None or herramienta is None:
        return solido
    resultado = solido.cut(herramienta)
    if resultado is not None and resultado.isValid():
        return resultado
    return solido


def _corte_notch_lateral(solido, pos, notch_ancho, notch_alto, lg):
    """
    Cajeado trasero en lateral: sustrae prisma de notch_ancho (profundidad Y)
    x notch_alto (altura Z) en el talón inferior-trasero.
    """
    caja_notch = _get_part().makeBox(
        pos["largo_x"],           # X: todo el grosor del lateral
        notch_ancho,              # Y: 35 mm desde el borde trasero
        notch_alto,               # Z: 12 mm desde el borde inferior
        _get_app().Vector(
            pos["x"],
            pos["y"] + lg - notch_ancho,  # Y: desde lg-ancho hasta lg
            pos["z"],
        ),
    )
    return _aplicar_corte(solido, caja_notch)


def _corte_pin_trasero(solido, pos, diam, profundidad, z_piso, g_fondo,
                       alto_contra, ancho_contra, g_caja):
    """
    Taladro para pin de bloqueo en cara posterior del testero trasero.
    Cilindro Ødiam x profundidad mm, partiendo de la cara trasera
    y yendo hacia adelante (-Y).
    """
    cx = pos["x"] + ancho_contra / 2.0
    cy = pos["y"] + pos["largo_y"]       # cara posterior (Y max)
    cz = pos["z"] + alto_contra / 2.0    # centro en Z
    pin = _cilindro(diam / 2.0, profundidad,
                    _get_app().Vector(cx, cy, cz),
                    _get_app().Vector(0, -1, 0))
    return _aplicar_corte(solido, pin)


def _corte_ranura_piso(solido, pos, prof_ranura, z_piso, grosor_piso, lg):
    """
    Ranura perimetral para piso delgado (telescópica).
    Sustrae prisma de prof_ranura (profundidad X) x grosor_piso (altura Z)
    en la cara interna del lateral, a la altura del piso.
    """
    caja_ranura = _get_part().makeBox(
        prof_ranura,              # X: profundidad de la ranura desde cara interna
        lg,                       # Y: todo el largo del lateral
        grosor_piso,              # Z: grosor del piso
        _get_app().Vector(
            pos["x"] + pos["largo_x"] - prof_ranura,  # X: cara interna
            pos["y"],
            z_piso,               # Z: altura del piso
        ),
    )
    return _aplicar_corte(solido, caja_ranura)


def _aplicar_bisel_45_fachada(solido, pos, ancho, alto, bisel_dist=5.0):
    """
    Bisel paramétrico a 45° en la arista superior frontal de la fachada.
    Crea una cara triangular en el plano Y-Z y la extruye a lo largo de X.
    """
    # Puntos del triángulo a remover (plano Y-Z en la cara frontal):
    #   p1: esquina superior-frente  (y=0, z=alto)
    #   p2: retrasado en cima        (y=-bisel_dist, z=alto)
    #   p3: abajo en cara frontal    (y=0, z=alto-bisel_dist)
    p1 = _get_app().Vector(0, 0, alto)
    p2 = _get_app().Vector(0, -bisel_dist, alto)
    p3 = _get_app().Vector(0, 0, alto - bisel_dist)

    wire = _get_part().makePolygon([p1, p2, p3], True)
    cara = _get_part().Face(wire)
    herramienta = cara.extrude(_get_app().Vector(ancho, 0, 0))
    herramienta.translate(_get_app().Vector(pos["x"], pos["y"], pos["z"]))

    return _aplicar_corte(solido, herramienta)
