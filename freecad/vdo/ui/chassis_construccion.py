"""Construccion de interfaz y senales del chasis. Parte de ui/chassis_widget.py (M7, D-45)."""

from freecad.vdo.qt_compat import QtCore, QtWidgets
from freecad.vdo.ui.qt import VDO_DoubleSpinBox

from freecad.vdo.ui.chassis_canvas import _VDOChassisCrossSectionCanvas
from freecad.vdo.ui.chassis_constantes import (
    TIPOS_FONDO,
    obtener_svg_icon,
)
from freecad.vdo.ui import tema


class ChassisConstruccionMixin:
    """Mixin de VDOChassisControllerWidget: construccion de interfaz y senales. Sin cambios de codigo (D-45)."""

    def _init_ui(self):
        layout_raiz = QtWidgets.QVBoxLayout(self)
        layout_raiz.setContentsMargins(8, 8, 8, 8)
        layout_raiz.setSpacing(8)
        self._construir_barra_superior(layout_raiz)
        # -------------------------------------------------------------
        # 2. Matriz 3x3 del Corte Transversal Interactivo
        # -------------------------------------------------------------
        frame_matriz = QtWidgets.QFrame()
        frame_matriz.setObjectName("frameMatriz")
        grid = QtWidgets.QGridLayout(frame_matriz)
        grid.setContentsMargins(4, 4, 4, 4)
        grid.setSpacing(4)
        self._construir_matriz_esquinas(grid)
        self._construir_matriz_caras(grid)
        layout_raiz.addWidget(frame_matriz)
        # -------------------------------------------------------------
        # 3. Micro-Panel de Fondo Trasero
        # -------------------------------------------------------------
        self._construir_fondo(layout_raiz)
        # -------------------------------------------------------------
        # 4. Estrategia de Base / Anclaje al Piso
        # -------------------------------------------------------------
        grupo_base = QtWidgets.QGroupBox("ESTRATEGIA DE ANCLAJE AL PISO")
        grupo_base.setProperty("class", "grupo-base")
        layout_base = QtWidgets.QVBoxLayout(grupo_base)
        layout_base.setContentsMargins(6, 6, 6, 6)
        layout_base.setSpacing(6)

        self._construir_selector_estrategias(layout_base)
        # Parámetros dinámicos según estrategia
        self.stack_params = QtWidgets.QStackedWidget()
        self._construir_pagina_zocalo()
        self._construir_pagina_suspendido()
        self._construir_pagina_patas()
        layout_base.addWidget(self.stack_params)
        layout_raiz.addWidget(grupo_base)

    def _construir_barra_superior(self, layout_raiz):
        # -------------------------------------------------------------
        # 1. Barra Superior: Título y Arquetipos Rápidos
        # -------------------------------------------------------------
        barra_sup = QtWidgets.QHBoxLayout()
        barra_sup.setSpacing(6)

        lbl_titulo = QtWidgets.QLabel("🪵 <b>CHASIS PARAMÉTRICO</b>")
        tema.aplicar_estilo(lbl_titulo, tema.ESTILO_TITULO_ESPACIADO)
        barra_sup.addWidget(lbl_titulo)

        barra_sup.addStretch()

        lbl_arq = QtWidgets.QLabel("Arquetipos:")
        tema.aplicar_estilo(lbl_arq, tema.ESTILO_ARQUITECTURA_9PX)
        barra_sup.addWidget(lbl_arq)

        self.btn_arquetipos = {}
        arquetipos = [
            ("COCO", "coco", "Carcasa estándar con 5 caras activas"),
            ("Mesa", "escritorio", "Sin base inferior (escritorio / mesa)"),
            ("Estante", "estanteria", "Sin tapa superior ni fondo"),
            ("Aéreo", "aereo", "Módulo suspendido para muro"),
        ]
        for nombre, icono_id, tip in arquetipos:
            b = QtWidgets.QPushButton(nombre)
            b.setIcon(obtener_svg_icon(icono_id, 14))
            b.setToolTip(tip)
            b.setProperty("class", "arquetipo-chip")
            b.setFixedHeight(22)
            b.setCursor(QtCore.Qt.PointingHandCursor)
            b.clicked.connect(lambda _, n=nombre: self._on_arquetipo_clicked(n))
            barra_sup.addWidget(b)
            self.btn_arquetipos[nombre] = b

        layout_raiz.addLayout(barra_sup)

    def _construir_matriz_esquinas(self, grid):
        # Esquinas (4 botones interactivos con iconos de encuentro)
        self.btn_esquina = {}
        esquinas_spec = [
            ("superior_izq", 0, 0, "Sup-Izq"),
            ("superior_der", 0, 2, "Sup-Der"),
            ("inferior_izq", 2, 0, "Inf-Izq"),
            ("inferior_der", 2, 2, "Inf-Der"),
        ]
        for clave, fila, col, _tag in esquinas_spec:
            btn = QtWidgets.QPushButton()
            btn.setProperty("class", "btn-esquina")
            btn.setFixedSize(28, 28)
            btn.setCursor(QtCore.Qt.PointingHandCursor)
            btn.setIconSize(QtCore.QSize(18, 18))
            btn.clicked.connect(lambda _, c=clave: self._on_esquina_clicked(c))
            grid.addWidget(btn, fila, col)
            self.btn_esquina[clave] = btn

    def _construir_matriz_caras(self, grid):
        # Botón Tapa Superior (Borde Norte)
        self.btn_cara_sup = QtWidgets.QPushButton("━━ TAPA SUPERIOR · Activa ━━")
        self.btn_cara_sup.setCheckable(True)
        self.btn_cara_sup.setChecked(True)
        self.btn_cara_sup.setProperty("class", "btn-cara-horiz")
        self.btn_cara_sup.setFixedHeight(24)
        self.btn_cara_sup.setCursor(QtCore.Qt.PointingHandCursor)
        self.btn_cara_sup.clicked.connect(lambda: self._on_cara_toggled("superior"))
        grid.addWidget(self.btn_cara_sup, 0, 1)

        # Botón Lateral Izquierdo (Borde Oeste)
        self.btn_cara_izq = QtWidgets.QPushButton("◀ Lat Izq")
        self.btn_cara_izq.setCheckable(True)
        self.btn_cara_izq.setChecked(True)
        self.btn_cara_izq.setProperty("class", "btn-cara-vert")
        self.btn_cara_izq.setFixedWidth(64)
        self.btn_cara_izq.setCursor(QtCore.Qt.PointingHandCursor)
        self.btn_cara_izq.clicked.connect(lambda: self._on_cara_toggled("izquierda"))
        grid.addWidget(self.btn_cara_izq, 1, 0)

        # Centro: Canvas de Sección 2D
        self.canvas = _VDOChassisCrossSectionCanvas()
        self.canvas.faceClicked.connect(self._on_cara_toggled)
        grid.addWidget(self.canvas, 1, 1)

        # Botón Lateral Derecho (Borde Este)
        self.btn_cara_der = QtWidgets.QPushButton("Lat Der ▶")
        self.btn_cara_der.setCheckable(True)
        self.btn_cara_der.setChecked(True)
        self.btn_cara_der.setProperty("class", "btn-cara-vert")
        self.btn_cara_der.setFixedWidth(64)
        self.btn_cara_der.setCursor(QtCore.Qt.PointingHandCursor)
        self.btn_cara_der.clicked.connect(lambda: self._on_cara_toggled("derecha"))
        grid.addWidget(self.btn_cara_der, 1, 2)

        # Botón Base Inferior (Borde Sur)
        self.btn_cara_inf = QtWidgets.QPushButton("━━ BASE INFERIOR · Activa ━━")
        self.btn_cara_inf.setCheckable(True)
        self.btn_cara_inf.setChecked(True)
        self.btn_cara_inf.setProperty("class", "btn-cara-horiz")
        self.btn_cara_inf.setFixedHeight(24)
        self.btn_cara_inf.setCursor(QtCore.Qt.PointingHandCursor)
        self.btn_cara_inf.clicked.connect(lambda: self._on_cara_toggled("inferior"))
        grid.addWidget(self.btn_cara_inf, 2, 1)

    def _construir_fondo(self, layout_raiz):
        layout_fondo = QtWidgets.QHBoxLayout()
        layout_fondo.setSpacing(6)

        lbl_fondo = QtWidgets.QLabel("Fondo Trasero:")
        tema.aplicar_estilo(lbl_fondo, tema.ESTILO_ETIQUETA_10PX)
        layout_fondo.addWidget(lbl_fondo)

        self.combo_fondo = QtWidgets.QComboBox()
        self.combo_fondo.setProperty("class", "combo-fondo")
        for val, label, icono_id, tip in TIPOS_FONDO:
            self.combo_fondo.addItem(obtener_svg_icon(icono_id, 16), label, val)
        self.combo_fondo.currentIndexChanged.connect(self._on_fondo_changed)
        layout_fondo.addWidget(self.combo_fondo, 1)

        layout_raiz.addLayout(layout_fondo)

    def _construir_selector_estrategias(self, layout_base):
        # Selector de 3 estrategias
        fila_estrategias = QtWidgets.QHBoxLayout()
        fila_estrategias.setSpacing(4)
        self.btn_estrategias = {}

        estrategias_spec = [
            ("zocalo", "🪵 Zócalo Taller", "zocalo", "Tarima / zócalo frontal de taller"),
            ("suspendido", "🧗 Suspendido", "suspendido", "Fijación a muro estructural sin apoyo en piso"),
            ("patas", "🛞 Patas / Niveladores", "patas", "Patas plásticas regulables en altura"),
        ]
        for key, label, icono_id, tip in estrategias_spec:
            btn = QtWidgets.QPushButton(label)
            btn.setIcon(obtener_svg_icon(icono_id, 16))
            btn.setCheckable(True)
            btn.setToolTip(tip)
            btn.setProperty("class", "estrategia-btn")
            btn.setFixedHeight(28)
            btn.setCursor(QtCore.Qt.PointingHandCursor)
            btn.clicked.connect(lambda _, k=key: self._on_estrategia_clicked(k))
            fila_estrategias.addWidget(btn)
            self.btn_estrategias[key] = btn

        self.btn_estrategias["zocalo"].setChecked(True)
        layout_base.addLayout(fila_estrategias)

    def _construir_pagina_zocalo(self):
        # Página Zócalo
        page_zocalo = QtWidgets.QWidget()
        lay_pz = QtWidgets.QHBoxLayout(page_zocalo)
        lay_pz.setContentsMargins(0, 0, 0, 0)
        lay_pz.setSpacing(6)

        lay_pz.addWidget(QtWidgets.QLabel("Altura zócalo:"))
        self.spin_altura_zocalo = VDO_DoubleSpinBox()
        self.spin_altura_zocalo.setRange(20.0, 300.0)
        self.spin_altura_zocalo.setValue(100.0)
        self.spin_altura_zocalo.setSuffix(" mm")
        self.spin_altura_zocalo.valueChanged.connect(self._on_param_base_changed)
        lay_pz.addWidget(self.spin_altura_zocalo)

        lay_pz.addWidget(QtWidgets.QLabel("Separación:"))
        self.spin_offset_zocalo = VDO_DoubleSpinBox()
        self.spin_offset_zocalo.setRange(0.0, 150.0)
        self.spin_offset_zocalo.setValue(50.0)
        self.spin_offset_zocalo.setSuffix(" mm")
        self.spin_offset_zocalo.valueChanged.connect(self._on_param_base_changed)
        lay_pz.addWidget(self.spin_offset_zocalo)
        self.stack_params.addWidget(page_zocalo)

    def _construir_pagina_suspendido(self):
        # Página Suspendido
        page_susp = QtWidgets.QWidget()
        lay_ps = QtWidgets.QHBoxLayout(page_susp)
        lay_ps.setContentsMargins(0, 0, 0, 0)
        lay_ps.setSpacing(6)

        lay_ps.addWidget(QtWidgets.QLabel("Despegue de piso:"))
        self.spin_despegue_piso = VDO_DoubleSpinBox()
        self.spin_despegue_piso.setRange(50.0, 1500.0)
        self.spin_despegue_piso.setValue(300.0)
        self.spin_despegue_piso.setSuffix(" mm")
        self.spin_despegue_piso.valueChanged.connect(self._on_param_base_changed)
        lay_ps.addWidget(self.spin_despegue_piso)

        lbl_camar = QtWidgets.QLabel("🧗 Herrajes Camar / Scilm")
        tema.aplicar_estilo(lbl_camar, tema.ESTILO_AVISO_10PX)
        lay_ps.addWidget(lbl_camar)
        self.stack_params.addWidget(page_susp)

    def _construir_pagina_patas(self):
        # Página Patas
        page_patas = QtWidgets.QWidget()
        lay_pp = QtWidgets.QHBoxLayout(page_patas)
        lay_pp.setContentsMargins(0, 0, 0, 0)
        lay_pp.setSpacing(6)

        lay_pp.addWidget(QtWidgets.QLabel("Altura patas:"))
        self.spin_altura_patas = VDO_DoubleSpinBox()
        self.spin_altura_patas.setRange(50.0, 200.0)
        self.spin_altura_patas.setValue(100.0)
        self.spin_altura_patas.setSuffix(" mm")
        self.spin_altura_patas.valueChanged.connect(self._on_param_base_changed)
        lay_pp.addWidget(self.spin_altura_patas)

        lay_pp.addWidget(QtWidgets.QLabel("Retranqueo:"))
        self.spin_offset_patas = VDO_DoubleSpinBox()
        self.spin_offset_patas.setRange(0.0, 100.0)
        self.spin_offset_patas.setValue(50.0)
        self.spin_offset_patas.setSuffix(" mm")
        self.spin_offset_patas.valueChanged.connect(self._on_param_base_changed)
        lay_pp.addWidget(self.spin_offset_patas)
        self.stack_params.addWidget(page_patas)
