# =====================================================================
# vdo_cajon_correderas.py
# Catálogo de correderas ocultas y telescópicas y selección de guía.
# Separado de vdo_cajon_despiece.py (M7, D-36).
# Axioma 2: lógica pura, SIN FreeCAD ni UI (testable con python3)
# =====================================================================

from types import MappingProxyType

from freecad.vdo.core.vdo_manifest import _obtener_json
from freecad.vdo.datos.valores import OCULTA

_MANIFEST = MappingProxyType(_obtener_json())  # solo lectura (D-18)

# Tipologías de corredera (compatibles con cad/cajon.py)
CORREDERA_TELESCOPICA = "telescopica"
CORREDERA_OCULTA = OCULTA
CAJA_METALICA = "metalica"

try:
    from freecad.vdo.core import vdo_hardware_hub as H
except ImportError:
    H = None


def obtener_marca(marca_id):
    """Devuelve la definición de una corredera oculta.

    Fuente primaria: catálogo de Capa H (vdo_hardware_hub).
    Fallback graceful: vdo_manifest.json para configuraciones antiguas.

    Returns:
        dict con la misma forma que las entradas de
        manifest["correderas_ocultas"]:
            nombre, delta_ancho, unidad_delta, descripcion,
            longitudes_comerciales, mecanizado, ...
    """
    # --- Intento 1: catálogo de Capa H ---------------------------------
    if H is not None:
        hw = None
        try:
            hw = H.resolve_drawer_slide(tipo=OCULTA, marca=marca_id)
        except (KeyError, ValueError):
            hw = None
        if hw is not None:
            tecnicos = hw["parametros_tecnicos"]
            mecanizado = {
                "diam_taladro": float(
                    tecnicos.get("diametro_pin_trasero", 6.0)),
                "prof_taladro": float(
                    tecnicos.get("profundidad_pin_trasero", 12.0)),
                "dist_taladro_borde_trasero": float(
                    tecnicos.get("distancia_pin_borde_trasero", 8.0)),
                "dist_taladro_sobre_ranura": 11.0,
                "prof_ranura_lateral": float(
                    tecnicos.get("prof_ranura_lateral", 4.0)),
                "notch_ancho": float(tecnicos.get("notch_ancho", 25.0)),
                "notch_alto": float(tecnicos.get("notch_alto", 20.0)),
            }
            return {
                "nombre": hw.get("nombre", marca_id),
                "delta_ancho": float(tecnicos.get("delta_ancho", 45.0)),
                "unidad_delta": "mm",
                "descripcion": hw.get("proveedor", ""),
                "longitudes_comerciales": [
                    float(l)
                    for l in tecnicos.get("longitudes_comerciales", [300, 350])
                ],
                "mecanizado": mecanizado,
                "proveedor": hw.get("proveedor", ""),
                "precio_unitario": hw.get("precio_unitario", 0.0),
                "moneda": hw.get("moneda", "USD"),
            }

        # --- Intento 2: fallback al manifest (archivo viejo) ---
        marcas = _MANIFEST.get("correderas_ocultas", {})
        if marca_id in marcas:
            return marcas[marca_id]

        disponibles = sorted(_MANIFEST.get("correderas_ocultas", {}).keys())
        if H is not None:
            try:
                disponibles_h = sorted(
                    H.get_family("corredera_oculta").keys())
                disponibles = sorted(
                    list(dict.fromkeys(disponibles_h + disponibles)))
            except KeyError:
                disponibles_h = []
                disponibles = sorted(
                    list(dict.fromkeys(disponibles_h + disponibles)))
        raise ValueError(
            f"Marca de corredera desconocida: '{marca_id}'. "
            f"Disponibles: {', '.join(disponibles)}")

    # --- Intento 2: fallback al manifest (archivo viejo) ---------------
    marcas = _MANIFEST.get("correderas_ocultas", {})
    if marca_id in marcas:
        return marcas[marca_id]

    disponibles = sorted(_MANIFEST.get("correderas_ocultas", {}).keys())
    if H is not None:
        try:
            disponibles_h = sorted(
                H.get_family("corredera_oculta").keys())
            disponibles = sorted(
                list(dict.fromkeys(disponibles_h + disponibles)))
        except KeyError:
            disponibles_h = []
            disponibles = sorted(
                list(dict.fromkeys(disponibles_h + disponibles)))
    raise ValueError(
        f"Marca de corredera desconocida: '{marca_id}'. "
        f"Disponibles: {', '.join(disponibles)}")


def listar_marcas():
    """Lista las claves de correderas ocultas disponibles.

    Combina los SKUs del catálogo de Capa H con las claves del manifest,
    priorizando los SKUs del catálogo.
    """
    manifest_keys = sorted(_MANIFEST.get("correderas_ocultas", {}).keys())
    if H is not None:
        try:
            catalogo_keys = sorted(
                H.get_family("corredera_oculta").keys())
            combinadas = list(dict.fromkeys(catalogo_keys + manifest_keys))
            return sorted(combinadas)
        except KeyError:
            catalogo_keys = []
            combinadas = list(dict.fromkeys(catalogo_keys + manifest_keys))
            return sorted(combinadas)
    return manifest_keys


def seleccionar_guia(prof_int, longitudes_comerciales):
    """Selecciona la guía comercial inmediatamente inferior o igual.

    Args:
        prof_int (float): profundidad libre interior del mueble (mm)
        longitudes_comerciales (list): longitudes nominales (mm)

    Returns:
        float: LG seleccionada

    Raises:
        ValueError: si ProfInt es menor que la guía más corta
    """
    validas = sorted(float(l) for l in longitudes_comerciales)
    aptas = [l for l in validas if l <= float(prof_int)]
    if not aptas:
        raise ValueError(
            f"ProfInt={prof_int} mm es menor que la guía comercial mínima "
            f"({validas[0]} mm). No hay corredera que encaje.")
    return aptas[-1]
