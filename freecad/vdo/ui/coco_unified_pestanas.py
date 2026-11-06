"""Pestanas de espacios, botones y grupo de hijos del panel COCO."""

from freecad.vdo.qt_compat import QtWidgets
from freecad.vdo.ui.coco_unified_tabla import SpacesTableWidget


class CocoUnifiedPestanasMixin:
    """Mixin del panel COCO: Pestanas de espacios, botones y grupo de hijos del panel COCO."""

    def _crear_tab_espacios(self, layout, axis):
        """Crea la UI para un eje (X o Y)."""
        table = SpacesTableWidget(
            reorder_callback=lambda ids, a=axis: self._reordenar_raiz(a, ids))
        table.cellChanged.connect(
            lambda r, c, a=axis: self._on_cell_changed(r, c, a))
        if axis == "X":
            self.table_x = table
        else:
            self.table_y = table
        layout.addWidget(table)
        self._crear_botones_espacios(layout, axis)
        self._crear_grupo_hijos(layout, axis)

    def _crear_botones_espacios(self, layout, axis):
        """Botones de acción para la tabla principal de espacios."""
        layout_botones = QtWidgets.QHBoxLayout()

        btn_add = QtWidgets.QPushButton("+ Añadir vano")
        btn_add.clicked.connect(lambda: self._agregar_espacio(axis))
        layout_botones.addWidget(btn_add)

        btn_remove = QtWidgets.QPushButton("- Eliminar vano")
        btn_remove.clicked.connect(lambda: self._eliminar_espacio(axis))
        layout_botones.addWidget(btn_remove)

        layout_botones.addWidget(QtWidgets.QLabel("  |  "))

        layout_botones.addWidget(QtWidgets.QLabel("Dividir en:"))
        spin = QtWidgets.QSpinBox()
        spin.setRange(2, 20)
        spin.setValue(2)
        spin.setToolTip("Número de partes iguales")
        spin.setMaximumWidth(60)
        self.spin_dividir[axis] = spin
        layout_botones.addWidget(spin)

        btn_dividir = QtWidgets.QPushButton("Dividir")
        btn_dividir.setToolTip(
            "Divide el vano seleccionado en N partes iguales")
        btn_dividir.clicked.connect(
            lambda: self._dividir_seleccion(
                axis, self.spin_dividir[axis].value()))
        layout_botones.addWidget(btn_dividir)

        btn_nest = QtWidgets.QPushButton("Sub-dividir")
        btn_nest.setToolTip(
            "Sub-divide el vano seleccionado en el eje opuesto")
        btn_nest.clicked.connect(lambda: self._subconfigurar(axis))
        layout_botones.addWidget(btn_nest)

        layout.addLayout(layout_botones)

    def _crear_grupo_hijos(self, layout, axis):
        """Grupo para sub-configuración recursiva de hijos."""
        group = QtWidgets.QGroupBox("Sub-dividir vano seleccionado")
        group.setVisible(False)
        group_layout = QtWidgets.QVBoxLayout(group)

        lbl = QtWidgets.QLabel("")
        lbl.setWordWrap(True)
        group_layout.addWidget(lbl)

        lbl_eje = QtWidgets.QLabel("Eje de sub-división:")
        group_layout.addWidget(lbl_eje)

        table = self._crear_tabla_hijos(axis, group_layout)

        btn_back = self._crear_botones_hijos(axis, group_layout)
        layout.addWidget(group)

        self._registrar_widgets_hijos(axis, group, lbl, lbl_eje, table, btn_back)

        return group

    def _crear_tabla_hijos(self, axis, group_layout):
        table = SpacesTableWidget(
            reorder_callback=lambda ids, a=axis: self._reordenar_hijos(a, ids))
        table.setMaximumHeight(200)
        table.cellChanged.connect(
            lambda r, c, a=axis: self._on_child_cell_changed(r, c, a))
        group_layout.addWidget(table)
        return table

    def _crear_botones_hijos(self, axis, group_layout):
        btn_layout = QtWidgets.QHBoxLayout()

        btn_add = QtWidgets.QPushButton("+ Añadir vano")
        btn_add.clicked.connect(lambda: self._agregar_hijo(axis))
        btn_layout.addWidget(btn_add)

        btn_remove = QtWidgets.QPushButton("- Eliminar vano")
        btn_remove.clicked.connect(lambda: self._eliminar_hijo(axis))
        btn_layout.addWidget(btn_remove)

        btn_layout.addWidget(QtWidgets.QLabel("Dividir en:"))
        spin = QtWidgets.QSpinBox()
        spin.setRange(2, 20)
        spin.setValue(2)
        spin.setToolTip("Número de partes iguales")
        spin.setMaximumWidth(60)
        self.spin_dividir_hijo[axis] = spin
        btn_layout.addWidget(spin)

        btn_dividir = QtWidgets.QPushButton("Dividir")
        btn_dividir.setToolTip(
            "Divide el sub-vano seleccionado en N partes iguales")
        btn_dividir.clicked.connect(
            lambda: self._dividir_hijo(
                axis, self.spin_dividir_hijo[axis].value()))
        btn_layout.addWidget(btn_dividir)

        btn_back = QtWidgets.QPushButton("Atrás")
        btn_back.setToolTip("Subir un nivel en la jerarquía")
        btn_back.clicked.connect(lambda: self._subir_nivel(axis))
        btn_layout.addWidget(btn_back)

        btn_close = QtWidgets.QPushButton("Cerrar")
        btn_close.clicked.connect(lambda: self._cerrar_hijos(axis))
        btn_layout.addWidget(btn_close)

        group_layout.addLayout(btn_layout)
        return btn_back

    def _registrar_widgets_hijos(self, axis, group, lbl, lbl_eje, table, btn_back):
        if axis == "X":
            self.group_hijos_x = group
            self.lbl_hijo_info_x = lbl
            self.lbl_hijo_eje_x = lbl_eje
            self.table_hijos_x = table
            self.btn_hijo_atras_x = btn_back
        else:
            self.group_hijos_y = group
            self.lbl_hijo_info_y = lbl
            self.lbl_hijo_eje_y = lbl_eje
            self.table_hijos_y = table
            self.btn_hijo_atras_y = btn_back
