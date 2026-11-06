"""Cabecera del inspector: migas de pan y micro-cabecera de dimensiones."""

from freecad.vdo.qt_compat import QtCore, QtGui, QtWidgets
from freecad.vdo.ui.vdo_selection_bridge import VDOSelectionBridge
from freecad.vdo.ui.vdo_qt import VDO_DoubleSpinBox
from freecad.vdo.ui.inspector_paginas import PAGE_CHASIS, PAGE_CIERRE, PAGE_PIEZA, PAGE_VANO
from freecad.vdo.ui import tema


# tipo de destino -> (ruta del breadcrumb, clave activa)
_RUTA_BREADCRUMB_DEFECTO = ((("Mueble", "mueble"),), "mueble")
_RUTA_BREADCRUMB_POR_TARGET = {
    VDOSelectionBridge.TARGET_COCO: (
        (("Mueble", "mueble"), ("Chasis L2", "chasis")), "chasis"),
    getattr(VDOSelectionBridge, "TARGET_VANO", "VANO"): (
        (("Mueble", "mueble"), ("Vano L0", "vano")), "vano"),
    "VANO": (
        (("Mueble", "mueble"), ("Vano L0", "vano")), "vano"),
    VDOSelectionBridge.TARGET_PANEL: (
        (("Mueble", "mueble"), ("Pieza L1", "pieza")), "pieza"),
    VDOSelectionBridge.TARGET_CAJON: (
        (("Mueble", "mueble"), ("Cierre / Herraje", "cierre")), "cierre"),
    VDOSelectionBridge.TARGET_PUERTA: (
        (("Mueble", "mueble"), ("Cierre / Herraje", "cierre")), "cierre"),
    VDOSelectionBridge.TARGET_ZOCALO: (
        (("Mueble", "mueble"), ("Cierre / Herraje", "cierre")), "cierre"),
}
# clave del breadcrumb -> (pagina, tipo de destino) para _ir_a_nivel
_CLAVE_BREADCRUMB_A_NIVEL = {
    "mueble": (PAGE_CHASIS, VDOSelectionBridge.TARGET_COCO),
    "chasis": (PAGE_CHASIS, VDOSelectionBridge.TARGET_COCO),
    "vano": (PAGE_VANO, getattr(VDOSelectionBridge, "TARGET_VANO", "VANO")),
    "pieza": (PAGE_PIEZA, VDOSelectionBridge.TARGET_PANEL),
    "cierre": (PAGE_CIERRE, VDOSelectionBridge.TARGET_CAJON),
}


# ----------------------------------------------------------------------
# Barra de Migas de Pan (Breadcrumbs)
# ----------------------------------------------------------------------
class _BreadcrumbBar(QtWidgets.QWidget):
    """Barra superior con eslabones interactivos para regresar a un nivel."""

    sigNivelClickeado = QtCore.Signal(str)  # emite el nombre del nivel

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("VDOBreadcrumbBar")
        self.setFixedHeight(30)
        self._niveles = []
        self._nivel_activo = None

        self.layout = QtWidgets.QHBoxLayout(self)
        self.layout.setContentsMargins(8, 2, 8, 2)
        self.layout.setSpacing(4)

        self.lbl_inicio = QtWidgets.QLabel("🏠 Mueble")
        self.lbl_inicio.setObjectName("lblBreadcrumbRoot")
        self.lbl_inicio.setCursor(QtCore.Qt.PointingHandCursor)
        tema.aplicar_estilo(self.lbl_inicio, tema.ESTILO_BREADCRUMB_RAIZ)
        self.lbl_inicio.mousePressEvent = lambda _e: self.sigNivelClickeado.emit("mueble")
        self.layout.addWidget(self.lbl_inicio)

        self.layout.addStretch()

    def set_ruta(self, niveles, activo=None):
        """niveles: lista de (label, clave). Activo: clave del nivel actual."""
        while self.layout.count() > 2:
            item = self.layout.takeAt(1)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        self._niveles = list(niveles)
        self._nivel_activo = activo

        for label, clave in niveles:
            sep = QtWidgets.QLabel(" › ")
            tema.aplicar_estilo(sep, tema.ESTILO_SEPARADOR)
            self.layout.insertWidget(self.layout.count() - 1, sep)

            lbl = QtWidgets.QLabel(label)
            lbl.setObjectName(f"lblBreadcrumb_{clave}")
            lbl.setCursor(QtCore.Qt.PointingHandCursor)
            activo_es = (clave == activo)
            tema.aplicar_estilo(lbl, tema.estilo_breadcrumb(clave, activo_es))
            lbl.mousePressEvent = (
                lambda _e, c=clave: self.sigNivelClickeado.emit(c))
            self.layout.insertWidget(self.layout.count() - 1, lbl)

    def limpiar(self):
        self.set_ruta([], activo=None)


# ----------------------------------------------------------------------
# Micro-Header Editable de Alta Densidad
# ----------------------------------------------------------------------
class _MicroHeaderWidget(QtWidgets.QFrame):
    """
    Micro-Header editable de una sola línea según la Ley de Tufte:
    📐 [ 600 W ] × [ 720 H ] × [ 580 D ] mm  │  Esp: [ 18 ] mm
    """

    sigDimensionesCambiadas = QtCore.Signal(float, float, float, float)  # (w, h, d, e)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._estilizar()
        layout = self._crear_layout()
        self._crear_icono(layout)
        self._crear_medidas(layout)
        self._crear_espesor(layout)
        layout.addStretch()
        self._conectar_senales()

    def _estilizar(self):
        self.setObjectName("VDOMicroHeader")
        self.setFixedHeight(30)
        tema.aplicar_estilo(self, tema.ESTILO_MICRO_HEADER)

    def _crear_layout(self):
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(6, 2, 6, 2)
        layout.setSpacing(4)
        return layout

    def _crear_icono(self, layout):
        icon_lbl = QtWidgets.QLabel("📐")
        tema.aplicar_estilo(icon_lbl, tema.ESTILO_TEXTO_11PX)
        layout.addWidget(icon_lbl)

    def _crear_medidas(self, layout):
        # Ancho (W)
        self.spin_w = VDO_DoubleSpinBox()
        self.spin_w.setDecimals(1)
        self.spin_w.setRange(50.0, 5000.0)
        self.spin_w.setValue(600.0)
        self.spin_w.setSuffix(" W")
        self.spin_w.setFixedWidth(64)
        layout.addWidget(self.spin_w)

        layout.addWidget(QtWidgets.QLabel("×"))

        # Alto (H)
        self.spin_h = VDO_DoubleSpinBox()
        self.spin_h.setDecimals(1)
        self.spin_h.setRange(50.0, 5000.0)
        self.spin_h.setValue(720.0)
        self.spin_h.setSuffix(" H")
        self.spin_h.setFixedWidth(64)
        layout.addWidget(self.spin_h)

        layout.addWidget(QtWidgets.QLabel("×"))

        # Fondo (D)
        self.spin_d = VDO_DoubleSpinBox()
        self.spin_d.setDecimals(1)
        self.spin_d.setRange(50.0, 5000.0)
        self.spin_d.setValue(580.0)
        self.spin_d.setSuffix(" D")
        self.spin_d.setFixedWidth(64)
        layout.addWidget(self.spin_d)

    def _crear_espesor(self, layout):
        lbl_sep = QtWidgets.QLabel("mm │ Esp:")
        layout.addWidget(lbl_sep)

        # Espesor (E)
        self.spin_e = VDO_DoubleSpinBox()
        self.spin_e.setDecimals(1)
        self.spin_e.setRange(3.0, 100.0)
        self.spin_e.setValue(18.0)
        self.spin_e.setSuffix(" mm")
        self.spin_e.setFixedWidth(60)
        layout.addWidget(self.spin_e)

    def _conectar_senales(self):
        self._bloqueo_signals = False
        self.spin_w.editingFinished.connect(self._on_edited)
        self.spin_h.editingFinished.connect(self._on_edited)
        self.spin_d.editingFinished.connect(self._on_edited)
        self.spin_e.editingFinished.connect(self._on_edited)

    def cargar_dimensiones(self, w, h, d, e):
        self._bloqueo_signals = True
        if w is not None and w > 0:
            self.spin_w.setValue(float(w))
        if h is not None and h > 0:
            self.spin_h.setValue(float(h))
        if d is not None and d > 0:
            self.spin_d.setValue(float(d))
        if e is not None and e > 0:
            self.spin_e.setValue(float(e))
        self._bloqueo_signals = False

    def _on_edited(self):
        if self._bloqueo_signals:
            return
        w = float(self.spin_w.value())
        h = float(self.spin_h.value())
        d = float(self.spin_d.value())
        e = float(self.spin_e.value())
        self.sigDimensionesCambiadas.emit(w, h, d, e)
