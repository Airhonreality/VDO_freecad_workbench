# =====================================================================
# puerta_task_construccion.py
# Construccion del formulario del panel de puerta (mixin de PuertaTaskPanel).
# Los campos vienen de la especificacion datos/formularios.py (PUERTA_BLOQUES)
# y se crean con FormBuilder (M6, MN-08, D-72).
# =====================================================================

from freecad.vdo.datos.formularios import PUERTA_BLOQUES
from freecad.vdo.qt_compat import QtWidgets
from freecad.vdo.ui import tema
from freecad.vdo.ui.form_builder import FormBuilder
from freecad.vdo.ui.puerta_task_cabecera import PanelHeaderWidget

# Estilos de presentacion referenciados por clave desde la especificacion.
ESTILOS_PUERTA = {
    "texto": tema.ESTILO_PUERTA_TEXTO,
    "info": tema.ESTILO_ETIQUETA_OSCURA,
    "piston": tema.ESTILO_PUERTA_PISTON,
}

ESTILO_GRUPO_PUERTA = tema.ESTILO_PUERTA_GRUPO


class PuertaTaskConstruccionMixin:
    """Construye el formulario de PuertaTaskPanel (sin cambios de comportamiento)."""

    def _crear_widget(self):
        widget = QtWidgets.QWidget()
        tema.aplicar_estilo(widget, tema.ESTILO_PUERTA_FONDO)
        main = QtWidgets.QVBoxLayout(widget)
        main.setContentsMargins(8, 8, 8, 8)
        main.setSpacing(8)

        # Cabecera universal de pieza (obligatoria por Manifiesto UI)
        self.header = PanelHeaderWidget()
        self.header.set_pieza("Puerta", 0, 0, 0)
        main.addWidget(self.header)

        self._form_builder = FormBuilder(widget)
        grupos = self._form_builder.construir_bloques(
            main, PUERTA_BLOQUES, ESTILOS_PUERTA, ESTILO_GRUPO_PUERTA)
        self._enlazar_widgets(grupos)

        main.addStretch()
        self._crear_botones(main)
        self._conectar_senales()
        return widget

    def _enlazar_widgets(self, grupos):
        """Nombres cortos de los widgets del formulario, usados por la carga, la escritura y la visibilidad."""
        fb = self._form_builder
        self.grp_montaje = grupos["montaje"]
        self.grp_herraje = grupos["herraje"]
        self.grp_piston = grupos["piston"]
        self.combo_sistema = fb.widget("sistema")
        self.combo_montaje = fb.widget("montaje")
        self.combo_sentido = fb.widget("sentido")
        self.combo_apertura = fb.widget("apertura")
        self.combo_sku = fb.widget("sku")
        self.spin_ancho = fb.widget("ancho")
        self.spin_alto = fb.widget("alto")
        self.spin_espesor = fb.widget("espesor")
        self.lbl_herraje_info = fb.widget("info_herraje")
        self.lbl_piston = fb.widget("info_piston")
        self.chk_expulsor = fb.widget("expulsor")
        self.spin_pos_x = fb.widget("pos_x")
        self.spin_pos_y = fb.widget("pos_y")
        self.spin_pos_z = fb.widget("pos_z")
        self.combo_anclaje = fb.widget("anclaje")

    def _crear_botones(self, main):
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

    def _conectar_senales(self):
        # Señales de cambio
        self.combo_sistema.currentIndexChanged.connect(self._on_cambio_sistema)
        self.combo_apertura.currentIndexChanged.connect(self._actualizar_todo)
        self.combo_sku.currentIndexChanged.connect(self._actualizar_herraje_info)
        self.combo_montaje.currentIndexChanged.connect(self._actualizar_todo)
        self.combo_sentido.currentIndexChanged.connect(self._actualizar_todo)
        self.spin_ancho.valueChanged.connect(self._actualizar_todo)
        self.spin_alto.valueChanged.connect(self._actualizar_todo)
        self.spin_espesor.valueChanged.connect(self._actualizar_todo)
