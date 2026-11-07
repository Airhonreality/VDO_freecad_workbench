"""Instala los mocks de FreeCAD/Part al importarse.

Un test que necesite los mocks importa este modulo antes que freecad.vdo.
Los mocks se quedan instalados para el resto del proceso (igual que antes).
"""

from .freecad_falso import instalado

_CONTEXTO = instalado()
_CONTEXTO.__enter__()
