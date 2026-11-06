"""Modificador de reengrose: normalizacion de entrada, espesor efectivo y lectura/escritura en el objeto."""

import json

from freecad.vdo.core.reengrose_modelo import (
    ALCANCES, ALINEACIONES, BORDES_2D, BordeConfig, CARAS, DEFAULTS,
    DISTANCIA_AL_CANTO_DEFAULT, ENCUENTROS_ESQUINAS,
    ENCUENTRO_ESQUINAS_DEFAULT, ESQUINAS_2D, FABRICACIONES, LARGOS_TIRA,
    LARGO_TIRA_DEFAULT, MODOS, ORIENTACIONES, PRIORIDADES_ENCUENTRO, PROPS,
    ReengroseDTO, ReengroseError, _MAPA_MODO_LEGACY, _a_bool, _a_float,
    _normalizar_modo_choque, _validar_enum)


class ReengroseModifier:
    """DTO puro del modificador de reengrose.

    Mantiene las propiedades planas historicas (orientacion, ancho, cara,
    etc.) y expone ademas ``bordes`` como ``BordeConfig`` para la nueva UI
    de modificador universal.
    """

    def __init__(self, datos=None):
        datos = normalizar_modificador(datos)
        for clave, valor in datos.items():
            if clave == "bordes":
                self.bordes = {
                    borde: BordeConfig.from_dict(cfg)
                    for borde, cfg in valor.items()
                }
            else:
                setattr(self, clave, valor)

    def to_dict(self):
        datos = {clave: getattr(self, clave) for clave in PROPS}
        datos.update({
            "esquinas": self.esquinas,
            "fabricacion": self.fabricacion,
            "choque_nucleo": self.choque_nucleo,
            "bordes": {
                borde: cfg.to_dict()
                for borde, cfg in self.bordes.items()
            },
            "usa_bordes": bool(getattr(self, "usa_bordes", False)),
        })
        return datos

    def to_json(self):
        return json.dumps(self.to_dict(), ensure_ascii=False)

    @classmethod
    def from_dict(cls, datos):
        return cls(datos)

    @classmethod
    def from_json(cls, texto):
        if not texto:
            return cls()
        return cls(json.loads(texto))


def _normalizar_borde_config(datos, ancho_defecto=70.0,
                             espesor_defecto=None):
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


def _normalizar_bordes(datos, ancho_defecto=70.0, espesor_defecto=None):
    datos = datos or {}
    return {
        borde: _normalizar_borde_config(
            datos.get(borde), ancho_defecto, espesor_defecto)
        for borde in BORDES_2D
    }


def _bordes_desde_legacy(datos):
    ancho = float(datos["ancho"])
    espesor = datos["espesor"]
    bordes = {
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


def _legacy_desde_bordes(activo, bordes, esquinas, fabricacion,
                         choque, datos):
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


def _datos_modificador(datos):
    """Resuelve el dict del modificador desde DTO, objeto, None o envoltorio."""
    if isinstance(datos, ReengroseDTO):
        datos = datos.to_dict()
    if isinstance(datos, ReengroseModifier):
        datos = datos.to_dict()
    if datos is None:
        datos = {}
    if not isinstance(datos, dict):
        raise ReengroseError("El modificador de reengrose debe ser un dict.")
    if "modificador_reengrose" in datos:
        datos = datos["modificador_reengrose"] or {}
    return datos


def _usa_bordes(datos):
    """Decide si el modificador usa el esquema nuevo (por bordes)."""
    if "usa_bordes" in datos:
        return _a_bool(datos.get("usa_bordes"))
    return any(
        clave in datos for clave in
        ("bordes", "esquinas", "fabricacion", "choque_nucleo"))


def _normalizar_modificador_bordes(datos):
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


def _modo_nucleo_legacy(datos):
    """Resuelve el comportamiento de choque con núcleo del esquema legacy."""
    if datos.get("comportamiento_choque_nucleo") not in (None, ""):
        return _normalizar_modo_choque(
            datos.get("comportamiento_choque_nucleo"),
            "comportamiento_choque_nucleo")
    if datos.get("politica_repisa") not in (None, ""):
        return _normalizar_modo_choque(
            datos.get("politica_repisa"), "politica_repisa")
    return DEFAULTS["comportamiento_choque_nucleo"]


def _normalizar_modificador_legacy(datos):
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

    resultado = {
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


def normalizar_modificador(datos=None):
    datos = _datos_modificador(datos)
    if _usa_bordes(datos):
        return _normalizar_modificador_bordes(datos)
    return _normalizar_modificador_legacy(datos)


def espesor_efectivo(panel_base, modifier):
    mod = normalizar_modificador(modifier)
    if mod["espesor"]:
        return float(mod["espesor"])
    return float(panel_base.get("espesor", 0.0))


def _normalizar_encuentro(encuentro_esquinas):
    """Devuelve dict {esquina: tipo} a partir de un str global o un dict."""
    if isinstance(encuentro_esquinas, dict):
        resultado = {}
        for esquina in ESQUINAS_2D:
            valor = encuentro_esquinas.get(esquina, ENCUENTRO_ESQUINAS_DEFAULT)
            resultado[esquina] = _validar_enum(
                valor, "encuentro_esquinas", ENCUENTROS_ESQUINAS)
        return resultado
    # str global: se aplica a las 4 esquinas (compatibilidad).
    tipo = _validar_enum(
        encuentro_esquinas, "encuentro_esquinas", ENCUENTROS_ESQUINAS)
    return {esquina: tipo for esquina in ESQUINAS_2D}


def _prioridad_legacy_desde_esquinas(esquinas):
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


def desde_objeto(obj):
    texto = getattr(obj, "VDO_Reengrose_JSON", "") or ""
    guardado = None
    if texto:
        try:
            guardado = json.loads(texto)
        except (TypeError, ValueError):
            guardado = None
    if (guardado is not None
            and isinstance(guardado, dict)
            and any(clave in guardado for clave in
                    ("bordes", "esquinas", "fabricacion",
                     "choque_nucleo"))):
        return ReengroseModifier(guardado)
    datos = {}
    for clave, prop in PROPS.items():
        datos[clave] = getattr(obj, prop, DEFAULTS[clave])
    datos["espesor"] = _a_float(datos.get("espesor"), "espesor")
    if datos.get("espesor") == 0.0:
        datos["espesor"] = None
    return ReengroseModifier(datos)


def aplicar_a_objeto(obj, modifier):
    mod = ReengroseModifier(modifier)
    datos = mod.to_dict()
    for clave, prop in PROPS.items():
        valor = datos[clave]
        if clave == "espesor" and valor is None:
            valor = 0.0
        setattr(obj, prop, valor)
    obj.VDO_Reengrose_JSON = mod.to_json()
    return mod


def leer_reengroses(obj) -> dict:
    """Lee el JSON de reengroses almacenado en un objeto (unificado F19.7).

    Reemplaza las copias _cargar_reengroses (core) y _leer_reengroses (ui).
    """
    texto = getattr(obj, "VDO_Reengrose_JSON", "") or "{}"
    try:
        datos = json.loads(texto) if isinstance(texto, str) else dict(texto)
    except (TypeError, ValueError):
        return {}
    return datos if isinstance(datos, dict) else {}
