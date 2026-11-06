# =====================================================================
# puerta_task_construccion.py
# Construccion del formulario del panel de puerta (mixin de PuertaTaskPanel).
# =====================================================================

from freecad.vdo.core.aperturas import ETIQUETAS
from freecad.vdo.core.vdo_module_props import (
    ANCLAJE_LABELS,
    ANCLAJES,
)
from freecad.vdo.core.vdo_puerta_despiece import SISTEMAS_APERTURA
from freecad.vdo.qt_compat import QtWidgets
from freecad.vdo.ui.puerta_task_cabecera import PanelHeaderWidget
from freecad.vdo.ui.puerta_task_constantes import (
    COLOR_BORDE,
    COLOR_FONDO,
    COLOR_TEXTO,
    FAMILIAS,
    SENTIDOS_BATIENTE,
)
from freecad.vdo.ui.vdo_qt import VDO_DoubleSpinBox


class PuertaTaskConstruccionMixin:
    """Construye el formulario de PuertaTaskPanel (sin cambios de comportamiento)."""

    # -----------------------------------------------------------------
    # Construcción del formulario
    # -----------------------------------------------------------------
    def _crear_widget(self):
        widget = QtWidgets.QWidget()
        widget.setStyleSheet(f"QWidget {{ background: {COLOR_FONDO}; "
                             f"color: {COLOR_TEXTO}; }}")
        main = QtWidgets.QVBoxLayout(widget)
        main.setContentsMargins(8, 8, 8, 8)
        main.setSpacing(8)

        # --- Cabecera universal de pieza (obligatoria por Manifiesto UI) ---
        self.header = PanelHeaderWidget()
        self.header.set_pieza("Puerta", 0, 0, 0)
        main.addWidget(self.header)

        # --- Familia ---
        grp_fam = QtWidgets.QGroupBox("Familia de puerta")
        grp_fam.setStyleSheet(
            f"QGroupBox {{ color: {COLOR_TEXTO}; border: 1px solid "
            f"{COLOR_BORDE}; border-radius: 4px; margin-top: 8px; }}"
            f"QGroupBox::title {{ subcontrol-origin: margin; left: 8px; }}")
        grid_fam = QtWidgets.QGridLayout(grp_fam)
        grid_fam.addWidget(QtWidgets.QLabel("Tipo de sistema:"), 0, 0)
        self.combo_sistema = QtWidgets.QComboBox()
        self.combo_sistema.addItems(FAMILIAS)
        self.combo_sistema.setToolTip(
            "Batiente Vertical, Basculante Horizontal o Corrediza.")
        grid_fam.addWidget(self.combo_sistema, 0, 1)
        main.addWidget(grp_fam)

        # --- Montaje (solo batiente) ---
        self.grp_montaje = QtWidgets.QGroupBox("Montaje (batiente)")
        self.grp_montaje.setStyleSheet(grp_fam.styleSheet())
        grid_m = QtWidgets.QGridLayout(self.grp_montaje)
        grid_m.addWidget(QtWidgets.QLabel("Tipo de montaje:"), 0, 0)
        self.combo_montaje = QtWidgets.QComboBox()
        self.combo_montaje.addItems(["Parche", "Semiparche", "Embebida"])
        grid_m.addWidget(self.combo_montaje, 0, 1)
        grid_m.addWidget(QtWidgets.QLabel("Sentido de apertura:"), 1, 0)
        self.combo_sentido = QtWidgets.QComboBox()
        self.combo_sentido.addItems(SENTIDOS_BATIENTE)
        grid_m.addWidget(self.combo_sentido, 1, 1)
        main.addWidget(self.grp_montaje)

        # --- Dimensiones ---
        grp_dim = QtWidgets.QGroupBox("Dimensiones de la puerta (mm)")
        grp_dim.setStyleSheet(grp_fam.styleSheet())
        grid_d = QtWidgets.QGridLayout(grp_dim)

        grid_d.addWidget(QtWidgets.QLabel("Ancho (W):"), 0, 0)
        self.spin_ancho = VDO_DoubleSpinBox()
        self.spin_ancho.setRange(100, 3000)
        self.spin_ancho.setSuffix(" mm")
        self.spin_ancho.setDecimals(1)
        grid_d.addWidget(self.spin_ancho, 0, 1)

        grid_d.addWidget(QtWidgets.QLabel("Alto (H):"), 1, 0)
        self.spin_alto = VDO_DoubleSpinBox()
        self.spin_alto.setRange(100, 2600)
        self.spin_alto.setSuffix(" mm")
        self.spin_alto.setDecimals(1)
        grid_d.addWidget(self.spin_alto, 1, 1)

        grid_d.addWidget(QtWidgets.QLabel("Espesor (mm):"), 2, 0)
        self.spin_espesor = QtWidgets.QSpinBox()
        self.spin_espesor.setRange(10, 50)
        self.spin_espesor.setSuffix(" mm")
        self.spin_espesor.setValue(18)
        grid_d.addWidget(self.spin_espesor, 2, 1)

        main.addWidget(grp_dim)

        # --- Sistema de apertura ---
        grp_ape = QtWidgets.QGroupBox("Sistema de apertura / fachada")
        grp_ape.setStyleSheet(grp_fam.styleSheet())
        grid_a = QtWidgets.QGridLayout(grp_ape)
        grid_a.addWidget(QtWidgets.QLabel("Tipo:"), 0, 0)
        self.combo_apertura = QtWidgets.QComboBox()
        self.combo_apertura.addItems(
            [ETIQUETAS[k] for k in SISTEMAS_APERTURA])
        grid_a.addWidget(self.combo_apertura, 0, 1)
        main.addWidget(grp_ape)

        # --- Herraje comercial (dropdown poblado desde Capa H) ---
        self.grp_herraje = QtWidgets.QGroupBox("Herraje comercial")
        self.grp_herraje.setStyleSheet(grp_fam.styleSheet())
        grid_h = QtWidgets.QGridLayout(self.grp_herraje)
        grid_h.addWidget(QtWidgets.QLabel("SKU:"), 0, 0)
        self.combo_sku = QtWidgets.QComboBox()
        grid_h.addWidget(self.combo_sku, 0, 1)
        self.lbl_herraje_info = QtWidgets.QLabel("")
        self.lbl_herraje_info.setWordWrap(True)
        self.lbl_herraje_info.setStyleSheet(
            f"QLabel {{ background: #2b2b2b; color: {COLOR_TEXTO}; "
            f"padding: 4px; border: 1px solid {COLOR_BORDE}; }}")
        grid_h.addWidget(self.lbl_herraje_info, 1, 0, 1, 2)
        main.addWidget(self.grp_herraje)

        # --- Pistón a gas (solo basculante) ---
        self.grp_piston = QtWidgets.QGroupBox("Cálculo de pistón a gas")
        self.grp_piston.setStyleSheet(grp_fam.styleSheet())
        grid_p = QtWidgets.QGridLayout(self.grp_piston)
        self.lbl_piston = QtWidgets.QLabel("")
        self.lbl_piston.setWordWrap(True)
        self.lbl_piston.setStyleSheet(
            "QLabel { background: #1e4a1e; color: #8fbc8f; padding: 6px; "
            "border: 1px solid #3a7a3a; font-weight: bold; }")
        grid_p.addWidget(self.lbl_piston, 0, 0, 1, 2)
        main.addWidget(self.grp_piston)

        # --- Expulsor magnético (solo push) ---
        self.chk_expulsor = QtWidgets.QCheckBox("Inyectar expulsor magnético al BOM")
        self.chk_expulsor.setStyleSheet(f"color: {COLOR_TEXTO};")
        main.addWidget(self.chk_expulsor)

        # --- Posición ---
        grp_pos = QtWidgets.QGroupBox("Posición (mm)")
        grp_pos.setStyleSheet(grp_fam.styleSheet())
        grid_p = QtWidgets.QGridLayout(grp_pos)
        grid_p.addWidget(QtWidgets.QLabel("Pos X:"), 0, 0)
        self.spin_pos_x = VDO_DoubleSpinBox()
        self.spin_pos_x.setRange(-5000, 5000)
        self.spin_pos_x.setSuffix(" mm")
        self.spin_pos_x.setDecimals(1)
        grid_p.addWidget(self.spin_pos_x, 0, 1)
        grid_p.addWidget(QtWidgets.QLabel("Pos Y:"), 1, 0)
        self.spin_pos_y = VDO_DoubleSpinBox()
        self.spin_pos_y.setRange(-5000, 5000)
        self.spin_pos_y.setSuffix(" mm")
        self.spin_pos_y.setDecimals(1)
        grid_p.addWidget(self.spin_pos_y, 1, 1)
        grid_p.addWidget(QtWidgets.QLabel("Pos Z:"), 2, 0)
        self.spin_pos_z = VDO_DoubleSpinBox()
        self.spin_pos_z.setRange(-5000, 5000)
        self.spin_pos_z.setSuffix(" mm")
        self.spin_pos_z.setDecimals(1)
        grid_p.addWidget(self.spin_pos_z, 2, 1)
        main.addWidget(grp_pos)

        # --- Anclaje ---
        grid_p.addWidget(QtWidgets.QLabel("Anclaje:"), 3, 0)
        self.combo_anclaje = QtWidgets.QComboBox()
        self.combo_anclaje.setStyleSheet(f"color: {COLOR_TEXTO};")
        for a in ANCLAJES:
            self.combo_anclaje.addItem(ANCLAJE_LABELS.get(a, a), a)
        grid_p.addWidget(self.combo_anclaje, 3, 1)

        main.addStretch()

        # Botones
        botones = QtWidgets.QDialogButtonBox()
        botones.addButton(
            "Aplicar" if self.auto_transaction else "Crear y colocar",
            QtWidgets.QDialogButtonBox.AcceptRole)
        botones.addButton(
            "Cancelar", QtWidgets.QDialogButtonBox.RejectRole)
        botones.accepted.connect(self._on_ok)
        botones.rejected.connect(self._on_cancel)
        main.addWidget(botones)

        # Señales de cambio
        self.combo_sistema.currentIndexChanged.connect(self._on_cambio_sistema)
        self.combo_apertura.currentIndexChanged.connect(self._actualizar_todo)
        self.combo_sku.currentIndexChanged.connect(self._actualizar_herraje_info)
        self.combo_montaje.currentIndexChanged.connect(self._actualizar_todo)
        self.combo_sentido.currentIndexChanged.connect(self._actualizar_todo)
        self.spin_ancho.valueChanged.connect(self._actualizar_todo)
        self.spin_alto.valueChanged.connect(self._actualizar_todo)
        self.spin_espesor.valueChanged.connect(self._actualizar_todo)

        return widget
