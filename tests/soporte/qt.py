"""QApplication de proceso para los tests que construyen widgets Qt.

Un QWidget sin QApplication aborta el intérprete (SIGABRT, no es una excepción),
así que cualquier test que cree widgets debe llamar a ``qapplication()`` antes.

La instancia se guarda en un módulo global y no se destruye hasta que termina
el proceso: destruirla antes de tiempo provoca el segfault al salir (ver ADR-005).
Sin pantalla usa la plataforma ``offscreen``.
"""

from __future__ import annotations

import importlib
import os
import sys
from typing import Any

_APP: Any | None = None


def qapplication() -> Any:
    """Devuelve la QApplication del proceso, creándola si no existe."""
    global _APP
    qtw = importlib.import_module(_modulo_qt() + ".QtWidgets")
    existente = qtw.QApplication.instance()
    if existente is not None:
        _APP = existente
        return existente
    if not (os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY")):
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    _APP = qtw.QApplication(sys.argv[:1] or ["vdo-tests"])
    return _APP


def _modulo_qt() -> str:
    for nombre in ("PySide6", "PySide2", "PySide"):
        try:
            importlib.import_module(nombre + ".QtWidgets")
        except ImportError:
            continue
        return nombre
    raise ImportError("ninguno de PySide6/PySide2/PySide es importable")


__all__ = ["qapplication"]
