"""Datos y tipos del reengrose: constantes de dominio, BordeConfig, ReengroseDTO y
validadores de valor."""

from collections.abc import Sequence


class ReengroseError(ValueError):
    """Error de validacion del modificador de reengrose."""


ORIENTACIONES = ("paralela", "transversal")
CARAS = ("cara_a", "cara_b", "ambos")
ALINEACIONES = ("frente", "centrado", "fondo")
MODOS = ("independiente", "pacha")
ALCANCES = ("parcial", "total")
POLITICAS_REPISA = ("retroceder", "mochear")
PRIORIDADES_ENCUENTRO = (
    "vertical_domina", "horizontal_domina", "inglete_45")
MODOS_CHOQUE_NUCLEO = ("retroceso", "mocheo", "interrumpir_tira")

_MAPA_MODO_CHOQUE = {
    "retroceder": "retroceso",
    "retroceso": "retroceso",
    "mochear": "mocheo",
    "mocheo": "mocheo",
    "interrumpir": "interrumpir_tira",
    "interrumpir_tira": "interrumpir_tira",
}
_MAPA_MODO_LEGACY = {
    "retroceso": "retroceder",
    "mocheo": "mochear",
    "interrumpir_tira": "interrumpir_tira",
}

BORDES_2D = ("frente", "fondo", "izquierda", "derecha")
ESQUINAS_2D = ("frente_izquierda", "frente_derecha", "fondo_izquierda", "fondo_derecha")
ESQUINAS = ("vertical_domina", "horizontal_domina", "inglete_45", "marco_interior")
ENCUENTROS_ESQUINAS = ESQUINAS
LARGOS_TIRA = ("marco_interior", "punta_a_punta")
DISTANCIA_AL_CANTO_DEFAULT = 0.0
LARGO_TIRA_DEFAULT = "marco_interior"
ENCUENTRO_ESQUINAS_DEFAULT = "vertical_domina"
FABRICACIONES = ("pacha", "independiente")
SUFIJOS_BORDE = {
    "frente": "Frente",
    "fondo": "Fondo",
    "izquierda": "Izq",
    "derecha": "Der",
}


class BordeConfig:
    """Configuracion de un borde del tablero.

    Vocabulario de taller:
      - ``distancia_al_canto``: distancia desde el canto del tablero hacia
        adentro (0 = al ras).
      - ``largo_tira``: ``marco_interior`` (respeta la luz de las esquinas)
        o ``punta_a_punta`` (de orilla a orilla del tablero).
      - ``encuentro_esquinas``: como se resuelve el cruce con otro borde.
    """

    def __init__(self, activo=False, ancho=70.0, distancia_al_canto=None,
                 largo_tira=LARGO_TIRA_DEFAULT, espesor=None,
                 encuentro_esquinas=None, offset_borde=None):
        self.activo = bool(activo)
        self.ancho = float(ancho)
        if distancia_al_canto is None:
            distancia_al_canto = (
                offset_borde if offset_borde is not None
                else DISTANCIA_AL_CANTO_DEFAULT)
        self.distancia_al_canto = float(distancia_al_canto)
        self.largo_tira = str(largo_tira or LARGO_TIRA_DEFAULT)
        self.encuentro_esquinas = encuentro_esquinas
        self.espesor = espesor

    @property
    def offset_borde(self):
        """Alias retrocompatible de ``distancia_al_canto``."""
        return self.distancia_al_canto

    @offset_borde.setter
    def offset_borde(self, valor):
        self.distancia_al_canto = float(valor)

    def to_dict(self):
        return {
            "activo": self.activo,
            "ancho": self.ancho,
            "distancia_al_canto": self.distancia_al_canto,
            "largo_tira": self.largo_tira,
            "encuentro_esquinas": self.encuentro_esquinas,
            "espesor": self.espesor,
            "offset_borde": self.distancia_al_canto,
        }

    @classmethod
    def from_dict(cls, datos):
        datos = datos or {}
        return cls(
            activo=datos.get("activo", False),
            ancho=datos.get("ancho", 70.0),
            distancia_al_canto=datos.get("distancia_al_canto"),
            largo_tira=datos.get("largo_tira", LARGO_TIRA_DEFAULT),
            espesor=datos.get("espesor"),
            encuentro_esquinas=datos.get("encuentro_esquinas"),
            offset_borde=datos.get("offset_borde"))


class ReengroseDTO:
    """DTO universal de bordes 2D."""

    def __init__(self, activo=False, esquinas="vertical_domina",
                 fabricacion="pacha", choque_nucleo="retroceso",
                 bordes=None):
        self.activo = bool(activo)
        self.esquinas = esquinas
        self.fabricacion = fabricacion
        self.choque_nucleo = choque_nucleo
        self.bordes = {}
        for borde in BORDES_2D:
            cfg = (bordes or {}).get(borde)
            if isinstance(cfg, BordeConfig):
                self.bordes[borde] = cfg
            else:
                self.bordes[borde] = BordeConfig.from_dict(cfg)

    def to_dict(self):
        return {
            "activo": self.activo,
            "esquinas": self.esquinas,
            "fabricacion": self.fabricacion,
            "choque_nucleo": self.choque_nucleo,
            "bordes": {
                borde: cfg.to_dict()
                for borde, cfg in self.bordes.items()
            },
            "usa_bordes": True,
        }


CANTO_VISTO = "RIG"
CANTO_OCULTO = "FX"

PROPS = {
    "activo": "VDO_Reengrose_Activo",
    "orientacion": "VDO_Reengrose_Orientacion",
    "ancho": "VDO_Reengrose_Ancho",
    "espesor": "VDO_Reengrose_Espesor",
    "cara": "VDO_Reengrose_Cara",
    "alineacion_profundidad": "VDO_Reengrose_Alineacion",
    "modo_fabricacion": "VDO_Reengrose_Modo",
    "alcance": "VDO_Reengrose_Alcance",
    "politica_repisa": "VDO_Reengrose_PoliticaRepisa",
    "prioridad_encuentro_tiras": "VDO_Reengrose_PrioridadEncuentro",
    "comportamiento_choque_nucleo": "VDO_Reengrose_ChoqueNucleo",
}

DEFAULTS = {
    "activo": False,
    "orientacion": "paralela",
    "ancho": 70.0,
    "espesor": None,
    "cara": "cara_a",
    "alineacion_profundidad": "frente",
    "modo_fabricacion": "pacha",
    "alcance": "parcial",
    "politica_repisa": "retroceder",
    "prioridad_encuentro_tiras": "vertical_domina",
    "comportamiento_choque_nucleo": "retroceso",
}


def _a_float(valor, nombre, defecto=None):
    if valor is None or valor == "":
        return defecto
    try:
        return float(valor)
    except (TypeError, ValueError) as exc:
        raise ReengroseError(
            f"Valor numerico invalido para '{nombre}': {valor!r}.") from exc


def _a_bool(valor):
    if isinstance(valor, bool):
        return valor
    if isinstance(valor, str):
        return valor.strip().lower() in ("1", "true", "si", "sí", "yes", "on")
    return bool(valor)


def _validar_enum(valor: object, nombre: str, validos: Sequence[str]) -> str:
    texto = str(valor or "").strip().lower()
    if texto not in validos:
        raise ReengroseError(
            f"Valor invalido para '{nombre}': {valor!r}. "
            f"Validos: {', '.join(validos)}.")
    return texto


def _normalizar_modo_choque(valor, nombre="comportamiento_choque_nucleo"):
    texto = str(valor or "").strip().lower()
    try:
        return _MAPA_MODO_CHOQUE[texto]
    except KeyError as exc:
        raise ReengroseError(
            f"Valor invalido para '{nombre}': {valor!r}. "
            f"Validos: {', '.join(MODOS_CHOQUE_NUCLEO)}.") from exc


_EJES = ("x", "y", "z")
