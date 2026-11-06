# =====================================================================
# manifest.py
# Cargador de manifesto JSON para VDO
# PRINCIPIO: JSON es la fuente única de verdad
# Carga FRESCA del JSON cada acceso (sin caché de módulo)
# Absorbe los métodos de vdo_loader.py como funciones de nivel módulo.
# =====================================================================

import json
import os
from types import MappingProxyType
from typing import Any


def _obtener_json() -> Any:  # Any: JSON del manifiesto, sin esquema fijo en código
    """Carga vdo_manifest.json directamente, sin caché de módulo."""
    macro_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(macro_dir, "vdo_manifest.json")

    if not os.path.exists(json_path):
        raise FileNotFoundError(f"vdo_manifest.json no encontrado en: {json_path}")

    with open(json_path, encoding='utf-8') as f:
        return json.load(f)


# --- Funciones de acceso tipado (absorbidas de vdo_loader.py) ---------

def get_material(material_id):
    """Obtiene especificación de material."""
    return _obtener_json().get("materiales", {}).get(material_id)


def get_hardware(hardware_id):
    """Obtiene especificación de herraje."""
    return _obtener_json().get("herrajes", {}).get(hardware_id)


def calcular_costo_material(material_id, area_m2):
    """Calcula costo de material."""
    material = get_material(material_id)
    if not material:
        return 0
    return material.get("costo_m2", 0) * area_m2


def get_loader():
    """Devuelve el manifiesto cargado (carga fresca)."""
    return _obtener_json()


# Cargar JSON al importar (conservado para compatibilidad; las funciones
# de acceso siempre leen fresco del fichero).
# Solo lectura (D-18): mapping de nivel superior inmutable. Los sub-dicts siguen siendo
# dicts; ningún código los muta (verificado por grep).
VDO_MANIFEST = MappingProxyType(_obtener_json())
