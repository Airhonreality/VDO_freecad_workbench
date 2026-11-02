"""app/casos_uso/__init__.py — Casos de uso de la capa app/.

Cada caso de uso recibe un DTO de entrada (frozen dataclass en app/dto.py)
y un Documento (puerto), y devuelve un DTO de salida. No importa PySide ni
escribe en objetos FreeCAD directamente (eso es responsabilidad de cad/).
"""

from __future__ import annotations

from freecad.vdo.app.dto import (
    CajonDTO, CajonResultado,
    CocoDTO, CocoResultado,
    ColocarModuloDTO, ColocarModuloResultado,
    ConsultarHerrajesDTO, ConsultarHerrajesResultado,
    EditarModuloDTO, EditarModuloResultado,
    ExportarListaCorteDTO, ExportarListaCorteResultado,
    HojaDTO, HojaResultado,
    NestingDTO, NestingResultado,
    OptimizarCorteDTO, OptimizarCorteResultado,
    PanelDTO, PanelResultado,
    PuertaDTO, PuertaResultado,
    RecargarCatalogoDTO, RecargarCatalogoResultado,
    ZocaloDTO, ZocaloResultado,
)

__all__ = [
    "crear_hoja", "crear_panel", "crear_zocalo", "crear_cajon", "crear_puerta",
    "crear_coco", "editar_modulo", "colocar_modulo",
    "exportar_lista_corte", "optimizar_corte", "nesting",
    "consultar_herrajes", "recargar_catalogo",
    "CajonDTO", "CajonResultado",
    "CocoDTO", "CocoResultado",
    "ColocarModuloDTO", "ColocarModuloResultado",
    "ConsultarHerrajesDTO", "ConsultarHerrajesResultado",
    "EditarModuloDTO", "EditarModuloResultado",
    "ExportarListaCorteDTO", "ExportarListaCorteResultado",
    "HojaDTO", "HojaResultado",
    "NestingDTO", "NestingResultado",
    "OptimizarCorteDTO", "OptimizarCorteResultado",
    "PanelDTO", "PanelResultado",
    "PuertaDTO", "PuertaResultado",
    "RecargarCatalogoDTO", "RecargarCatalogoResultado",
    "ZocaloDTO", "ZocaloResultado",
]
