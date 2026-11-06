# =====================================================================
# cajon_correderas.py
# Catálogo de correderas ocultas y telescópicas y selección de guía.
# Separado de vdo_cajon_despiece.py (M7, D-36).
# Axioma 2: lógica pura, SIN FreeCAD ni UI (testable con python3)
# =====================================================================

import logging
from types import MappingProxyType
from typing import Any

from freecad.vdo.core.manifest import _obtener_json
from freecad.vdo.datos.valores import OCULTA

_LOG = logging.getLogger(__name__)

_MANIFEST = MappingProxyType(_obtener_json())  # solo lectura (D-18)

# Tipologías de corredera (compatibles con cad/cajon.py)
CORREDERA_TELESCOPICA = "telescopica"
CORREDERA_OCULTA = OCULTA
CAJA_METALICA = "metalica"

try:
    from freecad.vdo.core import hardware_hub as H
except ImportError as exc:
    _LOG.debug("cajon_correderas: import opcional H no disponible: %s", exc)
    H = None


def _mecanizado_corredera(tecnicos):
    """Parametros de mecanizado de una corredera oculta del catalogo."""
    return {
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


def _marca_desde_catalogo(hw, marca_id):
    """Forma de entrada de manifest a partir de una entrada del catalogo."""
    tecnicos = hw["parametros_tecnicos"]
    return {
        "nombre": hw.get("nombre", marca_id),
        "delta_ancho": float(tecnicos.get("delta_ancho", 45.0)),
        "unidad_delta": "mm",
        "descripcion": hw.get("proveedor", ""),
        "longitudes_comerciales": [
            float(lon)
            for lon in tecnicos.get("longitudes_comerciales", [300, 350])
        ],
        "mecanizado": _mecanizado_corredera(tecnicos),
        "proveedor": hw.get("proveedor", ""),
        "precio_unitario": hw.get("precio_unitario", 0.0),
        "moneda": hw.get("moneda", "USD"),
    }


def _marcas_disponibles():
    """Marcas conocidas: catalogo de Capa H (si existe) y manifest, ordenadas."""
    disponibles = sorted(_MANIFEST.get("correderas_ocultas", {}).keys())
    if H is None:
        return disponibles
    try:
        disponibles_h = sorted(H.get_family("corredera_oculta").keys())
    except KeyError as exc:
        _LOG.debug("cajon_correderas: marca sin herrajes en el catalogo: %s", exc)
        disponibles_h = []
    return sorted(list(dict.fromkeys(disponibles_h + disponibles)))


def obtener_marca(marca_id: Any) -> Any:  # Any: definicion de marca leida del catalogo JSON
    """Devuelve la definición de una corredera oculta.

    Fuente primaria: catálogo de Capa H (hardware_hub).
    Fallback graceful: vdo_manifest.json para configuraciones antiguas.

    Returns:
        dict con la misma forma que las entradas de
        manifest["correderas_ocultas"]:
            nombre, delta_ancho, unidad_delta, descripcion,
            longitudes_comerciales, mecanizado, ...
    """
    if H is not None:
        hw = None
        try:
            hw = H.resolve_drawer_slide(tipo=OCULTA, marca=marca_id)
        except (KeyError, ValueError) as exc:
            _LOG.debug("cajon_correderas: herraje no encontrado: %s", exc)
            hw = None
        if hw is not None:
            return _marca_desde_catalogo(hw, marca_id)

    marcas = _MANIFEST.get("correderas_ocultas", {})
    if marca_id in marcas:
        return marcas[marca_id]
    raise ValueError(
        f"Marca de corredera desconocida: '{marca_id}'. "
        f"Disponibles: {', '.join(_marcas_disponibles())}")


def listar_marcas() -> list[str]:
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
        except KeyError as exc:
            _LOG.debug("cajon_correderas: catalogo de marca no disponible: %s", exc)
            catalogo_keys = []
            combinadas = list(dict.fromkeys(catalogo_keys + manifest_keys))
            return sorted(combinadas)
    return manifest_keys


# Any en longitudes_comerciales: lista JSON de longitudes.
def seleccionar_guia(prof_int: float, longitudes_comerciales: Any) -> float:
    """Selecciona la guía comercial inmediatamente inferior o igual.

    Args:
        prof_int (float): profundidad libre interior del mueble (mm)
        longitudes_comerciales (list): longitudes nominales (mm)

    Returns:
        float: LG seleccionada

    Raises:
        ValueError: si ProfInt es menor que la guía más corta
    """
    validas = sorted(float(lon) for lon in longitudes_comerciales)
    aptas = [lon for lon in validas if lon <= float(prof_int)]
    if not aptas:
        raise ValueError(
            f"ProfInt={prof_int} mm es menor que la guía comercial mínima "
            f"({validas[0]} mm). No hay corredera que encaje.")
    return aptas[-1]
