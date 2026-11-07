"""Canvas concentrico gestaltico. Parte de ui/box_controller.py (M7, D-44)."""

from freecad.vdo.core import reengrose_modelo as VDO_RE_MODELO
from freecad.vdo.qt_compat import QtCore, QtGui, QtWidgets
from freecad.vdo.ui import tema_colores
from freecad.vdo.ui.box_constantes import _SEGMENTO_MARGEN_SEL, ESQUINAS


# ----------------------------------------------------------------------
# Canvas Concéntrico Gestáltico (Calibre 1px Canto + Calibre 3px Tiras)
# ----------------------------------------------------------------------
class _VDOConcentricCenterCanvas(QtWidgets.QWidget):
    """
    Dibuja concéntricamente el canto del tablero (calibre 1px) y las tiras
    de reengrose (calibre 3px), mostrando visualmente la brecha de offset.
    Permite hacer clic sobre cualquier margen para seleccionarlo.
    """

    sigMarginClicked = QtCore.Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(130, 95)
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.setMouseTracking(True)
        self.activos = {b: False for b in VDO_RE_MODELO.BORDES_2D}
        self.valores = {b: {"ancho": 70.0, "offset": 0.0} for b in VDO_RE_MODELO.BORDES_2D}
        self.esquinas = {e: "vertical_domina" for e in ESQUINAS}
        self.margen_sel = "frente"

    def actualizar(self, activos, valores, esquinas, margen_sel):
        self.activos = dict(activos)
        self.valores = {b: dict(valores[b]) for b in VDO_RE_MODELO.BORDES_2D}
        self.esquinas = dict(esquinas)
        self.margen_sel = margen_sel
        self.update()

    def mousePressEvent(self, event):
        pos = event.pos()
        w = self.width()
        h = self.height()
        # Determinar qué margen exterior está más cerca del clic
        dx_left = pos.x()
        dx_right = w - pos.x()
        dy_top = pos.y()
        dy_bottom = h - pos.y()

        minimo = min(dx_left, dx_right, dy_top, dy_bottom)
        if minimo == dy_top:
            self.sigMarginClicked.emit("fondo")
        elif minimo == dy_bottom:
            self.sigMarginClicked.emit("frente")
        elif minimo == dx_left:
            self.sigMarginClicked.emit("izquierda")
        else:
            self.sigMarginClicked.emit("derecha")

        super().mousePressEvent(event)

    def paintEvent(self, event):
        p = QtGui.QPainter(self)
        p.setRenderHint(QtGui.QPainter.Antialiasing)

        x0, y0, bw, bh = self._geometria_tablero()

        if bw <= 10 or bh <= 10:
            p.end()
            return

        self._pintar_base(p, x0, y0, bw, bh)
        gap_norte, gap_sur, gap_oeste, gap_este = self._calcular_brechas()
        self._pintar_lineas_offset(p, x0, y0, bw, bh)
        self._pintar_tiras(p, x0, y0, bw, bh, gap_norte, gap_sur, gap_oeste, gap_este)
        self._pintar_ingletes(p, x0, y0, bw, bh, gap_norte, gap_sur, gap_oeste, gap_este)

        p.end()

    def _geometria_tablero(self):
        w = self.width()
        h = self.height()
        x0 = 8
        y0 = 8
        bw = w - 16
        bh = h - 16
        return x0, y0, bw, bh

    def _pintar_base(self, p, x0, y0, bw, bh):
        # 1. Fondo del tablero interior
        p.fillRect(QtCore.QRectF(x0, y0, bw, bh), QtGui.QColor(tema_colores.COLOR_FONDO_CANVAS))

        # 2. Calibre 1px: Canto exterior del tablero
        pen_canto_base = QtGui.QPen(QtGui.QColor(tema_colores.BORDE), 1, QtCore.Qt.SolidLine)
        p.setPen(pen_canto_base)
        p.drawRect(QtCore.QRectF(x0, y0, bw, bh))

        # Resaltado del margen seleccionado en Calibre 1.5px Cyan
        pen_sel = QtGui.QPen(QtGui.QColor(tema_colores.ACEINTO), 1.8, QtCore.Qt.SolidLine)
        p.setPen(pen_sel)
        segmento = _SEGMENTO_MARGEN_SEL.get(self.margen_sel)
        if segmento is not None:
            x1, y1, x2, y2 = segmento(x0, y0, bw, bh)
            p.drawLine(QtCore.QPointF(x1, y1), QtCore.QPointF(x2, y2))

    def _calcular_brechas(self):
        # 3. Brechas y Calibre 3px: Tiras de Melamina
        # Si offset == 0: gap = 3 px (al ras)
        # Si offset > 0: gap = 11 px (retranqueado / visiblemente separado)
        def calc_gap(borde):
            return 11.0 if self.valores[borde]["offset"] > 0.0 else 3.0

        gap_norte = calc_gap("fondo")
        gap_sur = calc_gap("frente")
        gap_oeste = calc_gap("izquierda")
        gap_este = calc_gap("derecha")
        return gap_norte, gap_sur, gap_oeste, gap_este

    def _pintar_lineas_offset(self, p, x0, y0, bw, bh):
        # Línea indicadora de offset en la brecha si offset > 0 (Dotted ámbar/azul)
        pen_offset_line = QtGui.QPen(QtGui.QColor(tema_colores.COLOR_NARANJA), 1, QtCore.Qt.DotLine)
        p.setPen(pen_offset_line)
        if self.valores["fondo"]["offset"] > 0.0 and self.activos["fondo"]:
            p.drawLine(QtCore.QPointF(x0 + 4, y0 + 6), QtCore.QPointF(x0 + bw - 4, y0 + 6))
        if self.valores["frente"]["offset"] > 0.0 and self.activos["frente"]:
            p.drawLine(QtCore.QPointF(x0 + 4, y0 + bh - 6), QtCore.QPointF(x0 + bw - 4, y0 + bh - 6))
        if self.valores["izquierda"]["offset"] > 0.0 and self.activos["izquierda"]:
            p.drawLine(QtCore.QPointF(x0 + 6, y0 + 4), QtCore.QPointF(x0 + 6, y0 + bh - 4))
        if self.valores["derecha"]["offset"] > 0.0 and self.activos["derecha"]:
            p.drawLine(QtCore.QPointF(x0 + bw - 6, y0 + 4), QtCore.QPointF(x0 + bw - 6, y0 + bh - 4))

    def _pintar_tiras(self, p, x0, y0, bw, bh, gap_norte, gap_sur, gap_oeste, gap_este):
        # Tiras de Calibre 3px
        pen3_act = QtGui.QPen(QtGui.QColor(tema_colores.ACEINTO), 3, QtCore.Qt.SolidLine)
        pen3_sel = QtGui.QPen(QtGui.QColor(tema_colores.COLOR_ACENTO_CIAN), 3, QtCore.Qt.SolidLine)
        pen3_inact = QtGui.QPen(QtGui.QColor(tema_colores.COLOR_FONDO_INACTIVO), 1, QtCore.Qt.DashLine)

        # FONDO (Norte)
        p_top = pen3_sel if self.margen_sel == "fondo" and self.activos["fondo"] else (
            pen3_act if self.activos["fondo"] else pen3_inact)
        p.setPen(p_top)
        p.drawLine(QtCore.QPointF(x0 + gap_oeste, y0 + gap_norte),
                   QtCore.QPointF(x0 + bw - gap_este, y0 + gap_norte))

        # FRENTE (Sur)
        p_bot = pen3_sel if self.margen_sel == "frente" and self.activos["frente"] else (
            pen3_act if self.activos["frente"] else pen3_inact)
        p.setPen(p_bot)
        p.drawLine(QtCore.QPointF(x0 + gap_oeste, y0 + bh - gap_sur),
                   QtCore.QPointF(x0 + bw - gap_este, y0 + bh - gap_sur))

        # IZQUIERDA (Oeste)
        p_izq = pen3_sel if self.margen_sel == "izquierda" and self.activos["izquierda"] else (
            pen3_act if self.activos["izquierda"] else pen3_inact)
        p.setPen(p_izq)
        p.drawLine(QtCore.QPointF(x0 + gap_oeste, y0 + gap_norte),
                   QtCore.QPointF(x0 + gap_oeste, y0 + bh - gap_sur))

        # DERECHA (Este)
        p_der = pen3_sel if self.margen_sel == "derecha" and self.activos["derecha"] else (
            pen3_act if self.activos["derecha"] else pen3_inact)
        p.setPen(p_der)
        p.drawLine(QtCore.QPointF(x0 + bw - gap_este, y0 + gap_norte),
                   QtCore.QPointF(x0 + bw - gap_este, y0 + bh - gap_sur))

    def _pintar_ingletes(self, p, x0, y0, bw, bh, gap_norte, gap_sur, gap_oeste, gap_este):
        # 4. Encuentros de esquina (Miters)
        # Inglete 45°: Línea diagonal en esquinas activas
        pen_miter = QtGui.QPen(QtGui.QColor(tema_colores.ACEINTO), 1.2, QtCore.Qt.SolidLine)
        p.setPen(pen_miter)
        if self.esquinas.get("fondo_izquierda") == "inglete_45" and (self.activos["fondo"] or self.activos["izquierda"]):
            p.drawLine(QtCore.QPointF(x0, y0), QtCore.QPointF(x0 + gap_oeste, y0 + gap_norte))
        if self.esquinas.get("fondo_derecha") == "inglete_45" and (self.activos["fondo"] or self.activos["derecha"]):
            p.drawLine(QtCore.QPointF(x0 + bw, y0), QtCore.QPointF(x0 + bw - gap_este, y0 + gap_norte))
        if self.esquinas.get("frente_izquierda") == "inglete_45" and (self.activos["frente"] or self.activos["izquierda"]):
            p.drawLine(QtCore.QPointF(x0, y0 + bh), QtCore.QPointF(x0 + gap_oeste, y0 + bh - gap_sur))
        if self.esquinas.get("frente_derecha") == "inglete_45" and (self.activos["frente"] or self.activos["derecha"]):
            p.drawLine(QtCore.QPointF(x0 + bw, y0 + bh), QtCore.QPointF(x0 + bw - gap_este, y0 + bh - gap_sur))
