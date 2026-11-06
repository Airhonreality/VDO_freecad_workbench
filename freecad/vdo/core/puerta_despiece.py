# =====================================================================
# puerta_despiece.py
# Capa 0 - Fórmulas de corte, cálculo de Newtons, holguras y posiciones
# de mecanizado para Puertas y Cierres (L2).
# No importa FreeCAD ni Qt. Solo lógica, decimales y catálogo de Capa H.
# =====================================================================

from __future__ import annotations

from typing import Any

from freecad.vdo.core.aperturas import (
    SISTEMAS_APERTURA,
    normalizar_apertura,
)
from freecad.vdo.core.facade_contract import (
    APERTURA_45_GRADOS,
    APERTURA_GOLA,
    APERTURA_PUSH_OPEN,
    APERTURA_TIRADOR,
    BISEL_45_ANGULO_DEFAULT,
    GOLA_DESCUENTO_ALTURA_DEFAULT,
    HOLGURA_PERIMETRAL_DEFAULT,
    MONTAJE_EMBEBIDA,
    MONTAJE_PARCHE,
    MONTAJE_SEMIPARCHE,
    SOLAPE_PARCHE_NOMINAL,
    aplicar_sistema_apertura,
    calcular_fachada_base,
    cantos_por_sistema_apertura,
    necesita_bisel_45,
    necesita_cantos_45,
    necesita_descuento_gola,
    necesita_expulsor_magnetico,
)
from freecad.vdo.core.hardware_hub import (
    calculate_sliding_doors,
    resolve_hinge,
    resolve_sliding,
)

# ---------------------------------------------------------------------
# Constantes de taller (fuente única: facade_contract.py)
# ---------------------------------------------------------------------

CAZALETA_DIAMETRO = 35.0      # mm
CAZALETA_PROFUNDIDAD = 11.5   # mm
COTA_K_DEFAULT = 4.0          # mm (distancia de la cara al centro de la cazoleta)
COTA_CAZOLETA_X = COTA_K_DEFAULT + CAZALETA_DIAMETRO / 2.0  # 21.5 mm
COTA_CAZOLETA_Z_EXTREMO = 100.0  # mm desde el borde superior/inferior

HOLGURA_LUZ_DEFAULT = HOLGURA_PERIMETRAL_DEFAULT  # mm (parche / semiparche)
SOLAPE_SEMIPARCHE_NOMINAL = 8.0   # mm sobre montante compartido (legacy default)

DENSIDAD_MELAMINA_KG_M3 = 720.0   # kg/m^3
ESPESOR_PANEL_M = 0.018           # m (18 mm)
GRAVEDAD = 9.81                   # m/s^2
BRAZO_PALANCA_M = 0.12            # m
NUM_PISTONES = 2
FACTOR_SEGURIDAD = 1.2

PISTONES_COMERCIALES_N = [60, 80, 100, 120, 150]

# Umbrales de altura para cantidad de bisagras (mm)
UMBRAL_2_BISAGRAS = 1000.0
UMBRAL_3_BISAGRAS = 1500.0


# =====================================================================
# A. Puertas Batientes Verticales
# =====================================================================

def calcular_dimensiones_batiente(W_neto, H_neto, tipo_montaje,
                                  solape=SOLAPE_SEMIPARCHE_NOMINAL,
                                  holgura=None):
    """Calcula el corte neto de la puerta batiente vertical.

    Consume `calcular_fachada_base` de facade_contract.py como fuente
    unica de verdad para todos los frentes del sistema.

    Args:
        W_neto: luz libre horizontal del vano (mm).
        H_neto: luz libre vertical del vano (mm).
        tipo_montaje: "parche", "semiparche" o "embebida".
        solape: solape nominal (mm) para semiparche (default 8 mm).
        holgura: holgura perimetral/luz (mm). Default 2.0 mm.

    Returns:
        dict con W, H, tipo_montaje, holgura, solape.
    """
    tipo_montaje = str(tipo_montaje).strip().lower()
    if holgura is None:
        holgura = HOLGURA_PERIMETRAL_DEFAULT

    # Usar el contrato central para el calculo puro
    w, h = calcular_fachada_base(W_neto, H_neto, tipo_montaje,
                                  holgura=holgura, solape=solape)

    return {
        "W": w,
        "H": h,
        "tipo_montaje": tipo_montaje,
        "holgura": holgura,
        "solape": solape,
    }


def cantidad_bisagras(H):
    """Devuelve la cantidad de bisagras segun la regla de altura de taller.

    H < 1000 -> 2
    1000 <= H < 1500 -> 3
    H >= 1500 -> 4
    """
    H = float(H)
    if H < UMBRAL_2_BISAGRAS:
        return 2
    if H < UMBRAL_3_BISAGRAS:
        return 3
    return 4


def posiciones_cazoleta(H, n_bisagras=None, cota_extremo=COTA_CAZOLETA_Z_EXTREMO):
    """Calcula las cotas Z de los centros de las cazoletas.

    Los extremos superior e inferior se colocan a cota_extremo del borde.
    Las intermedias se distribuyen equitativamente en Z.

    Args:
        H: altura de la puerta (mm).
        n_bisagras: cantidad (se calcula si no se pasa).
        cota_extremo: distancia desde el borde superior/inferior (mm).

    Returns:
        lista de cotas Z (mm) desde el borde superior de la puerta.
    """
    H = float(H)
    if n_bisagras is None:
        n_bisagras = cantidad_bisagras(H)
    n_bisagras = int(n_bisagras)

    if n_bisagras <= 0:
        return []

    if n_bisagras == 1:
        return [round(H / 2.0, 6)]

    # Extremos fijos, intermedias equidistantes.
    if n_bisagras == 2:
        zs = [cota_extremo, H - cota_extremo]
    else:
        paso = (H - 2.0 * cota_extremo) / (n_bisagras - 1)
        zs = [round(cota_extremo + i * paso, 6) for i in range(n_bisagras)]

    return zs


def cazoleta_tecnica():
    """Devuelve los parámetros técnicos de la cazoleta de 35 mm."""
    return {
        "diametro": CAZALETA_DIAMETRO,
        "radio": CAZALETA_DIAMETRO / 2.0,
        "profundidad": CAZALETA_PROFUNDIDAD,
        "cota_k": COTA_K_DEFAULT,
        "cota_x": COTA_CAZOLETA_X,
        "cota_z_extremo": COTA_CAZOLETA_Z_EXTREMO,
    }


def bisagras_para_puerta(H: float, tipo_montaje: str = "parche",
                         prefer_sku: str | None = None) -> dict[str, Any]:
    """Resuelve las bisagras y sus posiciones para una puerta batiente.

    Consulta Capa H (resolve_hinge) y aplica la regla de altura de taller.

    Returns:
        dict con sku, nombre, proveedor, precio_unitario, n_bisagras,
        posiciones_z, cota_x, profundidad_cazoleta, diametro_cazoleta.
    """
    herraje = resolve_hinge(tipo_montaje, prefer_sku=prefer_sku)
    tecnicos = herraje["parametros_tecnicos"]
    n = cantidad_bisagras(H)
    zs = posiciones_cazoleta(H, n)
    return {
        "sku": herraje.get("sku", tipo_montaje.upper()),
        "nombre": herraje["nombre"],
        "proveedor": herraje["proveedor"],
        "precio_unitario": herraje["precio_unitario"],
        "moneda": herraje["moneda"],
        "tipo_montaje": tipo_montaje,
        "n_bisagras": n,
        "posiciones_z": zs,
        "cota_x": COTA_CAZOLETA_X,
        "profundidad_cazoleta": float(tecnicos.get("profundidad_cazoleta",
                                                   CAZALETA_PROFUNDIDAD)),
        "diametro_cazoleta": float(tecnicos.get("diametro_cazoleta",
                                                CAZALETA_DIAMETRO)),
        "cota_k": float(tecnicos.get("cota_k_default", COTA_K_DEFAULT)),
        "total": round(herraje["precio_unitario"] * n, 2),
    }


# =====================================================================
# B. Puertas Horizontales (Basculantes / Abatibles) - Newtons
# =====================================================================

def masa_puerta(W, H, t=ESPESOR_PANEL_M, rho=DENSIDAD_MELAMINA_KG_M3):
    """Masa estimada de la puerta en kg.

    M = (W/1000) * (H/1000) * t * rho
    """
    W_m = float(W) / 1000.0
    H_m = float(H) / 1000.0
    return W_m * H_m * t * rho


def fuerza_piston_teorica(W, H, n_pistones=NUM_PISTONES,
                          brazo_palanca=BRAZO_PALANCA_M,
                          factor_seguridad=FACTOR_SEGURIDAD,
                          t=ESPESOR_PANEL_M, rho=DENSIDAD_MELAMINA_KG_M3):
    """Fuerza teorica requerida por pistón (Newtons).

    F ≈ (M * g * (H / 2000)) / (2 * brazo_palanca) * factor_seguridad
    """
    M = masa_puerta(W, H, t, rho)
    H_m = float(H) / 1000.0
    F = (M * GRAVEDAD * (H_m / 2.0)) / (n_pistones * brazo_palanca) * factor_seguridad
    return F


def piston_recomendado(W, H, n_pistones=NUM_PISTONES):
    """Devuelve el pistón comercial más cercano >= fuerza teorica.

    Catálogo: [60, 80, 100, 120, 150] N.
    """
    F = fuerza_piston_teorica(W, H, n_pistones)
    for comercial in PISTONES_COMERCIALES_N:
        if comercial >= F - 1e-9:
            return comercial, F
    return PISTONES_COMERCIALES_N[-1], F


def descripcion_piston(W: float, H: float) -> tuple[str, int, float]:
    """Texto legible para la interfaz: '80N (2 unidades)'."""
    comercial, F = piston_recomendado(W, H)
    return f"{comercial}N ({NUM_PISTONES} unidades)", comercial, F


# =====================================================================
# C. Puertas Corredizas (Ducasse D-52 / AL-1535)
# =====================================================================

def calcular_corrediza(inner_w: float, inner_h: float, tipo_mueble: str = "closet",
                       n_hojas: int = 2, prefer_sku: str | None = None) -> dict[str, Any]:
    """Calcula el despiece de hojas corredizas consumiendo Capa H.

    Args:
        inner_w: luz libre interior (mm).
        inner_h: luz libre interior (mm).
        tipo_mueble: "closet"/"placard" -> DUC-KIT-D52;
                     "mueble"/"alacena" -> DUC-AL-1535-MAD.
        n_hojas: cantidad de hojas (2 o 3).
        prefer_sku: SKU comercial a forzar.

    Returns:
        dict con el resultado de calculate_sliding_doors + sku_resuelto.
    """
    sku = prefer_sku
    if not sku:
        # resolve_sliding valida el tipo_mueble y devuelve el hardware dict;
        # necesitamos el SKU string para calculate_sliding_doors.
        resolve_sliding(tipo_mueble)  # valida que exista
        tipo_lower = str(tipo_mueble).strip().lower()
        _default_map = {
            "closet": "DUC-KIT-D52", "placard": "DUC-KIT-D52",
            "mueble": "DUC-AL-1535-MAD", "alacena": "DUC-AL-1535-MAD",
        }
        sku = _default_map.get(tipo_lower)
        if sku is None:
            raise KeyError(
                f"Tipo de mueble corredizo {tipo_mueble!r} no soportado.")
    res = calculate_sliding_doors(inner_w, inner_h, sku, n_hojas=n_hojas)
    res["sku_resuelto"] = sku
    res["tipo_mueble"] = tipo_mueble
    res["n_hojas"] = n_hojas
    return res


# =====================================================================
# D. Sistemas de Apertura (consumen facade_contract.py)
# =====================================================================

# Tabla única de sistemas de apertura en core/aperturas (MN-06). Aquí solo se
# re-exportan los nombres que usan los consumidores.

def ajuste_altura_apertura(tipo_apertura: str, H: float) -> tuple[float, float]:
    """Devuelve la altura ajustada segun el sistema de apertura.

    Consume `aplicar_sistema_apertura` de facade_contract.py.
    Retorna (h_ajustada, descuento).
    """
    contrato = normalizar_apertura(tipo_apertura)
    h_ajustada, _operacion = aplicar_sistema_apertura(
        float(H), contrato,
        descuento_gola=GOLA_DESCUENTO_ALTURA_DEFAULT)
    descuento = max(0.0, float(H) - h_ajustada)
    return (round(h_ajustada, 6), round(descuento, 6))





__all__ = [
    "APERTURA_45_GRADOS",
    "APERTURA_GOLA",
    "APERTURA_PUSH_OPEN",
    # Contrato de fachadas (reexportados)
    "APERTURA_TIRADOR",
    "BISEL_45_ANGULO_DEFAULT",
    "BRAZO_PALANCA_M",
    "CAZALETA_DIAMETRO",
    "CAZALETA_PROFUNDIDAD",
    "COTA_CAZOLETA_X",
    "COTA_CAZOLETA_Z_EXTREMO",
    "COTA_K_DEFAULT",
    "DENSIDAD_MELAMINA_KG_M3",
    "ESPESOR_PANEL_M",
    "FACTOR_SEGURIDAD",
    "GOLA_DESCUENTO_ALTURA_DEFAULT",
    "GRAVEDAD",
    "HOLGURA_LUZ_DEFAULT",
    "HOLGURA_PERIMETRAL_DEFAULT",
    "MONTAJE_EMBEBIDA",
    "MONTAJE_PARCHE",
    "MONTAJE_SEMIPARCHE",
    "NUM_PISTONES",
    "PISTONES_COMERCIALES_N",
    "SISTEMAS_APERTURA",
    "SOLAPE_PARCHE_NOMINAL",
    "SOLAPE_SEMIPARCHE_NOMINAL",
    "aplicar_sistema_apertura",
    "bisagras_para_puerta",
    "calcular_corrediza",
    "calcular_dimensiones_batiente",
    "calcular_fachada_base",
    "cantidad_bisagras",
    "cantos_por_sistema_apertura",
    "cazoleta_tecnica",
    "descripcion_piston",
    "fuerza_piston_teorica",
    "masa_puerta",
    "necesita_bisel_45",
    "necesita_cantos_45",
    "necesita_descuento_gola",
    "necesita_expulsor_magnetico",
    "piston_recomendado",
    "posiciones_cazoleta",
]
