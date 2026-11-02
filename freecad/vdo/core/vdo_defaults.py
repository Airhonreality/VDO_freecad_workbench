# =====================================================================
# vdo_defaults.py
# Proveedor único de valores por defecto desde vdo_manifest.json.
# Sin estado mutable de módulo (M-08): el manifiesto se pasa como parámetro
# o se carga fresco por llamada (sin caché en _MANIFEST).
# =====================================================================

from freecad.vdo.core.vdo_manifest import _obtener_json as _cargar_json_fresco


def get_param(ruta, default=None, manifest=None):
    """
    Obtiene un parámetro del manifest por ruta de acceso.

    Ejemplo:
        get_param("parametros_locales.alto.valor")  → 720
        get_param("parametros_globales.espesor_default.valor", 18, manifiesto)

    Args:
        ruta (str): Ruta separada por puntos
        default: Valor si no encuentra
        manifest: dict del manifiesto (si None, se carga fresco por llamada)

    Returns:
        El valor encontrado o default
    """
    if manifest is None:
        manifest = _cargar_json_fresco()
    partes = ruta.split(".")
    valor = manifest

    try:
        for parte in partes:
            valor = valor[parte]
        return valor
    except (KeyError, TypeError):
        if default is not None:
            return default
        raise ValueError(f"Parámetro no encontrado en manifest: {ruta}")


# === DIMENSIONES LOCALES (Params) ===
ALTO_DEFAULT = get_param("parametros_locales.alto.valor", 720)
ANCHO_DEFAULT = get_param("parametros_locales.ancho.valor", 600)
FONDO_DEFAULT = get_param("parametros_locales.fondo.valor", 580)
ESPESOR_DEFAULT = get_param("parametros_locales.espesor.valor", 18)

# === DIMENSIONES GLOBALES (Params_Melamina) ===
ESPESOR_MELAMINA_DEFAULT = get_param("parametros_globales.espesor_default.valor", 18)
CANTO_GRUESO_DEFAULT = get_param("parametros_globales.canto_grueso.valor", 2)
CANTO_MEDIO_DEFAULT = get_param("parametros_globales.canto_medio.valor", 1)
CANTO_FINO_DEFAULT = get_param("parametros_globales.canto_fino.valor", 0.4)
RANURA_FONDO_DEFAULT = get_param("parametros_globales.ranura_fondo.valor", 3)

# === CONFIGURACIÓN DEL FONDO (valores por defecto sensatos) ===
FONDO_HABILITADO = True
FONDO_CALIBRE = 6
FONDO_PROFUNDIDAD_RANURA = 3.0
FONDO_DISTANCIA_BORDE = 18.0
FONDO_UMBRAL_DELGADO = get_param(
    "parametros_globales.fondo_umbral_delgado.valor", 8.0)

# === ESTRUCTURA (Tapa y Base) ===
TAPA_POSICION = "externo"
BASE_POSICION = "interno"

# === ORIENTACIÓN (vocabulario del manifiesto) ===
ORIENTACIONES = get_param("orientaciones", {})
ORIENTACIONES_VALIDAS = list(ORIENTACIONES.keys())
ORIENTACION_DEFAULT = (
    "horizontal" if "horizontal" in ORIENTACIONES_VALIDAS
    else (ORIENTACIONES_VALIDAS[0] if ORIENTACIONES_VALIDAS else "horizontal")
)


def obtener_mapeo_orientacion(orientacion):
    """Devuelve el mapeo de ejes de una orientación desde el manifest.

    Args:
        orientacion (str): clave en manifest["orientaciones"].

    Returns:
        dict: {"X": parametro, "Y": parametro, "Z": parametro}

    Raises:
        ValueError: si la orientación no existe en el vocabulario.
    """
    info = ORIENTACIONES.get(orientacion)
    if info is None:
        raise ValueError(
            f"Orientación desconocida: '{orientacion}'. "
            f"Disponibles: {', '.join(ORIENTACIONES_VALIDAS)}")
    return info["ejes"]

# === CAJÓN CON CORREDERA OCULTA (params de parametros_cajon) ===
CAJON_ALTO_DEFAULT = get_param("parametros_cajon.alto_caja.valor", 120)
CAJON_GROSOR_DEFAULT = get_param("parametros_cajon.grosor_caja.valor", 16)
CAJON_FONDO_DEFAULT = get_param("parametros_cajon.grosor_fondo.valor", 6)
CAJON_FACHADA_DEFAULT = get_param("parametros_cajon.grosor_fachada.valor", 18)
CAJON_HOLGURA_LAT_FACHADA = get_param("parametros_cajon.holgura_lateral_fachada.valor", 2)
CAJON_HOLGURA_SUP_FACHADA = get_param("parametros_cajon.holgura_superior_fachada.valor", 2)
CAJON_HOLGURA_INF_FACHADA = get_param("parametros_cajon.holgura_inferior_fachada.valor", 2)
CAJON_PENETRACION_RANURA = get_param("parametros_cajon.penetracion_ranura_piso.valor", 10)
CAJON_EJE_RANURA = get_param("parametros_cajon.eje_ranura_piso.valor", 11.5)
