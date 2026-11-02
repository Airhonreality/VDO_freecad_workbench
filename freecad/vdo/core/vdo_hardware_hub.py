# -*- coding: utf-8 -*-
"""Capa H - Motor puro de consulta del catálogo de herrajes VDO.

No importa FreeCAD ni Qt. Solo lógica, JSON y decimales.
Sin estado mutable de módulo (M-08): el catálogo se carga fresco por llamada
o se inyecta como parámetro.
"""

from __future__ import annotations

import json
import os

try:
    _HERE = os.path.dirname(os.path.abspath(__file__))
except NameError:
    _HERE = os.getcwd()
_CATALOGO_PATH = os.path.join(_HERE, "vdo_hardware_catalog.json")

# ---------------------------------------------------------------------
# Datos de fallback integrados (usados si el catálogo en disco falta o
# no tiene las familias esperadas). Nunca rompe con FileNotFoundError.
# ---------------------------------------------------------------------
_FALLBACK_BISAGRA = {
    "GEN-CAZ-35-PARCHE": {
        "nombre": "Bisagra Cazoleta 35mm Cierre Suave - Recta (Parche)",
        "proveedor": "Genérico / Taller",
        "precio_unitario": 1.20,
        "moneda": "USD",
        "parametros_tecnicos": {
            "tipo_montaje": "parche",
            "brazo": "recta",
            "diametro_cazoleta": 35.0,
            "profundidad_cazoleta": 11.5,
            "cota_k_default": 4.0,
            "distancia_base_frente": 37.0,
            "separacion_tornillos_base": 32.0,
            "solape_nominal": 16.0,
            "holgura_luz": 2.0,
        },
    },
    "GEN-CAZ-35-SEMIPARCHE": {
        "nombre": "Bisagra Cazoleta 35mm Cierre Suave - Acodada (Semiparche)",
        "proveedor": "Genérico / Taller",
        "precio_unitario": 1.30,
        "moneda": "USD",
        "parametros_tecnicos": {
            "tipo_montaje": "semiparche",
            "brazo": "acodada",
            "diametro_cazoleta": 35.0,
            "profundidad_cazoleta": 11.5,
            "cota_k_default": 4.0,
            "solape_nominal": 8.0,
            "holgura_luz": 2.0,
        },
    },
    "GEN-CAZ-35-EMBEBIDA": {
        "nombre": "Bisagra Cazoleta 35mm Cierre Suave - Súper Acodada (Embebida)",
        "proveedor": "Genérico / Taller",
        "precio_unitario": 1.40,
        "moneda": "USD",
        "parametros_tecnicos": {
            "tipo_montaje": "embebida",
            "brazo": "super_acodada",
            "diametro_cazoleta": 35.0,
            "profundidad_cazoleta": 11.5,
            "cota_k_default": 4.0,
            "holgura_perimetral_min": 2.0,
        },
    },
}

_FALLBACK_CORREDIZO = {
    "DUC-KIT-D52": {
        "nombre": "Kit Corredizo Ducasse D-52 (Closet / Placard al Piso)",
        "proveedor": "Ducasse Industrial",
        "precio_unitario": 18.50,
        "moneda": "USD",
        "parametros_tecnicos": {
            "aplicacion": "closet_placard",
            "capacidad_peso_kg": 50.0,
            "montaje": "al_piso_dentro_vano",
            "ancho_minimo_hoja": 650.0,
            "descuento_altura_hoja": 33.0,
            "traslape_minimo": 35.0,
            "ancho_piso_riel_doble": 60.0,
            "espesor_hoja_min": 15.0,
        },
    },
    "DUC-AL-1535-MAD": {
        "nombre": "Sistema Corredizo Ducasse AL 1535 Madera (Muebles / Alacenas)",
        "proveedor": "Ducasse Industrial",
        "precio_unitario": 9.80,
        "moneda": "USD",
        "parametros_tecnicos": {
            "aplicacion": "muebles_alacenas",
            "capacidad_peso_kg": 15.0,
            "montaje": "al_piso_dentro_vano",
            "descuento_altura_hoja": 10.0,
            "traslape_minimo": 25.0,
            "ancho_piso_riel_doble": 26.0,
            "espesor_hoja_min": 15.0,
            "luz_cerrada_sin_cenefa": True,
        },
    },
}

_FAMILIAS = (
    "bisagra_cazoleta",
    "sistema_corredizo",
    "corredera_oculta",
    "corredera_telescopica",
)

_DEFAULT_HINGE_BY_MONTAJE = {
    "parche": "GEN-CAZ-35-PARCHE",
    "semiparche": "GEN-CAZ-35-SEMIPARCHE",
    "embebida": "GEN-CAZ-35-EMBEBIDA",
}

_DEFAULT_SLIDING_BY_MUEBLE = {
    "closet": "DUC-KIT-D52",
    "placard": "DUC-KIT-D52",
    "mueble": "DUC-AL-1535-MAD",
    "alacena": "DUC-AL-1535-MAD",
}

# Mapeo de claves del manifest (vdo_manifest.json → correderas_ocultas)
# hacia los SKU del catálogo de Capa H. Permite consumir el catálogo desde
# vdo_cajon_despiece sin romper configuraciones existentes.
_MARCA_A_SKU = {
    "blum_tandem": "BLUM-TANDEM",
    "generica": "GEN-OCULTA",
    "hafele": "HAFELE-OCULTA",
    "ducasse": "DUCASSE-OCULTA",
}


def _cargar_catalogo():
    """Carga el catálogo desde disco de forma segura.

    Nunca lanza FileNotFoundError: si el archivo falta o está mal formado,
    devuelve un dict vacío y se confía en los datos de fallback integrados.
    """
    datos = {}
    try:
        with open(_CATALOGO_PATH, encoding="utf-8") as _fh:
            datos = json.load(_fh)
    except (FileNotFoundError, json.JSONDecodeError, OSError, ValueError):
        datos = {}
    if isinstance(datos, dict):
        return datos
    return {}


def _catalogo_completo():
    """Devuelve el catálogo con fallbacks inyectados, cargado fresco.

    No guarda en variable de módulo: cada llamada lee de disco. Así no hay
    estado mutable de módulo (M-08). El llamador puede inyectar su propio
    catálogo si ya lo cargó una vez (app/composicion.py).
    """
    catalogo = _cargar_catalogo()
    for _fam in ("bisagra_cazoleta", "sistema_corredizo"):
        if _fam not in catalogo or not catalogo[_fam]:
            if _fam == "bisagra_cazoleta":
                catalogo[_fam] = dict(_FALLBACK_BISAGRA)
            elif _fam == "sistema_corredizo":
                catalogo[_fam] = dict(_FALLBACK_CORREDIZO)
    return catalogo


def _index_sku(catalogo):
    indice = {}
    for familia in _FAMILIAS:
        for sku in catalogo.get(familia, {}):
            indice[sku] = familia
    return indice


def _resolver_catalogo(catalogo=None):
    """Devuelve (catalogo, sku_a_familia). Si catalogo es None, carga fresco."""
    if catalogo is None:
        catalogo = _catalogo_completo()
    sku_a_familia = _index_sku(catalogo)
    return catalogo, sku_a_familia


def get_hardware(sku, catalogo=None):
    """Devuelve el diccionario completo del herraje (comercial + técnicos).

    Lanza KeyError descriptivo si el SKU no existe.

    Args:
        sku: SKU del herraje.
        catalogo: dict opcional (inyectado). Si None, se carga fresco.
    """
    catalogo, sku_a_familia = _resolver_catalogo(catalogo)
    sku = str(sku)
    familia = sku_a_familia.get(sku)
    if familia is None:
        raise KeyError(
            f"SKU {sku!r} no registrado en el catálogo de herrajes VDO.")
    return catalogo[familia][sku]


def get_family(familia, catalogo=None):
    """Devuelve todos los SKUs registrados bajo una familia."""
    catalogo, _ = _resolver_catalogo(catalogo)
    familia = str(familia)
    if familia not in _FAMILIAS:
        raise KeyError(
            f"Familia {familia!r} no existe en el catálogo de herrajes VDO.")
    return dict(catalogo.get(familia, {}))


def query_family(familia, catalogo=None):
    """Alias público de ``get_family`` para consultas de familia de herraje."""
    return get_family(familia, catalogo)


def resolve_hinge(tipo_montaje, prefer_sku=None, catalogo=None):
    """Helper para puertas batientes.

    Devuelve la bisagra de cazoleta 35 mm segun el tipo de montaje
    (parche / semiparche / embebida). Si se pide prefer_sku y existe,
    se devuelve ese SKU directamente.
    """
    catalogo, _ = _resolver_catalogo(catalogo)
    tipo_montaje = str(tipo_montaje).strip().lower()
    if prefer_sku:
        prefer_sku = str(prefer_sku)
        hw = None
        try:
            hw = get_hardware(prefer_sku, catalogo)
        except KeyError:
            hw = None
        if hw is not None:
            return hw
    sku = _DEFAULT_HINGE_BY_MONTAJE.get(tipo_montaje)
    if sku is None:
        raise KeyError(
            f"Tipo de montaje de bisagra {tipo_montaje!r} no soportado. "
            f"Validos: {tuple(_DEFAULT_HINGE_BY_MONTAJE)}.")
    return get_hardware(sku, catalogo)


def resolve_sliding(tipo_mueble="closet", catalogo=None):
    """Helper para puertas corredizas.

    closet/placard -> DUC-KIT-D52
    mueble/alacena   -> DUC-AL-1535-MAD
    """
    catalogo, _ = _resolver_catalogo(catalogo)
    tipo_mueble = str(tipo_mueble).strip().lower()
    sku = _DEFAULT_SLIDING_BY_MUEBLE.get(tipo_mueble)
    if sku is None:
        raise KeyError(
            f"Tipo de mueble corredizo {tipo_mueble!r} no soportado. "
            f"Validos: {tuple(_DEFAULT_SLIDING_BY_MUEBLE)}.")
    return get_hardware(sku, catalogo)


def resolve_drawer_slide(tipo="oculta", marca="blum_tandem", catalogo=None):
    """Helper para correderas de cajón.

    Devuelve el diccionario completo del herraje (comercial +
    ``parametros_tecnicos``) de la corredera solicitada.

    Acepta tanto SKU del catálogo (ej. ``BLUM-TANDEM``) como claves del
    manifest (ej. ``blum_tandem``). Si el SKU no existe en el catálogo,
    lanza ``KeyError`` descriptivo.

    Args:
        tipo: tipo de corredera ("oculta" o "telescopica").
        marca: SKU del catálogo o clave del manifest.
        catalogo: dict opcional (inyectado). Si None, se carga fresco.

    Returns:
        dict: entrada completa del catálogo para esa corredera,
        con una clave adicional ``"sku"`` que indica el SKU resuelto.
    """
    catalogo, sku_a_familia = _resolver_catalogo(catalogo)
    tipo = str(tipo).strip().lower()
    marca = str(marca).strip()
    sku_encontrado = None

    # 1. Intento directo: el caller ya pasó un SKU del catálogo.
    hw = None
    try:
        hw = get_hardware(marca, catalogo)
    except KeyError:
        hw = None
    if hw is not None and hw["parametros_tecnicos"].get("tipo_corredera") in (tipo, None, ""):
        sku_encontrado = marca
        return {**hw, "sku": sku_encontrado}

    # 2. Normalización: blum_tandem -> BLUM-TANDEM
    normalizada = marca.upper().replace("_", "-")
    if normalizada != marca:
        hw = None
        try:
            hw = get_hardware(normalizada, catalogo)
        except KeyError:
            hw = None
        if hw is not None and hw["parametros_tecnicos"].get("tipo_corredera") in (tipo, None, ""):
            sku_encontrado = normalizada
            return {**hw, "sku": sku_encontrado}

    # 3. Tabla de mapeo de claves del manifest.
    sku = _MARCA_A_SKU.get(marca.lower())
    if sku:
        hw = None
        try:
            hw = get_hardware(sku, catalogo)
        except KeyError:
            hw = None
        if hw is not None and hw["parametros_tecnicos"].get("tipo_corredera") in (tipo, None, ""):
            sku_encontrado = sku
            return {**hw, "sku": sku_encontrado}

    # 4. Búsqueda por familia si se pasó el tipo genérico.
    familia = "corredera_oculta" if tipo == "oculta" else "corredera_telescopica"
    try:
        familia_skus = get_family(familia, catalogo)
    except KeyError:
        familia_skus = {}
    if marca.lower() in {s.lower() for s in familia_skus}:
        for sku_cand in familia_skus:
            if sku_cand.lower() == marca.lower():
                hw = get_hardware(sku_cand, catalogo)
                sku_encontrado = sku_cand
                return {**hw, "sku": sku_encontrado}

    raise KeyError(
        f"Corredera {tipo} / {marca!r} no encontrada en el catálogo de "
        f"herrajes VDO. SKUs disponibles: {sorted(sku_a_familia)}.")


def calculate_sliding_doors(inner_w, inner_h, sku, n_hojas=2, catalogo=None):
    """Calcula el despiece de hojas corredizas.

    H_hoja = inner_h - descuento_altura_hoja
    W_hoja = (inner_w + (n_hojas - 1) * traslape) / n_hojas
    """
    catalogo, _ = _resolver_catalogo(catalogo)
    inner_w = float(inner_w)
    inner_h = float(inner_h)
    n_hojas = int(n_hojas)
    if n_hojas < 1:
        raise ValueError("n_hojas debe ser >= 1.")
    herraje = get_hardware(sku, catalogo)
    tecnicos = herraje["parametros_tecnicos"]
    descuento = float(tecnicos["descuento_altura_hoja"])
    traslape = float(tecnicos["traslape_minimo"])

    h_hoja = inner_h - descuento
    w_hoja = (inner_w + (n_hojas - 1) * traslape) / n_hojas

    hojas = []
    for i in range(n_hojas):
        hojas.append({
            "hoja": i + 1,
            "sku": sku,
            "nombre": herraje["nombre"],
            "proveedor": herraje["proveedor"],
            "ancho_corte": round(w_hoja, 6),
            "alto_corte": round(h_hoja, 6),
            "descuento_altura_hoja": descuento,
            "traslape_minimo": traslape,
        })

    return {
        "sku": sku,
        "nombre": herraje["nombre"],
        "proveedor": herraje["proveedor"],
        "precio_unitario": herraje["precio_unitario"],
        "moneda": herraje["moneda"],
        "inner_w": inner_w,
        "inner_h": inner_h,
        "n_hojas": n_hojas,
        "descuento_altura_hoja": descuento,
        "traslape_minimo": traslape,
        "alto_hoja": round(h_hoja, 6),
        "ancho_hoja": round(w_hoja, 6),
        "hojas": hojas,
    }


__all__ = [
    "get_hardware",
    "get_family",
    "query_family",
    "resolve_hinge",
    "resolve_sliding",
    "resolve_drawer_slide",
    "calculate_sliding_doors",
]
