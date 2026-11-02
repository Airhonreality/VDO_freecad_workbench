"""app/puertos.py — Puerto único Documento (M-06).

Define la interfaz ``Documento`` que app/ usa para crear, leer y escribir
objetos en el documento FreeCAD. cad/ la implementa. Los tests usan una
implementación en memoria (tests/soporte/documento_falso.py).

No hay otros puertos.
"""

from __future__ import annotations

from typing import Protocol


class Documento(Protocol):
    """Puerto de documento: crear/leer/escribir objetos, transacción, recompute."""

    def addObject(self, tipo: str, nombre: str) -> object: ...

    def getObject(self, nombre: str) -> object | None: ...

    def removeObject(self, nombre: str) -> None: ...

    def openTransaction(self, nombre: str) -> None: ...

    def commitTransaction(self) -> None: ...

    def abortTransaction(self) -> None: ...

    @property
    def HasPendingTransaction(self) -> bool: ...

    def recompute(self) -> None: ...

    @property
    def ActiveDocument(self) -> Documento | None: ...

    @property
    def Name(self) -> str: ...


def crear_documento(nombre: str = "VDO") -> Documento:
    """Crea un documento nuevo (delegado en cad/ en tiempo de ejecución)."""
    from freecad.vdo.cad.vdo_guardian import asegurar_documento as _cad_asegurar

    doc = _cad_asegurar()
    return doc
