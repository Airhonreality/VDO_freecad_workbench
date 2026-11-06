# =====================================================================
# cajon_task_construccion.py
# Construcción de la ventana del panel de cajón (mixin de CajonTaskPanel).
# =====================================================================

from freecad.vdo.core.vdo_cajon_correderas import listar_marcas
from freecad.vdo.core.vdo_module_props import ANCLAJE_LABELS, ANCLAJES
from freecad.vdo.qt_compat import QtWidgets
from freecad.vdo.ui.cajon_task_cabecera import PanelHeaderWidget
from freecad.vdo.ui.vdo_qt import VDO_DoubleSpinBox


class CajonTaskConstruccionMixin:
    """Construye los widgets del panel de cajón (sin lógica de dominio)."""


    # -----------------------------------------------------------------
    # Construcción del widget
    # -----------------------------------------------------------------
    def _crear_widget(self):
        widget = QtWidgets.QWidget()
        widget.setStyleSheet(
            "QWidget { background-color: #2b2b2b; color: #e0e0e0; }"
            "QGroupBox { font-weight: bold; color: #e0e0e0; "
            "border: 1px solid #555555; border-radius: 6px; "
            "margin-top: 10px; padding-top: 8px; }"
            "QGroupBox::title { subcontrol-origin: margin; left: 10px; "
            "padding: 0 4px; }"
            "QLabel { color: #e0e0e0; }"
            "QComboBox, QDoubleSpinBox, QSpinBox {"
            "  background-color: #3a3a3a; color: #e0e0e0;"
            "  border: 1px solid #555555; border-radius: 3px; padding: 3px;"
            "}"
            "QPushButton {"
            "  background-color: #3a3a3a; color: #e0e0e0;"
            "  border: 1px solid #555555; border-radius: 4px;"
            "  padding: 6px 14px; font-weight: bold;"
            "}"
            "QPushButton:hover { background-color: #444444; }")

        main_layout = QtWidgets.QVBoxLayout(widget)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(10)

        # --- PanelHeaderWidget (cabecera) ---
        self.header = PanelHeaderWidget()
        main_layout.addWidget(self.header)

        # --- Grupo: Espacio interior del mueble ---
        grupo_espacio = QtWidgets.QGroupBox("Espacio interior (datos de partida)")
        grid_esp = QtWidgets.QGridLayout(grupo_espacio)

        grid_esp.addWidget(QtWidgets.QLabel("Ancho libre LI (mm):"), 0, 0)
        self.spin_li = VDO_DoubleSpinBox()
        self.spin_li.setRange(1, 3000)
        self.spin_li.setSuffix(" mm")
        self.spin_li.setDecimals(1)
        grid_esp.addWidget(self.spin_li, 0, 1)

        grid_esp.addWidget(QtWidgets.QLabel("Profundidad libre (mm):"), 1, 0)
        self.spin_prof = VDO_DoubleSpinBox()
        self.spin_prof.setRange(1, 1500)
        self.spin_prof.setSuffix(" mm")
        self.spin_prof.setDecimals(1)
        grid_esp.addWidget(self.spin_prof, 1, 1)

        grid_esp.addWidget(QtWidgets.QLabel("Ancho módulo (fachada):"), 2, 0)
        self.spin_ancho_mod = VDO_DoubleSpinBox()
        self.spin_ancho_mod.setRange(1, 3000)
        self.spin_ancho_mod.setSuffix(" mm")
        self.spin_ancho_mod.setDecimals(1)
        grid_esp.addWidget(self.spin_ancho_mod, 2, 1)

        grid_esp.addWidget(QtWidgets.QLabel("Alto frente (mm):"), 3, 0)
        self.spin_alto_frente = VDO_DoubleSpinBox()
        self.spin_alto_frente.setRange(1, 800)
        self.spin_alto_frente.setSuffix(" mm")
        self.spin_alto_frente.setDecimals(1)
        grid_esp.addWidget(self.spin_alto_frente, 3, 1)

        main_layout.addWidget(grupo_espacio)

        # --- Grupo: Corredera y herraje ---
        grupo_herraje = QtWidgets.QGroupBox("Corredera y herraje")
        grid_h = QtWidgets.QGridLayout(grupo_herraje)

        grid_h.addWidget(QtWidgets.QLabel("Tipo de corredera:"), 0, 0)
        self.combo_tipo = QtWidgets.QComboBox()
        self.combo_tipo.addItems([
            "Oculta (Blum Tandem / Genérica)",
            "Telescópica",
            "Metálica (Slim Box / Tandembox)",
        ])
        self.combo_tipo.setToolTip(
            "Oculta: corredera bajo cajón con notch y pin.\n"
            "Telescópica: guía lateral con piso delgado en ranura.\n"
            "Metálica: sin laterales de madera, solo piso y trasera.")
        grid_h.addWidget(self.combo_tipo, 0, 1)

        grid_h.addWidget(QtWidgets.QLabel("SKU comercial:"), 1, 0)
        self.combo_sku = QtWidgets.QComboBox()
        self.combo_sku.setEditable(True)
        self.combo_sku.setToolTip(
            "SKU de la corredera (vía vdo_hardware_hub.py).")
        grid_h.addWidget(self.combo_sku, 1, 1)

        grid_h.addWidget(QtWidgets.QLabel("Marca:"), 2, 0)
        self.combo_marca = QtWidgets.QComboBox()
        self.combo_marca.addItems(listar_marcas())
        self.combo_marca.setToolTip(
            "Marca de corredera oculta (delta y cotas).")
        grid_h.addWidget(self.combo_marca, 2, 1)

        grid_h.addWidget(QtWidgets.QLabel("Longitud guía (mm):"), 3, 0)
        self.spin_guia = VDO_DoubleSpinBox()
        self.spin_guia.setRange(0, 800)
        self.spin_guia.setSuffix(" mm")
        self.spin_guia.setDecimals(0)
        self.spin_guia.setSpecialValueText("Auto (según profundidad)")
        grid_h.addWidget(self.spin_guia, 3, 1)

        grid_h.addWidget(QtWidgets.QLabel("Montaje trasera:"), 4, 0)
        self.combo_montaje = QtWidgets.QComboBox()
        self.combo_montaje.addItems(["entre_laterales", "testa"])
        grid_h.addWidget(self.combo_montaje, 4, 1)

        self.combo_tipo.currentIndexChanged.connect(self._on_tipo_cambiado)
        self._on_tipo_cambiado(0)

        main_layout.addWidget(grupo_herraje)

        # --- Grupo: Sistema de apertura (fachada) ---
        grupo_apertura = QtWidgets.QGroupBox("Sistema de apertura (fachada)")
        grid_a = QtWidgets.QGridLayout(grupo_apertura)

        grid_a.addWidget(QtWidgets.QLabel("Sistema:"), 0, 0)
        self.combo_apertura = QtWidgets.QComboBox()
        self.combo_apertura.addItems([
            "Tirador",
            "Gola aluminio (−35 mm altura)",
            "45° (bisel en arista superior)",
            "Push open (expulsor magnético)",
        ])
        self.combo_apertura.setToolTip(
            "Tirador: manija postiza, altura completa.\n"
            "Gola: perfil C/L integrado, descuenta 35 mm en altura.\n"
            "45°: bisel paramétrico en arista superior frontal.\n"
            "Push open: émbolo magnético, holgura perimetral ajustada.")
        self.combo_apertura.currentIndexChanged.connect(
            self._on_apertura_cambiado)
        grid_a.addWidget(self.combo_apertura, 0, 1)

        grid_a.addWidget(QtWidgets.QLabel("Montaje fachada:"), 1, 0)
        self.combo_montaje_fachada = QtWidgets.QComboBox()
        self.combo_montaje_fachada.addItems(["Parche", "Semiparche", "Embebida"])
        self.combo_montaje_fachada.setToolTip(
            "Parche: solapa sobre los cantos del vano.\n"
            "Semiparche: comparte montante central.\n"
            "Embebida: a ras dentro del vano (deja cantos vistos).")
        grid_a.addWidget(self.combo_montaje_fachada, 1, 1)

        main_layout.addWidget(grupo_apertura)

        # --- Grupo: Caja y fachada ---
        grupo_caja = QtWidgets.QGroupBox("Caja y fachada")
        grid_caja = QtWidgets.QGridLayout(grupo_caja)

        grid_caja.addWidget(QtWidgets.QLabel("Alto caja (mm):"), 0, 0)
        self.spin_alto_caja = VDO_DoubleSpinBox()
        self.spin_alto_caja.setRange(1, 300)
        self.spin_alto_caja.setSuffix(" mm")
        self.spin_alto_caja.setDecimals(1)
        grid_caja.addWidget(self.spin_alto_caja, 0, 1)

        grid_caja.addWidget(QtWidgets.QLabel("Grosor caja (mm):"), 1, 0)
        self.spin_g_caja = QtWidgets.QSpinBox()
        self.spin_g_caja.setRange(1, 25)
        self.spin_g_caja.setSuffix(" mm")
        grid_caja.addWidget(self.spin_g_caja, 1, 1)

        grid_caja.addWidget(QtWidgets.QLabel("Grosor piso (mm):"), 2, 0)
        self.spin_g_fondo = QtWidgets.QSpinBox()
        self.spin_g_fondo.setRange(1, 12)
        self.spin_g_fondo.setSuffix(" mm")
        grid_caja.addWidget(self.spin_g_fondo, 2, 1)

        grid_caja.addWidget(QtWidgets.QLabel("Grosor fachada (mm):"), 3, 0)
        self.spin_g_fachada = QtWidgets.QSpinBox()
        self.spin_g_fachada.setRange(1, 30)
        self.spin_g_fachada.setSuffix(" mm")
        grid_caja.addWidget(self.spin_g_fachada, 3, 1)

        main_layout.addWidget(grupo_caja)

        # --- Grupo: Colocación ---
        grupo_coloc = QtWidgets.QGroupBox("Colocación")
        grid_coloc = QtWidgets.QGridLayout(grupo_coloc)

        grid_coloc.addWidget(QtWidgets.QLabel("Rotación Z:"), 0, 0)
        self.spin_rotacion = VDO_DoubleSpinBox()
        self.spin_rotacion.setRange(-360.0, 360.0)
        self.spin_rotacion.setDecimals(1)
        self.spin_rotacion.setSuffix(" °")
        self.spin_rotacion.setWrapping(True)
        grid_coloc.addWidget(self.spin_rotacion, 0, 1)

        grid_coloc.addWidget(QtWidgets.QLabel("Anclaje:"), 1, 0)
        self.combo_anclaje = QtWidgets.QComboBox()
        for anclaje in ANCLAJES:
            self.combo_anclaje.addItem(
                ANCLAJE_LABELS.get(anclaje, anclaje), anclaje)
        grid_coloc.addWidget(self.combo_anclaje, 1, 1)

        main_layout.addWidget(grupo_coloc)
        main_layout.addStretch()

        # --- Botones ---
        botones = QtWidgets.QDialogButtonBox()
        botones.addButton(
            "Crear y colocar" if not self.auto_transaction else "Aplicar",
            QtWidgets.QDialogButtonBox.AcceptRole)
        botones.addButton(
            "Cancelar", QtWidgets.QDialogButtonBox.RejectRole)
        botones.accepted.connect(self._on_ok)
        botones.rejected.connect(self._on_cancel)
        main_layout.addWidget(botones)

        return widget
