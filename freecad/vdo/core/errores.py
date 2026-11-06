"""core/errores.py — Jerarquía tipada de errores VDO (M-13).

Todos los errores de dominio heredan de ``VDOError``. Se prohíbe
``except Exception`` en core/cad/app y ``except … pass`` en todo el
paquete (R7).
"""

from __future__ import annotations

from typing import Any


class VDOError(Exception):
    """Excepción base de todos los errores del dominio VDO."""

    def __init__(self, mensaje: str, contexto: dict[str, Any] | None = None) -> None:
        super().__init__(mensaje)
        self.mensaje = mensaje
        self.contexto = contexto or {}

    def __str__(self) -> str:
        if self.contexto:
            ctx = ", ".join(f"{k}={v!r}" for k, v in self.contexto.items())
            return f"{self.mensaje} ({ctx})"
        return self.mensaje


class ParametroInvalido(VDOError):
    """Valor de parámetro fuera de rango o con formato inválido."""


class ReglaDeDominio(VDOError):
    """Violación de una regla de negocio del taller (p. ej. gola sin margen)."""


class CatalogoError(VDOError):
    """Error al consultar o cargar el catálogo de herrajes/manifiesto."""


class GeometriaError(VDOError):
    """Error de geometría (p. ej. reengrose que no cabe en la pieza)."""


__all__ = ["CatalogoError", "GeometriaError", "ParametroInvalido", "ReglaDeDominio", "VDOError"]
