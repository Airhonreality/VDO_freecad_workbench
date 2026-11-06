# =====================================================================
# cajon_task_construccion.py
# Construcción de la ventana del panel de cajón (mixin de CajonTaskPanel).
# Los campos vienen de la especificación datos/formularios.py (cajon_bloques)
# y se crean con FormBuilder (M6, MN-08, D-73).
# =====================================================================

from freecad.vdo.core.cajon_correderas import listar_marcas
from freecad.vdo.datos.formularios import cajon_bloques
from freecad.vdo.qt_compat import QtWidgets
from freecad.vdo.ui import tema
from freecad.vdo.ui.cajon_task_cabecera import PanelHeaderWidget
from freecad.vdo.ui.form_builder import FormBuilder


class CajonTaskConstruccionMixin:
    """Construye los widgets del panel de cajón (sin lógica de dominio)."""

    # -----------------------------------------------------------------
    # Construcción del widget
    # -----------------------------------------------------------------
    def _crear_widget(self):
        widget = QtWidgets.QWidget()
        tema.aplicar_estilo(widget, tema.ESTILO_CAJON)

        main_layout = QtWidgets.QVBoxLayout(widget)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(10)

        self.header = PanelHeaderWidget()
        main_layout.addWidget(self.header)

        self._form_builder = FormBuilder(widget)
        self._form_builder.construir_bloques(
            main_layout, cajon_bloques(listar_marcas()))
        self._enlazar_widgets()

        main_layout.addStretch()
        self._crear_botonera_vdo(main_layout)
        self._conectar_senales()
        return widget

    def _enlazar_widgets(self):
        """Nombres cortos de los widgets, usados por la carga, la escritura y los selectores."""
        fb = self._form_builder
        self.spin_li = fb.widget("li")
        self.spin_prof = fb.widget("prof")
        self.spin_ancho_mod = fb.widget("ancho_mod")
        self.spin_alto_frente = fb.widget("alto_frente")
        self.combo_tipo = fb.widget("tipo")
        self.combo_sku = fb.widget("sku")
        self.combo_marca = fb.widget("marca")
        self.spin_guia = fb.widget("guia")
        self.combo_montaje = fb.widget("montaje")
        self.combo_apertura = fb.widget("apertura")
        self.combo_montaje_fachada = fb.widget("montaje_fachada")
        self.spin_alto_caja = fb.widget("alto_caja")
        self.spin_g_caja = fb.widget("g_caja")
        self.spin_g_fondo = fb.widget("g_fondo")
        self.spin_g_fachada = fb.widget("g_fachada")
        self.spin_rotacion = fb.widget("rotacion")
        self.combo_anclaje = fb.widget("anclaje")

    def _conectar_senales(self):
        self.combo_tipo.currentIndexChanged.connect(self._on_tipo_cambiado)
        self.combo_apertura.currentIndexChanged.connect(
            self._on_apertura_cambiado)
        self._on_tipo_cambiado(0)
