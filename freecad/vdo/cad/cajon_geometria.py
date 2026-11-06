# =====================================================================
# cajon_geometria.py
# Capa cad: helpers geométricos puros del cajón (sustracciones con
# prismas y cilindros en coordenadas calculadas). Extraído de cajon.py (D-49).
# =====================================================================

from typing import Any

from freecad.vdo.core.cajon_correderas import CAJA_METALICA, CORREDERA_OCULTA, CORREDERA_TELESCOPICA
from freecad.vdo.core.facade_contract import BISEL_45_ANGULO_DEFAULT, necesita_bisel_45
from freecad.vdo.core.helpers import _get_app, _get_part


def _box(pos: dict[str, Any]) -> Any:  # pos: dict de FreeCAD-agnóstico (JSON del despiece)
    """Crea un sólido Box desde un dict de posición/dimensiones."""
    return _get_part().makeBox(
        pos["largo_x"], pos["largo_y"], pos["largo_z"],
        _get_app().Vector(pos["x"], pos["y"], pos["z"]))


# base y direccion son App.Vector de FreeCAD (sin tipos): Any.
def _cilindro(radio: float, alto: float, base: Any, direccion: Any) -> Any:
    """Crea un cilindro para operaciones booleanas."""
    return _get_part().makeCylinder(radio, alto, base, direccion)


def _aplicar_corte(solido: Any, herramienta: Any) -> Any:  # sólidos Part.Shape
    """Aplica una sustracción booleana segura."""
    if solido is None or herramienta is None:
        return solido
    resultado = solido.cut(herramienta)
    if resultado is not None and resultado.isValid():
        return resultado
    return solido


def _corte_notch_lateral(solido: Any, pos: dict[str, Any], notch_ancho: float,
                         notch_alto: float, lg: float) -> Any:
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


def _corte_pin_trasero(solido: Any, pos: dict[str, Any], diam: float, profundidad: float,
                       z_piso: float, g_fondo: float, alto_contra: float,
                       ancho_contra: float, g_caja: float) -> Any:
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


def _corte_ranura_piso(solido: Any, pos: dict[str, Any], prof_ranura: float,
                       z_piso: float, grosor_piso: float, lg: float) -> Any:
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


def _aplicar_bisel_45_fachada(solido: Any, pos: dict[str, Any], ancho: float, alto: float,
                              bisel_dist: float = 5.0) -> Any:
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


# =====================================================================
# Constructores de bloques del cajón (D-55). Mismo orden de llamadas a
# FreeCAD que el cuerpo original de CajonFeature.execute.
# =====================================================================

def _construir_laterales(tipo_corredera: str, posiciones: dict[str, dict[str, Any]],
                         notch_ancho: float, notch_alto: float,
                         diam_t: float, prof_t: float, prof_ranura: float, z_piso: float,
                         g_fondo: float, alto_lateral: float, lg: float,
                         g_caja: float) -> list[Any]:
    """Laterales de madera con su mecanizado; vacío en caja metálica."""
    solids: list[Any] = []
    if tipo_corredera != CAJA_METALICA:
        for clave in ("lateral_izquierdo", "lateral_derecho"):
            lateral = _box(posiciones[clave])

            if tipo_corredera == CORREDERA_OCULTA:
                # Notch: 35 x 12 mm en talón inferior-trasero
                lateral = _corte_notch_lateral(
                    lateral, posiciones[clave],
                    notch_ancho, notch_alto, lg)
                # Pin de bloqueo en cara posterior del lateral
                lateral = _corte_pin_trasero(
                    lateral, posiciones[clave],
                    diam_t, prof_t, z_piso, g_fondo,
                    alto_lateral, lg, g_caja)

            elif tipo_corredera == CORREDERA_TELESCOPICA:
                # Ranura para piso delgado (5.5 mm) en cara interna
                lateral = _corte_ranura_piso(
                    lateral, posiciones[clave],
                    prof_ranura, z_piso, g_fondo, lg)

            solids.append(lateral)
    return solids


def _construir_contra(tipo_corredera: str, posiciones: dict[str, dict[str, Any]],
                      notch_ancho: float, notch_alto: float,
                      diam_t: float, prof_t: float, z_piso: float, g_fondo: float,
                      alto_contra: float, ancho_contra: float, g_caja: float) -> Any:
    """Contra-frente (trasera de madera, siempre presente)."""
    contra = _box(posiciones["contra_frente"])
    if tipo_corredera == CORREDERA_OCULTA:
        # Notch en esquinas inferiores de la contra-frente
        contra = _corte_notch_lateral(
            contra, posiciones["contra_frente"],
            notch_ancho, notch_alto,
            posiciones["contra_frente"]["largo_y"])
        # Pin de bloqueo en cara posterior del testero trasero
        contra = _corte_pin_trasero(
            contra, posiciones["contra_frente"],
            diam_t, prof_t, z_piso, g_fondo,
            alto_contra, ancho_contra, g_caja)
    return contra


def _construir_fachada(sistema_apertura: str, fachada_pos: dict[str, Any],
                       fachada: dict[str, Any]) -> Any:
    """Fachada decorativa, con bisel 45 si el sistema de apertura lo exige."""
    fachada_solid = _box(fachada_pos)
    if necesita_bisel_45(sistema_apertura):
        fachada_solid = _aplicar_bisel_45_fachada(
            fachada_solid, fachada_pos,
            fachada["ancho"], fachada["alto"],
            bisel_dist=BISEL_45_ANGULO_DEFAULT / 9.0  # ~5 mm bisel
        )
    return fachada_solid


def _solidos_cajon(d: dict[str, Any], tipo_corredera: str,
                   sistema_apertura: str) -> list[Any]:
    """Sólidos del cajón en orden: laterales, contra, frente, piso, fachada."""
    caja = d["caja"]
    posiciones = d["posiciones"]
    mecanizados = d["mecanizados"]

    g_caja = caja["grosor"]
    g_fondo = caja["grosor_piso"]
    z_piso = caja["z_piso"]
    lg = caja["largo_lateral"]
    alto_lateral = caja["alto_lateral"]
    ancho_contra = caja["ancho_contra"]
    alto_contra = caja["alto_contra"]

    notch_ancho = float(mecanizados.get("notch_ancho", 35.0))
    notch_alto = float(mecanizados.get("notch_alto", 12.0))
    diam_t = float(mecanizados.get("diam_taladro", 6.0))
    prof_t = float(mecanizados.get("prof_taladro", 10.0))
    prof_ranura = float(mecanizados.get("prof_ranura_lateral", 4.0))

    # 1. Laterales (solo si no es caja metálica)
    solids = _construir_laterales(
        tipo_corredera, posiciones, notch_ancho, notch_alto,
        diam_t, prof_t, prof_ranura, z_piso, g_fondo,
        alto_lateral, lg, g_caja)

    # 2. Contra-frente (trasera de madera - siempre presente)
    solids.append(_construir_contra(
        tipo_corredera, posiciones, notch_ancho, notch_alto,
        diam_t, prof_t, z_piso, g_fondo, alto_contra,
        ancho_contra, g_caja))

    # 3. Frente interior (solo si no es caja metálica)
    if tipo_corredera != CAJA_METALICA:
        solids.append(_box(posiciones["frente_interior"]))

    # 4. Piso
    solids.append(_box(posiciones["piso"]))

    # 5. Fachada (con integración de contrato universal)
    solids.append(_construir_fachada(
        sistema_apertura, posiciones["fachada"], d["fachada"]))
    return solids
