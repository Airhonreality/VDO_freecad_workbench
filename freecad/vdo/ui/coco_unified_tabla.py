"""Tabla de espacios: columnas, tipos y widget de tabla."""

from freecad.vdo.core.spaces import (
    ESPACIO_FIJO,
    ESPACIO_IGUALES,
    ESPACIO_RESTANTE,
    SpaceNode,
)
from freecad.vdo.qt_compat import QtCore, QtWidgets

COL_TIPO = 0
COL_VALOR = 1
COL_RESUMEN = 2
COL_ACCIONES = 3
ROLE_NODE_ID = QtCore.Qt.UserRole + 1
TIPOS_LABELS = {
    ESPACIO_FIJO: "Fijo (mm)",
    ESPACIO_RESTANTE: "Restante",
    ESPACIO_IGUALES: "Iguales (N partes)",
}


class EspacioRow:
    """Representa una fila visual en la tabla de espacios."""

    def __init__(self, node=None, depth=0):
        self.node = node or SpaceNode(space_type=ESPACIO_RESTANTE)
        self.depth = depth
        self.children_rows = []


class SpacesTableWidget(QtWidgets.QTableWidget):
    """QTableWidget con reordenamiento basado en modelo.

    No mueve filas por sí mismo: calcula el nuevo orden de nodos y delega
    en el panel, que reconstruye la tabla desde el modelo.
    """

    def __init__(self, parent=None, reorder_callback=None):
        super().__init__(parent)
        self.reorder_callback = reorder_callback
        self.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.setColumnCount(4)
        self.setHorizontalHeaderLabels(
            ["Tipo", "Valor", "Resultado", "Acciones"])
        header = self.horizontalHeader()
        header.setResizeMode(COL_TIPO, QtWidgets.QHeaderView.ResizeToContents)
        header.setResizeMode(COL_VALOR, QtWidgets.QHeaderView.Stretch)
        header.setResizeMode(COL_RESUMEN, QtWidgets.QHeaderView.Stretch)
        header.setResizeMode(COL_ACCIONES, QtWidgets.QHeaderView.ResizeToContents)
        self.verticalHeader().setVisible(False)
        self.setAlternatingRowColors(True)

    def _ids_actuales(self):
        ids = []
        for row in range(self.rowCount()):
            item = self.item(row, COL_TIPO)
            node_id = item.data(ROLE_NODE_ID) if item else None
            ids.append(node_id)
        return ids

    def dropEvent(self, event):
        if event.source() is not self or self.reorder_callback is None:
            super().dropEvent(event)
            return

        ids = self._ids_actuales()
        selected_rows = sorted(
            set(idx.row() for idx in self.selectedIndexes()))
        if not selected_rows:
            event.ignore()
            return

        drop_index = self.indexAt(event.pos())
        drop_row = None
        if drop_index.isValid():
            pos = self.dropIndicatorPosition()
            if pos == QtWidgets.QAbstractItemView.AboveItem:
                drop_row = drop_index.row()
            elif pos in (QtWidgets.QAbstractItemView.BelowItem,
                         QtWidgets.QAbstractItemView.OnItem):
                drop_row = drop_index.row() + 1
        if drop_row is None:
            drop_row = self.rowCount()

        moving = [ids[r] for r in selected_rows]
        rest = [node_id for i, node_id in enumerate(ids)
                if i not in selected_rows]
        insert_at = drop_row - sum(1 for r in selected_rows if r < drop_row)
        insert_at = max(0, min(insert_at, len(rest)))
        new_ids = rest[:insert_at] + moving + rest[insert_at:]

        event.setDropAction(QtCore.Qt.MoveAction)
        event.accept()
        self.reorder_callback(new_ids)
