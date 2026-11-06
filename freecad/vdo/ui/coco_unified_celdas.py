"""Pintado y edicion de celdas de la tabla de espacios."""

import logging

_LOG = logging.getLogger(__name__)

from freecad.vdo.core.spaces import ESPACIO_FIJO, ESPACIO_IGUALES
from freecad.vdo.qt_compat import QtCore, QtWidgets
from freecad.vdo.ui.coco_unified_tabla import (
    COL_ACCIONES,
    COL_RESUMEN,
    COL_TIPO,
    COL_VALOR,
    ROLE_NODE_ID,
    TIPOS_LABELS,
    EspacioRow,
)


class CocoUnifiedCeldasMixin:
    """Mixin del panel COCO: Pintado y edicion de celdas de la tabla de espacios."""

    def _row_from_node(self, node, depth=0):
        """Hidrata recursivamente el árbol visual desde el modelo."""
        row = EspacioRow(node, depth=depth)
        row.children_rows = [
            self._row_from_node(child, depth=depth + 1)
            for child in getattr(node, "children", [])
        ]
        return row

    def _get_rows(self, axis):
        return self._rows_x if axis == "X" else self._rows_y

    def _get_table(self, axis):
        return self.table_x if axis == "X" else self.table_y

    def _get_hijo_widgets(self, axis):
        if axis == "X":
            return (self.group_hijos_x, self.lbl_hijo_info_x,
                    self.lbl_hijo_eje_x, self.table_hijos_x,
                    self.btn_hijo_atras_x)
        return (self.group_hijos_y, self.lbl_hijo_info_y,
                self.lbl_hijo_eje_y, self.table_hijos_y,
                self.btn_hijo_atras_y)

    def _get_row_by_path(self, axis, path):
        if not path:
            return None
        rows = self._get_rows(axis)
        try:
            row = rows[path[0]]
            for idx in path[1:]:
                row = row.children_rows[idx]
            return row
        except (IndexError, TypeError) as exc:
            _LOG.debug("coco_unified_celdas: ruta de fila no encontrada: %s", exc)
            return None

    def _path_text(self, axis, path):
        partes = []
        for i in range(len(path)):
            row = self._get_row_by_path(axis, path[:i + 1])
            if row is not None:
                partes.append(str(row.node.space_id))
        return " → ".join(partes)

    def _refrescar_tabla(self, axis):
        table = self._get_table(axis)
        rows = self._get_rows(axis)
        table.blockSignals(True)
        table.setRowCount(0)
        for i, row in enumerate(rows):
            table.insertRow(i)
            self._pintar_fila(table, i, row, axis, [i])
        table.blockSignals(False)

    def _pintar_fila(self, table, row_idx, esp_row, axis, path):
        node = esp_row.node
        indent = "  " * esp_row.depth

        tipo_item = QtWidgets.QTableWidgetItem(
            indent + TIPOS_LABELS.get(node.space_type, node.space_type))
        tipo_item.setFlags(tipo_item.flags() & ~QtCore.Qt.ItemIsEditable)
        tipo_item.setData(ROLE_NODE_ID, id(node))
        table.setItem(row_idx, COL_TIPO, tipo_item)

        if node.space_type == ESPACIO_FIJO:
            valor_item = QtWidgets.QTableWidgetItem(f"{node.value:.1f}")
        elif node.space_type == ESPACIO_IGUALES:
            valor_item = QtWidgets.QTableWidgetItem(str(int(node.value)))
        else:
            valor_item = QtWidgets.QTableWidgetItem("—")
            valor_item.setFlags(
                valor_item.flags() & ~QtCore.Qt.ItemIsEditable)
        table.setItem(row_idx, COL_VALOR, valor_item)

        if node.children:
            resumen = f"{len(node.children)} sub-vanos"
        elif node.space_type == ESPACIO_IGUALES:
            resumen = f"{int(node.value)} partes"
        elif node.space_type == ESPACIO_FIJO:
            resumen = f"{node.value:.0f}mm fijos"
        else:
            resumen = node.space_id
        res_item = QtWidgets.QTableWidgetItem(resumen)
        res_item.setFlags(res_item.flags() & ~QtCore.Qt.ItemIsEditable)
        table.setItem(row_idx, COL_RESUMEN, res_item)

        widget_acciones = QtWidgets.QWidget()
        layout_acciones = QtWidgets.QHBoxLayout(widget_acciones)
        layout_acciones.setContentsMargins(2, 2, 2, 2)
        layout_acciones.setSpacing(2)

        btn_nid = QtWidgets.QPushButton("...")
        btn_nid.setMaximumWidth(30)
        btn_nid.setToolTip("Sub-dividir este vano")
        btn_nid.setEnabled(node.space_type != ESPACIO_IGUALES)
        btn_nid.clicked.connect(
            lambda checked, a=axis, p=list(path):
                self._abrir_hijos(a, p))
        layout_acciones.addWidget(btn_nid)

        table.setCellWidget(row_idx, COL_ACCIONES, widget_acciones)

    def _on_medida_changed(self, *args):
        if self._building:
            return
        self.editor_divisiones.set_dimensions(
            self.spin_alto.value(), self.spin_ancho.value(),
            self.spin_espesor.value())
        self._actualizar_resumen()

    def _on_divisiones_changed(self):
        self._actualizar_resumen()

    def _aplicar_valor(self, table, row, col, axis, path):
        if col != COL_VALOR:
            return
        row_obj = self._get_row_by_path(axis, path)
        if row_obj is None:
            return
        item = table.item(row, col)
        if item is None:
            return
        texto = item.text().strip()
        try:
            valor = float(texto)
        except ValueError as exc:
            _LOG.debug("coco_unified_celdas: valor de celda no valido en edicion: %s", exc)
            return
        if row_obj.node.space_type == ESPACIO_IGUALES:
            valor = max(1.0, float(round(valor)))
            table.blockSignals(True)
            item.setText(str(int(valor)))
            table.blockSignals(False)
        row_obj.node.value = valor
        self._actualizar_resumen()

    def _on_cell_changed(self, row, col, axis):
        if self._building:
            return
        self._aplicar_valor(
            self._get_table(axis), row, col, axis, [row])

    def _on_child_cell_changed(self, row, col, axis):
        if self._building:
            return
        path = [*list(self._selected_paths[axis]), row]
        self._aplicar_valor(
            self._get_hijo_widgets(axis)[3], row, col, axis, path)
