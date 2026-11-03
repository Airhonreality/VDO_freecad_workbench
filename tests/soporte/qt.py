"""QApplication de proceso para los tests que construyen widgets Qt.

Un QWidget sin QApplication aborta el intérprete (SIGABRT, no es una excepción),
así que cualquier test que cree widgets debe llamar a ``qapplication()`` antes.

La instancia se guarda en un módulo global. Antes de terminar el proceso, el runner
debe llamar a ``liberar_widgets()``: los widgets vivos al cerrar el intérprete hacen
segfaultear a Qt (ver ADR-005). Sin pantalla usa la plataforma ``offscreen``.
"""

from __future__ import annotations

import importlib
import os
import sys
from typing import Any

_APP: Any | None = None
_PASADAS_LIMPIEZA = 20


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


def liberar_widgets() -> int:
    """Cierra y libera todos los widgets de nivel superior. Devuelve cuántos quedaban.

    Lo llama el runner (tools/run_tests.py) con Python todavía vivo, justo antes de
    terminar. No se usa atexit: bajo freecadcmd los manejadores de atexit no llegan
    a ejecutarse (medido: ningún print de atexit en 5 corridas), y el segfault ocurre
    en la destrucción estática de shiboken, que va después (ADR-005).
    """
    if _APP is None:
        return 0
    return _vaciar_widgets(_APP)


def _vaciar_widgets(app: Any) -> int:
    """Varias pasadas: cerrar un widget puede dejar otros de nivel superior pendientes.

    deleteLater() encola un DeferredDelete que processEvents() NO procesa fuera de un
    bucle de eventos: hace falta sendPostedEvents(None, DeferredDelete).
    """
    qtc = importlib.import_module(_modulo_qt() + ".QtCore")
    liberados = 0
    for _ in range(_PASADAS_LIMPIEZA):
        pendientes = list(app.topLevelWidgets())
        if not pendientes:
            break
        liberados += len(pendientes)
        for widget in pendientes:
            widget.close()
            widget.deleteLater()
        qtc.QCoreApplication.sendPostedEvents(None, int(qtc.QEvent.Type.DeferredDelete))
        app.processEvents()
    return liberados


def _modulo_qt() -> str:
    for nombre in ("PySide6", "PySide2", "PySide"):
        try:
            importlib.import_module(nombre + ".QtWidgets")
        except ImportError:
            continue
        return nombre
    raise ImportError("ninguno de PySide6/PySide2/PySide es importable")


__all__ = ["liberar_widgets", "qapplication"]
