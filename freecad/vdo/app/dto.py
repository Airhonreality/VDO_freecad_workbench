"""app/dto.py — Objetos de transferencia de datos (DTO) para los casos de uso.

Todos los DTOs son dataclasses frozen (inmutables) para garantizar que la UI
no pueda modificar el estado de dominio. Los casos de uso reciben un DTO de
entrada y devuelven un DTO de salida.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PanelDTO:
    nombre: str
    etiqueta: str
    orientacion: str  # "horizontal" | "vertical"
    largo: float
    ancho: float
    espesor: float
    cantos: dict  # {"norte": str, "sur": str, "este": str, "oeste": str}
    material_ref: str = "melamina_standar"
    usar_params: bool = True
    rotacion: float = 0.0
    anclaje: str = "inferior_izquierda_frente"


@dataclass(frozen=True)
class PanelResultado:
    nombre: str
    volumen: float


@dataclass(frozen=True)
class CocoDTO:
    nombre: str
    alto: float
    ancho: float
    fondo_modulo: float
    espesor: float = 18.0
    tiene_fondo: bool = True
    calibre_fondo: float = 6.0
    divisiones: str = ""
    reengroses: dict | None = None
    rotacion: float = 0.0
    anclaje: str = "inferior_izquierda_frente"
    lados_vistos: list | None = None
    lados_apoyados: list | None = None


@dataclass(frozen=True)
class CocoResultado:
    nombre: str
    volumen: float


@dataclass(frozen=True)
class ZocaloDTO:
    nombre: str
    ancho: float
    fondo: float
    alto_zocalo: float
    espesor_tablero: float = 18.0
    distancia_frente: float = 50.0
    distancia_costados: float = 0.0
    distancia_trasera: float = 20.0
    tiene_trasera: bool = True
    amarres_intermedios: int = 0
    material_ref: str = "melamina_standar"
    rotacion: float = 0.0
    anclaje: str = "inferior_izquierda_frente"


@dataclass(frozen=True)
class ZocaloResultado:
    nombre: str
    volumen: float


@dataclass(frozen=True)
class CajonDTO:
    nombre: str
    ancho_libre: float
    prof_libre: float
    ancho_modulo: float
    alto_frente: float
    alto_caja: float = 120.0
    grosor_caja: float = 16.0
    grosor_fondo: float = 6.0
    grosor_fachada: float = 18.0
    marca: str = "blum_tandem"
    longitud_guia: float = 0.0
    montaje_trasera: str = "entre_laterales"
    tipo_corredera: str = "oculta"
    sistema_apertura: str = "tirador"
    tipo_montaje: str = "parche"
    material_ref: str = "melamina_standar"
    rotacion: float = 0.0
    anclaje: str = "inferior_izquierda_frente"


@dataclass(frozen=True)
class CajonResultado:
    nombre: str
    tipo_corredera: str


@dataclass(frozen=True)
class PuertaDTO:
    nombre: str
    ancho: float
    alto: float
    espesor: float = 18.0
    tipo_montaje: str = "parche"
    sistema_apertura: str = "tirador"
    material_ref: str = "melamina_standar"
    rotacion: float = 0.0
    anclaje: str = "inferior_izquierda_frente"


@dataclass(frozen=True)
class PuertaResultado:
    nombre: str
    alto: float


@dataclass(frozen=True)
class HojaDTO:
    nombre: str = "VDO"


@dataclass(frozen=True)
class HojaResultado:
    nombre: str


@dataclass(frozen=True)
class EditarModuloDTO:
    nombre: str
    cambios: dict


@dataclass(frozen=True)
class EditarModuloResultado:
    nombre: str
    aplicado: bool


@dataclass(frozen=True)
class ColocarModuloDTO:
    nombre: str
    x: float
    y: float
    z: float
    rotacion: float = 0.0


@dataclass(frozen=True)
class ColocarModuloResultado:
    nombre: str
    colocado: bool


@dataclass(frozen=True)
class ExportarListaCorteDTO:
    modulo: str
    formato: str = "csv"


@dataclass(frozen=True)
class ExportarListaCorteResultado:
    archivo: str
    piezas: int


@dataclass(frozen=True)
class OptimizarCorteDTO:
    modulos: list
    ancho_tablero: float
    alto_tablero: float


@dataclass(frozen=True)
class OptimizarCorteResultado:
    eficiencia: float
    desperdicio: float


@dataclass(frozen=True)
class NestingDTO:
    piezas: list


@dataclass(frozen=True)
class NestingResultado:
    placas: int


@dataclass(frozen=True)
class ConsultarHerrajesDTO:
    tipo: str | None = None


@dataclass(frozen=True)
class ConsultarHerrajesResultado:
    herrajes: list


@dataclass(frozen=True)
class RecargarCatalogoDTO:
    pass


@dataclass(frozen=True)
class RecargarCatalogoResultado:
    version: str


__all__ = [
    "CajonDTO",
    "CajonResultado",
    "CocoDTO",
    "CocoResultado",
    "ColocarModuloDTO",
    "ColocarModuloResultado",
    "ConsultarHerrajesDTO",
    "ConsultarHerrajesResultado",
    "EditarModuloDTO",
    "EditarModuloResultado",
    "ExportarListaCorteDTO",
    "ExportarListaCorteResultado",
    "HojaDTO",
    "HojaResultado",
    "NestingDTO",
    "NestingResultado",
    "OptimizarCorteDTO",
    "OptimizarCorteResultado",
    "PanelDTO",
    "PanelResultado",
    "PuertaDTO",
    "PuertaResultado",
    "RecargarCatalogoDTO",
    "RecargarCatalogoResultado",
    "ZocaloDTO",
    "ZocaloResultado",
]
