"""app/casos_uso/crear_zocalo.py — Caso de uso: crear zócalo."""

from __future__ import annotations

from dataclasses import dataclass

from freecad.vdo.app.casos_uso import Resultado
from freecad.vdo.core.vdo_zocalo_core import make_zocalo


@dataclass(frozen=True)
class ParametrosZocalo:
    ancho: float
    fondo: float
    alto_zocalo: float
    espesor_tablero: int
    distancia_frente: float
    distancia_costados: float
    distancia_trasera: float
    tiene_trasera: bool
    amarres_intermedios: int
    material_ref: str
    nombre: str = "Zocalo"


def crear_zocalo(contexto, documento, params: ParametrosZocalo) -> Resultado:
    """Crea un zócalo en el documento usando el plano puro de core/."""
    cfg = {
        "nombre": params.nombre,
        "ancho": params.ancho,
        "fondo": params.fondo,
        "alto_zocalo": params.alto_zocalo,
        "espesor_tablero": params.espesor_tablero,
        "distancia_frente": params.distancia_frente,
        "distancia_costados": params.distancia_costados,
        "distancia_trasera": params.distancia_trasera,
        "tiene_trasera": params.tiene_trasera,
        "amarres_intermedios": params.amarres_intermedios,
        "material_ref": params.material_ref,
    }
    obj = make_zocalo(cfg)
    return Resultado(ok=True, objeto=obj)
