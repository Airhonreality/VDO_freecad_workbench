"""Pintado y edicion de celdas de la tabla de espacios."""

import logging

from freecad.vdo.core.spaces import ESPACIO_FIJO, ESPACIO_IGUALES
from freecad.vdo.qt_compat import QtCore, QtWidgets

_LOG = logging.getLogger(__name__)


class CocoUnifiedCeldasMixin:
    """Mixin del panel COCO: Pintado y edicion de celdas de la tabla de espacios."""

    def _on_medida_changed(self, *args):
        if self._building:
            return
        self.editor_divisiones.set_dimensions(
            self.spin_alto.value(), self.spin_ancho.value(),
            self.spin_espesor.value())
        self._actualizar_resumen()

    def _on_divisiones_changed(self):
        self._actualizar_resumen()
