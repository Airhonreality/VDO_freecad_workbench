# =====================================================================
# vdo_universal_inspector.py
# Inspector Universal Reactivo Consolidado — Sistema VDO (FreeCAD).
#
# Panel unificado permanente lateral con:
# 1. Micro-Header editable de alta densidad:
#    📐 [ W ] × [ H ] × [ D ] mm │ Espesor: [ E ] mm
# 2. Visor 2D frontal en elevación completa (CocoPreview2D)
# 3. QSplitter horizontal inferior que aloja:
#    - Izquierda: QTreeWidget Maestro unificado (Chasis, Piezas, Vanos e Insertos)
#    - Derecha: QStackedWidget reactivo (Páginas Chasis, Vano, Pieza y Cierre)
#
# Sincronización bidireccional total entre 3D, 2D, Árbol y Páginas.
# =====================================================================

import json
import os
if os.environ.get("QT_QPA_PLATFORM") is None:
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
import FreeCAD as App
from freecad.vdo.qt_compat import QtCore, QtGui, QtWidgets
try:
    import FreeCADGui as Gui
except ImportError:  # pragma: no cover
    Gui = None
from freecad.vdo.ui.vdo_selection_bridge import VDOSelectionBridge
try:
    from freecad.vdo.ui.vdo_box_controller import VDOBoxControllerWidget
except ImportError:  # pragma: no cover
    VDOBoxControllerWidget = None
try:
    from freecad.vdo.ui.vdo_coco_preview2d import CocoPreview2D
except ImportError:  # pragma: no cover
    CocoPreview2D = None
try:
    from freecad.vdo.core.vdo_layout_matriz import Layout
    from freecad.vdo.core.vdo_layout_modelo import cavidad_interior
    from freecad.vdo.core.vdo_layout_resolucion import resolve_layout
except ImportError:  # pragma: no cover
    Layout = None
    resolve_layout = None
    cavidad_interior = None
from freecad.vdo.cad.documento import recalcular
from freecad.vdo.cad.propiedades import anadir_propiedad_texto, asignar_propiedades
from freecad.vdo.core import vdo_hardware_hub as HH
from freecad.vdo.datos.valores import BLUM_TANDEM, OCULTA
from freecad.vdo.ui.vdo_qt import VDO_DoubleSpinBox
from freecad.vdo.ui.inspector_paginas import (
    PAGE_CHASIS,
    PAGE_CIERRE,
    PAGE_PIEZA,
    PAGE_VANO,
    PaginaChasis,
    PaginaCierre,
    _PaginaBase,
    _TARGET_TO_PAGE,
    _float_seguro,
    _str_seguro,
)


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
        self.lbl_inicio.setStyleSheet(
            "QLabel#lblBreadcrumbRoot { color: #007acc; font-weight: bold; font-size: 11px; }")
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
            sep.setStyleSheet("color: #666666; font-size: 10px;")
            self.layout.insertWidget(self.layout.count() - 1, sep)

            lbl = QtWidgets.QLabel(label)
            lbl.setObjectName(f"lblBreadcrumb_{clave}")
            lbl.setCursor(QtCore.Qt.PointingHandCursor)
            activo_es = (clave == activo)
            lbl.setStyleSheet(
                f"QLabel#lblBreadcrumb_{clave} {{ "
                f"color: {'#ffffff' if activo_es else '#aaaaaa'}; "
                f"font-weight: {'bold' if activo_es else 'normal'}; "
                f"font-size: 10px; }}"
            )
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
        self.setObjectName("VDOMicroHeader")
        self.setFixedHeight(30)
        self.setStyleSheet("""
            QFrame#VDOMicroHeader {
                background-color: #1e1e1e;
                border-top: 1px solid #2d2d2d;
                border-bottom: 1px solid #2d2d2d;
                padding: 1px 4px;
            }
            QLabel {
                color: #888888;
                font-size: 10px;
                font-weight: bold;
            }
            QDoubleSpinBox {
                background-color: #282828;
                color: #00d4ff;
                border: 1px solid #3d3d3d;
                border-radius: 3px;
                padding: 1px 2px;
                font-size: 10px;
                font-weight: bold;
            }
            QDoubleSpinBox:focus {
                border-color: #007acc;
                background-color: #333333;
            }
        """)

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(6, 2, 6, 2)
        layout.setSpacing(4)

        icon_lbl = QtWidgets.QLabel("📐")
        icon_lbl.setStyleSheet("font-size: 11px;")
        layout.addWidget(icon_lbl)

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

        layout.addStretch()

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


# ----------------------------------------------------------------------
# PÁGINA 1: VANO L0 (Luz Neta y Dock Táctil de Habitantes)
# ----------------------------------------------------------------------
class PaginaVano(_PaginaBase):
    """Nivel Vano Libre (L0): Luz neta y Dock táctil de habitantes."""

    sigHabitanteCambiado = QtCore.Signal(str, dict)  # (tipo_habitante, configuracion)

    def __init__(self, parent=None):
        super().__init__("Vano Libre / Cavidad Útil (L0)", parent)
        self._obj_actual = None
        self._luz = {"w": 564.0, "h": 280.0, "d": 550.0}
        self._celda_actual = "(x1, y1)"

        # Etiquetas retrocompatibles de datos
        self.lbl_luz_w = self._add_dato("Luz neta W", "—")
        self.lbl_luz_h = self._add_dato("Luz neta H", "—")
        self.lbl_luz_d = self._add_dato("Luz neta D", "—")
        self.lbl_subdiv = self._add_dato("Subdivisión", "—")

        # -------------------------------------------------------------
        # Banner de Luz Libre Real
        # -------------------------------------------------------------
        self.banner_luz = QtWidgets.QFrame()
        self.banner_luz.setStyleSheet(
            "QFrame { background-color: #22252a; border: 1px solid #007acc; "
            "border-radius: 4px; padding: 3px; }")
        lay_b = QtWidgets.QHBoxLayout(self.banner_luz)
        lay_b.setContentsMargins(6, 3, 6, 3)

        self.lbl_luz_banner = QtWidgets.QLabel("📐 <b>LUZ LIBRE NETA:</b> 564 × 280 × 550 mm")
        self.lbl_luz_banner.setStyleSheet("color: #00d4ff; font-size: 10px;")
        lay_b.addWidget(self.lbl_luz_banner)
        self.contenedor_datos.addWidget(self.banner_luz)

        # -------------------------------------------------------------
        # Dock Táctil de Habitantes (4 Acciones)
        # -------------------------------------------------------------
        lbl_dock = QtWidgets.QLabel("HABITANTE DEL VANO:")
        lbl_dock.setStyleSheet("color: #888888; font-size: 9px; font-weight: bold; margin-top: 4px;")
        self.contenedor_datos.addWidget(lbl_dock)

        fila_dock = QtWidgets.QHBoxLayout()
        fila_dock.setSpacing(3)

        self.btn_dock = {}
        habitantes_spec = [
            ("subdividir", "➗ Subdiv", "Subdividir el vano con vdo_layout"),
            ("cajon", "🗄 Cajón", "Insertar torre de cajones y rieles"),
            ("puerta", "🚪 Puerta", "Insertar puerta batiente, basculante o corrediza"),
            ("vacio", "🔲 Vacío", "Restaurar vano libre sin insertos"),
        ]
        for key, text, tip in habitantes_spec:
            btn = QtWidgets.QPushButton(text)
            btn.setCheckable(True)
            btn.setToolTip(tip)
            btn.setFixedHeight(26)
            btn.setCursor(QtCore.Qt.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #282828;
                    border: 1px solid #3d3d3d;
                    border-radius: 4px;
                    font-size: 9px;
                    color: #cccccc;
                    padding: 2px 4px;
                }
                QPushButton:checked {
                    background-color: #007acc;
                    border-color: #007acc;
                    color: #ffffff;
                    font-weight: bold;
                }
                QPushButton:hover:!checked {
                    background-color: #333333;
                    color: #ffffff;
                }
            """)
            btn.clicked.connect(lambda _, k=key: self._on_dock_clicked(k))
            fila_dock.addWidget(btn)
            self.btn_dock[key] = btn

        self.btn_dock["vacio"].setChecked(True)
        self.contenedor_datos.addLayout(fila_dock)

        # -------------------------------------------------------------
        # Sub-paneles Contextuales del Dock
        # -------------------------------------------------------------
        self.stack_dock = QtWidgets.QStackedWidget()
        self.stack_dock.setStyleSheet("background-color: #1a1a1a; border-radius: 4px;")

        # 0. Subdividir
        panel_subdiv = QtWidgets.QWidget()
        lay_sub = QtWidgets.QVBoxLayout(panel_subdiv)
        lay_sub.setContentsMargins(6, 6, 6, 6)
        lay_sub.setSpacing(4)

        f_eje = QtWidgets.QHBoxLayout()
        f_eje.addWidget(QtWidgets.QLabel("Eje:"))
        self.combo_eje = QtWidgets.QComboBox()
        self.combo_eje.addItems(["Horizontal (Repisas en Y)", "Vertical (Montantes en X)"])
        f_eje.addWidget(self.combo_eje, 1)
        lay_sub.addLayout(f_eje)

        f_n = QtWidgets.QHBoxLayout()
        f_n.addWidget(QtWidgets.QLabel("Partes:"))
        self.spin_n_partes = QtWidgets.QSpinBox()
        self.spin_n_partes.setRange(2, 8)
        self.spin_n_partes.setValue(2)
        f_n.addWidget(self.spin_n_partes, 1)
        lay_sub.addLayout(f_n)

        f_modo = QtWidgets.QHBoxLayout()
        f_modo.addWidget(QtWidgets.QLabel("Modo:"))
        self.combo_dist = QtWidgets.QComboBox()
        self.combo_dist.addItems(["Equitativo (1/N)", "Medida fija"])
        f_modo.addWidget(self.combo_dist, 1)
        lay_sub.addLayout(f_modo)

        btn_ap_sub = QtWidgets.QPushButton("➗ Aplicar Subdivisión")
        btn_ap_sub.setStyleSheet("background-color: #007acc; color: white; font-weight: bold; padding: 4px; font-size: 10px;")
        btn_ap_sub.clicked.connect(self._aplicar_subdivision)
        lay_sub.addWidget(btn_ap_sub)
        self.stack_dock.addWidget(panel_subdiv)

        # 1. Cajón
        panel_cajon = QtWidgets.QWidget()
        lay_caj = QtWidgets.QVBoxLayout(panel_cajon)
        lay_caj.setContentsMargins(6, 6, 6, 6)
        lay_caj.setSpacing(4)

        f_nc = QtWidgets.QHBoxLayout()
        f_nc.addWidget(QtWidgets.QLabel("Cajones:"))
        self.spin_cajones = QtWidgets.QSpinBox()
        self.spin_cajones.setRange(1, 4)
        self.spin_cajones.setValue(1)
        f_nc.addWidget(self.spin_cajones, 1)
        lay_caj.addLayout(f_nc)

        f_cor = QtWidgets.QHBoxLayout()
        f_cor.addWidget(QtWidgets.QLabel("Corredera:"))
        self.combo_corredera = QtWidgets.QComboBox()
        self.combo_corredera.addItems(["Oculta Blum Tandem", "Telescópica 45mm"])
        f_cor.addWidget(self.combo_corredera, 1)
        lay_caj.addLayout(f_cor)

        f_ag_caj = QtWidgets.QHBoxLayout()
        f_ag_caj.addWidget(QtWidgets.QLabel("Frente:"))
        self.combo_agarre_caj = QtWidgets.QComboBox()
        self.combo_agarre_caj.addItems(["Tirador", "Perfil Gola", "Chaflán 45°"])
        f_ag_caj.addWidget(self.combo_agarre_caj, 1)
        lay_caj.addLayout(f_ag_caj)

        self.lbl_cajon_hub = QtWidgets.QLabel("SKU: BLUM-TANDEM · Blum · $12.50 USD")
        self.lbl_cajon_hub.setStyleSheet("color: #28a745; font-size: 9px;")
        lay_caj.addWidget(self.lbl_cajon_hub)

        btn_ap_caj = QtWidgets.QPushButton("🗄 Insertar Cajón")
        btn_ap_caj.setStyleSheet("background-color: #007acc; color: white; font-weight: bold; padding: 4px; font-size: 10px;")
        btn_ap_caj.clicked.connect(self._aplicar_cajon)
        lay_caj.addWidget(btn_ap_caj)
        self.stack_dock.addWidget(panel_cajon)

        # 2. Puerta
        panel_puerta = QtWidgets.QWidget()
        lay_pue = QtWidgets.QVBoxLayout(panel_puerta)
        lay_pue.setContentsMargins(6, 6, 6, 6)
        lay_pue.setSpacing(4)

        f_sis = QtWidgets.QHBoxLayout()
        f_sis.addWidget(QtWidgets.QLabel("Sistema:"))
        self.combo_sistema_pue = QtWidgets.QComboBox()
        self.combo_sistema_pue.addItems(["Batiente (Cazoleta 35mm)", "Basculante (Pistón)", "Corrediza (Ducasse)"])
        f_sis.addWidget(self.combo_sistema_pue, 1)
        lay_pue.addLayout(f_sis)

        f_sen = QtWidgets.QHBoxLayout()
        f_sen.addWidget(QtWidgets.QLabel("Sentido:"))
        self.combo_sentido_pue = QtWidgets.QComboBox()
        self.combo_sentido_pue.addItems(["Izquierda", "Derecha", "Doble Hoja"])
        f_sen.addWidget(self.combo_sentido_pue, 1)
        lay_pue.addLayout(f_sen)

        f_ag_pue = QtWidgets.QHBoxLayout()
        f_ag_pue.addWidget(QtWidgets.QLabel("Agarre:"))
        self.combo_agarre_pue = QtWidgets.QComboBox()
        self.combo_agarre_pue.addItems(["Tirador", "Perfil Gola", "Bisel 45°", "Push-to-open"])
        f_ag_pue.addWidget(self.combo_agarre_pue, 1)
        lay_pue.addLayout(f_ag_pue)

        self.lbl_puerta_hub = QtWidgets.QLabel("Bisagras Cazoleta 35mm Cierre Suave (Parche)")
        self.lbl_puerta_hub.setStyleSheet("color: #28a745; font-size: 9px;")
        lay_pue.addWidget(self.lbl_puerta_hub)

        btn_ap_pue = QtWidgets.QPushButton("🚪 Insertar Puerta")
        btn_ap_pue.setStyleSheet("background-color: #007acc; color: white; font-weight: bold; padding: 4px; font-size: 10px;")
        btn_ap_pue.clicked.connect(self._aplicar_puerta)
        lay_pue.addWidget(btn_ap_pue)
        self.stack_dock.addWidget(panel_puerta)

        # 3. Vacío
        panel_vacio = QtWidgets.QWidget()
        lay_vac = QtWidgets.QVBoxLayout(panel_vacio)
        lay_vac.setContentsMargins(6, 6, 6, 6)
        lbl_v = QtWidgets.QLabel("🔲 Vano libre de almacenamiento útil")
        lbl_v.setStyleSheet("color: #888888; font-size: 9px;")
        lay_vac.addWidget(lbl_v)
        btn_ap_vac = QtWidgets.QPushButton("Restaurar Vacío")
        btn_ap_vac.setStyleSheet("background-color: #333333; color: #cccccc; padding: 4px; font-size: 10px;")
        btn_ap_vac.clicked.connect(self._aplicar_vacio)
        lay_vac.addWidget(btn_ap_vac)
        self.stack_dock.addWidget(panel_vacio)

        self.stack_dock.setCurrentIndex(3)
        self.contenedor_datos.addWidget(self.stack_dock)

    def _on_dock_clicked(self, habitante):
        for k, btn in self.btn_dock.items():
            btn.blockSignals(True)
            btn.setChecked(k == habitante)
            btn.blockSignals(False)

        idx = {"subdividir": 0, "cajon": 1, "puerta": 2, "vacio": 3}.get(habitante, 3)
        self.stack_dock.setCurrentIndex(idx)

        if habitante == "puerta":
            h = HH.resolve_hinge("parche")
            if h:
                self.lbl_puerta_hub.setText(f"{h.get('nombre')} · ${h.get('precio_unitario', 0.0):.2f} {h.get('moneda', 'USD')}")
        elif habitante == "cajon":
            s = HH.resolve_drawer_slide(OCULTA, BLUM_TANDEM)
            if s:
                self.lbl_cajon_hub.setText(f"{s.get('nombre')} · ${s.get('precio_unitario', 0.0):.2f} {s.get('moneda', 'USD')}")

        self.sigHabitanteCambiado.emit(habitante, self.get_habitante_config())

    def _aplicar_subdivision(self):
        cfg = self.get_habitante_config()
        self.lbl_subdiv.setText(f"{cfg['eje']} × {cfg['n_partes']}")
        self.sigHabitanteCambiado.emit("subdividir", cfg)

    def _aplicar_cajon(self):
        cfg = self.get_habitante_config()
        self.lbl_subdiv.setText(f"Cajón ({cfg['n_cajones']}x)")
        self.sigHabitanteCambiado.emit("cajon", cfg)

    def _aplicar_puerta(self):
        cfg = self.get_habitante_config()
        self.lbl_subdiv.setText(f"Puerta ({cfg['sistema']})")
        self.sigHabitanteCambiado.emit("puerta", cfg)

    def _aplicar_vacio(self):
        self.lbl_subdiv.setText("Libre")
        self.sigHabitanteCambiado.emit("vacio", {"tipo": "vacio"})

    def get_habitante_config(self):
        act = "vacio"
        for k, b in self.btn_dock.items():
            if b.isChecked():
                act = k
                break
        if act == "subdividir":
            return {
                "tipo": "subdividir",
                "celda": self._celda_actual,
                "eje": "X" if "Vertical" in self.combo_eje.currentText() else "Y",
                "n_partes": self.spin_n_partes.value(),
                "modo": "equitativo" if "Equitativo" in self.combo_dist.currentText() else "fijo"
            }
        elif act == "cajon":
            return {
                "tipo": "cajon",
                "celda": self._celda_actual,
                "n_cajones": self.spin_cajones.value(),
                "corredera": self.combo_corredera.currentText(),
                "agarre": self.combo_agarre_caj.currentText()
            }
        elif act == "puerta":
            return {
                "tipo": "puerta",
                "celda": self._celda_actual,
                "sistema": self.combo_sistema_pue.currentText(),
                "sentido": self.combo_sentido_pue.currentText(),
                "agarre": self.combo_agarre_pue.currentText()
            }
        return {"tipo": "vacio", "celda": self._celda_actual}

    def cargar_vano(self, obj):
        """Carga medidas de vano desde un objeto FreeCAD o dict."""
        self._obj_actual = obj
        w = _float_seguro(getattr(obj, "LuzLibreX", getattr(obj, "w", 564.0)), 564.0)
        h = _float_seguro(getattr(obj, "LuzLibreY", getattr(obj, "h", 280.0)), 280.0)
        d = _float_seguro(getattr(obj, "LuzLibreZ", getattr(obj, "d", 550.0)), 550.0)

        self._luz = {"w": w, "h": h, "d": d}
        self.lbl_luz_w.setText(f"{w:.1f} mm")
        self.lbl_luz_h.setText(f"{h:.1f} mm")
        self.lbl_luz_d.setText(f"{d:.1f} mm")
        self.lbl_luz_banner.setText(f"📐 <b>LUZ LIBRE NETA:</b> {w:.1f} × {h:.1f} × {d:.1f} mm")

    def cargar_vano_cell(self, cell, fondo=550.0):
        """Carga medidas desde una ResolvedCell de vdo_layout."""
        if hasattr(cell, "label"):
            self._celda_actual = cell.label
        w = float(getattr(cell, "w", 564.0))
        h = float(getattr(cell, "h", 280.0))
        d = float(fondo)

        self._luz = {"w": w, "h": h, "d": d}
        self.lbl_luz_w.setText(f"{w:.1f} mm")
        self.lbl_luz_h.setText(f"{h:.1f} mm")
        self.lbl_luz_d.setText(f"{d:.1f} mm")
        self.lbl_luz_banner.setText(f"📐 <b>LUZ {self._celda_actual}:</b> {w:.1f} × {h:.1f} × {d:.1f} mm")


# ----------------------------------------------------------------------
# PÁGINA 2: PIEZA L1 (PanelHeader + Cuadrado Figma)
# ----------------------------------------------------------------------
class PaginaPieza(_PaginaBase):
    """Nivel Pieza Física (PANEL): Header + Cuadrado Figma (VDOBoxController)."""

    def __init__(self, parent=None):
        super().__init__("Pieza / Tablero (Panel L1)", parent)
        self._obj_actual = None

        self.header = QtWidgets.QGroupBox("PanelHeader")
        self.header.setObjectName("grpPanelHeader")
        self.header.setStyleSheet(
            "QGroupBox#grpPanelHeader { color: #e0e0e0; font-weight: bold; "
            "border: 1px solid #444444; border-radius: 4px; margin-top: 6px; }"
            "QGroupBox#grpPanelHeader::title { subcontrol-origin: margin; "
            "left: 8px; padding: 0 4px; color: #007acc; }")
        h_layout = QtWidgets.QGridLayout(self.header)
        h_layout.setContentsMargins(8, 14, 8, 8)
        h_layout.setHorizontalSpacing(8)
        h_layout.setVerticalSpacing(3)

        self.lbl_largo = QtWidgets.QLabel("—")
        self.lbl_ancho = QtWidgets.QLabel("—")
        self.lbl_espesor = QtWidgets.QLabel("—")
        self.lbl_canto_norte = QtWidgets.QLabel("—")
        self.lbl_canto_sur = QtWidgets.QLabel("—")
        self.lbl_canto_este = QtWidgets.QLabel("—")
        self.lbl_canto_oeste = QtWidgets.QLabel("—")

        def _fila(r, clave, lbl_widget, label_txt):
            k = QtWidgets.QLabel(label_txt)
            k.setStyleSheet("color: #aaaaaa; font-size: 10px;")
            v = lbl_widget
            v.setStyleSheet("color: #e0e0e0; font-size: 10px; font-weight: bold;")
            h_layout.addWidget(k, r, 0)
            h_layout.addWidget(v, r, 1)

        _fila(0, "Largo", self.lbl_largo, "Largo (mm):")
        _fila(0, "Ancho", self.lbl_ancho, "Ancho (mm):")
        _fila(0, "Espesor", self.lbl_espesor, "Espesor (mm):")
        _fila(1, "CantoNorte", self.lbl_canto_norte, "Canto N:")
        _fila(1, "CantoSur", self.lbl_canto_sur, "Canto S:")
        _fila(2, "CantoEste", self.lbl_canto_este, "Canto E:")
        _fila(2, "CantoOeste", self.lbl_canto_oeste, "Canto O:")

        self.contenedor_datos.addWidget(self.header)

        # Cuadrado Figma (VDOBoxControllerWidget)
        self.box_controller = None
        if VDOBoxControllerWidget is not None:
            self.box_controller = VDOBoxControllerWidget()
            self.box_controller.sigConfigChanged.connect(self._on_box_changed)
            self.contenedor_datos.addWidget(self.box_controller)

    def cargar_panel(self, obj):
        self._obj_actual = obj
        largo = _float_seguro(getattr(obj, "Largo", None))
        ancho = _float_seguro(getattr(obj, "Ancho", None))
        espesor = _float_seguro(getattr(obj, "Espesor", None))

        self.lbl_largo.setText(f"{largo:.1f}" if largo else "—")
        self.lbl_ancho.setText(f"{ancho:.1f}" if ancho else "—")
        self.lbl_espesor.setText(f"{espesor:.1f}" if espesor else "—")

        canto_norte = _str_seguro(getattr(obj, "VDO_Canto_Norte", None), "FX")
        canto_sur = _str_seguro(getattr(obj, "VDO_Canto_Sur", None), "FX")
        canto_este = _str_seguro(getattr(obj, "VDO_Canto_Este", None), "FX")
        canto_oeste = _str_seguro(getattr(obj, "VDO_Canto_Oeste", None), "FX")
        self.lbl_canto_norte.setText(canto_norte)
        self.lbl_canto_sur.setText(canto_sur)
        self.lbl_canto_este.setText(canto_este)
        self.lbl_canto_oeste.setText(canto_oeste)

        if self.box_controller is not None:
            raw_cfg = getattr(obj, "VDO_Reengrose_JSON", None)
            if raw_cfg:
                try:
                    cfg = json.loads(raw_cfg) if isinstance(raw_cfg, str) else raw_cfg
                    self.box_controller.setConfig(cfg)
                    return
                except Exception:
                    App.Console.PrintWarning(
                        "[VDO] No se pudo cargar VDO_Reengrose_JSON")

            self.box_controller.setConfig({
                "activo": True,
                "uniforme": True,
                "ancho_uniforme": 70.0,
                "distancia_uniforme": 0.0,
                "espesor": espesor if espesor else None,
                "bordes": {
                    b: {"activo": True, "ancho": 70.0, "offset_borde": 0.0}
                    for b in ("frente", "fondo", "izquierda", "derecha")
                },
            })

    def cargar_pieza_dict(self, pieza):
        """Carga las cotas de una pieza física a partir de un dict calculado."""
        largo = float(pieza.get("largo", 0.0))
        ancho = float(pieza.get("ancho", 0.0))
        espesor = float(pieza.get("espesor", 18.0))
        self.lbl_largo.setText(f"{largo:.1f}")
        self.lbl_ancho.setText(f"{ancho:.1f}")
        self.lbl_espesor.setText(f"{espesor:.1f}")

        cantos = pieza.get("cantos", {})
        if isinstance(cantos, dict):
            self.lbl_canto_norte.setText(cantos.get("norte", "FX"))
            self.lbl_canto_sur.setText(cantos.get("sur", "FX"))
            self.lbl_canto_este.setText(cantos.get("este", "FX"))
            self.lbl_canto_oeste.setText(cantos.get("oeste", "FX"))

    def _on_box_changed(self, cfg):
        obj = self._obj_actual
        if obj is None:
            return
        try:
            if hasattr(obj, "VDO_Reengrose_JSON"):
                asignar_propiedades(obj, {"VDO_Reengrose_JSON": json.dumps(cfg)})
            elif hasattr(obj, "addProperty"):
                try:
                    anadir_propiedad_texto(obj, "VDO_Reengrose_JSON", "VDO", "Regrueso JSON")
                    asignar_propiedades(obj, {"VDO_Reengrose_JSON": json.dumps(cfg)})
                except Exception:
                    App.Console.PrintWarning(
                        "[VDO] No se pudo añadir propiedad VDO_Reengrose_JSON")
            doc = getattr(obj, "Document", None)
            if doc is not None:
                recalcular(doc)
        except Exception:
            App.Console.PrintWarning(
                "[VDO] No se pudo persistir VDO_Reengrose_JSON")


class VDOUniversalInspectorWidget(QtWidgets.QWidget):
    """
    Inspector universal lateral reactivo para el Sistema VDO.
    Unifica en un solo panel permanente:
    - Micro-Header editable
    - Visor 2D frontal (CocoPreview2D)
    - Árbol Maestro Izquierdo (QTreeWidget)
    - Stack Contextual Derecho (Chasis, Vano, Pieza, Cierre)
    """
    sigNivelCambiado = QtCore.Signal(int, str)  # (page_index, target_type)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("VDOUniversalInspector")
        self.setMinimumWidth(320)

        self._puente = None
        self._obj_actual = None
        self._tipo_actual = VDOSelectionBridge.TARGET_UNKNOWN

        self._resolved_layout = None
        self._piezas_calculadas = []

        self._construir_ui()
        self._inicializar_puente()
    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------
    def _construir_ui(self):
        root = QtWidgets.QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # 1. Breadcrumbs
        self.breadcrumbs = _BreadcrumbBar(self)
        self.breadcrumbs.sigNivelClickeado.connect(self._on_breadcrumb_clicked)
        root.addWidget(self.breadcrumbs)

        # 2. Micro-Header editable
        self.micro_header = _MicroHeaderWidget(self)
        self.micro_header.sigDimensionesCambiadas.connect(self._on_dimensiones_header_cambiadas)
        root.addWidget(self.micro_header)

        # 3. Visor 2D (CocoPreview2D)
        self.preview = None
        if CocoPreview2D is not None:
            self.preview = CocoPreview2D(self)
            self.preview.setMinimumHeight(150)
            self.preview.setMaximumHeight(210)
            self.preview.cellClicked.connect(self._on_preview_cell_clicked)
            self.preview.panelClicked.connect(self._on_preview_panel_clicked)
            self.preview.reengroseClicked.connect(self._on_preview_reengrose_clicked)
            root.addWidget(self.preview)

        # 4. QSplitter Horizontal Inferior
        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal, self)
        self.splitter.setChildrenCollapsible(False)
        self.splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #2b2b2b;
                width: 3px;
            }
            QSplitter::handle:hover {
                background-color: #007acc;
            }
        """)

        # Panel Izquierdo: QTreeWidget Maestro
        self.master_tree = QtWidgets.QTreeWidget(self.splitter)
        self.master_tree.setHeaderHidden(True)
        self.master_tree.setIndentation(12)
        self.master_tree.setUniformRowHeights(True)
        self.master_tree.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.master_tree.setStyleSheet("""
            QTreeWidget {
                background-color: #1a1a1a;
                border: 1px solid #2d2d2d;
                color: #dcdcdc;
                font-size: 10px;
            }
            QTreeWidget::item:selected {
                background-color: #007acc;
                color: #ffffff;
                font-weight: bold;
            }
            QTreeWidget::item:hover:!selected {
                background-color: #262626;
            }
        """)
        self.master_tree.itemClicked.connect(self._on_tree_item_clicked)
        self.splitter.addWidget(self.master_tree)

        # Panel Derecho: QStackedWidget con las 4 páginas
        self.stack = QtWidgets.QStackedWidget(self.splitter)

        self.pagina_chasis = PaginaChasis()
        self.pagina_vano = PaginaVano()
        self.pagina_pieza = PaginaPieza()
        self.pagina_cierre = PaginaCierre()

        # Conectar cambios de vano para actualizar preview
        self.pagina_vano.sigHabitanteCambiado.connect(self._on_habitante_vano_cambiado)

        self.stack.addWidget(self.pagina_chasis)   # 0
        self.stack.addWidget(self.pagina_vano)     # 1
        self.stack.addWidget(self.pagina_pieza)    # 2
        self.stack.addWidget(self.pagina_cierre)   # 3

        self.splitter.addWidget(self.stack)

        # Proporción inicial del splitter (130px árbol : 230px stack)
        self.splitter.setSizes([130, 230])
        root.addWidget(self.splitter, 1)

        # Iniciar en nivel Chasis
        self._ir_a_nivel(PAGE_CHASIS, VDOSelectionBridge.TARGET_UNKNOWN)
    def _ir_a_nivel(self, page_index, target_type):
        if self.stack is None:
            return
        self.stack.setCurrentIndex(page_index)
        self._tipo_actual = target_type

        # Actualizar breadcrumbs
        ruta, activo = _RUTA_BREADCRUMB_POR_TARGET.get(
            target_type, _RUTA_BREADCRUMB_DEFECTO)
        self.breadcrumbs.set_ruta(list(ruta), activo=activo)

        self.sigNivelCambiado.emit(page_index, target_type)
    def _on_breadcrumb_clicked(self, clave):
        destino = _CLAVE_BREADCRUMB_A_NIVEL.get(clave)
        if destino is not None:
            self._ir_a_nivel(*destino)
    # ------------------------------------------------------------------
    # Sincronización del Árbol Maestro y Preview 2D
    # ------------------------------------------------------------------
    def cargar_coco(self, obj):
        """Carga y sincroniza el COCO completo en Preview 2D, Árbol y Chasis."""
        self._obj_actual = obj
        alto = _float_seguro(getattr(obj, "Alto", None), 720.0)
        ancho = _float_seguro(getattr(obj, "Ancho", None), 600.0)
        fondo = _float_seguro(getattr(obj, "FondoModulo", None), 580.0)
        espesor = _float_seguro(getattr(obj, "Espesor", None), 18.0)

        # 1. Actualizar Micro-Header
        self.micro_header.cargar_dimensiones(ancho, alto, fondo, espesor)

        # 2. Cargar página Chasis
        self.pagina_chasis.cargar_coco(obj)

        # 3. Resolver Layout y calcular piezas
        self._actualizar_vista_completa()
    def _actualizar_vista_completa(self):
        """Recalcula layout, actualiza CocoPreview2D y regenera el QTreeWidget Maestro."""
        obj = self._obj_actual
        alto = _float_seguro(getattr(obj, "Alto", None), 720.0)
        ancho = _float_seguro(getattr(obj, "Ancho", None), 600.0)
        fondo = _float_seguro(getattr(obj, "FondoModulo", None), 580.0)
        espesor = _float_seguro(getattr(obj, "Espesor", None), 18.0)

        texto_div = getattr(obj, "VDO_Divisiones", "") or ""
        layout = Layout.loads(texto_div) if Layout is not None else None

        texto_reeng = getattr(obj, "VDO_Reengrose_JSON", "{}") or "{}"
        try:
            reengroses = json.loads(texto_reeng) if isinstance(texto_reeng, str) else dict(texto_reeng)
        except Exception:
            reengroses = {}

        texto_contenido = getattr(obj, "VDO_Contenido_JSON", "{}") or "{}"
        try:
            contenido_por_celda = json.loads(texto_contenido) if isinstance(texto_contenido, str) else dict(texto_contenido)
        except Exception:
            contenido_por_celda = {}

        resolved = None
        if layout is not None and resolve_layout is not None and cavidad_interior is not None:
            cavidad = cavidad_interior(alto, ancho, espesor)
            resolved = resolve_layout(
                layout,
                max(0.0, cavidad["ancho"]),
                max(0.0, cavidad["alto"]),
                espesor,
                reengroses=reengroses
            )
        self._resolved_layout = resolved

        # Calcular lista de piezas físicas
        cav_w = (ancho - 2.0 * espesor) if ancho > 2.0 * espesor else ancho
        (alto - 2.0 * espesor) if alto > 2.0 * espesor else alto

        piezas = [
            {
                "key": "base",
                "nombre": "Base",
                "largo": ancho,
                "ancho": fondo,
                "espesor": espesor,
                "caja": {"x": 0.0, "y": 0.0, "z": 0.0, "w": cav_w, "h": fondo, "d": espesor},
                "cantos": {"norte": "RIG", "sur": "FX", "este": "FX", "oeste": "FX"},
            },
            {
                "key": "techo",
                "nombre": "Tapa / Techo",
                "largo": ancho,
                "ancho": fondo,
                "espesor": espesor,
                "caja": {"x": 0.0, "y": 0.0, "z": max(0.0, alto - espesor), "w": cav_w, "h": fondo, "d": espesor},
                "cantos": {"norte": "RIG", "sur": "FX", "este": "FX", "oeste": "FX"},
            },
            {
                "key": "lat_izq",
                "nombre": "Lateral Izquierdo",
                "largo": alto,
                "ancho": fondo,
                "espesor": espesor,
                "caja": {"x": 0.0, "y": 0.0, "z": 0.0, "w": espesor, "h": fondo, "d": alto},
                "cantos": {"norte": "RIG", "sur": "RIG", "este": "FX", "oeste": "FX"},
            },
            {
                "key": "lat_der",
                "nombre": "Lateral Derecho",
                "largo": alto,
                "ancho": fondo,
                "espesor": espesor,
                "caja": {"x": max(0.0, ancho - espesor), "y": 0.0, "z": 0.0, "w": espesor, "h": fondo, "d": alto},
                "cantos": {"norte": "RIG", "sur": "RIG", "este": "FX", "oeste": "FX"},
            },
        ]

        # Agregar divisiones de layout si existen
        if resolved is not None:
            for idx, p in enumerate(resolved.pieces):
                piezas.append({
                    "key": f"div_{p.axis.lower()}_{idx}",
                    "nombre": f"{'Repisa' if p.axis == 'Y' else 'Montante'} {idx + 1}",
                    "largo": p.w if p.axis == 'Y' else p.h,
                    "ancho": fondo,
                    "espesor": espesor,
                    "caja": {"x": p.x, "y": 0.0, "z": p.z, "w": p.w, "h": fondo, "d": p.h},
                    "cantos": {"norte": "FX", "sur": "FX", "este": "FX", "oeste": "FX"},
                })

        self._piezas_calculadas = piezas

        # 4. Actualizar Visor 2D (CocoPreview2D)
        if self.preview is not None and resolved is not None:
            try:
                self.preview.set_layout(
                    resolved,
                    outer_w=ancho,
                    outer_h=alto,
                    entities=piezas,
                    fondo=fondo,
                    reengroses=reengroses,
                )
            except Exception:
                App.Console.PrintWarning(
                    "[VDO] No se pudo actualizar el visor 2D")

        # 5. Regenerar Árbol Maestro
        self._regenerar_arbol_maestro(obj, piezas, resolved, contenido_por_celda)
    def _regenerar_arbol_maestro(self, obj, piezas, resolved, contenido_por_celda):
        self.master_tree.blockSignals(True)
        self.master_tree.clear()

        nombre_raiz = getattr(obj, "Label", getattr(obj, "Name", "COCO")) if obj else "COCO"
        raiz = QtWidgets.QTreeWidgetItem([f"📦 {nombre_raiz}"])
        raiz.setData(0, QtCore.Qt.UserRole, {"tipo": "coco", "obj": obj})
        self.master_tree.addTopLevelItem(raiz)

        # Rama 1: Chasis y Envolvente
        item_chasis = QtWidgets.QTreeWidgetItem(["🪵 Chasis y Envolvente"])
        item_chasis.setData(0, QtCore.Qt.UserRole, {"tipo": "chasis", "obj": obj})
        raiz.addChild(item_chasis)

        caras_chasis = [
            ("━━ Tapa Superior", "superior"),
            ("━━ Base Inferior", "inferior"),
            ("◀ Lateral Izquierdo", "izquierda"),
            ("Lateral Derecho ▶", "derecha"),
            ("▦ Fondo Trasero", "fondo"),
            ("⌸ Zócalo Base", "zocalo"),
        ]
        for nom, face_id in caras_chasis:
            it = QtWidgets.QTreeWidgetItem([nom])
            it.setData(0, QtCore.Qt.UserRole, {"tipo": "chasis_face", "face": face_id})
            item_chasis.addChild(it)

        # Rama 2: Piezas Físicas
        item_piezas = QtWidgets.QTreeWidgetItem(["🪵 Piezas Físicas"])
        item_piezas.setData(0, QtCore.Qt.UserRole, {"tipo": "piezas_header", "obj": obj})
        raiz.addChild(item_piezas)

        for p in piezas:
            it = QtWidgets.QTreeWidgetItem([f"🪵 {p['nombre']} [{p['largo']:.0f}×{p['ancho']:.0f}]"])
            it.setData(0, QtCore.Qt.UserRole, {"tipo": "pieza", "clave": p["key"], "pieza": p})
            item_piezas.addChild(it)

        # Rama 3: Vanos y Cavidades
        item_vanos = QtWidgets.QTreeWidgetItem(["🔲 Vanos y Cavidades"])
        item_vanos.setData(0, QtCore.Qt.UserRole, {"tipo": "vanos_header", "obj": obj})
        raiz.addChild(item_vanos)

        if resolved is not None:
            for cell in resolved.walk_cells():
                lbl = getattr(cell, "label", "(x1, y1)")
                it_cell = QtWidgets.QTreeWidgetItem([f"🔲 {lbl} [{cell.w:.0f}×{cell.h:.0f}]"])
                it_cell.setData(0, QtCore.Qt.UserRole, {"tipo": "vano", "label": lbl, "cell": cell})
                item_vanos.addChild(it_cell)

                # Insertos anidados bajo la celda
                ins_cfg = contenido_por_celda.get(lbl, {})
                tipo_ins = ins_cfg.get("tipo")
                if tipo_ins == "cajon":
                    it_ins = QtWidgets.QTreeWidgetItem([f"🗄️ Cajón ({ins_cfg.get('n_cajones', 1)}x)"])
                    it_ins.setData(0, QtCore.Qt.UserRole, {"tipo": "inserto_cajon", "cfg": ins_cfg, "cell": cell})
                    it_cell.addChild(it_ins)
                elif tipo_ins == "puerta":
                    it_ins = QtWidgets.QTreeWidgetItem([f"🚪 Puerta ({ins_cfg.get('sistema', 'Batiente')})"])
                    it_ins.setData(0, QtCore.Qt.UserRole, {"tipo": "inserto_puerta", "cfg": ins_cfg, "cell": cell})
                    it_cell.addChild(it_ins)

        raiz.setExpanded(True)
        item_chasis.setExpanded(True)
        item_vanos.setExpanded(True)
        self.master_tree.blockSignals(False)
    def _on_tree_item_clicked(self, item, column):
        data = item.data(0, QtCore.Qt.UserRole)
        if not data or not isinstance(data, dict):
            return

        tipo = data.get("tipo")
        if tipo in ("coco", "chasis", "chasis_face"):
            self._ir_a_nivel(PAGE_CHASIS, VDOSelectionBridge.TARGET_COCO)
            if self.preview is not None:
                self.preview.set_selected(None)

        elif tipo == "pieza":
            p = data.get("pieza", {})
            self.pagina_pieza.cargar_pieza_dict(p)
            self._ir_a_nivel(PAGE_PIEZA, VDOSelectionBridge.TARGET_PANEL)
            if self.preview is not None:
                self.preview.set_selected_panel(p.get("key", ""))

        elif tipo == "piezas_header":
            self._ir_a_nivel(PAGE_PIEZA, VDOSelectionBridge.TARGET_PANEL)

        elif tipo == "vano":
            cell = data.get("cell")
            self.pagina_vano.cargar_vano_cell(cell, fondo=_float_seguro(getattr(self._obj_actual, "FondoModulo", 550.0)))
            self._ir_a_nivel(PAGE_VANO, getattr(VDOSelectionBridge, "TARGET_VANO", "VANO"))
            if self.preview is not None:
                self.preview.set_selected(data.get("label", ""))

        elif tipo in ("inserto_cajon", "inserto_puerta"):
            cfg = data.get("cfg", {})
            self.pagina_cierre.cargar_cierre_desde_config(tipo, cfg)
            self._ir_a_nivel(PAGE_CIERRE, "CAJON" if "cajon" in tipo else "PUERTA")
    # ------------------------------------------------------------------
    # Clics del Visor 2D (CocoPreview2D) -> Árbol y Páginas
    # ------------------------------------------------------------------
    def _on_preview_cell_clicked(self, label):
        self._seleccionar_item_en_arbol("label", label)
        if self._resolved_layout is not None:
            for cell in self._resolved_layout.walk_cells():
                if getattr(cell, "label", "") == label:
                    self.pagina_vano.cargar_vano_cell(cell, fondo=_float_seguro(getattr(self._obj_actual, "FondoModulo", 550.0)))
                    break
        self._ir_a_nivel(PAGE_VANO, getattr(VDOSelectionBridge, "TARGET_VANO", "VANO"))
    def _on_preview_panel_clicked(self, clave):
        self._seleccionar_item_en_arbol("clave", clave)
        for p in self._piezas_calculadas:
            if p.get("key") == clave:
                self.pagina_pieza.cargar_pieza_dict(p)
                break
        self._ir_a_nivel(PAGE_PIEZA, VDOSelectionBridge.TARGET_PANEL)
    def _on_preview_reengrose_clicked(self, clave):
        self._on_preview_panel_clicked(clave)
    def _seleccionar_item_en_arbol(self, campo, valor):
        """Busca y selecciona el elemento en el QTreeWidget Maestro."""
        it = QtWidgets.QTreeWidgetItemIterator(self.master_tree)
        while it.value():
            item = it.value()
            data = item.data(0, QtCore.Qt.UserRole)
            if isinstance(data, dict) and data.get(campo) == valor:
                self.master_tree.blockSignals(True)
                self.master_tree.setCurrentItem(item)
                self.master_tree.blockSignals(False)
                return
            it += 1
    # ------------------------------------------------------------------
    # Ediciones de Usuario en MicroHeader y Páginas
    # ------------------------------------------------------------------
    def _on_dimensiones_header_cambiadas(self, w, h, d, e):
        obj = self._obj_actual
        if obj is not None:
            try:
                if hasattr(obj, "Ancho"):
                    asignar_propiedades(obj, {"Ancho": w})
                if hasattr(obj, "Alto"):
                    asignar_propiedades(obj, {"Alto": h})
                if hasattr(obj, "FondoModulo"):
                    asignar_propiedades(obj, {"FondoModulo": d})
                if hasattr(obj, "Espesor"):
                    try:
                        asignar_propiedades(obj, {"Espesor": e})
                    except TypeError:
                        asignar_propiedades(obj, {"Espesor": round(e)})
                doc = getattr(obj, "Document", None)
                if doc is not None:
                    recalcular(doc)
            except Exception:
                App.Console.PrintWarning(
                    "[VDO] No se pudieron actualizar las dimensiones del header")
        self._actualizar_vista_completa()
    def _on_habitante_vano_cambiado(self, tipo_hab, cfg):
        obj = self._obj_actual
        if obj is None or Layout is None:
            return

        def _guardar_prop(prop_name, prop_val):
            try:
                if hasattr(obj, prop_name):
                    asignar_propiedades(obj, {prop_name: prop_val})
                elif hasattr(obj, "addProperty"):
                    anadir_propiedad_texto(obj, prop_name, "VDO", prop_name)
                    asignar_propiedades(obj, {prop_name: prop_val})
            except Exception:
                App.Console.PrintWarning(
                    f"[VDO] No se pudo guardar propiedad {prop_name}")

        celda_lbl = cfg.get("celda", "(x1, y1)")
        texto_div = getattr(obj, "VDO_Divisiones", "") or ""
        layout = Layout.loads(texto_div)

        texto_contenido = getattr(obj, "VDO_Contenido_JSON", "{}") or "{}"
        try:
            contenido = json.loads(texto_contenido) if isinstance(texto_contenido, str) else dict(texto_contenido)
        except Exception:
            contenido = {}

        if tipo_hab == "subdividir":
            cell = layout.find_label(celda_lbl)
            if cell is not None:
                layout.set_split(cell, cfg.get("eje", "Y"), int(cfg.get("n_partes", 2)))
                _guardar_prop("VDO_Divisiones", layout.dumps())
        elif tipo_hab == "cajon" or tipo_hab == "puerta":
            contenido[celda_lbl] = cfg
            _guardar_prop("VDO_Contenido_JSON", json.dumps(contenido))
        elif tipo_hab == "vacio":
            cell = layout.find_label(celda_lbl)
            if cell is not None:
                layout.disable_split(cell)
                _guardar_prop("VDO_Divisiones", layout.dumps())
            if celda_lbl in contenido:
                del contenido[celda_lbl]
                _guardar_prop("VDO_Contenido_JSON", json.dumps(contenido))

        try:
            doc = getattr(obj, "Document", None)
            if doc is not None:
                recalcular(doc)
        except Exception:
            App.Console.PrintWarning(
                "[VDO] No se pudo recomputar el documento")

        self._actualizar_vista_completa()
    # ------------------------------------------------------------------
    # Puente de selección nativa FreeCAD
    # ------------------------------------------------------------------
    def _inicializar_puente(self):
        self._puente = VDOSelectionBridge(
            on_target_changed=self._on_selection_changed)
        self._puente.attach()
    def _on_selection_changed(self, obj, target_type):
        """Reacción reactiva a un cambio de selección en FreeCAD."""
        try:
            self._obj_actual = obj
            self._tipo_actual = target_type

            if obj is None or target_type == VDOSelectionBridge.TARGET_UNKNOWN:
                self._ir_a_nivel(PAGE_CHASIS, VDOSelectionBridge.TARGET_UNKNOWN)
                return

            page = _TARGET_TO_PAGE.get(target_type, PAGE_CHASIS)

            if page == PAGE_CHASIS and target_type == VDOSelectionBridge.TARGET_COCO:
                self.cargar_coco(obj)
            elif page == PAGE_PIEZA and target_type == VDOSelectionBridge.TARGET_PANEL:
                self.pagina_pieza.cargar_panel(obj)
            elif page == PAGE_CIERRE:
                self.pagina_cierre.cargar_cierre(obj, target_type)
            elif page == PAGE_VANO:
                self.pagina_vano.cargar_vano(obj)
            else:
                self._ir_a_nivel(PAGE_CHASIS, VDOSelectionBridge.TARGET_UNKNOWN)
                return

            self._ir_a_nivel(page, target_type)

        except Exception:
            App.Console.PrintWarning(
                "[VDO] Error navegando a nivel de página")
            try:
                self._ir_a_nivel(PAGE_CHASIS, VDOSelectionBridge.TARGET_UNKNOWN)
            except Exception:
                App.Console.PrintWarning(
                    "[VDO] No se pudo navegar a la página de chasis")
    # ------------------------------------------------------------------
    # API pública y Ciclo de Vida
    # ------------------------------------------------------------------
    def pagina_actual(self):
        return self.stack.currentIndex() if self.stack is not None else -1
    def tipo_actual(self):
        return self._tipo_actual
    def objeto_actual(self):
        return self._obj_actual
    def puente(self):
        return self._puente
    def cerrar_inspector(self):
        """Limpieza: desregistra el observer de FreeCAD sin fugas."""
        try:
            if self._puente is not None:
                self._puente.detach()
                self._puente = None
        except Exception:
            App.Console.PrintWarning(
                "[VDO] No se pudo desregistrar el observer de selección")
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cerrar_inspector()
    def closeEvent(self, event):
        self.cerrar_inspector()
        super().closeEvent(event)
    @classmethod
    def mostrar_en_freecad(cls, parent=None):
        """Abre el inspector en FreeCAD GUI dentro de un QDockWidget lateral."""
        from freecad.vdo.ui.vdo_inspector_dock import obtener_o_crear_dock_inspector
        dock = obtener_o_crear_dock_inspector()
        if dock is not None:
            dock.show()
            dock.raise_()
            return dock.widget()
        instancia = cls(parent=parent)
        if Gui is not None and hasattr(Gui, "Control"):
            try:
                Gui.Control.showDialog(instancia)
            except Exception:
                instancia.show()
        else:
            instancia.show()
        return instancia


__all__ = [
    "VDOUniversalInspectorWidget",
]
