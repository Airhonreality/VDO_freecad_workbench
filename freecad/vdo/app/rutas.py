"""app/rutas.py — Rutas de recursos sin estado de módulo.

Proporciona funciones puras para localizar recursos (iconos, plantillas,
etc.) sin depender de variables globales mutables.
"""

from __future__ import annotations

from pathlib import Path

_HERE = Path(__file__).resolve().parent


def ruta_recursos(*subpath: str) -> str:
    """Devuelve la ruta absoluta a un recurso dentro de app/."""
    return str(_HERE.joinpath(*subpath))
