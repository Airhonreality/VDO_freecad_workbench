"""Modificador de reengrose: DTO, normalizacion de entrada, espesor efectivo y
lectura/escritura en el objeto. La normalizacion de bordes vive en
reengrose_modificador_normalizacion.py."""

import json
import logging
from collections.abc import Mapping
from typing import Any, cast

from freecad.vdo.core.reengrose_modelo import (
    DEFAULTS,
    PROPS,
    BordeConfig,
    ReengroseDTO,
    ReengroseError,
    _a_float,
)
from freecad.vdo.core.reengrose_modificador_normalizacion import (
    _normalizar_modificador_bordes,
    _normalizar_modificador_legacy,
    _usa_bordes,
)

_LOG = logging.getLogger(__name__)


class ReengroseModifier:
    """DTO puro del modificador de reengrose.

    Mantiene las propiedades planas historicas (orientacion, ancho, cara,
    etc.) y expone ademas ``bordes`` como ``BordeConfig`` para la nueva UI
    de modificador universal.
    """

    activo: bool
    bordes: dict[str, BordeConfig]
    esquinas: dict[str, str] | str
    fabricacion: str
    choque_nucleo: str
    # Atributo fijado por setattr desde normalizar_modificador(); solo se declara para el tipo.
    comportamiento_choque_nucleo: str

    def __init__(self, datos: Any = None) -> None:
        datos = normalizar_modificador(datos)
        for clave, valor in datos.items():
            if clave == "bordes":
                self.bordes = {
                    borde: BordeConfig.from_dict(cfg)
                    for borde, cfg in valor.items()
                }
            else:
                setattr(self, clave, valor)

    def to_dict(self) -> dict[str, Any]:
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

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False)

    @classmethod
    def from_dict(cls, datos: Any) -> "ReengroseModifier":
        return cls(datos)


# Any: datos puede ser DTO, objeto, dict, None o envoltorio.
def _datos_modificador(datos: Any) -> dict[str, Any]:
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
    # cast: tras el isinstance y el envoltorio, mypy pierde el tipo (Any).
    return cast(dict[str, Any], datos)


# Any: datos es la entrada cruda de UI o JSON, sin tipo fijo.
def normalizar_modificador(datos: Any = None) -> dict[str, Any]:
    datos = _datos_modificador(datos)
    if _usa_bordes(datos):
        return _normalizar_modificador_bordes(datos)
    return _normalizar_modificador_legacy(datos)


def espesor_efectivo(panel_base: Mapping[str, Any], modifier: Any) -> float:
    mod = normalizar_modificador(modifier)
    if mod["espesor"]:
        return float(mod["espesor"])
    return float(panel_base.get("espesor", 0.0))


def desde_objeto(obj: Any) -> ReengroseModifier:
    texto = getattr(obj, "VDO_Reengrose_JSON", "") or ""
    guardado: Any = None
    if texto:
        try:
            guardado = json.loads(texto)
        except (TypeError, ValueError) as exc:
            _LOG.warning("reengrose_modificador: estado guardado no valido: %s", exc)
            guardado = None
    if (guardado is not None
            and isinstance(guardado, dict)
            and any(clave in guardado for clave in
                    ("bordes", "esquinas", "fabricacion",
                     "choque_nucleo"))):
        return ReengroseModifier(guardado)
    datos: dict[str, Any] = {}
    for clave, prop in PROPS.items():
        datos[clave] = getattr(obj, prop, DEFAULTS[clave])
    datos["espesor"] = _a_float(datos.get("espesor"), "espesor")
    if datos.get("espesor") == 0.0:
        datos["espesor"] = None
    return ReengroseModifier(datos)


def aplicar_a_objeto(obj: Any, modifier: Any) -> ReengroseModifier:
    mod = ReengroseModifier(modifier)
    datos = mod.to_dict()
    for clave, prop in PROPS.items():
        valor = datos[clave]
        if clave == "espesor" and valor is None:
            valor = 0.0
        setattr(obj, prop, valor)
    obj.VDO_Reengrose_JSON = mod.to_json()
    return mod


def leer_reengroses(obj: Any) -> dict[str, Any]:
    """Lee el JSON de reengroses almacenado en un objeto (unificado F19.7).

    Reemplaza las copias _cargar_reengroses (core) y _leer_reengroses (ui).
    """
    texto = getattr(obj, "VDO_Reengrose_JSON", "") or "{}"
    try:
        datos = json.loads(texto) if isinstance(texto, str) else dict(texto)
    except (TypeError, ValueError) as exc:
        _LOG.warning("reengrose_modificador: reengroses no leidos, usa vacio: %s", exc)
        return {}
    return datos if isinstance(datos, dict) else {}


def modificador_de_mapa(mapa: Any, clave: str, origen: str) -> ReengroseModifier:
    """Modificador de `clave` en un mapa de reengroses; vacío si falta o es inválido.

    `origen` nombra al módulo que llama y aparece en el aviso de reengrose inválido.
    """
    datos = (mapa or {}).get(clave)
    if not datos:
        return ReengroseModifier()
    try:
        return ReengroseModifier(datos)
    except ReengroseError as exc:
        _LOG.warning("%s: reengrose invalido, usa modificador vacio: %s", origen, exc)
        return ReengroseModifier()
