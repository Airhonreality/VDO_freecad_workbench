"""Paquete VDO. Subpaquetes: core (motor), ui (interfaz).

No hay __init__.py en freecad/: el paquete freecad es un espacio de nombres compartido
con FreeCAD y los addons.
"""

import os

# Fijar la plataforma Qt antes de cualquier import de Qt del paquete (P1: un solo lugar).
if os.environ.get("QT_QPA_PLATFORM") is None:
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

# Logs del paquete a la consola de FreeCAD (E1). Un solo punto; sin FreeCAD no hace nada.
from .registro import instalar_consola_freecad as _instalar_consola_freecad

_instalar_consola_freecad()
