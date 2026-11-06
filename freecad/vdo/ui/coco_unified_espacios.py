"""Altas, bajas, divisiones, jerarquia y orden de espacios."""

from freecad.vdo.core.spaces import (
    ESPACIO_IGUALES,
    ESPACIO_RESTANTE,
    SpaceNode,
)
from freecad.vdo.qt_compat import QtWidgets
from freecad.vdo.ui.coco_unified_tabla import EspacioRow


class CocoUnifiedEspaciosMixin:
    """Mixin del panel COCO: Altas, bajas, divisiones, jerarquia y orden de espacios."""

    def _agregar_espacio(self, axis):
        rows = self._get_rows(axis)
        n = len(rows)
        node = SpaceNode(
            space_type=ESPACIO_RESTANTE,
            space_id=f"V{n+1}" if axis == "X" else f"H{n+1}")
        rows.append(EspacioRow(node, depth=0))
        table = self._get_table(axis)
        table.blockSignals(True)
        table.insertRow(n)
        self._pintar_fila(table, n, rows[n], axis, [n])
        table.blockSignals(False)
        self._actualizar_resumen()

    def _eliminar_espacio(self, axis):
        table = self._get_table(axis)
        selected = table.selectedItems()
        if not selected:
            return
        row = selected[0].row()
        rows = self._get_rows(axis)
        if 0 <= row < len(rows):
            rows.pop(row)
            self._refrescar_tabla(axis)
            self._actualizar_resumen()

    def _confirmar_borrado_hijos(self, node):
        if not getattr(node, "children", None):
            return True
        respuesta = QtWidgets.QMessageBox.question(
            self.form,
            "Sub-divisiones existentes",
            "Este vano tiene sub-divisiones.\n"
            "Si continúas se eliminarán.\n\n¿Continuar?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No)
        return respuesta == QtWidgets.QMessageBox.Yes

    def _dividir_seleccion(self, axis, n_partes):
        table = self._get_table(axis)
        selected = table.selectedItems()
        if not selected:
            return
        row = selected[0].row()
        rows = self._get_rows(axis)
        if not (0 <= row < len(rows)):
            return
        old = rows[row]
        if not self._confirmar_borrado_hijos(old.node):
            return
        node = SpaceNode(
            space_type=ESPACIO_IGUALES,
            value=float(n_partes),
            space_id=old.node.space_id)
        rows[row] = EspacioRow(node, depth=old.depth)
        self._refrescar_tabla(axis)
        self._actualizar_resumen()

    def _subconfigurar(self, axis):
        table = self._get_table(axis)
        selected = table.selectedItems()
        if not selected:
            return
        self._abrir_hijos(axis, [selected[0].row()])

    def _eje_hijos_label(self, axis, depth):
        """Etiqueta física del eje de los hijos según alternancia."""
        if axis == "X":
            return ("Horizontal (Repisas)" if depth % 2 == 1
                    else "Vertical (Columnas)")
        return ("Vertical (Columnas)" if depth % 2 == 1
                else "Horizontal (Repisas)")

    def _abrir_hijos(self, axis, path):
        row = self._get_row_by_path(axis, path)
        if row is None:
            return

        self._selected_paths[axis] = list(path)

        group, lbl, lbl_eje, table_hijos, btn_back = \
            self._get_hijo_widgets(axis)
        group.setVisible(True)
        btn_back.setEnabled(len(path) > 1)

        breadcrumb = self._path_text(axis, path)
        lbl.setText(
            f"Sub-dividiendo vano: <b>{breadcrumb}</b>")
        lbl_eje.setText(
            "Eje de sub-división: "
            + self._eje_hijos_label(axis, len(path)))

        table_hijos.blockSignals(True)
        table_hijos.setRowCount(0)
        for i, child in enumerate(row.children_rows):
            table_hijos.insertRow(i)
            self._pintar_fila(
                table_hijos, i, child, axis, [*list(path), i])
        table_hijos.blockSignals(False)

    def _agregar_hijo(self, axis):
        path = self._selected_paths[axis]
        parent = self._get_row_by_path(axis, path)
        if parent is None:
            return
        n = len(parent.children_rows)
        child = SpaceNode(
            space_type=ESPACIO_RESTANTE,
            space_id=f"{parent.node.space_id}.{n + 1}",
            parent_id=parent.node.space_id)
        parent.children_rows.append(
            EspacioRow(child, depth=parent.depth + 1))
        parent.node.children = [c.node for c in parent.children_rows]
        self._abrir_hijos(axis, path)
        self._actualizar_resumen()

    def _eliminar_hijo(self, axis):
        table_hijos = self._get_hijo_widgets(axis)[3]
        selected = table_hijos.selectedItems()
        if not selected:
            return
        row = selected[0].row()
        path = self._selected_paths[axis]
        parent = self._get_row_by_path(axis, path)
        if parent is None or not (0 <= row < len(parent.children_rows)):
            return
        parent.children_rows.pop(row)
        parent.node.children = [c.node for c in parent.children_rows]
        self._abrir_hijos(axis, path)
        self._actualizar_resumen()

    def _dividir_hijo(self, axis, n_partes):
        table_hijos = self._get_hijo_widgets(axis)[3]
        selected = table_hijos.selectedItems()
        if not selected:
            return
        row = selected[0].row()
        path = self._selected_paths[axis]
        parent = self._get_row_by_path(axis, path)
        if parent is None or not (0 <= row < len(parent.children_rows)):
            return
        old = parent.children_rows[row]
        if not self._confirmar_borrado_hijos(old.node):
            return
        child = SpaceNode(
            space_type=ESPACIO_IGUALES,
            value=float(n_partes),
            space_id=old.node.space_id,
            parent_id=parent.node.space_id)
        parent.children_rows[row] = EspacioRow(
            child, depth=old.depth)
        parent.node.children = [c.node for c in parent.children_rows]
        self._abrir_hijos(axis, path)
        self._actualizar_resumen()

    def _subir_nivel(self, axis):
        path = self._selected_paths[axis]
        if len(path) <= 1:
            return
        self._abrir_hijos(axis, path[:-1])

    def _cerrar_hijos(self, axis):
        group = self._get_hijo_widgets(axis)[0]
        group.setVisible(False)
        self._selected_paths[axis] = []
        self._refrescar_tabla(axis)
        self._actualizar_resumen()

    def _reordenar_por_ids(self, rows, ordered_ids):
        por_id = {id(row.node): row for row in rows}
        nuevas = [por_id[nid] for nid in ordered_ids if nid in por_id]
        usadas = {id(row.node) for row in nuevas}
        nuevas.extend(row for row in rows if id(row.node) not in usadas)
        return nuevas

    def _reordenar_raiz(self, axis, ordered_ids):
        rows = self._get_rows(axis)
        rows[:] = self._reordenar_por_ids(rows, ordered_ids)
        self._refrescar_tabla(axis)
        self._actualizar_resumen()

    def _reordenar_hijos(self, axis, ordered_ids):
        path = self._selected_paths[axis]
        parent = self._get_row_by_path(axis, path)
        if parent is None:
            return
        parent.children_rows[:] = self._reordenar_por_ids(
            parent.children_rows, ordered_ids)
        parent.node.children = [c.node for c in parent.children_rows]
        self._abrir_hijos(axis, path)
        self._actualizar_resumen()
