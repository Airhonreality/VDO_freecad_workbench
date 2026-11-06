"""Vista compacta del tablero con bordes activos y tipo de esquina."""

from freecad.vdo.qt_compat import QtCore, QtGui, QtWidgets
from freecad.vdo.ui import tema
from freecad.vdo.ui.reengrose_ui_constantes import COLOR_ESQUINA


class VDOBoardPreview(QtWidgets.QWidget):
    """Vista compacta del tablero con bordes activos y tipo de esquina."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(220, 150)
        self.setMaximumSize(260, 170)
        self._bordes = set()
        self._esquinas = {}

    def set_estado(self, bordes, esquinas):
        self._bordes = set(bordes or [])
        self._esquinas = dict(esquinas or {})
        self.update()

    def paintEvent(self, _event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        ancho = self.width()
        alto = self.height()
        margen = 24
        x0, y0 = margen, margen
        x1, y1 = ancho - margen, alto - margen
        if x1 <= x0 or y1 <= y0:
            return

        painter.setBrush(QtGui.QBrush(QtGui.QColor(tema.FONDO)))
        painter.setPen(QtGui.QPen(QtGui.QColor(tema.COLOR_BORDE_MEDIO), 1))
        painter.drawRoundedRect(x0, y0, x1 - x0, y1 - y0, 6, 6)

        grosor = 9
        activo = QtGui.QColor(tema.ACEINTO)
        inactivo = QtGui.QColor(tema.BORDE_SUAVE)

        def color_borde(borde):
            return activo if borde in self._bordes else inactivo

        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(QtGui.QBrush(color_borde("frente")))
        painter.drawRect(x0, y0, x1 - x0, grosor)
        painter.setBrush(QtGui.QBrush(color_borde("fondo")))
        painter.drawRect(x0, y1 - grosor, x1 - x0, grosor)
        painter.setBrush(QtGui.QBrush(color_borde("izquierda")))
        painter.drawRect(x0, y0, grosor, y1 - y0)
        painter.setBrush(QtGui.QBrush(color_borde("derecha")))
        painter.drawRect(x1 - grosor, y0, grosor, y1 - y0)

        posiciones = {
            "frente_izquierda": (x0 + grosor, y0 + grosor),
            "frente_derecha": (x1 - grosor, y0 + grosor),
            "fondo_izquierda": (x0 + grosor, y1 - grosor),
            "fondo_derecha": (x1 - grosor, y1 - grosor),
        }
        lado = 14
        for esquina, (cx, cy) in posiciones.items():
            tipo = self._esquinas.get(esquina)
            color = QtGui.QColor(COLOR_ESQUINA.get(tipo, tema.BORDE))
            painter.setBrush(QtGui.QBrush(color))
            painter.setPen(QtGui.QPen(QtGui.QColor(tema.COLOR_TRAZO_NEGRO), 1))
            painter.drawRect(cx - lado / 2.0, cy - lado / 2.0, lado, lado)
            if tipo == "inglete_45":
                painter.setPen(QtGui.QPen(QtGui.QColor(tema.COLOR_TRAZO_NEGRO), 1))
                painter.drawLine(cx - lado / 2.0, cy + lado / 2.0,
                                 cx + lado / 2.0, cy - lado / 2.0)
            elif tipo == "marco_interior":
                painter.setBrush(QtGui.QBrush(QtGui.QColor(tema.FONDO)))
                painter.setPen(QtGui.QPen(QtGui.QColor(tema.COLOR_TRAZO_CLARO), 1))
                painter.drawRect(cx - lado / 4.0, cy - lado / 4.0,
                                 lado / 2.0, lado / 2.0)

        painter.setPen(QtGui.QPen(QtGui.QColor(tema.COLOR_TRAZO_NEUTRO), 1))
        painter.drawText(
            QtCore.QRectF(x0, y0, x1 - x0, y1 - y0),
            QtCore.Qt.AlignCenter, "Tablero")
        painter.end()
