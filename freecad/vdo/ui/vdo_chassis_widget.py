"""
vdo_chassis_widget.py

Widget de Corte Transversal Interactivo 2D para la Envolvente / Chasis Paramétrico (Capa 1).
Parte del Sistema VDO (Ergonomía Cognitiva, Semiótica Espacial y Poka-Yoke para CAD/CAM).

Axioma:
    El COCO no es una primitiva; es solo un arquetipo de una envolvente paramétrica
    donde las caras pueden estar Activas o Ausentes, los encuentros de esquina conmutan
    entre las uniones de taller reales (tapa_domina, lateral_domina, inglete_45),
    y la base soporta múltiples estrategias (zócalo, suspendido, patas).

Compatible con PySide, PySide2 y PySide6 mediante vdo_qt.py.
"""

import logging
import sys

from freecad.vdo.qt_compat import QtCore, QtGui, QtSvg, QtWidgets
from freecad.vdo.ui.vdo_qt import VDO_DoubleSpinBox

from freecad.vdo.ui.chassis_canvas import _VDOChassisCrossSectionCanvas
from freecad.vdo.ui.chassis_constantes import (
    CARAS,
    ENCUENTROS,
    ENCUENTRO_LABELS,
    ENCUENTRO_TOOLTIPS,
    TIPOS_ENCUENTRO,
    TIPOS_FONDO,
    _ARQUETIPOS,
    obtener_svg_icon,
)

_LOG = logging.getLogger(__name__)



# ----------------------------------------------------------------------
# Widget Principal: VDOChassisControllerWidget
# ----------------------------------------------------------------------
class VDOChassisControllerWidget(QtWidgets.QWidget):
    """
    Controlador semiótico 2D para la Envolvente / Chasis Paramétrico (Capa 1).
    Permite conmutar caras activas/ausentes, ciclar uniones de esquina y
    definir la estrategia de base de forma interactiva y Poka-Yoke.
    """

    sigChassisChanged = QtCore.Signal(dict)
    sigConfigChanged = sigChassisChanged  # Alias de conveniencia

    def __init__(self, parent=None):
        super().__init__(parent)
        self._cargando = False

        # Estado del modelo de Capa 1
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

        self._init_ui()
        self._aplicar_estilos()
        self._actualizar_ui()

    def _init_ui(self):
        layout_raiz = QtWidgets.QVBoxLayout(self)
        layout_raiz.setContentsMargins(8, 8, 8, 8)
        layout_raiz.setSpacing(8)

        # -------------------------------------------------------------
        # 1. Barra Superior: Título y Arquetipos Rápidos
        # -------------------------------------------------------------
        barra_sup = QtWidgets.QHBoxLayout()
        barra_sup.setSpacing(6)

        lbl_titulo = QtWidgets.QLabel("🪵 <b>CHASIS PARAMÉTRICO</b>")
        lbl_titulo.setStyleSheet("font-size: 11px; color: #e0e0e0; letter-spacing: 0.5px;")
        barra_sup.addWidget(lbl_titulo)

        barra_sup.addStretch()

        lbl_arq = QtWidgets.QLabel("Arquetipos:")
        lbl_arq.setStyleSheet("font-size: 9px; color: #888888;")
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

        # -------------------------------------------------------------
        # 2. Matriz 3x3 del Corte Transversal Interactivo
        # -------------------------------------------------------------
        frame_matriz = QtWidgets.QFrame()
        frame_matriz.setObjectName("frameMatriz")
        grid = QtWidgets.QGridLayout(frame_matriz)
        grid.setContentsMargins(4, 4, 4, 4)
        grid.setSpacing(4)

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

        layout_raiz.addWidget(frame_matriz)

        # -------------------------------------------------------------
        # 3. Micro-Panel de Fondo Trasero
        # -------------------------------------------------------------
        layout_fondo = QtWidgets.QHBoxLayout()
        layout_fondo.setSpacing(6)

        lbl_fondo = QtWidgets.QLabel("Fondo Trasero:")
        lbl_fondo.setStyleSheet("font-size: 10px; color: #aaaaaa;")
        layout_fondo.addWidget(lbl_fondo)

        self.combo_fondo = QtWidgets.QComboBox()
        self.combo_fondo.setProperty("class", "combo-fondo")
        for val, label, icono_id, tip in TIPOS_FONDO:
            self.combo_fondo.addItem(obtener_svg_icon(icono_id, 16), label, val)
        self.combo_fondo.currentIndexChanged.connect(self._on_fondo_changed)
        layout_fondo.addWidget(self.combo_fondo, 1)

        layout_raiz.addLayout(layout_fondo)

        # -------------------------------------------------------------
        # 4. Estrategia de Base / Anclaje al Piso
        # -------------------------------------------------------------
        grupo_base = QtWidgets.QGroupBox("ESTRATEGIA DE ANCLAJE AL PISO")
        grupo_base.setProperty("class", "grupo-base")
        layout_base = QtWidgets.QVBoxLayout(grupo_base)
        layout_base.setContentsMargins(6, 6, 6, 6)
        layout_base.setSpacing(6)

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

        # Parámetros dinámicos según estrategia
        self.stack_params = QtWidgets.QStackedWidget()

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
        lbl_camar.setStyleSheet("color: #ffaa00; font-size: 10px;")
        lay_ps.addWidget(lbl_camar)
        self.stack_params.addWidget(page_susp)

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

        layout_base.addWidget(self.stack_params)
        layout_raiz.addWidget(grupo_base)

    def _aplicar_estilos(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                color: #e0e0e0;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
            }
            #frameMatriz {
                background-color: #161616;
                border: 1px solid #2d2d2d;
                border-radius: 6px;
            }
            .arquetipo-chip {
                background-color: #2b2b2b;
                border: 1px solid #444444;
                border-radius: 4px;
                padding: 2px 8px;
                font-size: 9px;
                color: #cccccc;
            }
            .arquetipo-chip:hover {
                background-color: #383838;
                border-color: #007acc;
                color: #ffffff;
            }
            .btn-cara-horiz {
                background-color: #25282c;
                border: 1.5px solid #007acc;
                border-radius: 4px;
                font-size: 10px;
                font-weight: bold;
                color: #ffffff;
            }
            .btn-cara-horiz:!checked {
                background-color: #1a1a1a;
                border: 1px dashed #555555;
                color: #777777;
            }
            .btn-cara-vert {
                background-color: #25282c;
                border: 1.5px solid #007acc;
                border-radius: 4px;
                font-size: 8px;
                font-weight: bold;
                color: #ffffff;
                line-height: 10px;
            }
            .btn-cara-vert:!checked {
                background-color: #1a1a1a;
                border: 1px dashed #555555;
                color: #777777;
            }
            .btn-esquina {
                background-color: #262626;
                border: 1px solid #444444;
                border-radius: 5px;
            }
            .btn-esquina:hover {
                background-color: #333333;
                border-color: #007acc;
            }
            .btn-esquina:pressed {
                background-color: #007acc;
            }
            .grupo-base {
                border: 1px solid #333333;
                border-radius: 5px;
                margin-top: 6px;
                padding-top: 8px;
                font-size: 9px;
                font-weight: bold;
                color: #888888;
            }
            .estrategia-btn {
                background-color: #282828;
                border: 1px solid #3d3d3d;
                border-radius: 4px;
                font-size: 10px;
                color: #cccccc;
            }
            .estrategia-btn:checked {
                background-color: #007acc;
                border-color: #007acc;
                color: #ffffff;
                font-weight: bold;
            }
            .estrategia-btn:hover:!checked {
                background-color: #333333;
                color: #ffffff;
            }
            QComboBox {
                background-color: #252525;
                border: 1px solid #444444;
                border-radius: 4px;
                padding: 3px 6px;
                font-size: 10px;
            }
            QComboBox:hover {
                border-color: #007acc;
            }
            QDoubleSpinBox {
                background-color: #252525;
                border: 1px solid #444444;
                border-radius: 4px;
                padding: 2px 4px;
                font-size: 10px;
                color: #ffffff;
            }
            QDoubleSpinBox:focus {
                border-color: #007acc;
            }
        """)

    # ------------------------------------------------------------------
    # Manejadores de Eventos
    # ------------------------------------------------------------------
    def _on_cara_toggled(self, cara):
        if self._cargando:
            return
        if cara not in self._caras:
            return

        nueva_activa = not self._caras[cara]["activa"]
        self._caras[cara]["activa"] = nueva_activa

        self._actualizar_botones_caras()
        self.canvas.update_state(self._caras, self._encuentros, self._base)
        self._emitir_cambio()

    def _on_esquina_clicked(self, esquina):
        if self._cargando:
            return
        actual = self._encuentros.get(esquina, "tapa_domina")
        idx = (TIPOS_ENCUENTRO.index(actual) + 1) % len(TIPOS_ENCUENTRO)
        nuevo_tipo = TIPOS_ENCUENTRO[idx]

        self._encuentros[esquina] = nuevo_tipo
        self._actualizar_botones_esquinas()
        self.canvas.update_state(self._caras, self._encuentros, self._base)
        self._emitir_cambio()

    def _on_fondo_changed(self):
        if self._cargando:
            return
        tipo = self.combo_fondo.currentData()
        self._caras["fondo"]["tipo"] = tipo
        self._caras["fondo"]["activa"] = tipo != "abierto"
        self.canvas.update_state(self._caras, self._encuentros, self._base)
        self._emitir_cambio()

    def _on_estrategia_clicked(self, estrategia):
        if self._cargando:
            return
        self._base["estrategia"] = estrategia

        for k, btn in self.btn_estrategias.items():
            btn.blockSignals(True)
            btn.setChecked(k == estrategia)
            btn.blockSignals(False)

        idx_stack = {"zocalo": 0, "suspendido": 1, "patas": 2}.get(estrategia, 0)
        self.stack_params.setCurrentIndex(idx_stack)

        self._actualizar_valores_base_dict()
        self.canvas.update_state(self._caras, self._encuentros, self._base)
        self._emitir_cambio()

    def _on_param_base_changed(self):
        if self._cargando:
            return
        self._actualizar_valores_base_dict()
        self.canvas.update_state(self._caras, self._encuentros, self._base)
        self._emitir_cambio()

    def _actualizar_valores_base_dict(self):
        estrategia = self._base.get("estrategia", "zocalo")
        if estrategia == "zocalo":
            self._base["altura"] = float(self.spin_altura_zocalo.value())
            self._base["separacion_frente"] = float(self.spin_offset_zocalo.value())
        elif estrategia == "suspendido":
            self._base["altura"] = float(self.spin_despegue_piso.value())
            self._base["separacion_frente"] = 0.0
        elif estrategia == "patas":
            self._base["altura"] = float(self.spin_altura_patas.value())
            self._base["separacion_frente"] = float(self.spin_offset_patas.value())

    def _on_arquetipo_clicked(self, nombre):
        if self._cargando:
            return

        cfg = _ARQUETIPOS.get(nombre)
        if cfg is None:
            return

        self.setChassisConfig(cfg)
        self._emitir_cambio()

    # ------------------------------------------------------------------
    # Sincronización Visual
    # ------------------------------------------------------------------
    def _actualizar_ui(self):
        self._actualizar_botones_caras()
        self._actualizar_botones_esquinas()
        self._actualizar_combo_fondo()
        self._actualizar_estrategia_base()
        self.canvas.update_state(self._caras, self._encuentros, self._base)

    def _actualizar_botones_caras(self):
        act_sup = self._caras["superior"]["activa"]
        self.btn_cara_sup.blockSignals(True)
        self.btn_cara_sup.setChecked(act_sup)
        self.btn_cara_sup.setText("━━ TAPA SUPERIOR · Activa ━━" if act_sup else "┄ TAPA SUPERIOR · Ausente ┄")
        self.btn_cara_sup.blockSignals(False)

        act_inf = self._caras["inferior"]["activa"]
        self.btn_cara_inf.blockSignals(True)
        self.btn_cara_inf.setChecked(act_inf)
        self.btn_cara_inf.setText("━━ BASE INFERIOR · Activa ━━" if act_inf else "┄ BASE INFERIOR · Ausente ┄")
        self.btn_cara_inf.blockSignals(False)

        act_izq = self._caras["izquierda"]["activa"]
        self.btn_cara_izq.blockSignals(True)
        self.btn_cara_izq.setChecked(act_izq)
        self.btn_cara_izq.setText("◀ Lat Izq" if act_izq else "◀ Izq Aus.")
        self.btn_cara_izq.blockSignals(False)

        act_der = self._caras["derecha"]["activa"]
        self.btn_cara_der.blockSignals(True)
        self.btn_cara_der.setChecked(act_der)
        self.btn_cara_der.setText("Lat Der ▶" if act_der else "Der Aus. ▶")
        self.btn_cara_der.blockSignals(False)

    def _actualizar_botones_esquinas(self):
        for e, btn in self.btn_esquina.items():
            tipo = self._encuentros.get(e, "tapa_domina")
            btn.setIcon(obtener_svg_icon(tipo, 22))
            btn.setToolTip(f"<b>{ENCUENTRO_LABELS.get(tipo, tipo)}</b><br>{ENCUENTRO_TOOLTIPS.get(tipo, '')}")

    def _actualizar_combo_fondo(self):
        tipo = self._caras["fondo"].get("tipo", "ranurado_5mm")
        idx = self.combo_fondo.findData(tipo)
        if idx >= 0:
            self.combo_fondo.blockSignals(True)
            self.combo_fondo.setCurrentIndex(idx)
            self.combo_fondo.blockSignals(False)

    def _actualizar_estrategia_base(self):
        estrategia = self._base.get("estrategia", "zocalo")
        for k, btn in self.btn_estrategias.items():
            btn.blockSignals(True)
            btn.setChecked(k == estrategia)
            btn.blockSignals(False)

        idx_stack = {"zocalo": 0, "suspendido": 1, "patas": 2}.get(estrategia, 0)
        self.stack_params.setCurrentIndex(idx_stack)

        self.spin_altura_zocalo.blockSignals(True)
        self.spin_offset_zocalo.blockSignals(True)
        self.spin_despegue_piso.blockSignals(True)
        self.spin_altura_patas.blockSignals(True)
        self.spin_offset_patas.blockSignals(True)

        if estrategia == "zocalo":
            self.spin_altura_zocalo.setValue(float(self._base.get("altura", 100.0)))
            self.spin_offset_zocalo.setValue(float(self._base.get("separacion_frente", 50.0)))
        elif estrategia == "suspendido":
            self.spin_despegue_piso.setValue(float(self._base.get("altura", 300.0)))
        elif estrategia == "patas":
            self.spin_altura_patas.setValue(float(self._base.get("altura", 100.0)))
            self.spin_offset_patas.setValue(float(self._base.get("separacion_frente", 50.0)))

        self.spin_altura_zocalo.blockSignals(False)
        self.spin_offset_zocalo.blockSignals(False)
        self.spin_despegue_piso.blockSignals(False)
        self.spin_altura_patas.blockSignals(False)
        self.spin_offset_patas.blockSignals(False)

    def _emitir_cambio(self):
        if not self._cargando:
            self.sigChassisChanged.emit(self.getChassisConfig())

    # ------------------------------------------------------------------
    # Contrato Público API (Capa 1)
    # ------------------------------------------------------------------
    def setChassisConfig(self, cfg: dict):
        """Carga la configuración sin emitir señales redundantes."""
        if not isinstance(cfg, dict):
            return

        self._cargando = True
        try:
            # Caras
            caras_cfg = cfg.get("caras", {})
            for c in CARAS:
                if c in caras_cfg:
                    self._caras[c] = dict(caras_cfg[c])

            # Encuentros
            enc_cfg = cfg.get("encuentros", {})
            for e in ENCUENTROS:
                if e in enc_cfg:
                    self._encuentros[e] = enc_cfg[e]

            # Base
            base_cfg = cfg.get("base", {})
            if base_cfg:
                self._base.update(base_cfg)

            self._actualizar_ui()
        finally:
            self._cargando = False

    def getChassisConfig(self) -> dict:
        """Devuelve el diccionario canónico de Capa 1 para el chasis."""
        return {
            "caras": {
                c: dict(self._caras[c]) for c in CARAS
            },
            "encuentros": {
                e: self._encuentros[e] for e in ENCUENTROS
            },
            "base": {
                "estrategia": self._base.get("estrategia", "zocalo"),
                "altura": float(self._base.get("altura", 100.0)),
                "separacion_frente": float(self._base.get("separacion_frente", 50.0)),
            }
        }

    # Aliases de compatibilidad y estilo snake_case
    set_chassis_config = setChassisConfig
    get_chassis_config = getChassisConfig


# ----------------------------------------------------------------------
# Ejecución Standalone para Validación Visual Directa
# ----------------------------------------------------------------------
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")

    # Paleta oscura global coherente
    paleta = QtGui.QPalette()
    paleta.setColor(QtGui.QPalette.Window, QtGui.QColor("#1e1e1e"))
    paleta.setColor(QtGui.QPalette.WindowText, QtGui.QColor("#e0e0e0"))
    paleta.setColor(QtGui.QPalette.Base, QtGui.QColor("#252525"))
    paleta.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor("#1e1e1e"))
    paleta.setColor(QtGui.QPalette.Text, QtGui.QColor("#e0e0e0"))
    paleta.setColor(QtGui.QPalette.Button, QtGui.QColor("#2b2b2b"))
    paleta.setColor(QtGui.QPalette.ButtonText, QtGui.QColor("#ffffff"))
    paleta.setColor(QtGui.QPalette.Highlight, QtGui.QColor("#007acc"))
    paleta.setColor(QtGui.QPalette.HighlightedText, QtGui.QColor("#ffffff"))
    app.setPalette(paleta)

    ventana = QtWidgets.QMainWindow()
    ventana.setWindowTitle("VDO Chassis Controller - Corte Transversal Interactivo 2D")
    ventana.setMinimumSize(360, 480)

    widget = VDOChassisControllerWidget()

    def on_change(cfg):
        activas = [c for c, d in cfg["caras"].items() if d.get("activa")]
        _LOG.debug(f"[VDO Chassis Event] Caras activas: {activas} | Encuentros: {cfg['encuentros']} | Base: {cfg['base']['estrategia']}")

    widget.sigChassisChanged.connect(on_change)

    ventana.setCentralWidget(widget)
    ventana.show()
    exec_func = getattr(app, "exec", getattr(app, "exec_", None))
    sys.exit(exec_func())
