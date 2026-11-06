"""Normalizacion del modificador de reengrose: bordes (esquema nuevo),
esquema legacy y encuentros de esquina. Extraido de reengrose_modificador.py."""

from typing import Any, cast

from freecad.vdo.core.reengrose_modelo import (
    _MAPA_MODO_LEGACY,
    ALCANCES,
    ALINEACIONES,
    BORDES_2D,
    CARAS,
    DEFAULTS,
    DISTANCIA_AL_CANTO_DEFAULT,
    ENCUENTRO_ESQUINAS_DEFAULT,
    ENCUENTROS_ESQUINAS,
    ESQUINAS_2D,
    FABRICACIONES,
    LARGO_TIRA_DEFAULT,
    LARGOS_TIRA,
    MODOS,
    ORIENTACIONES,
    PRIORIDADES_ENCUENTRO,
    BordeConfig,
    ReengroseError,
    _a_bool,
    _a_float,
    _normalizar_modo_choque,
    _validar_enum,
)


# Any: datos es un dict de JSON o de UI, o un BordeConfig.
def _normalizar_borde_config(datos: Any, ancho_defecto: float = 70.0,
                             espesor_defecto: float | None = None) -> dict[str, Any]:
    if isinstance(datos, BordeConfig):
        datos = datos.to_dict()
    datos = dict(datos or {})
    activo = _a_bool(datos.get("activo", False))
    ancho = _a_float(datos.get("ancho", ancho_defecto), "ancho")
    if ancho is None:
        ancho = float(ancho_defecto)
    distancia = datos.get("distancia_al_canto")
    if distancia is None or distancia == "":
        distancia = datos.get("offset_borde", DISTANCIA_AL_CANTO_DEFAULT)
    distancia = _a_float(distancia, "distancia_al_canto")
    if distancia is None:
        distancia = DISTANCIA_AL_CANTO_DEFAULT
    largo_tira = _validar_enum(
        datos.get("largo_tira", LARGO_TIRA_DEFAULT),
        "largo_tira", LARGOS_TIRA)
    encuentro = datos.get("encuentro_esquinas")
    if encuentro in (None, ""):
        encuentro = None
    else:
        encuentro = _validar_enum(
            encuentro, "encuentro_esquinas", ENCUENTROS_ESQUINAS)
    espesor = _a_float(datos.get("espesor"), "espesor")
    if espesor is not None and espesor <= 0:
        raise ReengroseError("El espesor de la tira debe ser mayor que 0.")
    if ancho < 0:
        raise ReengroseError("El ancho de la tira no puede ser negativo.")
    if activo and ancho <= 0:
        raise ReengroseError("El ancho del borde activo debe ser mayor que 0.")
    if distancia < 0:
        raise ReengroseError(
            "La distancia_al_canto no puede ser negativa.")
    return {
        "activo": activo,
        "ancho": float(ancho),
        "distancia_al_canto": float(distancia),
        "largo_tira": largo_tira,
        "encuentro_esquinas": encuentro,
        "espesor": espesor,
        "offset_borde": float(distancia),
    }


def _normalizar_bordes(datos: Any, ancho_defecto: float = 70.0,
                       espesor_defecto: float | None = None) -> dict[str, dict[str, Any]]:
    datos = datos or {}
    return {
        borde: _normalizar_borde_config(
            datos.get(borde), ancho_defecto, espesor_defecto)
        for borde in BORDES_2D
    }


def _bordes_desde_legacy(datos: dict[str, Any]) -> dict[str, dict[str, Any]]:
    ancho = float(datos["ancho"])
    espesor = datos["espesor"]
    bordes: dict[str, dict[str, Any]] = {
        borde: {
            "activo": False, "ancho": ancho,
            "distancia_al_canto": 0.0,
            "largo_tira": LARGO_TIRA_DEFAULT,
            "encuentro_esquinas": None,
            "espesor": espesor,
            "offset_borde": 0.0,
        }
        for borde in BORDES_2D
    }
    if datos["activo"] and datos["modo_fabricacion"] != "pacha":
        if datos["orientacion"] == "paralela":
            if datos["alineacion_profundidad"] in ("frente", "fondo"):
                borde = datos["alineacion_profundidad"]
                bordes[borde]["activo"] = True
        elif datos["orientacion"] == "transversal":
            # El modo transversal historico no es un borde: se conserva
            # como geometria legacy y no se usa como marco perimetral.
            pass
    return bordes


def _legacy_desde_bordes(activo: bool, bordes: dict[str, dict[str, Any]],
                         esquinas: dict[str, str] | str, fabricacion: str,
                         choque: str, datos: dict[str, Any]) -> dict[str, Any]:
    activos = [borde for borde in BORDES_2D
               if bordes[borde]["activo"]]
    primero = bordes[activos[0]] if activos else None
    ancho = primero["ancho"] if primero else _a_float(
        datos.get("ancho", DEFAULTS["ancho"]), "ancho")
    espesor = primero["espesor"] if primero else _a_float(
        datos.get("espesor"), "espesor")
    if any(b in activos for b in ("frente", "fondo")):
        orientacion = "paralela"
    elif any(b in activos for b in ("izquierda", "derecha")):
        orientacion = "transversal"
    else:
        orientacion = "paralela"
    if "frente" in activos:
        alineacion = "frente"
    elif "fondo" in activos:
        alineacion = "fondo"
    else:
        alineacion = "centrado"
    cara = _validar_enum(
        datos.get("cara", DEFAULTS["cara"]), "cara", CARAS)
    return {
        "activo": bool(activo),
        "orientacion": orientacion,
        "ancho": ancho if ancho and ancho > 0 else DEFAULTS["ancho"],
        "espesor": espesor,
        "cara": cara,
        "alineacion_profundidad": alineacion,
        "modo_fabricacion": fabricacion,
        "alcance": "parcial",
        "politica_repisa": _MAPA_MODO_LEGACY[choque],
        "prioridad_encuentro_tiras": _prioridad_legacy_desde_esquinas(
            esquinas),
        "comportamiento_choque_nucleo": choque,
    }


def _usa_bordes(datos: dict[str, Any]) -> bool:
    """Decide si el modificador usa el esquema nuevo (por bordes)."""
    if "usa_bordes" in datos:
        return _a_bool(datos.get("usa_bordes"))
    return any(
        clave in datos for clave in
        ("bordes", "esquinas", "fabricacion", "choque_nucleo"))


def _normalizar_modificador_bordes(datos: dict[str, Any]) -> dict[str, Any]:
    """Normaliza el esquema nuevo (por bordes)."""
    activo = _a_bool(datos.get("activo", DEFAULTS["activo"]))
    esquinas = _normalizar_encuentro(
        datos.get("esquinas", DEFAULTS["prioridad_encuentro_tiras"]))
    fabricacion = _validar_enum(
        datos.get("fabricacion", DEFAULTS["modo_fabricacion"]),
        "fabricacion", FABRICACIONES)
    choque = _normalizar_modo_choque(
        datos.get("choque_nucleo",
                  datos.get("comportamiento_choque_nucleo",
                            DEFAULTS["comportamiento_choque_nucleo"])),
        "choque_nucleo")
    bordes = _normalizar_bordes(datos.get("bordes"))
    resultado = _legacy_desde_bordes(
        activo, bordes, esquinas, fabricacion, choque, datos)
    resultado.update({
        "esquinas": esquinas,
        "fabricacion": fabricacion,
        "choque_nucleo": choque,
        "bordes": bordes,
        "usa_bordes": True,
    })
    return resultado


def _modo_nucleo_legacy(datos: dict[str, Any]) -> str:
    """Resuelve el comportamiento de choque con núcleo del esquema legacy."""
    if datos.get("comportamiento_choque_nucleo") not in (None, ""):
        return _normalizar_modo_choque(
            datos.get("comportamiento_choque_nucleo"),
            "comportamiento_choque_nucleo")
    if datos.get("politica_repisa") not in (None, ""):
        return _normalizar_modo_choque(
            datos.get("politica_repisa"), "politica_repisa")
    # cast: DEFAULTS es dict[str, Any]; este valor es siempre un str.
    return cast(str, DEFAULTS["comportamiento_choque_nucleo"])


def _normalizar_modificador_legacy(datos: dict[str, Any]) -> dict[str, Any]:
    """Normaliza el esquema legacy (campos planos)."""
    activo = _a_bool(datos.get("activo", DEFAULTS["activo"]))
    orientacion = _validar_enum(
        datos.get("orientacion", DEFAULTS["orientacion"]),
        "orientacion", ORIENTACIONES)
    ancho = _a_float(datos.get("ancho", DEFAULTS["ancho"]), "ancho")
    if ancho is None or ancho <= 0:
        raise ReengroseError("El ancho del reengrose debe ser mayor que 0.")
    espesor = _a_float(datos.get("espesor"), "espesor")
    if espesor is not None and espesor <= 0:
        raise ReengroseError("El espesor del reengrose debe ser mayor que 0.")
    cara = _validar_enum(datos.get("cara", DEFAULTS["cara"]), "cara", CARAS)
    alineacion = _validar_enum(
        datos.get("alineacion_profundidad",
                  DEFAULTS["alineacion_profundidad"]),
        "alineacion_profundidad", ALINEACIONES)
    modo = _validar_enum(
        datos.get("modo_fabricacion", DEFAULTS["modo_fabricacion"]),
        "modo_fabricacion", MODOS)
    alcance = _validar_enum(
        datos.get("alcance", DEFAULTS["alcance"]),
        "alcance", ALCANCES)
    modo_nucleo = _modo_nucleo_legacy(datos)
    politica = _MAPA_MODO_LEGACY[modo_nucleo]
    prioridad = _validar_enum(
        datos.get("prioridad_encuentro_tiras",
                  DEFAULTS["prioridad_encuentro_tiras"]),
        "prioridad_encuentro_tiras", PRIORIDADES_ENCUENTRO)

    resultado: dict[str, Any] = {
        "activo": activo,
        "orientacion": orientacion,
        "ancho": ancho,
        "espesor": espesor,
        "cara": cara,
        "alineacion_profundidad": alineacion,
        "modo_fabricacion": modo,
        "alcance": alcance,
        "politica_repisa": politica,
        "prioridad_encuentro_tiras": prioridad,
        "comportamiento_choque_nucleo": modo_nucleo,
    }
    bordes = _bordes_desde_legacy(resultado)
    resultado.update({
        "esquinas": prioridad,
        "fabricacion": modo,
        "choque_nucleo": modo_nucleo,
        "bordes": bordes,
        "usa_bordes": False,
    })
    return resultado


# Any: str global o dict por esquina, sin tipo fijo.
def _normalizar_encuentro(encuentro_esquinas: Any) -> dict[str, str]:
    """Devuelve dict {esquina: tipo} a partir de un str global o un dict."""
    if isinstance(encuentro_esquinas, dict):
        resultado: dict[str, str] = {}
        for esquina in ESQUINAS_2D:
            valor = encuentro_esquinas.get(esquina, ENCUENTRO_ESQUINAS_DEFAULT)
            resultado[esquina] = _validar_enum(
                valor, "encuentro_esquinas", ENCUENTROS_ESQUINAS)
        return resultado
    # str global: se aplica a las 4 esquinas (compatibilidad).
    tipo = _validar_enum(
        encuentro_esquinas, "encuentro_esquinas", ENCUENTROS_ESQUINAS)
    return {esquina: tipo for esquina in ESQUINAS_2D}


def _prioridad_legacy_desde_esquinas(esquinas: dict[str, str] | str | None) -> str:
    """Deriva el enum legacy ``prioridad_encuentro_tiras`` desde el dict."""
    if isinstance(esquinas, str):
        if esquinas in PRIORIDADES_ENCUENTRO:
            return esquinas
        return ENCUENTRO_ESQUINAS_DEFAULT
    valores = {
        (esquinas or {}).get(esquina, ENCUENTRO_ESQUINAS_DEFAULT)
        for esquina in ESQUINAS_2D
    }
    if len(valores) == 1:
        unico = valores.pop()
        return unico if unico in PRIORIDADES_ENCUENTRO else (
            ENCUENTRO_ESQUINAS_DEFAULT)
    primero = (esquinas or {}).get(
        ESQUINAS_2D[0], ENCUENTRO_ESQUINAS_DEFAULT)
    return primero if primero in PRIORIDADES_ENCUENTRO else (
        ENCUENTRO_ESQUINAS_DEFAULT)
