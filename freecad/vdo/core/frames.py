"""Marco local unico VDO y vocabulario de lados.

Contrato:
    X+ = derecha
    Y+ = fondo
    Z+ = arriba
    frente funcional = Y-

Este modulo es puro: no importa FreeCAD ni Qt.
"""

import json
import math
from collections.abc import Iterable, Mapping, Sequence
from typing import Any, Final

FRENTE = "frente"
FONDO = "fondo"
IZQUIERDA = "izquierda"
DERECHA = "derecha"
SUPERIOR = "superior"
INFERIOR = "inferior"

LADOS: Final = (FRENTE, FONDO, IZQUIERDA, DERECHA, SUPERIOR, INFERIOR)

NORMALES: Final[Mapping[str, tuple[float, float, float]]] = {
    FRENTE: (0.0, -1.0, 0.0),
    FONDO: (0.0, 1.0, 0.0),
    IZQUIERDA: (-1.0, 0.0, 0.0),
    DERECHA: (1.0, 0.0, 0.0),
    SUPERIOR: (0.0, 0.0, 1.0),
    INFERIOR: (0.0, 0.0, -1.0),
}

OPUESTOS: Final[Mapping[str, str]] = {
    FRENTE: FONDO,
    FONDO: FRENTE,
    IZQUIERDA: DERECHA,
    DERECHA: IZQUIERDA,
    SUPERIOR: INFERIOR,
    INFERIOR: SUPERIOR,
}

ETIQUETA_FRENTE = "FRENTE (Y\u2212)"
EJES_PREVIEW = "X\u2192  Y\u2191"


def normal(lado: Any) -> tuple[float, float, float]:
    try:
        return NORMALES[str(lado).lower()]
    except KeyError as exc:
        raise ValueError(
            f"Lado VDO invalido: '{lado}'. Validos: {', '.join(LADOS)}.") from exc


def opuesto(lado: Any) -> str:
    try:
        return OPUESTOS[str(lado).lower()]
    except KeyError as exc:
        raise ValueError(
            f"Lado VDO invalido: '{lado}'. Validos: {', '.join(LADOS)}.") from exc


def rotar_z(vector: Sequence[float], grados: float) -> tuple[float, float, float]:
    """Rota un vector (x,y,z) alrededor de Z. Angulo en grados."""
    x, y, z = vector
    rad = math.radians(float(grados))
    c = math.cos(rad)
    s = math.sin(rad)
    return (x * c - y * s, x * s + y * c, z)


def normal_global(lado: Any, rotacion_z: float = 0.0) -> tuple[float, float, float]:
    return rotar_z(normal(lado), rotacion_z)


def interpretar_lados(valor: Any, por_defecto: Iterable[str] | None = None) -> list[str]:
    """Devuelve una lista de lados desde JSON, CSV o lista."""
    if valor is None or valor == "":
        return list(por_defecto or [])

    if isinstance(valor, str):
        texto = valor.strip()
        if not texto:
            return list(por_defecto or [])
        datos: list[Any] = json.loads(texto) if texto.startswith("[") else texto.split(",")
    elif isinstance(valor, (list, tuple, set)):
        datos = list(valor)
    else:
        raise ValueError(f"Exposicion VDO invalida: {valor!r}")

    resultado: list[str] = []
    for item in datos:
        lado = str(item).strip().lower()
        if not lado:
            continue
        if lado not in LADOS:
            raise ValueError(
                f"Lado VDO invalido: '{item}'. Validos: {', '.join(LADOS)}.")
        if lado not in resultado:
            resultado.append(lado)
    return resultado


def serializar_lados(lados: Any) -> str:
    return json.dumps(interpretar_lados(lados), ensure_ascii=False)


def cargar_exposicion(obj: Any, por_defecto_vistos: Iterable[str] = (FRENTE,),
                      por_defecto_apoyados: Iterable[str] = (FONDO,)
                      ) -> tuple[list[str], list[str]]:
    vistos = interpretar_lados(
        getattr(obj, "VDO_Lados_Vistos", ""), por_defecto_vistos)
    apoyados = interpretar_lados(
        getattr(obj, "VDO_Lados_Apoyados", ""), por_defecto_apoyados)
    apoyados = [lado for lado in apoyados if lado not in vistos]
    return vistos, apoyados


# Devuelve (vistos, apoyados) desde siempre: la anotacion previa -> None era erronea.
def guardar_exposicion(obj: Any, vistos: Any, apoyados: Any
                       ) -> tuple[list[str], list[str]]:
    vistos = interpretar_lados(vistos)
    apoyados = [
        lado for lado in interpretar_lados(apoyados) if lado not in vistos]
    obj.VDO_Lados_Vistos = serializar_lados(vistos)
    obj.VDO_Lados_Apoyados = serializar_lados(apoyados)
    return vistos, apoyados
