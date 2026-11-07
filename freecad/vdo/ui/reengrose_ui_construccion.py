"""Construccion de widgets y disposicion del editor de reengrose."""

from freecad.vdo.core import reengrose_modelo as VDO_RE_MODELO
from freecad.vdo.core.simbolos import SIMBOLO_MENOS
from freecad.vdo.qt_compat import QtCore, QtWidgets
from freecad.vdo.ui import tema_colores, tema_estilos
from freecad.vdo.ui.qt import VDO_DoubleSpinBox
from freecad.vdo.ui.reengrose_ui_constantes import LABEL_BORDE, LABEL_ESQUINA, OPCIONES_ESQUINA
from freecad.vdo.ui.reengrose_ui_preview import VDOBoardPreview


class ReengroseConstruccionMixin:
    """Construccion de widgets y disposicion del editor de reengrose."""

    # -----------------------------------------------------------------
    # Construccion
    # -----------------------------------------------------------------
    def _spin(self, valor=70.0, maximo=5000.0):
        spin = VDO_DoubleSpinBox()
        spin.setRange(0.0, maximo)
        spin.setDecimals(1)
        spin.setSuffix(" mm")
        spin.setValue(valor)
        return spin

    def _construir(self):
        grid = QtWidgets.QGridLayout(self)
        grid.setContentsMargins(8, 6, 8, 6)
        grid.setHorizontalSpacing(8)
        grid.setVerticalSpacing(6)

        self._construir_activo_y_bordes(grid)

        self._construir_medidas(grid)

        self._construir_largo(grid)

        self._construir_preview(grid)

        self._construir_sync_y_tabla(grid)

        self._construir_fabricacion_choque_cara(grid)

        self._construir_etiqueta_resumen(grid)

        self._aplicar_estilo_botones()

    def _construir_activo_y_bordes(self, grid):
        self.chk_activo = QtWidgets.QCheckBox(
            "Activar Reengrose en esta pieza")
        self.chk_activo.setToolTip(
            "Activa el modificador universal de bordes del tablero.")
        grid.addWidget(self.chk_activo, 0, 0, 1, 4)

        fila = QtWidgets.QHBoxLayout()
        self.btn_all = QtWidgets.QPushButton("All")
        self.btn_all.setCheckable(True)
        self.btn_all.setToolTip(
            "Enciende o apaga los cuatro bordes a la vez.")
        fila.addWidget(self.btn_all)
        self.btn_borde = {}
        for borde in VDO_RE_MODELO.BORDES_2D:
            btn = QtWidgets.QToolButton()
            btn.setText(LABEL_BORDE[borde])
            btn.setCheckable(True)
            btn.setToolButtonStyle(QtCore.Qt.ToolButtonTextOnly)
            btn.setToolTip(
                f"Activa una tira de refuerzo en el borde {borde}.")
            self.btn_borde[borde] = btn
            fila.addWidget(btn)
        fila.addStretch()
        grid.addLayout(fila, 1, 0, 1, 4)

    def _construir_medidas(self, grid):
        fila_medidas = QtWidgets.QHBoxLayout()
        self.chk_uniforme = QtWidgets.QCheckBox("🔗 Uniforme")
        self.chk_uniforme.setChecked(True)
        self.chk_uniforme.setToolTip(
            "Encadenado: mismo ancho, distancia al canto y largo de tira "
            "para todos los bordes. Desmarcalo para dar medidas "
            "independientes.")
        fila_medidas.addWidget(self.chk_uniforme)
        fila_medidas.addSpacing(10)
        fila_medidas.addWidget(QtWidgets.QLabel("Ancho:"))
        self.spin_ancho = self._spin(70.0)
        self.spin_ancho.setToolTip(
            "Ancho de la tira. 70 mm es habitual para bisagras; "
            "100 mm para zocalos.")
        fila_medidas.addWidget(self.spin_ancho)
        fila_medidas.addWidget(QtWidgets.QLabel("Distancia:"))
        self.spin_offset = self._spin(0.0, 500.0)
        self.spin_offset.setToolTip(
            "Distancia desde el canto del tablero hacia adentro.")
        fila_medidas.addWidget(self.spin_offset)
        fila_medidas.addWidget(QtWidgets.QLabel("Espesor:"))
        self.spin_espesor = self._spin(0.0, 100.0)
        self.spin_espesor.setSpecialValueText("Auto")
        self.spin_espesor.setToolTip(
            "Espesor de la tira. Auto usa el espesor del tablero madre.")
        fila_medidas.addWidget(self.spin_espesor)
        fila_medidas.addStretch()
        grid.addLayout(fila_medidas, 2, 0, 1, 4)

    def _construir_largo(self, grid):
        fila_largo = QtWidgets.QHBoxLayout()
        fila_largo.addWidget(QtWidgets.QLabel("Largo de tira:"))
        self.combo_largo_tira = QtWidgets.QComboBox()
        self.combo_largo_tira.addItem(
            "Marco interior (hace tope)", "marco_interior")
        self.combo_largo_tira.addItem(
            "Punta a punta (largo completo)", "punta_a_punta")
        self.combo_largo_tira.setToolTip(
            "Marco interior recorta la tira contra las vecinas; "
            "punta a punta conserva el largo total del borde.")
        fila_largo.addWidget(self.combo_largo_tira, 1)
        grid.addLayout(fila_largo, 3, 0, 1, 4)

    def _construir_preview(self, grid):
        self.preview = VDOBoardPreview()
        caja_preview = QtWidgets.QVBoxLayout()
        caja_preview.setContentsMargins(0, 0, 0, 0)
        caja_preview.addWidget(self.preview)
        leyenda = QtWidgets.QLabel(
            f'<span style="color:{tema_colores.COLOR_CATEGORIA_VERTICAL}">■</span> Vertical &nbsp;'
            f'<span style="color:{tema_colores.COLOR_NARANJA}">■</span> Horizontal &nbsp;'
            f'<span style="color:{tema_colores.COLOR_CATEGORIA_INGLETE}">■</span> Inglete &nbsp;'
            f'<span style="color:{tema_colores.COLOR_CATEGORIA_MARCO}">■</span> Marco')
        leyenda.setTextFormat(QtCore.Qt.RichText)
        tema_estilos.aplicar_estilo(leyenda, tema_estilos.ESTILO_TEXTO_10PX)
        caja_preview.addWidget(leyenda)

        panel = QtWidgets.QHBoxLayout()
        panel.addLayout(caja_preview, 0)
        panel.addLayout(self._construir_rejilla_esquinas(), 1)
        grid.addLayout(panel, 4, 0, 1, 4)

    def _construir_sync_y_tabla(self, grid):
        self.chk_sync_esquinas = QtWidgets.QCheckBox(
            "🔗 Sincronizar todas las esquinas")
        self.chk_sync_esquinas.setChecked(True)
        self.chk_sync_esquinas.setToolTip(
            "Activo: al cambiar una esquina se aplica el mismo tipo a las "
            "cuatro. Desactivado: cada esquina se configura por separado.")
        grid.addWidget(self.chk_sync_esquinas, 5, 0, 1, 4)

        self.widget_custom = self._construir_tabla_bordes()
        grid.addWidget(self.widget_custom, 6, 0, 1, 4)

    def _construir_fabricacion_choque_cara(self, grid):
        self.combo_fabricacion = QtWidgets.QComboBox()
        self.combo_fabricacion.addItem(
            "Pacha (bloque unificado)", "pacha")
        self.combo_fabricacion.addItem(
            "Independiente (cantear aparte)", "independiente")
        self.combo_fabricacion.setToolTip(
            "Fabricacion de las tiras y su canteado.")
        grid.addWidget(QtWidgets.QLabel("Fabricación:"), 7, 0)
        grid.addWidget(self.combo_fabricacion, 7, 1, 1, 3)

        self.combo_choque = QtWidgets.QComboBox()
        self.combo_choque.addItem("Retroceso (corte recto)", "retroceso")
        self.combo_choque.addItem("Mocheo / rebaje", "mocheo")
        self.combo_choque.addItem(
            "Interrumpir tira", "interrumpir_tira")
        self.combo_choque.setToolTip(
            "Comportamiento de la tira al chocar con el nucleo.")
        grid.addWidget(QtWidgets.QLabel("Choque núcleo:"), 8, 0)
        grid.addWidget(self.combo_choque, 8, 1, 1, 3)

        self.combo_cara = QtWidgets.QComboBox()
        self.combo_cara.addItem("Cara A (+)", "cara_a")
        self.combo_cara.addItem(f"Cara B ({SIMBOLO_MENOS})", "cara_b")
        self.combo_cara.addItem("Ambas caras", "ambos")
        self.combo_cara.setToolTip(
            "Cara del tablero donde se pegan las tiras.")
        grid.addWidget(QtWidgets.QLabel("Cara de pegado:"), 9, 0)
        grid.addWidget(self.combo_cara, 9, 1, 1, 3)

    def _construir_etiqueta_resumen(self, grid):
        self.lbl_resumen = QtWidgets.QLabel("Sin reengrose.")
        self.lbl_resumen.setWordWrap(True)
        tema_estilos.aplicar_estilo(self.lbl_resumen, tema_estilos.ESTILO_ETIQUETA_OSCURA_5PX)
        grid.addWidget(self.lbl_resumen, 10, 0, 1, 4)

    def _construir_rejilla_esquinas(self):
        grid = QtWidgets.QGridLayout()
        grid.setHorizontalSpacing(8)
        grid.setVerticalSpacing(4)
        titulo = QtWidgets.QLabel("Encuentro de esquinas")
        tema_estilos.aplicar_estilo(titulo, tema_estilos.ESTILO_NEGRITA)
        grid.addWidget(titulo, 0, 0, 1, 2)
        posiciones = {
            "frente_izquierda": (1, 0),
            "frente_derecha": (1, 1),
            "fondo_izquierda": (2, 0),
            "fondo_derecha": (2, 1),
        }
        self.combo_esquina = {}
        for esquina in VDO_RE_MODELO.ESQUINAS_2D:
            fila, col = posiciones[esquina]
            caja = QtWidgets.QVBoxLayout()
            caja.setSpacing(1)
            etiqueta = QtWidgets.QLabel(LABEL_ESQUINA[esquina])
            tema_estilos.aplicar_estilo(etiqueta, tema_estilos.ESTILO_TEXTO_11PX)
            combo = QtWidgets.QComboBox()
            for texto, dato in OPCIONES_ESQUINA:
                combo.addItem(texto, dato)
            combo.setToolTip(
                "Como se resuelve esta esquina entre los dos bordes "
                "que se cruzan.")
            self.combo_esquina[esquina] = combo
            caja.addWidget(etiqueta)
            caja.addWidget(combo)
            grid.addLayout(caja, fila, col)
        # Alias retrocompatible para paneles que usaban un combo global.
        self.combo_esquinas = self.combo_esquina["frente_izquierda"]
        return grid

    def _construir_tabla_bordes(self):
        contenedor = QtWidgets.QWidget()
        grid = QtWidgets.QGridLayout(contenedor)
        grid.setContentsMargins(18, 0, 0, 0)
        grid.setHorizontalSpacing(6)
        grid.setVerticalSpacing(2)
        self.spin_ancho_borde = {}
        self.spin_offset_borde = {}
        grid.addWidget(QtWidgets.QLabel(""), 0, 0)
        for col, borde in enumerate(VDO_RE_MODELO.BORDES_2D, start=1):
            etiqueta = QtWidgets.QLabel(LABEL_BORDE[borde])
            tema_estilos.aplicar_estilo(etiqueta, tema_estilos.ESTILO_NEGRITA_11PX)
            grid.addWidget(etiqueta, 0, col)
            ancho = self._spin(70.0)
            ancho.setMaximumWidth(96)
            offset = self._spin(0.0, 500.0)
            offset.setMaximumWidth(96)
            self.spin_ancho_borde[borde] = ancho
            self.spin_offset_borde[borde] = offset
            grid.addWidget(ancho, 1, col)
            grid.addWidget(offset, 2, col)
        grid.addWidget(QtWidgets.QLabel("ancho"), 1, 0)
        grid.addWidget(QtWidgets.QLabel("dist."), 2, 0)
        contenedor.setVisible(False)
        return contenedor

    def _aplicar_estilo_botones(self):
        """QSS para los botones checkables de bordes."""
        estilo = f"""
        QPushButton, QToolButton {{
            background-color: {tema_colores.FONDO3};
            color: {tema_colores.TEXTO};
            border: 1px solid {tema_colores.COLOR_BORDE_MEDIO};
            border-radius: 4px;
            padding: 5px 10px;
            font-weight: bold;
        }}
        QPushButton:hover, QToolButton:hover {{
            background-color: {tema_colores.BORDE};
            border-color: {tema_colores.COLOR_TEXTO_MUTED};
        }}
        QPushButton:checked, QToolButton:checked {{
            background-color: {tema_colores.ACEINTO};
            color: {tema_colores.TEXTO_CLARO};
            border: 1px solid {tema_colores.ACEINTO};
        }}
        QPushButton:disabled, QToolButton:disabled {{
            background-color: {tema_colores.COLOR_FONDO_HUB};
            color: {tema_colores.COLOR_TEXTO_MUTED};
            border: 1px solid {tema_colores.FONDO3};
        }}
        """
        tema_estilos.aplicar_estilo(self.btn_all, estilo)
        for btn in self.btn_borde.values():
            tema_estilos.aplicar_estilo(btn, estilo)

    def _conectar(self):
        self.chk_activo.toggled.connect(self._on_activo)
        self.btn_all.clicked.connect(self._on_all)
        for borde, btn in self.btn_borde.items():
            btn.toggled.connect(
                lambda estado, b=borde: self._on_borde(b, estado))
        self.chk_uniforme.toggled.connect(self._on_uniforme)
        self.spin_ancho.valueChanged.connect(self._on_uniforme_spin)
        self.spin_offset.valueChanged.connect(self._on_uniforme_spin)
        self.spin_espesor.valueChanged.connect(self._on_uniforme_spin)
        self.combo_largo_tira.currentIndexChanged.connect(
            self._on_uniforme_spin)
        for borde in VDO_RE_MODELO.BORDES_2D:
            self.spin_ancho_borde[borde].valueChanged.connect(
                self._on_custom_spin)
            self.spin_offset_borde[borde].valueChanged.connect(
                self._on_custom_spin)
        for esquina, combo in self.combo_esquina.items():
            combo.currentIndexChanged.connect(
                lambda _idx, e=esquina: self._on_esquina_changed(e))
        self.chk_sync_esquinas.toggled.connect(self._on_sync_toggled)
        self.combo_fabricacion.currentIndexChanged.connect(self._emitir)
        self.combo_choque.currentIndexChanged.connect(self._emitir)
        self.combo_cara.currentIndexChanged.connect(self._emitir)
