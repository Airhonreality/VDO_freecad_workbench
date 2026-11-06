"""
vdo_box_controller.py

Controlador espacial 2D de tablero al estilo Figma Box Model / CSS DevTools.
Implementa el "Cuadrado Paramétrico Gestáltico" con líneas de distinto calibre (1px y 3px)
para parametrizar visualmente tanto el ANCHO de las tiras como el OFFSET (distancia al canto / retranqueo).

Arquitectura Gestáltica de Doble Anillo (Opción A):
    - Calibre 1 px (Exterior): Canto físico del tablero y selección de márgenes.
    - Calibre 3 px (Interior): Tiras de melamina activas / inactivas.
    - Brecha concéntrica variable: Muestra visualmente si la tira está al ras (0 mm)
      o retranqueada (>0 mm) con línea guía de acotación.
    - Acceso rápido de taller: Chips para 0 (al ras), 18 (1 espesor), 36 (2 espesores), 50 (zócalo).

Totalmente agnóstico de FreeCAD: compatible con PySide, PySide2 y PySide6.
"""

import logging
import sys

from freecad.vdo.core import (
    vdo_reengrose_modelo as VDO_RE_MODELO,
    vdo_reengrose_modificador as VDO_RE_MODIFICADOR,
)
from freecad.vdo.qt_compat import QtCore, QtGui, QtWidgets
from freecad.vdo.ui.vdo_qt import VDO_DoubleSpinBox

from freecad.vdo.ui.box_canvas import _VDOConcentricCenterCanvas
from freecad.vdo.ui.box_constantes import (
    ENCUENTRO_LABELS,
    ENCUENTRO_TOOLTIPS,
    ESQUINAS,
    TIPOS_ENCUENTRO,
    _TEXTO_BOTON_BORDE,
    obtener_svg_icon,
)
from freecad.vdo.ui.box_hoja_estilos import ESTILO_WIDGET

_LOG = logging.getLogger(__name__)


# ----------------------------------------------------------------------
# Widget Principal VDOBoxControllerWidget
# ----------------------------------------------------------------------
class VDOBoxControllerWidget(QtWidgets.QWidget):
    """
    Controlador interactivo espacial de borde perimetral estilo Figma Box Model.
    Implementa el Cuadrado Gestáltico con calibres 1px (Canto/Offset) y 3px (Tira).
    """

    sigConfigChanged = QtCore.Signal(dict)
    changed = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("VDOBoxRoot")
        self.setStyleSheet(ESTILO_WIDGET)

        self._cargando = False
        self._margen_seleccionado = "frente"
        self._borde_seleccionado = "frente"
        self._valores_bordes = {
            borde: {"ancho": 70.0, "offset": 0.0}
            for borde in VDO_RE_MODELO.BORDES_2D
        }
        self._esquinas = {
            esquina: "vertical_domina"
            for esquina in ESQUINAS
        }
        self._fabricacion = "pacha"
        self._choque_nucleo = "retroceso"
        self._cara = "cara_a"

        self._construir_ui()
        self._conectar_senales()
        self._actualizar_canvas_concentrico()
        self._actualizar_estado_all()
        self._actualizar_iconos_esquinas()
        self._actualizar_resumen()

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

        # 2. Marco del Cuadrado Espacial Concéntrico
        self.container_canvas = QtWidgets.QFrame()
        self.container_canvas.setObjectName("canvas_container")
        grid = QtWidgets.QGridLayout(self.container_canvas)
        grid.setContentsMargins(6, 6, 6, 6)
        grid.setSpacing(4)

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

        # CENTRO: Canvas Concéntrico (Calibre 1px Canto + Calibre 3px Tiras + Brecha Offset)
        self.center_box = QtWidgets.QFrame()
        self.center_box.setStyleSheet("background: transparent;")
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

        # Alias chk_uniforme para compatibilidad backward
        self.chk_uniforme = self.btn_centro

        # 3. Selector Gestáltico de Margen
        bar_margenes = QtWidgets.QHBoxLayout()
        self.lbl_margen_tag = QtWidgets.QLabel("Margen:")
        self.lbl_margen_tag.setStyleSheet("font-weight: bold; color: #007acc;")
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

        # 5. Chips de Acceso Rápido para Offset de Taller
        bar_quick_offset = QtWidgets.QHBoxLayout()
        lbl_quick = QtWidgets.QLabel("Offset rápido:")
        lbl_quick.setStyleSheet("color: #888888; font-size: 10px;")
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

        # Compatibilidad: spins individuales mapeados en dict
        self.spin_ancho_borde = {}
        self.spin_offset_borde = {}
        for b in VDO_RE_MODELO.BORDES_2D:
            self.spin_ancho_borde[b] = self._spin(70.0)
            self.spin_offset_borde[b] = self._spin(0.0)

        # 6. Resumen compacto
        self.lbl_resumen = QtWidgets.QLabel("Sin reengrose.")
        self.lbl_resumen.setWordWrap(True)
        self.lbl_resumen.setStyleSheet(
            "QLabel { background: #252525; color: #d0d0d0; padding: 4px 6px; "
            "border: 1px solid #3a3a3a; border-radius: 4px; font-size: 11px; }")
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

    # ------------------------------------------------------------------
    # Lógica de Interacción (State Machine y Poka-Yoke)
    # ------------------------------------------------------------------
    def _on_activo_toggled(self, activo):
        if self._cargando:
            return
        if activo and not self._hay_bordes_activos():
            self._cargando = True
            self.btn_borde["frente"].setChecked(True)
            self._cargando = False
        self._actualizar_estado_habilitacion()
        self._actualizar_estado_all()
        self._actualizar_canvas_concentrico()
        self._emitir_cambio()

    def _hay_bordes_activos(self):
        return any(self.btn_borde[b].isChecked() for b in VDO_RE_MODELO.BORDES_2D)

    def _on_all_clicked(self):
        if self._cargando:
            return
        activos_actuales = sum(1 for b in VDO_RE_MODELO.BORDES_2D if self.btn_borde[b].isChecked())
        nuevo_estado = (activos_actuales < len(VDO_RE_MODELO.BORDES_2D))

        self._cargando = True
        for b in VDO_RE_MODELO.BORDES_2D:
            self.btn_borde[b].setChecked(nuevo_estado)
        self.btn_all.setChecked(nuevo_estado)
        if nuevo_estado and not self.chk_activo.isChecked():
            self.chk_activo.setChecked(True)
        self._cargando = False

        self._actualizar_estado_habilitacion()
        self._actualizar_canvas_concentrico()
        self._emitir_cambio()

    def _on_borde_clicked(self, borde):
        if self._cargando:
            return
        self._seleccionar_margen(borde)
        if self.btn_borde[borde].isChecked() and not self.chk_activo.isChecked():
            self._cargando = True
            self.chk_activo.setChecked(True)
            self._cargando = False
        self._actualizar_estado_all()
        self._actualizar_canvas_concentrico()
        self._emitir_cambio()

    def _seleccionar_margen(self, margen):
        self._margen_seleccionado = margen
        self._borde_seleccionado = margen

        # Actualizar estilo de chips de margen
        for b, btn in self.btn_margenes.items():
            btn.blockSignals(True)
            btn.setChecked(b == margen)
            btn.blockSignals(False)

        # Actualizar etiquetas de botones de borde
        for b, btn in self.btn_borde.items():
            btn.setProperty("selected", "true" if b == margen else "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)

        self.lbl_margen_tag.setText(f"Margen: <b>{margen.upper()}</b>")

        # Cargar valores en los spinboxes principales si estamos en modo individual
        if not self.btn_centro.isChecked():
            self._cargando = True
            w = self._valores_bordes[margen]["ancho"]
            d = self._valores_bordes[margen]["offset"]
            self.spin_ancho.setValue(w)
            self.spin_offset.setValue(d)
            self._cargando = False

        self._actualizar_canvas_concentrico()

    def _aplicar_chip_offset(self, val):
        self.spin_offset.setValue(float(val))

    def _on_spin_ancho_changed(self):
        if self._cargando:
            return
        w = self.spin_ancho.value()
        if self.btn_centro.isChecked():
            # Uniforme: replicar a todos los bordes
            for b in VDO_RE_MODELO.BORDES_2D:
                self._valores_bordes[b]["ancho"] = w
                self.spin_ancho_borde[b].setValue(w)
        else:
            # Individual: aplicar solo al margen seleccionado
            m = self._margen_seleccionado
            self._valores_bordes[m]["ancho"] = w
            self.spin_ancho_borde[m].setValue(w)

        self._actualizar_canvas_concentrico()
        self._emitir_cambio()

    def _on_spin_offset_changed(self):
        if self._cargando:
            return
        d = self.spin_offset.value()
        if self.btn_centro.isChecked():
            # Uniforme: replicar a todos los bordes
            for b in VDO_RE_MODELO.BORDES_2D:
                self._valores_bordes[b]["offset"] = d
                self.spin_offset_borde[b].setValue(d)
        else:
            # Individual: aplicar solo al margen seleccionado
            m = self._margen_seleccionado
            self._valores_bordes[m]["offset"] = d
            self.spin_offset_borde[m].setValue(d)

        self._actualizar_canvas_concentrico()
        self._emitir_cambio()

    def _on_uniforme_toggled(self):
        if self._cargando:
            return
        uniforme = self.btn_centro.isChecked()
        self._cargando = True
        if uniforme:
            self.btn_centro.setText(" Uniforme")
            self.btn_centro.setIcon(obtener_svg_icon("link"))
            ancho_u = self.spin_ancho.value()
            dist_u = self.spin_offset.value()
            for b in VDO_RE_MODELO.BORDES_2D:
                self._valores_bordes[b]["ancho"] = ancho_u
                self._valores_bordes[b]["offset"] = dist_u
                self.spin_ancho_borde[b].setValue(ancho_u)
                self.spin_offset_borde[b].setValue(dist_u)
        else:
            self.btn_centro.setText(" Individual")
            self.btn_centro.setIcon(obtener_svg_icon("unlink"))
            m = self._margen_seleccionado
            self.spin_ancho.setValue(self._valores_bordes[m]["ancho"])
            self.spin_offset.setValue(self._valores_bordes[m]["offset"])

        self._cargando = False
        self._actualizar_canvas_concentrico()
        self._emitir_cambio()

    def _actualizar_estado_all(self):
        todos = all(self.btn_borde[b].isChecked() for b in VDO_RE_MODELO.BORDES_2D)
        self.btn_all.blockSignals(True)
        self.btn_all.setChecked(todos)
        self.btn_all.blockSignals(False)

    def _actualizar_canvas_concentrico(self):
        activos = {b: self.btn_borde[b].isChecked() for b in VDO_RE_MODELO.BORDES_2D}
        self.canvas_concentrico.actualizar(
            activos, self._valores_bordes, self._esquinas, self._margen_seleccionado)

        # Actualizar texto explicativo en los 4 botones de borde
        for b in VDO_RE_MODELO.BORDES_2D:
            btn = self.btn_borde[b]
            w = self._valores_bordes[b]["ancho"]
            d = self._valores_bordes[b]["offset"]
            texto_offset = "0 mm (ras)" if d == 0.0 else f"⇥ {d:.0f} mm"

            plantilla = _TEXTO_BOTON_BORDE.get(b)
            if plantilla is not None:
                btn.setText(plantilla(w, texto_offset))

    def _on_esquina_clicked(self, esquina):
        if self._cargando:
            return
        esquina = {
            "no": "fondo_izquierda", "ne": "fondo_derecha",
            "so": "frente_izquierda", "se": "frente_derecha"
        }.get(esquina.lower(), esquina)
        actual = self._esquinas[esquina]
        idx = (TIPOS_ENCUENTRO.index(actual) + 1) % len(TIPOS_ENCUENTRO)
        nuevo_tipo = TIPOS_ENCUENTRO[idx]

        self._cargando = True
        self.combo_esquina[esquina].blockSignals(True)
        idx_c = self.combo_esquina[esquina].findData(nuevo_tipo)
        if idx_c >= 0:
            self.combo_esquina[esquina].setCurrentIndex(idx_c)
        self.combo_esquina[esquina].blockSignals(False)
        self._cargando = False

        self._on_combo_esquina_changed(esquina)

    def _on_combo_esquina_changed(self, esquina):
        if self._cargando:
            return
        esquina = {
            "no": "fondo_izquierda", "ne": "fondo_derecha",
            "so": "frente_izquierda", "se": "frente_derecha"
        }.get(esquina.lower(), esquina)
        tipo = self.combo_esquina[esquina].currentData()
        if not tipo:
            return
        self._esquinas[esquina] = tipo

        if self.chk_sync_esquinas.isChecked():
            self._cargando = True
            for e in ESQUINAS:
                if e != esquina:
                    self._esquinas[e] = tipo
                    self._set_combo_silencioso(self.combo_esquina[e], tipo)
            self._cargando = False

        self._actualizar_iconos_esquinas()
        self._actualizar_canvas_concentrico()
        self._emitir_cambio()

    def _on_sync_esquinas_toggled(self, activo):
        if self._cargando:
            return
        if activo:
            tipo = self._esquinas["frente_izquierda"]
            self._cargando = True
            for e in ESQUINAS:
                self._esquinas[e] = tipo
                self._set_combo_silencioso(self.combo_esquina[e], tipo)
            self._cargando = False
            self._actualizar_iconos_esquinas()
            self._actualizar_canvas_concentrico()
            self._emitir_cambio()

    def _actualizar_iconos_esquinas(self):
        for e in ESQUINAS:
            tipo = self._esquinas[e]
            btn = self.btn_esquina[e]
            btn.setIcon(obtener_svg_icon(tipo, 20))
            btn.setToolTip(f"Esquina {e}:\n{ENCUENTRO_TOOLTIPS.get(tipo, tipo)}")

    def _actualizar_estado_habilitacion(self):
        activo = self.chk_activo.isChecked()
        self.container_canvas.setEnabled(activo)
        self.btn_all.setEnabled(activo)
        self.chk_sync_esquinas.setEnabled(activo)
        self.panel_medidas.setEnabled(activo)

    def _actualizar_estado(self):
        """Alias retrocompatible."""
        self._actualizar_estado_habilitacion()

    @staticmethod
    def _set_combo_data(combo, valor):
        """Establece el valor de un QComboBox buscando en su userData."""
        idx = combo.findData(valor)
        if idx >= 0:
            combo.setCurrentIndex(idx)

    def _actualizar_resumen(self):
        if not self.chk_activo.isChecked():
            self.lbl_resumen.setText("Reengrose desactivado.")
            return
        activos = [b for b in VDO_RE_MODELO.BORDES_2D if self.btn_borde[b].isChecked()]
        if not activos:
            self.lbl_resumen.setText("Sin bordes perimetrales activos.")
            return

        nombres = [b.capitalize() for b in activos]
        if self.btn_centro.isChecked():
            offset_val = self.spin_offset.value()
            offset_txt = "al ras (offset 0)" if offset_val == 0 else f"offset {offset_val:.1f} mm"
            medidas = f"ancho {self.spin_ancho.value():.1f} mm · {offset_txt}"
        else:
            detalles = []
            for b in activos:
                w = self._valores_bordes[b]["ancho"]
                d = self._valores_bordes[b]["offset"]
                detalles.append(f"{b.capitalize()}: {w:.0f}mm @ {d:.0f}mm")
            medidas = " · ".join(detalles)

        tipos_esq = set(self._esquinas.values())
        if len(tipos_esq) == 1:
            texto_esq = ENCUENTRO_LABELS[next(iter(tipos_esq))]
        else:
            texto_esq = "Esquinas mixtas"

        esp = self.spin_espesor.value()
        texto_esp = f" · Espesor {esp:.1f} mm" if esp > 0 else ""

        self.lbl_resumen.setText(
            f"<b>{len(activos)} bordes</b> ({', '.join(nombres)})<br/>"
            f"{medidas}{texto_esp} · <i>{texto_esq}</i>"
        )

    def _emitir_cambio(self):
        if self._cargando:
            return
        self._actualizar_resumen()
        cfg = self.getConfig()
        self.sigConfigChanged.emit(cfg)
        self.changed.emit()

    @staticmethod
    def _set_combo_silencioso(combo, valor):
        combo.blockSignals(True)
        idx = combo.findData(valor)
        if idx >= 0:
            combo.setCurrentIndex(idx)
        combo.blockSignals(False)

    # ------------------------------------------------------------------
    # API Pública del Widget
    # ------------------------------------------------------------------
    def setConfig(self, cfg):
        """Carga la configuración existente en la UI sin emitir señales redundantes."""
        if cfg is None:
            cfg = {}
        elif hasattr(cfg, "to_dict"):
            cfg = cfg.to_dict()

        self._cargando = True
        try:
            # 1. Activo
            activo = bool(cfg.get("activo", False))
            self.chk_activo.setChecked(activo)

            # 2. Esquinas
            esquinas_raw = cfg.get("esquinas", VDO_RE_MODELO.ENCUENTRO_ESQUINAS_DEFAULT)
            esquinas_norm = VDO_RE_MODIFICADOR._normalizar_encuentro(esquinas_raw)
            for e in ESQUINAS:
                tipo = esquinas_norm.get(e, "vertical_domina")
                self._esquinas[e] = tipo
                self._set_combo_silencioso(self.combo_esquina[e], tipo)

            esquinas_unicas = len(set(self._esquinas.values())) == 1
            self.chk_sync_esquinas.setChecked(esquinas_unicas)
            self._actualizar_iconos_esquinas()

            # 3. Bordes
            bordes_data = cfg.get("bordes", {})
            activos = []
            for b in VDO_RE_MODELO.BORDES_2D:
                b_cfg = bordes_data.get(b, {})
                if hasattr(b_cfg, "to_dict"):
                    b_cfg = b_cfg.to_dict()
                b_activo = bool(b_cfg.get("activo", False))
                w = float(b_cfg.get("ancho", cfg.get("ancho", 70.0)))
                d = float(b_cfg.get("distancia_al_canto",
                                   b_cfg.get("offset_borde",
                                             cfg.get("offset", 0.0))))

                self.btn_borde[b].setChecked(b_activo)
                if b_activo:
                    activos.append(b)

                self._valores_bordes[b]["ancho"] = w
                self._valores_bordes[b]["offset"] = d
                self.spin_ancho_borde[b].setValue(w)
                self.spin_offset_borde[b].setValue(d)

            # Formato legacy sin bordes explícitos
            if not bordes_data and activo:
                self.btn_borde["frente"].setChecked(True)
                activos.append("frente")

            # 4. Modo Uniforme
            es_uniforme = cfg.get("uniforme")
            if es_uniforme is None:
                if activos:
                    w0 = self._valores_bordes[activos[0]]["ancho"]
                    d0 = self._valores_bordes[activos[0]]["offset"]
                    es_uniforme = all(
                        abs(self._valores_bordes[b]["ancho"] - w0) < 1e-4
                        and abs(self._valores_bordes[b]["offset"] - d0) < 1e-4
                        for b in activos
                    )
                else:
                    es_uniforme = True

            self.btn_centro.setChecked(es_uniforme)
            if es_uniforme:
                self.btn_centro.setText(" Uniforme")
                self.btn_centro.setIcon(obtener_svg_icon("link"))
            else:
                self.btn_centro.setText(" Individual")
                self.btn_centro.setIcon(obtener_svg_icon("unlink"))

            primero = activos[0] if activos else "frente"
            ancho_ref = self._valores_bordes[primero]["ancho"]
            dist_ref = self._valores_bordes[primero]["offset"]
            self.spin_ancho.setValue(float(cfg.get("ancho_uniforme", ancho_ref)))
            self.spin_offset.setValue(float(cfg.get("distancia_uniforme", dist_ref)))

            # 5. Espesor y parámetros de fabricación
            esp = cfg.get("espesor")
            self.spin_espesor.setValue(0.0 if esp is None else float(esp))
            self._fabricacion = cfg.get("fabricacion", "pacha")
            self._choque_nucleo = cfg.get("choque_nucleo", "retroceso")
            self._cara = cfg.get("cara", "cara_a")

            self._seleccionar_margen(self._margen_seleccionado)
            self._actualizar_estado_all()
            self._actualizar_estado_habilitacion()
            self._actualizar_canvas_concentrico()
            self._actualizar_resumen()

        finally:
            self._cargando = False

    def getConfig(self) -> dict:
        """Retorna la estructura compatible con vdo_reengrose.py."""
        uniforme = self.btn_centro.isChecked()
        ancho_u = float(self.spin_ancho.value())
        dist_u = float(self.spin_offset.value())
        esp_val = self.spin_espesor.value()
        espesor = float(esp_val) if esp_val > 0.0 else None

        bordes = {}
        for b in VDO_RE_MODELO.BORDES_2D:
            activo = self.btn_borde[b].isChecked()
            if uniforme:
                w = ancho_u
                d = dist_u
            else:
                w = float(self._valores_bordes[b]["ancho"])
                d = float(self._valores_bordes[b]["offset"])
            bordes[b] = {
                "activo": activo,
                "ancho": w,
                "offset_borde": d,
                "distancia_al_canto": d,
                "largo_tira": "marco_interior",
                "espesor": espesor,
            }

        esquinas = {e: self._esquinas[e] for e in ESQUINAS}

        return {
            "activo": bool(self.chk_activo.isChecked()),
            "uniforme": bool(uniforme),
            "ancho_uniforme": ancho_u,
            "distancia_uniforme": dist_u,
            "esquinas": esquinas,
            "bordes": bordes,
            "fabricacion": self._fabricacion,
            "choque_nucleo": self._choque_nucleo,
            "cara": self._cara,
            "espesor": espesor,
            "usa_bordes": True,
        }

    # Métodos compatibles con ReengroseModifier / ReengroseDTO / Convenciones Snake Case
    get_config = getConfig
    set_config = setConfig
    seleccionar_margen = _seleccionar_margen

    def cargar(self, modifier):
        """Alias para cargar un dict o ReengroseModifier."""
        self.setConfig(modifier)

    def leer_modificador(self):
        """Devuelve un objeto ReengroseModifier listo para el cálculo."""
        return VDO_RE_MODIFICADOR.ReengroseModifier(self.getConfig())

    def set_dimensiones_panel(self, ancho, fondo):
        """Referencia de medidas brutas."""
        pass


# ----------------------------------------------------------------------
# Ejecución Directa Standalone para Validación Visual
# ----------------------------------------------------------------------
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")

    # Paleta oscura global
    paleta = QtGui.QPalette()
    paleta.setColor(QtGui.QPalette.Window, QtGui.QColor("#1e1e1e"))
    paleta.setColor(QtGui.QPalette.WindowText, QtGui.QColor("#e0e0e0"))
    paleta.setColor(QtGui.QPalette.Base, QtGui.QColor("#252525"))
    paleta.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor("#1e1e1e"))
    paleta.setColor(QtGui.QPalette.ToolTipBase, QtGui.QColor("#ffffff"))
    paleta.setColor(QtGui.QPalette.ToolTipText, QtGui.QColor("#ffffff"))
    paleta.setColor(QtGui.QPalette.Text, QtGui.QColor("#e0e0e0"))
    paleta.setColor(QtGui.QPalette.Button, QtGui.QColor("#2b2b2b"))
    paleta.setColor(QtGui.QPalette.ButtonText, QtGui.QColor("#ffffff"))
    paleta.setColor(QtGui.QPalette.Highlight, QtGui.QColor("#007acc"))
    paleta.setColor(QtGui.QPalette.HighlightedText, QtGui.QColor("#ffffff"))
    app.setPalette(paleta)

    ventana = QtWidgets.QMainWindow()
    ventana.setWindowTitle("VDO Box Controller - Cuadrado Concéntrico Gestáltico (1px / 3px)")
    ventana.setMinimumSize(320, 440)

    widget = VDOBoxControllerWidget()
    widget.setConfig({
        "activo": True,
        "uniforme": True,
        "ancho_uniforme": 70.0,
        "distancia_uniforme": 0.0,
        "esquinas": "inglete_45",
        "bordes": {
            b: {"activo": True, "ancho": 70.0, "offset_borde": 0.0}
            for b in VDO_RE_MODELO.BORDES_2D
        }
    })

    def on_change(cfg):
        activos = [b for b, d in cfg["bordes"].items() if d["activo"]]
        _LOG.debug(f"[VDO Box Event] Activos={activos} Esquinas={cfg['esquinas']} Uniforme={cfg['uniforme']}")

    widget.sigConfigChanged.connect(on_change)

    ventana.setCentralWidget(widget)
    ventana.show()
    exec_func = getattr(app, "exec", getattr(app, "exec_", None))
    sys.exit(exec_func())
