"""Editor Qt del modificador universal de bordes de reengrose."""

from freecad.vdo.qt_compat import QtCore, QtWidgets
from freecad.vdo.ui.reengrose_ui_config import ReengroseConfigMixin
from freecad.vdo.ui.reengrose_ui_construccion import ReengroseConstruccionMixin
from freecad.vdo.ui.reengrose_ui_estado import ReengroseEstadoMixin
from freecad.vdo.ui.reengrose_ui_eventos import ReengroseEventosMixin


class ReengroseBorderEditor(
    ReengroseConstruccionMixin,
    ReengroseEventosMixin,
    ReengroseEstadoMixin,
    ReengroseConfigMixin,
    QtWidgets.QGroupBox):
    """Seccion Figma-like: bordes, distancia al canto, largos y esquinas."""

    changed = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__("Reengrose / Refuerzo", parent)
        self._cargando = False
        self._construir()
        self._conectar()
        self._actualizar_estado()
