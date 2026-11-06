"""Canvas 2D de seccion transversal del chasis. Parte de ui/chassis_widget.py (M7, D-45)."""

from freecad.vdo.qt_compat import QtCore, QtGui, QtWidgets


# ----------------------------------------------------------------------
# Canvas 2D de Sección Transversal
# ----------------------------------------------------------------------
class _VDOChassisCrossSectionCanvas(QtWidgets.QWidget):
    """
    Lienzo gráfico interactivo que renderiza el corte transversal 2D del chasis.
    Muestra en tiempo real:
      - Canto y espesor de las 4 caras (Activas en color sólido o Ausentes en línea punteada).
      - Cortes exactos en las 4 esquinas según el tipo de encuentro (tapa pasa, lateral pasa, inglete 45°).
      - Visualización del fondo trasero (canal de ranura, rebaje de galce o vacío abierto).
      - Estructura de anclaje inferior (zócalo retranqueado, herrajes suspendidos o patas regulables).
    """

    faceClicked = QtCore.Signal(str)
    cornerClicked = QtCore.Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(160, 130)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.setCursor(QtCore.Qt.PointingHandCursor)

        self._caras = {
            "superior": {"activa": True, "tipo": "estructural"},
            "inferior": {"activa": True, "tipo": "estructural"},
            "izquierda": {"activa": True, "tipo": "estructural"},
            "derecha": {"activa": True, "tipo": "estructural"},
            "fondo": {"activa": True, "tipo": "ranurado_5mm"},
        }
        self._encuentros = {
            "superior_izq": "tapa_domina",
            "superior_der": "tapa_domina",
            "inferior_izq": "lateral_domina",
            "inferior_der": "lateral_domina",
        }
        self._base = {
            "estrategia": "zocalo",
            "altura": 100.0,
            "separacion_frente": 50.0,
        }

        self._hover_target = None
        self.setMouseTracking(True)

    def update_state(self, caras, encuentros, base):
        self._caras = caras
        self._encuentros = encuentros
        self._base = base
        self.update()

    def paintEvent(self, event):
        p = QtGui.QPainter(self)
        p.setRenderHint(QtGui.QPainter.Antialiasing)

        # Fondo general del canvas
        rect = self.rect()
        self._pintar_fondo(p, rect)
        margin_x = 20
        margin_top = 16
        margin_bottom = 26  # Espacio para zócalo/patas
        w = self.width() - (2 * margin_x)
        h = self.height() - margin_top - margin_bottom

        if w < 60 or h < 50:
            p.end()
            return

        x0 = margin_x
        y0 = margin_top
        T = 12  # Espesor gráfico del tablero en píxeles
        self._pintar_cavidad(p, x0, y0, w, h, T)
        self._pintar_base(p, x0, y0, w, h)
        caras = self._caras
        enc = self._encuentros

        color_activa = QtGui.QColor("#2f353d")
        border_activa = QtGui.QColor("#007acc")
        color_ausente = QtGui.QColor("#1c1c1c")
        border_ausente = QtGui.QColor("#444444")

        # Configuración de límites por encuentro
        # Superior:
        sup_x1 = x0 if enc["superior_izq"] in ("tapa_domina", "inglete_45") else x0 + T
        sup_x2 = x0 + w if enc["superior_der"] in ("tapa_domina", "inglete_45") else x0 + w - T
        sup_y = y0

        # Inferior:
        inf_x1 = x0 if enc["inferior_izq"] in ("tapa_domina", "inglete_45") else x0 + T
        inf_x2 = x0 + w if enc["inferior_der"] in ("tapa_domina", "inglete_45") else x0 + w - T
        inf_y = y0 + h - T

        # Izquierda:
        izq_y1 = y0 if enc["superior_izq"] in ("lateral_domina", "inglete_45") else y0 + T
        izq_y2 = y0 + h if enc["inferior_izq"] in ("lateral_domina", "inglete_45") else y0 + h - T
        izq_x = x0

        # Derecha:
        der_y1 = y0 if enc["superior_der"] in ("lateral_domina", "inglete_45") else y0 + T
        der_y2 = y0 + h if enc["inferior_der"] in ("lateral_domina", "inglete_45") else y0 + h - T
        der_x = x0 + w - T
        self._pintar_caras_horizontales(p, caras, color_activa, border_activa, color_ausente, border_ausente, sup_x1, sup_x2, sup_y, inf_x1, inf_x2, inf_y, T)
        self._pintar_caras_verticales(p, caras, color_activa, border_activa, color_ausente, border_ausente, izq_x, izq_y1, izq_y2, der_x, der_y1, der_y2, T)
        self._pintar_inglete(p, caras, enc, x0, y0, w, h, T)
        p.end()

    def _pintar_fondo(self, p, rect):
        p.fillRect(rect, QtGui.QColor("#181818"))
        p.setPen(QtGui.QPen(QtGui.QColor("#262626"), 1))
        p.drawRoundedRect(rect.adjusted(1, 1, -1, -1), 6, 6)

    def _pintar_cavidad(self, p, x0, y0, w, h, T):
        cavidad_rect = QtCore.QRectF(x0 + T, y0 + T, w - (2 * T), h - (2 * T))
        p.fillRect(cavidad_rect, QtGui.QColor("#1f1f1f"))

        tipo_fondo = self._caras["fondo"].get("tipo", "ranurado_5mm")
        activa_fondo = self._caras["fondo"].get("activa", True)

        if activa_fondo and tipo_fondo != "abierto":
            if "ranurado" in tipo_fondo:
                # Línea cian discontinua representando canal fresado
                pen_ranura = QtGui.QPen(QtGui.QColor("#00d4ff"), 1.5, QtCore.Qt.DashLine)
                p.setPen(pen_ranura)
                # Canal a 8px del borde exterior
                inset = 6
                p.drawRect(QtCore.QRectF(x0 + inset, y0 + inset, w - 2 * inset, h - 2 * inset))
            elif tipo_fondo == "galce":
                # Rebaje escalonado perimetral ámbar
                pen_galce = QtGui.QPen(QtGui.QColor("#ffaa00"), 1.5, QtCore.Qt.DotLine)
                p.setPen(pen_galce)
                p.drawRect(QtCore.QRectF(x0 + 4, y0 + 4, w - 8, h - 8))
            elif tipo_fondo == "atornillado":
                # Tapa posterior sólida completa con tornillos verdes en esquinas
                p.fillRect(cavidad_rect.adjusted(2, 2, -2, -2), QtGui.QColor("#24272b"))
                p.setPen(QtCore.Qt.NoPen)
                p.setBrush(QtGui.QColor("#28a745"))
                p.drawEllipse(QtCore.QPointF(cavidad_rect.left() + 8, cavidad_rect.top() + 8), 2.5, 2.5)
                p.drawEllipse(QtCore.QPointF(cavidad_rect.right() - 8, cavidad_rect.top() + 8), 2.5, 2.5)
                p.drawEllipse(QtCore.QPointF(cavidad_rect.left() + 8, cavidad_rect.bottom() - 8), 2.5, 2.5)
                p.drawEllipse(QtCore.QPointF(cavidad_rect.right() - 8, cavidad_rect.bottom() - 8), 2.5, 2.5)
        else:
            # Abierto: rayitas de vacío diagonal suave
            p.setPen(QtGui.QPen(QtGui.QColor("#2a2a2a"), 1, QtCore.Qt.DotLine))
            p.drawLine(cavidad_rect.topLeft(), cavidad_rect.bottomRight())
            p.drawLine(cavidad_rect.bottomLeft(), cavidad_rect.topRight())

    def _pintar_base(self, p, x0, y0, w, h):
        # -------------------------------------------------------------
        # 2. Dibujar Estructura de Apoyo Inferior (Base / Anclaje)
        # -------------------------------------------------------------
        estrategia_base = self._base.get("estrategia", "zocalo")
        y_piso = y0 + h + 24

        # Línea de piso de taller
        pen_piso = QtGui.QPen(QtGui.QColor("#444444"), 1, QtCore.Qt.DashLine)
        p.setPen(pen_piso)
        p.drawLine(x0 - 15, int(y_piso), x0 + w + 15, int(y_piso))
        p.setPen(QtGui.QColor("#777777"))
        p.setFont(QtGui.QFont("SansSerif", 7))
        p.drawText(x0 - 15, int(y_piso) + 10, "PISO")

        if estrategia_base == "zocalo":
            # Zócalo de taller: bloque central retranqueado
            z_offset = 12  # Retranqueo visual
            z_w = w - (2 * z_offset)
            z_h = y_piso - (y0 + h)
            rect_zocalo = QtCore.QRectF(x0 + z_offset, y0 + h, z_w, z_h)
            p.fillRect(rect_zocalo, QtGui.QColor("#2b2b2b"))
            p.setPen(QtGui.QPen(QtGui.QColor("#007acc"), 1.5))
            p.drawRect(rect_zocalo)
            p.setPen(QtGui.QColor("#00d4ff"))
            p.drawText(rect_zocalo, QtCore.Qt.AlignCenter, "ZÓCALO")

        elif estrategia_base == "patas":
            # Dos patas regulables
            pata_w = 6
            pata_h = y_piso - (y0 + h)
            pata_x1 = x0 + 16
            pata_x2 = x0 + w - 16 - pata_w
            # Pata izquierda
            p.fillRect(QtCore.QRectF(pata_x1, y0 + h, pata_w, pata_h), QtGui.QColor("#007acc"))
            p.fillRect(QtCore.QRectF(pata_x1 - 4, y_piso - 3, pata_w + 8, 3), QtGui.QColor("#007acc"))
            # Pata derecha
            p.fillRect(QtCore.QRectF(pata_x2, y0 + h, pata_w, pata_h), QtGui.QColor("#007acc"))
            p.fillRect(QtCore.QRectF(pata_x2 - 4, y_piso - 3, pata_w + 8, 3), QtGui.QColor("#007acc"))

        elif estrategia_base == "suspendido":
            # Módulo flotando; soportes laterales en pared
            pen_muro = QtGui.QPen(QtGui.QColor("#ffaa00"), 3)
            p.setPen(pen_muro)
            p.drawLine(x0 - 4, y0 + 10, x0 - 4, y0 + 40)
            p.setPen(QtGui.QColor("#ffaa00"))
            p.drawText(x0 - 25, y0 + 28, "🧗")

    def _pintar_caras_horizontales(self, p, caras, color_activa, border_activa, color_ausente, border_ausente, sup_x1, sup_x2, sup_y, inf_x1, inf_x2, inf_y, T):
        # A. Cara Superior
        rect_sup = QtCore.QRectF(sup_x1, sup_y, sup_x2 - sup_x1, T)
        if caras["superior"]["activa"]:
            p.fillRect(rect_sup, color_activa)
            p.setPen(QtGui.QPen(border_activa, 1.5))
            p.drawRect(rect_sup)
        else:
            p.fillRect(rect_sup, color_ausente)
            p.setPen(QtGui.QPen(border_ausente, 1, QtCore.Qt.DashLine))
            p.drawRect(rect_sup)
            p.setPen(QtGui.QColor("#666666"))
            p.drawText(rect_sup, QtCore.Qt.AlignCenter, "TAPA AUSENTE")

        # B. Cara Inferior
        rect_inf = QtCore.QRectF(inf_x1, inf_y, inf_x2 - inf_x1, T)
        if caras["inferior"]["activa"]:
            p.fillRect(rect_inf, color_activa)
            p.setPen(QtGui.QPen(border_activa, 1.5))
            p.drawRect(rect_inf)
        else:
            p.fillRect(rect_inf, color_ausente)
            p.setPen(QtGui.QPen(border_ausente, 1, QtCore.Qt.DashLine))
            p.drawRect(rect_inf)
            p.setPen(QtGui.QColor("#666666"))
            p.drawText(rect_inf, QtCore.Qt.AlignCenter, "BASE AUSENTE")

    def _pintar_caras_verticales(self, p, caras, color_activa, border_activa, color_ausente, border_ausente, izq_x, izq_y1, izq_y2, der_x, der_y1, der_y2, T):
        # C. Lateral Izquierdo
        rect_izq = QtCore.QRectF(izq_x, izq_y1, T, izq_y2 - izq_y1)
        if caras["izquierda"]["activa"]:
            p.fillRect(rect_izq, color_activa)
            p.setPen(QtGui.QPen(border_activa, 1.5))
            p.drawRect(rect_izq)
        else:
            p.fillRect(rect_izq, color_ausente)
            p.setPen(QtGui.QPen(border_ausente, 1, QtCore.Qt.DashLine))
            p.drawRect(rect_izq)

        # D. Lateral Derecho
        rect_der = QtCore.QRectF(der_x, der_y1, T, der_y2 - der_y1)
        if caras["derecha"]["activa"]:
            p.fillRect(rect_der, color_activa)
            p.setPen(QtGui.QPen(border_activa, 1.5))
            p.drawRect(rect_der)
        else:
            p.fillRect(rect_der, color_ausente)
            p.setPen(QtGui.QPen(border_ausente, 1, QtCore.Qt.DashLine))
            p.drawRect(rect_der)

    def _pintar_inglete(self, p, caras, enc, x0, y0, w, h, T):
        # -------------------------------------------------------------
        # 4. Líneas Diagonales de Inglete 45°
        # -------------------------------------------------------------
        pen_inglete = QtGui.QPen(QtGui.QColor("#00d4ff"), 2)
        if enc["superior_izq"] == "inglete_45" and caras["superior"]["activa"] and caras["izquierda"]["activa"]:
            p.setPen(pen_inglete)
            p.drawLine(QtCore.QPointF(x0, y0), QtCore.QPointF(x0 + T, y0 + T))

        if enc["superior_der"] == "inglete_45" and caras["superior"]["activa"] and caras["derecha"]["activa"]:
            p.setPen(pen_inglete)
            p.drawLine(QtCore.QPointF(x0 + w, y0), QtCore.QPointF(x0 + w - T, y0 + T))

        if enc["inferior_izq"] == "inglete_45" and caras["inferior"]["activa"] and caras["izquierda"]["activa"]:
            p.setPen(pen_inglete)
            p.drawLine(QtCore.QPointF(x0, y0 + h), QtCore.QPointF(x0 + T, y0 + h - T))

        if enc["inferior_der"] == "inglete_45" and caras["inferior"]["activa"] and caras["derecha"]["activa"]:
            p.setPen(pen_inglete)
            p.drawLine(QtCore.QPointF(x0 + w, y0 + h), QtCore.QPointF(x0 + w - T, y0 + h - T))


    def mousePressEvent(self, event):
        x = event.pos().x()
        y = event.pos().y()

        margin_x = 20
        margin_top = 16
        margin_bottom = 26
        w = self.width() - (2 * margin_x)
        h = self.height() - margin_top - margin_bottom
        x0 = margin_x
        y0 = margin_top
        T = 12

        # Zonas de clic para las caras
        if y0 <= y <= y0 + T and x0 <= x <= x0 + w:
            self.faceClicked.emit("superior")
            return
        if y0 + h - T <= y <= y0 + h and x0 <= x <= x0 + w:
            self.faceClicked.emit("inferior")
            return
        if x0 <= x <= x0 + T and y0 <= y <= y0 + h:
            self.faceClicked.emit("izquierda")
            return
        if x0 + w - T <= x <= x0 + w and y0 <= y <= y0 + h:
            self.faceClicked.emit("derecha")
            return

        # Clic en el centro (fondo)
        if x0 + T < x < x0 + w - T and y0 + T < y < y0 + h - T:
            self.faceClicked.emit("fondo")
            return

        super().mousePressEvent(event)