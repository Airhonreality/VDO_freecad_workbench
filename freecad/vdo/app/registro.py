# -*- coding: utf-8 -*-
"""app/registro.py — Canal único de logging (M-14).

Envuelve App.Console cuando hay FreeCAD, y usa logging de respaldo
sin FreeCAD para pruebas. Prohibido print en el paquete.
"""

from __future__ import annotations

import logging
import sys

_logger = logging.getLogger("vdo")
_logger.setLevel(logging.INFO)
if not _logger.handlers:
    _h = logging.StreamHandler(sys.stdout)
    _h.setFormatter(logging.Formatter("[VDO] %(levelname)s %(message)s"))
    _logger.addHandler(_h)


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
    _logger.info(msg)


def warning(msg: str):
    c = _console()
    if c is not None:
        c.PrintWarning(f"{msg}\n")
    _logger.warning(msg)


def error(msg: str):
    c = _console()
    if c is not None:
        c.PrintError(f"{msg}\n")
    _logger.error(msg)
