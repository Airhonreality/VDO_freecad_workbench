"""app/registro.py — Canal único de logging (M-14).

Envuelve App.Console cuando hay FreeCAD, y usa logging de respaldo
sin FreeCAD para pruebas. Prohibido print en el paquete.
"""

from __future__ import annotations

import logging
import sys

LOGGER = logging.getLogger("vdo")
LOGGER.setLevel(logging.INFO)
if not LOGGER.handlers:
    _h = logging.StreamHandler(sys.stdout)
    _h.setFormatter(logging.Formatter("[VDO] %(levelname)s %(message)s"))
    LOGGER.addHandler(_h)


def _console():
    try:
        import FreeCAD as App  # perezoso, solo con FreeCAD real
        return App.Console
    except ImportError:
        return None


def info(msg: str):
    c = _console()
    if c is not None:
        c.PrintMessage(f"{msg}\n")
    LOGGER.info(msg)


def warning(msg: str):
    c = _console()
    if c is not None:
        c.PrintWarning(f"{msg}\n")
    LOGGER.warning(msg)


def error(msg: str):
    c = _console()
    if c is not None:
        c.PrintError(f"{msg}\n")
    LOGGER.error(msg)
