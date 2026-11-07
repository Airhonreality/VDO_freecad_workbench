"""Envia los logs del paquete freecad.vdo a la consola de FreeCAD (E1).

Los modulos de core/ registran con logging.getLogger(__name__) y no configuran handler.
Este modulo instala un unico handler en el logger "freecad.vdo", del que cuelgan todos
los loggers del paquete por propagacion.

Niveles: ERROR o superior -> App.Console.PrintError; WARNING -> PrintWarning;
INFO -> PrintMessage. DEBUG no se envia: queda en el logger.

Se instala una vez, desde freecad/vdo/__init__.py. Sin FreeCAD no instala nada.
Revertir: git revert del commit de E1 (b).
"""

from __future__ import annotations

import logging
from typing import Any

_NOMBRE_PAQUETE = "freecad.vdo"
_MARCA = "es_consola_freecad_vdo"


class HandlerConsolaFreeCAD(logging.Handler):
    """Entrega cada registro a App.Console segun su nivel."""

    es_consola_freecad_vdo = True

    def __init__(self, app: Any) -> None:
        super().__init__(level=logging.INFO)
        self._app = app

    def emit(self, record: logging.LogRecord) -> None:
        try:
            texto = self.format(record) + "\n"
            consola = self._app.Console
            if record.levelno >= logging.ERROR:
                consola.PrintError(texto)
            elif record.levelno >= logging.WARNING:
                consola.PrintWarning(texto)
            else:
                consola.PrintMessage(texto)
        except Exception:
            self.handleError(record)


def instalar_consola_freecad() -> logging.Handler | None:
    """Instala el handler una sola vez. Devuelve el handler, o None sin FreeCAD."""
    try:
        import FreeCAD as app
    except ImportError:
        return None
    logger = logging.getLogger(_NOMBRE_PAQUETE)
    for existente in logger.handlers:
        if getattr(existente, _MARCA, False):
            return existente
    handler = HandlerConsolaFreeCAD(app)
    handler.setFormatter(logging.Formatter("[%(name)s] %(message)s"))
    logger.addHandler(handler)
    return handler
