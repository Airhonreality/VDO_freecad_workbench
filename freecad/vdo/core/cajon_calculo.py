# =====================================================================
# cajon_calculo.py
# Cálculo del despiece del cajón con corredera oculta (Blum Tandem etc).
# Separado de vdo_cajon_despiece.py (M7, D-36).
#
# Datos de partida:
#   LI       = ancho libre interior del mueble (pared a pared)
#   ProfInt  = profundidad libre interior del mueble
#   LG       = largo nominal de la guía (auto: max(comerciales ≤ ProfInt))
#   Delta    = reducción por herraje (ej. Blum Tandem 16mm → 49 mm)
#   Gcaja    = grosor de laterales/trasera/frente interior (15-16 mm)
#   Gfondo   = grosor del piso (6-12 mm)
#   Gfrente  = grosor de la fachada (18 mm)
#
# Salida de calcular_despiece:
#   dict con:
#   "guia":        {lg, delta, marca, prof_int}
#   "caja":        medidas de las 5 piezas de la caja
#   "fachada":     medidas de la fachada
#   "posiciones":  coordenadas 3D (X=ancho, Y=prof, Z=alto)
#   "piezas":      lista de corte (para VDO_Paneles_JSON)
#   "mecanizados": cotas de mecanizado usadas
#   "avisos":      lista de advertencias (str)
# =====================================================================

from typing import Any

from freecad.vdo.core.cajon_calculo_bloques import (
    _ancho_exterior,
    _fachada_base,
    _geometria_caja,
    _leer_defectos,
    _leer_entradas,
    _posiciones,
    _resolver_guia,
    _sistema_apertura,
    _validar_entradas,
)
from freecad.vdo.core.cajon_correderas import (
    CAJA_METALICA,
)
from freecad.vdo.core.facade_contract import (
    necesita_bisel_45,
    necesita_descuento_gola,
    necesita_expulsor_magnetico,
)


def _cotas_mecanizado(
    mecanizado: dict[str, Any], marca_id: Any, z_piso: float, g_fondo: float,
) -> tuple[dict[str, Any], float, float, float, float, float, float]:
    """Cotas de mecanizado de la ficha técnica y su resumen."""
    # --- 8. Mecanizados (cotas de la ficha técnica) ---
    diam_t = float(mecanizado.get("diam_taladro", 6))
    prof_t = float(mecanizado.get("prof_taladro", 12))
    dist_t_tras = float(mecanizado.get("dist_taladro_borde_trasero", 8))
    prof_ranura = float(mecanizado.get("prof_ranura_lateral", 4))
    notch_ancho = float(mecanizado.get("notch_ancho", 25))
    notch_alto = float(mecanizado.get("notch_alto", 20))

    mecanizados_resumen = {
        "marca": marca_id,
        "diam_taladro": diam_t,
        "prof_taladro": prof_t,
        "dist_taladro_borde_trasero": dist_t_tras,
        "prof_ranura_lateral": prof_ranura,
        "notch_ancho": notch_ancho,
        "notch_alto": notch_alto,
        "eje_ranura": z_piso,
        "grosor_fondo": g_fondo,
    }
    return mecanizados_resumen, diam_t, prof_t, dist_t_tras, prof_ranura, notch_ancho, notch_alto


def _piezas_laterales(
    largo_lateral: float, alto_lateral: float, g_caja: float, material_ref: Any,
    z_piso: float, g_fondo: float, lg: float,
    prof_ranura: float, diam_t: float, prof_t: float, dist_t_tras: float,
) -> list[dict[str, Any]]:
    """Paneles laterales izquierdo y derecho de la caja, para la lista de corte."""
    piezas: list[dict[str, Any]] = [
        {
            "nombre": "Cajon_Lateral_Izq",
            "tipo": "panel",
            "largo": largo_lateral,
            "ancho": alto_lateral,
            "espesor": g_caja,
            "cantidad": 1,
            "material_ref": material_ref,
            "mecanizados": [
                {"tipo": "ranura_piso", "cara": "interna",
                 "z_base": z_piso, "ancho": g_fondo,
                 "prof": prof_ranura, "largo": lg},
                {"tipo": "taladro_fondo", "ø": diam_t, "prof": prof_t,
                 "y_desde_trasero": dist_t_tras, "x_centrada": True},
            ],
        },
        {
            "nombre": "Cajon_Lateral_Der",
            "tipo": "panel",
            "largo": largo_lateral,
            "ancho": alto_lateral,
            "espesor": g_caja,
            "cantidad": 1,
            "material_ref": material_ref,
            "mecanizados": [
                {"tipo": "ranura_piso", "cara": "interna",
                 "z_base": z_piso, "ancho": g_fondo,
                 "prof": prof_ranura, "largo": lg},
                {"tipo": "taladro_fondo", "ø": diam_t, "prof": prof_t,
                 "y_desde_trasero": dist_t_tras, "x_centrada": True},
            ],
        },
    ]
    return piezas


def _piezas_restantes(
    ancho_contra: float, alto_contra: float, g_caja: float, material_ref: Any,
    notch_ancho: float, notch_alto: float, alto_frente_int: float, ancho_piso: float,
    largo_piso: float, g_fondo: float, ancho_fachada: Any,
    alto_fachada: Any, g_fachada: float, sistema_apertura: Any, operacion_canto: Any,
    cantos_fachada: Any,
) -> list[dict[str, Any]]:
    """Paneles de contrafrente, frente interior, piso y fachada."""
    return [
        {
            "nombre": "Cajon_Contrafrente",
            "tipo": "panel",
            "largo": ancho_contra,
            "ancho": alto_contra,
            "espesor": g_caja,
            "cantidad": 1,
            "material_ref": material_ref,
            "mecanizados": [
                {"tipo": "notch_inferior", "lados": "ambos",
                 "ancho": notch_ancho, "alto": notch_alto},
            ],
        },
        {
            "nombre": "Cajon_Frente_Interior",
            "tipo": "panel",
            "largo": ancho_contra,
            "ancho": alto_frente_int,
            "espesor": g_caja,
            "cantidad": 1,
            "material_ref": material_ref,
            "mecanizados": [
                {"tipo": "zona_locking_device", "cara": "inferior",
                 "nota": "Gancho de acople (locking device) según ficha"},
            ],
        },
        {
            "nombre": "Cajon_Piso",
            "tipo": "panel",
            "largo": largo_piso,
            "ancho": ancho_piso,
            "espesor": g_fondo,
            "cantidad": 1,
            "material_ref": material_ref,
            "mecanizados": [],
        },
        _panel_fachada(
            material_ref, ancho_fachada, alto_fachada, g_fachada,
            sistema_apertura, operacion_canto, cantos_fachada,
        ),
    ]


def _panel_fachada(
    material_ref: Any, ancho_fachada: Any, alto_fachada: Any, g_fachada: float,
    sistema_apertura: Any, operacion_canto: Any, cantos_fachada: Any,
) -> dict[str, Any]:
    """Panel de fachada del cajon: 4 cantos y operacion de apertura."""
    return {
        "nombre": "Cajon_Fachada",
        "tipo": "panel",
        "largo": ancho_fachada,
        "ancho": alto_fachada,
        "espesor": g_fachada,
        "cantidad": 1,
        "material_ref": material_ref,
        "sistema_apertura": sistema_apertura,
        "operacion_canto": operacion_canto,
        "cantos": cantos_fachada,
        "mecanizados": [
            {"tipo": "canto", "caras": 4,
             "nota": "Fachada: 4 cantos (convención VDO)"},
            {"tipo": operacion_canto, "cara": "superior",
             "nota": f"Sistema de apertura: {sistema_apertura}"},
        ],
    }


def _resumen_caja(
    ancho_ext: float, largo_lateral: float, alto_lateral: float, g_caja: float,
    ancho_contra: float, alto_contra: float, montaje: Any, ancho_piso: float,
    largo_piso: float, g_fondo: float, z_piso: float,
) -> dict[str, Any]:
    """Medidas de la caja para el resultado de calcular_despiece."""
    return {
        "ancho_exterior": ancho_ext,
        "largo_lateral": largo_lateral,
        "alto_lateral": alto_lateral,
        "grosor": g_caja,
        "ancho_contra": ancho_contra,
        "alto_contra": alto_contra,
        "montaje_trasera": montaje,
        "ancho_piso": ancho_piso,
        "largo_piso": largo_piso,
        "grosor_piso": g_fondo,
        "z_piso": z_piso,
    }


def _resumen_fachada(
    ancho_fachada: Any, alto_fachada: Any, alto_fachada_nominal: float,
    g_fachada: float, sistema_apertura: Any, tipo_montaje_fachada: str,
    operacion_canto: Any, cantos_fachada: Any,
) -> dict[str, Any]:
    """Medidas y reglas de la fachada para el resultado."""
    return {
        "ancho": ancho_fachada,
        "alto": alto_fachada,
        "alto_nominal": alto_fachada_nominal,
        "espesor": g_fachada,
        "sistema_apertura": sistema_apertura,
        "tipo_montaje": tipo_montaje_fachada,
        "operacion_canto": operacion_canto,
        "cantos": cantos_fachada,
        "necesita_gola": necesita_descuento_gola(sistema_apertura),
        "necesita_bisel_45": necesita_bisel_45(sistema_apertura),
        "necesita_expulsor": necesita_expulsor_magnetico(sistema_apertura),
    }


def _filtrar_piezas(
    piezas: list[dict[str, Any]], tipo_corredera: str,
) -> list[dict[str, Any]]:
    """Quita los laterales en caja metalica (van en el perfil)."""
    if tipo_corredera != CAJA_METALICA:
        return piezas
    return [p for p in piezas
            if p["nombre"] not in ("Cajon_Lateral_Izq", "Cajon_Lateral_Der")]


def calcular_despiece(config: dict[str, Any]) -> dict[str, Any]:
    """Calcula el despiece del cajón (corredera oculta, telescópica o metálica).

    Entradas y valores por defecto: ver _leer_entradas y _leer_defectos.
    Salida: ver la cabecera de este módulo.
    """
    # --- Entradas obligatorias, marca y tipo de corredera ---
    (li, prof_int, alto_frente, marca_id, marca, delta, mecanizado,
     _tipo_corredera_result) = _leer_entradas(config)
    (alto_caja, g_caja, g_fondo, g_fachada, pen_ranura, eje_ranura,
     holg_lat, holg_sup, holg_inf, montaje, material_ref,
     tipo_montaje_fachada) = _leer_defectos(config)
    avisos = _validar_entradas(g_caja, g_fondo, montaje)
    lg, lg_manual = _resolver_guia(config, prof_int, marca)
    ancho_ext = _ancho_exterior(li, delta)
    # --- 3. Laterales ---
    largo_lateral = lg
    alto_lateral = alto_caja
    (ancho_contra, y_trasera, z_piso, alto_contra, alto_frente_int,
     ancho_piso, largo_piso) = _geometria_caja(montaje, ancho_ext, g_caja,
     lg, alto_caja, alto_lateral, eje_ranura, g_fondo, pen_ranura)
    ancho_fachada, alto_fachada_nominal = _fachada_base(
        alto_frente, holg_sup, holg_inf, ancho_ext, tipo_montaje_fachada, holg_lat)
    (sistema_apertura, alto_fachada, operacion_canto,
     cantos_fachada) = _sistema_apertura(config, alto_fachada_nominal)
    posiciones = _posiciones(
        ancho_ext, g_caja, lg, alto_lateral, ancho_contra, montaje, y_trasera,
        z_piso, g_fondo, alto_contra, alto_frente_int, pen_ranura, ancho_piso,
        largo_piso, g_fachada, ancho_fachada, alto_fachada)
    (mecanizados_resumen, diam_t, prof_t, dist_t_tras, prof_ranura,
     notch_ancho, notch_alto) = _cotas_mecanizado(mecanizado, marca_id,
     z_piso, g_fondo)
    # --- 9. Piezas para cutting list (VDO_Paneles_JSON) ---
    piezas = _piezas_laterales(largo_lateral, alto_lateral, g_caja,
                               material_ref, z_piso, g_fondo, lg, prof_ranura,
                               diam_t, prof_t, dist_t_tras) + _piezas_restantes(
        ancho_contra, alto_contra, g_caja, material_ref, notch_ancho,
        notch_alto, alto_frente_int, ancho_piso, largo_piso, g_fondo,
        ancho_fachada, alto_fachada, g_fachada, sistema_apertura,
        operacion_canto, cantos_fachada)
    return {
        "guia": {"lg": lg, "delta": delta, "marca": marca_id,
                 "prof_int": prof_int,
                 "auto": lg_manual <= 0},
        "tipo_corredera": _tipo_corredera_result,
        "caja": _resumen_caja(ancho_ext, largo_lateral, alto_lateral, g_caja,
                              ancho_contra, alto_contra, montaje, ancho_piso,
                              largo_piso, g_fondo, z_piso),
        "fachada": _resumen_fachada(ancho_fachada, alto_fachada,
                                    alto_fachada_nominal, g_fachada,
                                    sistema_apertura, tipo_montaje_fachada,
                                    operacion_canto, cantos_fachada),
        "posiciones": posiciones,
        "piezas": _filtrar_piezas(piezas, _tipo_corredera_result),
        "mecanizados": mecanizados_resumen,
        "avisos": avisos,
    }
