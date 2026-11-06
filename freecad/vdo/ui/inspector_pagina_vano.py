"""Pagina de vano del inspector: luz neta y dock de habitantes."""

from freecad.vdo.qt_compat import QtCore, QtGui, QtWidgets
from freecad.vdo.core import vdo_hardware_hub as HH
from freecad.vdo.datos.valores import BLUM_TANDEM, OCULTA
from freecad.vdo.ui.inspector_paginas import _PaginaBase, _float_seguro


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

        self._crear_banner_luz()
        self._crear_dock_habitantes()
        self._crear_stack_dock()

    def _crear_banner_luz(self):
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

    def _crear_dock_habitantes(self):
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

    def _crear_stack_dock(self):
        # -------------------------------------------------------------
        # Sub-paneles Contextuales del Dock
        # -------------------------------------------------------------
        self.stack_dock = QtWidgets.QStackedWidget()
        self.stack_dock.setStyleSheet("background-color: #1a1a1a; border-radius: 4px;")
        self._crear_panel_subdivision()
        self._crear_panel_cajon()
        self._crear_panel_puerta()
        self._crear_panel_vacio()

        self.stack_dock.setCurrentIndex(3)
        self.contenedor_datos.addWidget(self.stack_dock)

    def _crear_panel_subdivision(self):
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

    def _crear_panel_cajon(self):
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

    def _crear_panel_puerta(self):
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

    def _crear_panel_vacio(self):
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
