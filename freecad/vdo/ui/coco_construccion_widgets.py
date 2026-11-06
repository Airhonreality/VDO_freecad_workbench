"""Editor de divisiones del COCO (clase raiz): construccion de widgets y mensajes.

Extraido de vdo_widgets_coco.py (M7, D-40). Sin cambios de codigo."""

from freecad.vdo.core import vdo_defaults as VDO_D
from freecad.vdo.core.vdo_layout_matriz import Layout
from freecad.vdo.core.vdo_layout_modelo import AXIS_X, AXIS_Y
from freecad.vdo.qt_compat import QtCore, QtWidgets
from freecad.vdo.ui.coco_arbol_widgets import ArbolDivisionesMixin
from freecad.vdo.ui.coco_edicion_widgets import EdicionDivisionesMixin
from freecad.vdo.ui.coco_inspector_widgets import InspectorDivisionesMixin, PanelHeaderWidget
from freecad.vdo.ui.coco_reengrose_widgets import ReengroseDivisionesMixin
from freecad.vdo.ui.vdo_coco_preview2d import CocoPreview2D
from freecad.vdo.ui import tema


class DivisionesEditor(
    InspectorDivisionesMixin,
    ArbolDivisionesMixin,
    EdicionDivisionesMixin,
    ReengroseDivisionesMixin,
    QtWidgets.QWidget,
):
    """Editor único de divisiones, sin tablas de filas."""

    changed = QtCore.Signal()


    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = Layout()
        self.inner_w = 0.0
        self.inner_h = 0.0
        self.outer_w = 0.0
        self.outer_h = 0.0
        self.thickness = float(VDO_D.ESPESOR_DEFAULT)
        self._resolved = None
        self._resolved_map = {}
        self._items_by_label = {}
        self._items_by_key = {}
        self._selected_key = ("cell", "x1", "y1")
        self._selected_data = None
        self._building = False
        self._en_reengrose = False
        self._skip_cargar_reengrose = False
        self._legacy_warnings = []
        self.reengroses = {}
        self._selected_reengrose_key = None
        self._contenido_por_celda = {}
        self.mode = "vanos"
        self._obj = None
        self._fondo = 580.0
        self._tapa = "externo"
        self._base = "interno"
        self._tiene_fondo = True

        self._crear_widget()
        self._rebuild()

    # -----------------------------------------------------------------
    # Construcción
    # -----------------------------------------------------------------
    def _crear_widget(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self._construir_preview_y_modo(layout)
        cuerpo = QtWidgets.QHBoxLayout()
        self._construir_arbol(cuerpo)
        self._construir_inspector_base()
        self._construir_selector_contenido()
        self._construir_panel_subdivision()
        self._construir_panel_puerta()
        self._construir_panel_cajon()
        self._construir_aviso_reengrose()
        self._construir_resumen(layout, cuerpo)
        self._conectar_senales()

    def _construir_preview_y_modo(self, layout):
        self.preview = CocoPreview2D()
        self.preview.setMinimumHeight(190)
        self.preview.cellClicked.connect(self._seleccionar_por_label)
        self.preview.panelClicked.connect(self._seleccionar_panel_preview)
        self.preview.reengroseClicked.connect(
            self._seleccionar_reengrose_preview)
        layout.addWidget(self.preview, 1)

        self.tabs_modo = QtWidgets.QTabBar()
        self.tabs_modo.addTab("🔲 Vanos")
        self.tabs_modo.addTab("🪵 Estructura")
        self.tabs_modo.setToolTip(
            "Vanos: espacios libres y subdivisiones. "
            "Estructura: paneles físicos y sus reengroses.")
        self.tabs_modo.currentChanged.connect(self._on_modo_changed)
        layout.addWidget(self.tabs_modo)

    def _construir_arbol(self, cuerpo):
        self.tree = QtWidgets.QTreeWidget()
        self.tree.setColumnCount(4)
        self.tree.setHeaderLabels(
            ["Vano", "X libre", "Y libre", "Subdivisión"])
        self.tree.setAlternatingRowColors(True)
        self.tree.setSelectionMode(
            QtWidgets.QAbstractItemView.SingleSelection)
        self.tree.setUniformRowHeights(True)
        self.tree.setToolTip(
            "Árbol de vanos: selecciona una celda para editar sus medidas "
            "o una fila para fijar su alto.")
        cabecera = self.tree.header()
        cabecera.setSectionResizeMode(
            0, QtWidgets.QHeaderView.ResizeToContents)
        cabecera.setSectionResizeMode(
            1, QtWidgets.QHeaderView.ResizeToContents)
        cabecera.setSectionResizeMode(
            2, QtWidgets.QHeaderView.ResizeToContents)
        cabecera.setSectionResizeMode(
            3, QtWidgets.QHeaderView.Stretch)
        cuerpo.addWidget(self.tree, 2)

    def _construir_inspector_base(self):
        self.inspector = QtWidgets.QGroupBox("Inspector")
        self.form = QtWidgets.QFormLayout(self.inspector)
        self.header = PanelHeaderWidget()
        self.header.setVisible(False)
        self.form.addRow(self.header)

        self.lbl_sel = QtWidgets.QLabel("Sin selección.")
        self.lbl_sel.setWordWrap(True)
        self.form.addRow(self.lbl_sel)

        self.lbl_nominal_neto = QtWidgets.QLabel("")
        self.lbl_nominal_neto.setWordWrap(True)
        tema.aplicar_estilo(self.lbl_nominal_neto, tema.ESTILO_ETIQUETA_OSCURA)
        self.form.addRow(self.lbl_nominal_neto)

        self.lbl_invasores = QtWidgets.QLabel("")
        self.lbl_invasores.setWordWrap(True)
        self.form.addRow(self.lbl_invasores)

        self.chk_col_fixed = QtWidgets.QCheckBox("Fijar ancho de columna")
        self.chk_col_fixed.setToolTip(
            "Fija el ancho de esta columna. El resto de columnas libres se "
            "reparten el espacio sobrante.")
        self.spin_col_fixed = self._spin_medida()
        self.spin_col_fixed.setToolTip(
            "Ancho fijo de la columna en milímetros, sin contar divisiones.")
        self.widget_col_fixed = self._fila_check_spin(
            self.chk_col_fixed, self.spin_col_fixed)
        self.form.addRow(self.widget_col_fixed)

        self.chk_row_fixed = QtWidgets.QCheckBox("Fijar alto de fila")
        self.chk_row_fixed.setToolTip(
            "Fija el alto de esta fila. El resto de filas libres se reparten "
            "el espacio sobrante.")
        self.spin_row_fixed = self._spin_medida()
        self.spin_row_fixed.setToolTip(
            "Alto fijo de la fila en milímetros, sin contar repisas.")
        self.widget_row_fixed = self._fila_check_spin(
            self.chk_row_fixed, self.spin_row_fixed)
        self.form.addRow(self.widget_row_fixed)

        self.chk_cell_fixed = QtWidgets.QCheckBox("Medida fija")
        self.chk_cell_fixed.setToolTip(
            "Fija la medida de este sub-vano. Si el sub-vano está "
            "subdividido, primero hay que editar el padre.")
        self.spin_cell_fixed = self._spin_medida()
        self.spin_cell_fixed.setToolTip(
            "Medida fija del sub-vano en milímetros.")
        self.widget_cell_fixed = self._fila_check_spin(
            self.chk_cell_fixed, self.spin_cell_fixed)
        self.form.addRow(self.widget_cell_fixed)

    def _construir_selector_contenido(self):
        # ---- Selector unificado de contenido de vano ----
        self.lbl_contenido = QtWidgets.QLabel("Contenido del vano:")
        tema.aplicar_estilo(self.lbl_contenido, tema.ESTILO_NEGRITA_TEXTO)
        self.form.addRow(self.lbl_contenido)

        self.combo_contenido = QtWidgets.QComboBox()
        self.combo_contenido.addItem("🔲  Vacío", "vacio")
        self.combo_contenido.addItem("➗  Subdivisión", "subdivision")
        self.combo_contenido.addItem("🚪  Puerta", "puerta")
        self.combo_contenido.addItem("🗄️  Cajón", "cajon")
        self.combo_contenido.setToolTip(
            "Tipo de contenido para este vano. Los insertos (puerta, cajón) "
            "requieren un vano padre y se anidan bajo él en el árbol.")
        self.form.addRow(self.combo_contenido)

    def _construir_panel_subdivision(self):
        # ---- Panel reactivo: Subdivisión ----
        self.widget_split = QtWidgets.QWidget()
        split_layout = QtWidgets.QFormLayout(self.widget_split)
        split_layout.setContentsMargins(16, 0, 0, 0)
        self.combo_axis = QtWidgets.QComboBox()
        self.combo_axis.addItem("X (columnas)", AXIS_X)
        self.combo_axis.addItem("Y (repisas)", AXIS_Y)
        self.combo_axis.setToolTip(
            "X divide en columnas verticales. Y divide en repisas "
            "horizontales.")
        self.spin_n = QtWidgets.QSpinBox()
        self.spin_n.setRange(2, 100)
        self.spin_n.setValue(2)
        self.spin_n.setToolTip(
            "Cantidad de partes iguales en que se subdivide el vano.")
        split_layout.addRow("Eje:", self.combo_axis)
        split_layout.addRow("N partes:", self.spin_n)
        self.form.addRow(self.widget_split)
        self.widget_split.setVisible(False)

    def _construir_panel_puerta(self):
        # ---- Panel reactivo: Puerta ----
        self.widget_puerta = QtWidgets.QWidget()
        puerta_layout = QtWidgets.QFormLayout(self.widget_puerta)
        puerta_layout.setContentsMargins(16, 0, 0, 0)

        self.combo_puerta_familia = QtWidgets.QComboBox()
        self.combo_puerta_familia.addItems(["Batiente", "Corrediza", "Basculante"])
        self.combo_puerta_familia.setToolTip("Tipo de sistema de la puerta.")
        puerta_layout.addRow("Familia:", self.combo_puerta_familia)

        self.combo_puerta_montaje = QtWidgets.QComboBox()
        self.combo_puerta_montaje.addItems(["Parche", "Semiparche", "Embebida"])
        self.combo_puerta_montaje.setToolTip("Tipo de montaje frontal.")
        puerta_layout.addRow("Montaje:", self.combo_puerta_montaje)

        self.combo_puerta_apertura = QtWidgets.QComboBox()
        self.combo_puerta_apertura.addItems(
            ["Tirador", "Gola", "45°", "Push Open"])
        self.combo_puerta_apertura.setToolTip("Sistema de apertura/fachada.")
        puerta_layout.addRow("Apertura:", self.combo_puerta_apertura)

        self.combo_puerta_herraje = QtWidgets.QComboBox()
        self.combo_puerta_herraje.setToolTip("SKU de herraje comercial.")
        puerta_layout.addRow("Herraje:", self.combo_puerta_herraje)

        self.lbl_puerta_info = QtWidgets.QLabel(
            "Se creará al aceptar el Task Panel del COCO.")
        tema.aplicar_estilo(self.lbl_puerta_info, tema.ESTILO_ATENUADO_ITALICA)
        puerta_layout.addRow(self.lbl_puerta_info)
        self.form.addRow(self.widget_puerta)
        self.widget_puerta.setVisible(False)

    def _construir_panel_cajon(self):
        # ---- Panel reactivo: Cajón ----
        self.widget_cajon = QtWidgets.QWidget()
        cajon_layout = QtWidgets.QFormLayout(self.widget_cajon)
        cajon_layout.setContentsMargins(16, 0, 0, 0)

        self.spin_cajon_cantidad = QtWidgets.QSpinBox()
        self.spin_cajon_cantidad.setRange(1, 6)
        self.spin_cajon_cantidad.setValue(1)
        self.spin_cajon_cantidad.setToolTip("Cantidad de frentes (1 a 6).")
        cajon_layout.addRow("Cantidad:", self.spin_cajon_cantidad)

        self.combo_cajon_corredera = QtWidgets.QComboBox()
        self.combo_cajon_corredera.addItems(["Telescópica", "Oculta"])
        self.combo_cajon_corredera.setToolTip("Tipo de corredera del cajón.")
        cajon_layout.addRow("Corredera:", self.combo_cajon_corredera)

        self.combo_cajon_apertura = QtWidgets.QComboBox()
        self.combo_cajon_apertura.addItems(["Tirador", "Gola", "45°", "Push"])
        self.combo_cajon_apertura.setToolTip("Sistema de apertura del frente.")
        cajon_layout.addRow("Apertura:", self.combo_cajon_apertura)

        self.lbl_cajon_info = QtWidgets.QLabel(
            "Se creará al aceptar el Task Panel del COCO.")
        tema.aplicar_estilo(self.lbl_cajon_info, tema.ESTILO_ATENUADO_ITALICA)
        cajon_layout.addRow(self.lbl_cajon_info)
        self.form.addRow(self.widget_cajon)
        self.widget_cajon.setVisible(False)

    def _construir_aviso_reengrose(self):
        self.lbl_aviso = QtWidgets.QLabel("")
        self.lbl_aviso.setWordWrap(True)
        tema.aplicar_estilo(self.lbl_aviso, tema.ESTILO_ERROR_TEXTO)
        self.form.addRow(self.lbl_aviso)

        self.grupo_reengrose = self._crear_grupo_reengrose()
        self.form.addRow(self.grupo_reengrose)

    def _construir_resumen(self, layout, cuerpo):
        cuerpo.addWidget(self.inspector, 1)
        layout.addLayout(cuerpo, 2)

        self.lbl_resumen = QtWidgets.QLabel("")
        self.lbl_resumen.setWordWrap(True)
        tema.aplicar_estilo(self.lbl_resumen, tema.ESTILO_RESUMEN_MONO)
        layout.addWidget(self.lbl_resumen)

    def _conectar_senales(self):
        self.tree.itemSelectionChanged.connect(self._on_tree_selection)
        self.chk_col_fixed.toggled.connect(self._on_col_fixed)
        self.chk_row_fixed.toggled.connect(self._on_row_fixed)
        self.chk_cell_fixed.toggled.connect(self._on_cell_fixed)
        self.spin_col_fixed.valueChanged.connect(self._on_col_fixed)
        self.spin_row_fixed.valueChanged.connect(self._on_row_fixed)
        self.spin_cell_fixed.valueChanged.connect(self._on_cell_fixed)
        self.combo_contenido.currentIndexChanged.connect(
            self._on_contenido_changed)
        self.combo_axis.currentIndexChanged.connect(self._on_axis_changed)
        self.spin_n.valueChanged.connect(self._on_n_changed)
        self.combo_elemento_reengrose.currentIndexChanged.connect(
            self._on_reengrose_element_changed)
        self.re_editor.changed.connect(self._on_reengrose_changed)
        self.re_editor.sigConfigChanged.connect(self._on_reengrose_changed)
        self.combo_fabricacion.currentIndexChanged.connect(
            self._on_reengrose_changed)
        self.combo_choque.currentIndexChanged.connect(
            self._on_reengrose_changed)
        self.combo_cara.currentIndexChanged.connect(
            self._on_reengrose_changed)
        # Guardar config de insertos al cambiar cualquier widget reactivo
        self.combo_puerta_familia.currentIndexChanged.connect(
            self._guardar_config_desde_ui)
        self.combo_puerta_montaje.currentIndexChanged.connect(
            self._guardar_config_desde_ui)
        self.combo_puerta_apertura.currentIndexChanged.connect(
            self._guardar_config_desde_ui)
        self.combo_puerta_herraje.currentIndexChanged.connect(
            self._guardar_config_desde_ui)
        self.spin_cajon_cantidad.valueChanged.connect(
            self._guardar_config_desde_ui)
        self.combo_cajon_corredera.currentIndexChanged.connect(
            self._guardar_config_desde_ui)
        self.combo_cajon_apertura.currentIndexChanged.connect(
            self._guardar_config_desde_ui)


    def _guardar_config_desde_ui(self, *args):
        """Guarda la configuración actual de los paneles reactivos en
        _contenido_por_celda para la celda o hijo seleccionado."""
        if self._building or not self._selected_data:
            return
        data = self._selected_data
        kind = data.get("kind")
        if kind in ("cell", "nested"):
            col = data.get("col_index")
            row = data.get("row_index")
            if col is None or row is None:
                return
            self._guardar_config_actual(col, row)
        elif kind == "contenido_hijo":
            celda = data.get("celda")
            if not celda:
                return
            try:
                col, row = celda
            except (ValueError, TypeError):
                return
            self._guardar_config_actual(col, row)
            # Refrescar preview 2D al instante
            self._rebuild_y_avisar()

    def _mostrar_panel_contenido(self, tipo):
        self.widget_split.setVisible(tipo == "subdivision")
        self.widget_puerta.setVisible(tipo == "puerta")
        self.widget_cajon.setVisible(tipo == "cajon")
        if tipo == "subdivision":
            data = self._selected_data
            cell = data.get("cell") if data else None
            if cell and cell.axis and cell.children:
                idx = 0 if cell.axis == AXIS_X else 1
                self.combo_axis.setCurrentIndex(idx)
                self.spin_n.setValue(len(cell.children))
            self.widget_split.setVisible(True)

    def _rebuild_y_avisar(self):
        self._rebuild()
        self.changed.emit()

    def _confirmar(self, texto):
        respuesta = QtWidgets.QMessageBox.question(
            self, "Divisiones VDO", texto,
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No)
        return respuesta == QtWidgets.QMessageBox.Yes
    def _mostrar_error(self, texto):
        self.lbl_aviso.setText("⚠ " + texto)
