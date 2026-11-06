"""Construccion visual, senales y redimensionado. Parte de ui/box_controller.py (M7, D-44)."""

from freecad.vdo.core import reengrose_modelo as VDO_RE_MODELO
from freecad.vdo.qt_compat import QtCore, QtWidgets
from freecad.vdo.ui.qt import VDO_DoubleSpinBox

from freecad.vdo.ui.box_canvas import _VDOConcentricCenterCanvas
from freecad.vdo.ui.box_constantes import (
    ENCUENTRO_LABELS,
    ESQUINAS,
    TIPOS_ENCUENTRO,
    obtener_svg_icon,
)
from freecad.vdo.ui import tema


class BoxConstruccionMixin:
    """Mixin de VDOBoxControllerWidget: Construccion visual, senales y redimensionado. Sin cambios de codigo (D-44)."""

    # ------------------------------------------------------------------
    # Construcción Visual
    # ------------------------------------------------------------------
    def _spin(self, valor=0.0, maximo=2000.0, decimals=1):
        spin = VDO_DoubleSpinBox()
        spin.setRange(0.0, maximo)
        spin.setDecimals(decimals)
        spin.setSuffix(" mm")
        spin.setValue(float(valor))
        return spin

    def _construir_ui(self):
        vbox = QtWidgets.QVBoxLayout(self)
        vbox.setContentsMargins(6, 6, 6, 6)
        vbox.setSpacing(5)
        self._construir_barra_superior(vbox)
        # 2. Marco del Cuadrado Espacial Concéntrico
        self.container_canvas = QtWidgets.QFrame()
        self.container_canvas.setObjectName("canvas_container")
        grid = QtWidgets.QGridLayout(self.container_canvas)
        grid.setContentsMargins(6, 6, 6, 6)
        grid.setSpacing(4)
        self._construir_esquinas(grid)
        self._construir_bordes(grid)
        self._construir_centro(grid, vbox)
        # Alias chk_uniforme para compatibilidad backward
        self.chk_uniforme = self.btn_centro
        self._construir_selector_margenes(vbox)
        self._construir_panel_medidas(vbox)
        self._construir_chips_offset(vbox)
        self._construir_spins_borde()
        self._construir_resumen(vbox)

    def _construir_barra_superior(self, vbox):
        # 1. Barra superior: [ Activar ]  [ All ]  [ 🔗 Sincronizar esquinas ]
        top_bar = QtWidgets.QHBoxLayout()
        self.chk_activo = QtWidgets.QCheckBox("Activar reengrose")
        self.chk_activo.setChecked(True)
        self.chk_activo.setToolTip(
            "Activa o desactiva las tiras de reengrose perimetrales de esta pieza.")
        top_bar.addWidget(self.chk_activo)

        top_bar.addStretch()

        self.btn_all = QtWidgets.QPushButton("All")
        self.btn_all.setObjectName("btn_all")
        self.btn_all.setProperty("class", "all-btn")
        self.btn_all.setCheckable(True)
        self.btn_all.setToolTip(
            "Seleccionar todos / Deseleccionar todos los lados al unísono.")
        top_bar.addWidget(self.btn_all)

        self.chk_sync_esquinas = QtWidgets.QCheckBox("🔗 Sincronizar esquinas")
        self.chk_sync_esquinas.setChecked(True)
        self.chk_sync_esquinas.setToolTip(
            "Al estar activo, cualquier cambio en una esquina actualiza "
            "las 4 esquinas simultáneamente.")
        top_bar.addWidget(self.chk_sync_esquinas)
        vbox.addLayout(top_bar)

    def _construir_esquinas(self, grid):
        # Esquinas (botones cuadrados)
        self.btn_esquina = {}
        self.combo_esquina = {}  # Compatibilidad backward
        esquinas_grid = [
            ("NO", "fondo_izquierda", 0, 0),
            ("NE", "fondo_derecha", 0, 2),
            ("SO", "frente_izquierda", 2, 0),
            ("SE", "frente_derecha", 2, 2),
        ]
        for codigo, clave, fila, col in esquinas_grid:
            btn = QtWidgets.QPushButton()
            btn.setProperty("class", "esquina-btn")
            btn.setFixedSize(36, 36)
            btn.setCursor(QtCore.Qt.PointingHandCursor)
            btn.setIconSize(QtCore.QSize(20, 20))
            grid.addWidget(btn, fila, col)
            self.btn_esquina[clave] = btn
            self.btn_esquina[codigo.lower()] = btn

            # Combo interno retrocompatible para inspectores o tests legacy
            combo = QtWidgets.QComboBox()
            combo.setVisible(False)
            for tipo in TIPOS_ENCUENTRO:
                combo.addItem(ENCUENTRO_LABELS[tipo], tipo)
            self.combo_esquina[clave] = combo
            self.combo_esquina[codigo.lower()] = combo

        # Alias retrocompatibles para tests o inspecciones
        self.btn_esquinas = self.btn_esquina
        self.combo_esquinas = self.combo_esquina["frente_izquierda"]

    def _construir_bordes(self, grid):
        # Botones de Bordes (Tiras)
        self.btn_borde = {}
        # FONDO (Norte)
        btn_fondo = QtWidgets.QPushButton("▲ FONDO")
        btn_fondo.setProperty("class", "borde-btn")
        btn_fondo.setCheckable(True)
        btn_fondo.setFixedHeight(34)
        btn_fondo.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        btn_fondo.setCursor(QtCore.Qt.PointingHandCursor)
        grid.addWidget(btn_fondo, 0, 1)
        self.btn_borde["fondo"] = btn_fondo

        # FRENTE (Sur)
        btn_frente = QtWidgets.QPushButton("▼ FRENTE")
        btn_frente.setProperty("class", "borde-btn")
        btn_frente.setCheckable(True)
        btn_frente.setFixedHeight(34)
        btn_frente.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        btn_frente.setCursor(QtCore.Qt.PointingHandCursor)
        grid.addWidget(btn_frente, 2, 1)
        self.btn_borde["frente"] = btn_frente

        # IZQUIERDA (Oeste)
        btn_izq = QtWidgets.QPushButton("◄\nIZQ")
        btn_izq.setProperty("class", "borde-btn")
        btn_izq.setCheckable(True)
        btn_izq.setFixedWidth(46)
        btn_izq.setSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding)
        btn_izq.setCursor(QtCore.Qt.PointingHandCursor)
        grid.addWidget(btn_izq, 1, 0)
        self.btn_borde["izquierda"] = btn_izq

        # DERECHA (Este)
        btn_der = QtWidgets.QPushButton("DER\n►")
        btn_der.setProperty("class", "borde-btn")
        btn_der.setCheckable(True)
        btn_der.setFixedWidth(46)
        btn_der.setSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding)
        btn_der.setCursor(QtCore.Qt.PointingHandCursor)
        grid.addWidget(btn_der, 1, 2)
        self.btn_borde["derecha"] = btn_der

    def _construir_centro(self, grid, vbox):
        # CENTRO: Canvas Concéntrico (Calibre 1px Canto + Calibre 3px Tiras + Brecha Offset)
        self.center_box = QtWidgets.QFrame()
        tema.aplicar_estilo(self.center_box, tema.ESTILO_FONDO_TRANSPARENTE)
        c_layout = QtWidgets.QVBoxLayout(self.center_box)
        c_layout.setContentsMargins(0, 0, 0, 0)
        c_layout.setAlignment(QtCore.Qt.AlignCenter)

        # Canvas Concéntrico Gráfico
        self.canvas_concentrico = _VDOConcentricCenterCanvas(self.center_box)
        c_layout.addWidget(self.canvas_concentrico)

        # Candado Figma embebido en el centro
        self.btn_centro = QtWidgets.QPushButton(self.canvas_concentrico)
        self.btn_centro.setProperty("class", "centro-btn")
        self.btn_centro.setCheckable(True)
        self.btn_centro.setChecked(True)
        self.btn_centro.setCursor(QtCore.Qt.PointingHandCursor)
        self.btn_centro.setIconSize(QtCore.QSize(18, 18))
        self.btn_centro.setText(" Uniforme")
        self.btn_centro.setIcon(obtener_svg_icon("link"))
        self.btn_centro.setToolTip(
            "Candado Figma:\n"
            "🔗 Uniforme: Todos los bordes comparten Ancho y Offset.\n"
            "🔓 Desvinculado: Calibración independiente de Ancho y Offset por margen.")
        self.btn_centro.move(30, 26)

        grid.addWidget(self.center_box, 1, 1)
        grid.setRowStretch(1, 1)
        grid.setColumnStretch(1, 1)
        vbox.addWidget(self.container_canvas)

    def _construir_selector_margenes(self, vbox):
        # 3. Selector Gestáltico de Margen
        bar_margenes = QtWidgets.QHBoxLayout()
        self.lbl_margen_tag = QtWidgets.QLabel("Margen:")
        tema.aplicar_estilo(self.lbl_margen_tag, tema.ESTILO_ACENTO_NEGRITA)
        bar_margenes.addWidget(self.lbl_margen_tag)

        self.btn_margenes = {}
        for b in ("frente", "fondo", "izquierda", "derecha"):
            btn_m = QtWidgets.QPushButton(b.capitalize())
            btn_m.setCheckable(True)
            btn_m.setProperty("class", "chip-btn")
            btn_m.setCursor(QtCore.Qt.PointingHandCursor)
            bar_margenes.addWidget(btn_m)
            self.btn_margenes[b] = btn_m
        bar_margenes.addStretch()
        vbox.addLayout(bar_margenes)

    def _construir_panel_medidas(self, vbox):
        # 4. Panel de Cotas Numéricas Gestálticas (Ancho 3px & Offset 1px)
        self.panel_medidas = QtWidgets.QWidget()
        grid_med = QtWidgets.QGridLayout(self.panel_medidas)
        grid_med.setContentsMargins(0, 0, 0, 0)
        grid_med.setHorizontalSpacing(8)
        grid_med.setVerticalSpacing(4)

        # Cota de Ancho (Calibre 3px)
        lbl_ancho = QtWidgets.QLabel("Ancho tira (3px):")
        self.spin_ancho = self._spin(70.0, 1000.0)
        self.spin_ancho.setToolTip("Ancho del listón de reengrose (3px).")
        grid_med.addWidget(lbl_ancho, 0, 0)
        grid_med.addWidget(self.spin_ancho, 0, 1)

        # Cota de Offset / Distancia al Canto (Calibre 1px)
        lbl_dist = QtWidgets.QLabel("Offset canto (1px):")
        self.spin_offset = self._spin(0.0, 500.0)
        self.spin_offset.setToolTip("Distancia de retranqueo desde el canto exterior (1px).")
        grid_med.addWidget(lbl_dist, 0, 2)
        grid_med.addWidget(self.spin_offset, 0, 3)

        # Espesor
        lbl_esp = QtWidgets.QLabel("Espesor:")
        self.spin_espesor = self._spin(0.0, 100.0)
        self.spin_espesor.setSpecialValueText("Auto")
        self.spin_espesor.setToolTip("Espesor de la tira (Auto = espesor del tablero).")
        grid_med.addWidget(lbl_esp, 1, 0)
        grid_med.addWidget(self.spin_espesor, 1, 1)

        vbox.addWidget(self.panel_medidas)

    def _construir_chips_offset(self, vbox):
        # 5. Chips de Acceso Rápido para Offset de Taller
        bar_quick_offset = QtWidgets.QHBoxLayout()
        lbl_quick = QtWidgets.QLabel("Offset rápido:")
        tema.aplicar_estilo(lbl_quick, tema.ESTILO_ATENUADO_10PX)
        bar_quick_offset.addWidget(lbl_quick)

        self.chips_offset = [
            ("0 mm (Al ras)", 0.0),
            ("18 mm (1 Espesor)", 18.0),
            ("36 mm (2 Espesores)", 36.0),
            ("50 mm (Zócalo)", 50.0),
        ]
        for texto, val in self.chips_offset:
            chip = QtWidgets.QPushButton(texto)
            chip.setProperty("class", "chip-btn")
            chip.setCursor(QtCore.Qt.PointingHandCursor)
            chip.clicked.connect(lambda _, v=val: self._aplicar_chip_offset(v))
            bar_quick_offset.addWidget(chip)
        bar_quick_offset.addStretch()
        vbox.addLayout(bar_quick_offset)

    def _construir_spins_borde(self):
        # Compatibilidad: spins individuales mapeados en dict
        self.spin_ancho_borde = {}
        self.spin_offset_borde = {}
        for b in VDO_RE_MODELO.BORDES_2D:
            self.spin_ancho_borde[b] = self._spin(70.0)
            self.spin_offset_borde[b] = self._spin(0.0)

    def _construir_resumen(self, vbox):
        # 6. Resumen compacto
        self.lbl_resumen = QtWidgets.QLabel("Sin reengrose.")
        self.lbl_resumen.setWordWrap(True)
        tema.aplicar_estilo(self.lbl_resumen, tema.ESTILO_RESUMEN_CAJA)
        vbox.addWidget(self.lbl_resumen)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Centrar el botón candado dentro del canvas concéntrico
        cw = self.canvas_concentrico.width()
        ch = self.canvas_concentrico.height()
        bw = self.btn_centro.width() or 76
        bh = self.btn_centro.height() or 24
        self.btn_centro.move(int((cw - bw) / 2), int((ch - bh) / 2))

    # ------------------------------------------------------------------
    # Conexiones y Señales
    # ------------------------------------------------------------------
    def _conectar_senales(self):
        # Activo general
        self.chk_activo.toggled.connect(self._on_activo_toggled)

        # Master All
        self.btn_all.clicked.connect(self._on_all_clicked)

        # Bordes
        for borde, btn in self.btn_borde.items():
            btn.clicked.connect(lambda _, b=borde: self._on_borde_clicked(b))

        # Clic en el canvas gráfico
        self.canvas_concentrico.sigMarginClicked.connect(self._seleccionar_margen)

        # Centro (Candado Uniforme)
        self.btn_centro.clicked.connect(self._on_uniforme_toggled)

        # Esquinas
        for esquina in ESQUINAS:
            btn = self.btn_esquina[esquina]
            btn.clicked.connect(lambda _, e=esquina: self._on_esquina_clicked(e))

            combo = self.combo_esquina[esquina]
            combo.currentIndexChanged.connect(
                lambda _, e=esquina: self._on_combo_esquina_changed(e))

        # Sync esquinas
        self.chk_sync_esquinas.toggled.connect(self._on_sync_esquinas_toggled)

        # Chips de margen
        for b, btn in self.btn_margenes.items():
            btn.clicked.connect(lambda _, lado=b: self._seleccionar_margen(lado))

        # Spins maestros / individuales
        self.spin_ancho.valueChanged.connect(self._on_spin_ancho_changed)
        self.spin_offset.valueChanged.connect(self._on_spin_offset_changed)
        self.spin_espesor.valueChanged.connect(self._emitir_cambio)
