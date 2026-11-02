"""app/casos_uso/ — Un caso de uso por operación de usuario (M-04, F6).

Cada caso de uso recibe un Contexto y un Documento (puerto) y devuelve un
resultado. La escritura en el documento FreeCAD ocurre a través de cad/.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Resultado:
    ok: bool
    objeto: Any = None
    mensaje: str = ""
