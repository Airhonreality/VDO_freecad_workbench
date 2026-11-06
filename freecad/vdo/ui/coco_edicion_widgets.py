"""Edicion de la matriz COCO: items de celda, seleccion, acciones de matriz y contenido de celda.

Extraido de vdo_widgets_coco.py (M7, D-40). Sin cambios de codigo."""

import FreeCAD as App

from freecad.vdo.core.facade_contract import (
    APERTURA_45_GRADOS,
    APERTURA_GOLA,
    APERTURA_PUSH_OPEN,
    APERTURA_TIRADOR,
)
from freecad.vdo.core.layout_modelo import AXIS_X, LayoutError
from freecad.vdo.qt_compat import QtWidgets
from freecad.vdo.ui.coco_arbol_pintado import ROLE_DATA


class EdicionDivisionesMixin:
    """Mixin de DivisionesEditor (ver coco_construccion_widgets.py)."""

    def _crear_item_celda(self, resuelto, parent_item, kind,
                          col_index=None, row_index=None,
                          parent_axis=None):
        cell = resuelto.cell
        division = f"{len(cell.children)} {cell.axis}" if cell.axis and cell.children else "vacío"
        item = QtWidgets.QTreeWidgetItem([
            cell.label,
            f"{resuelto.w:.1f}",
            f"{resuelto.h:.1f}",
            division,
        ])
        data = {
            "kind": kind,
            "cell": cell,
            "col_index": col_index,
            "row_index": row_index,
            "parent_axis": parent_axis,
            "level": resuelto.level,
        }
        item.setData(0, ROLE_DATA, data)
        item.setToolTip(
            0, f"{cell.label}\nX libre: {resuelto.w:.1f} mm\n"
               f"Y libre: {resuelto.h:.1f} mm")
        parent_item.addChild(item)
        self._items_by_label[cell.label] = item
        key = ("nested", cell.px, cell.py)
        self._items_by_key[key] = item

        for child in resuelto.children:
            self._crear_item_celda(
                child, item, kind="nested",
                parent_axis=cell.axis)
        return item
    def _label_seleccionado(self):
        data = self._selected_data
        if not data:
            return None
        if data.get("kind") not in ("cell", "nested"):
            return None
        cell = data.get("cell")
        return cell.label if cell is not None else None

    def _restaurar_seleccion(self):
        item = self._items_by_key.get(self._selected_key)
        if item is None:
            if self.mode == "estructura":
                piezas = self._piezas_fisicas()
                if piezas:
                    key = ("piece", piezas[0]["key"])
                    item = self._items_by_key.get(key)
                    self._selected_key = key
            else:
                key = ("cell", self.layout.columns[0].id,
                       self.layout.rows[0].id)
                item = self._items_by_key.get(key)
                self._selected_key = key
        if item is not None:
            self.tree.blockSignals(True)
            self.tree.setCurrentItem(item)
            self.tree.blockSignals(False)
            self._seleccionar_item(item)
    def _on_tree_selection(self):
        items = self.tree.selectedItems()
        if not items:
            return
        self._seleccionar_item(items[0])
    def _seleccionar_item(self, item):
        data = item.data(0, ROLE_DATA)
        if not data:
            return
        kind = data.get("kind")
        if kind in ("elemento_reengrose", "piece", "reengrose_piece"):
            self._selected_data = data
            clave = data["clave"]
            if kind == "piece":
                self._selected_key = ("piece", clave)
            elif kind == "reengrose_piece":
                self._selected_key = ("reengrose", clave)
            else:
                self._selected_key = ("elemento", clave)
            self._selected_reengrose_key = clave
            idx = self.combo_elemento_reengrose.findData(clave)
            if idx >= 0:
                self._building = True
                self.combo_elemento_reengrose.setCurrentIndex(idx)
                self._building = False
            if not self._skip_cargar_reengrose:
                self._cargar_reengrose_controls(clave)
            if hasattr(self.preview, "set_selected_entity"):
                tipo_preview = (
                    "reengrose" if kind == "reengrose_piece"
                    else "panel")
                self.preview.set_selected_entity(tipo_preview, clave)
            else:
                self.preview.set_selected(None)
            self._actualizar_inspector()
            return

        self._selected_data = data
        cell = data.get("cell")
        if kind == "row":
            self._selected_key = ("row", data["row_index"])
        elif kind == "cell":
            self._selected_key = (
                "cell", self.layout.columns[data["col_index"]].id,
                self.layout.rows[data["row_index"]].id)
        else:
            self._selected_key = ("nested", cell.px, cell.py)
        self.preview.set_selected(
            cell.label if cell is not None else None)
        self._actualizar_inspector()

    def _seleccionar_por_label(self, label):
        if self.mode != "vanos":
            self._ir_a_modo("vanos", None)
        item = self._items_by_label.get(label)
        if item is None:
            return
        self.tree.blockSignals(True)
        self.tree.setCurrentItem(item)
        self.tree.blockSignals(False)
        self._seleccionar_item(item)

    def _seleccionar_panel_preview(self, clave):
        self._seleccionar_clave_en_modo("estructura", ("piece", clave))

    def _seleccionar_reengrose_preview(self, clave):
        self._seleccionar_clave_en_modo(
            "estructura", ("reengrose", clave))

    def _seleccionar_clave_en_modo(self, modo, key):
        if self.mode != modo:
            self._ir_a_modo(modo, key)
            return
        item = self._items_by_key.get(key)
        if item is None and key and key[0] == "reengrose":
            item = self._items_by_key.get(("piece", key[1]))
        if item is None:
            return
        self.tree.blockSignals(True)
        self.tree.setCurrentItem(item)
        self.tree.blockSignals(False)
        self._seleccionar_item(item)

    def _ir_a_modo(self, modo, key):
        self.mode = modo
        self._selected_key = key
        self._selected_data = None
        self._building = True
        self.tabs_modo.setCurrentIndex(0 if modo == "vanos" else 1)
        self._building = False
        self._rebuild()

    # -----------------------------------------------------------------
    # Acciones de matriz

    # -----------------------------------------------------------------
    # Acciones del inspector
    # -----------------------------------------------------------------
    def _on_col_fixed(self, *args):
        self._aplicar_fijo(("cell",), self.chk_col_fixed, self.spin_col_fixed,
                           "col_index", self.layout.set_column_fixed)
    def _on_row_fixed(self, *args):
        self._aplicar_fijo(("cell", "row"), self.chk_row_fixed, self.spin_row_fixed,
                           "row_index", self.layout.set_row_fixed)
    def _aplicar_fijo(self, tipos, chk, spin, clave_indice, fijar):
        """Fija (o libera) la columna/fila de la selección con el valor de `spin` si `chk` está marcado."""
        if self._building or not self._selected_data:
            return
        data = self._selected_data
        if data["kind"] not in tipos:
            return
        valor = spin.value() if chk.isChecked() else None
        fijar(data[clave_indice], valor)
        self._rebuild_y_avisar()
    def _on_cell_fixed(self, *args):
        if self._building or not self._selected_data:
            return
        data = self._selected_data
        if data["kind"] != "nested":
            return
        cell = data["cell"]
        if cell.axis:
            return
        valor = (self.spin_cell_fixed.value()
                 if self.chk_cell_fixed.isChecked() else None)
        self.layout.set_cell_fixed(cell, valor)
        self._rebuild_y_avisar()
    def _on_n_changed(self, valor):
        if self._building or not self._selected_data:
            return
        data = self._selected_data
        cell = data.get("cell")
        if cell is None or not cell.axis:
            return
        if (valor < len(cell.children)
                and any(c.axis or c.children
                        for c in cell.children[valor:])
                and not self._confirmar(
                    "Reducir N eliminará subdivisiones internas.\n"
                    "¿Continuar?")):
            self._building = True
            self.spin_n.setValue(len(cell.children))
            self._building = False
            return
        self.layout.set_split(cell, cell.axis, valor)
        self._rebuild_y_avisar()
    def _on_axis_changed(self, *args):
        if self._building or not self._selected_data:
            return
        data = self._selected_data
        cell = data.get("cell")
        if cell is None or not cell.axis:
            return
        axis = self.combo_axis.currentData()
        if axis == cell.axis:
            return
        if cell.children and not self._confirmar(
                "Cambiar el eje borrará las subdivisiones actuales.\n"
                "¿Continuar?"):
            self._building = True
            self.combo_axis.setCurrentIndex(
                0 if cell.axis == AXIS_X else 1)
            self._building = False
            return
        self.layout.set_split(cell, axis, self.spin_n.value())
        self._rebuild_y_avisar()

    def _on_contenido_changed(self, index):
        if self._building or not self._selected_data:
            return
        data = self._selected_data
        if data.get("kind") not in ("cell", "nested"):
            return
        tipo = self.combo_contenido.currentData()
        col = data.get("col_index")
        row = data.get("row_index")
        if col is None or row is None:
            return
        prev = self._contenido_por_celda.get((col, row), {"tipo": "vacio"})
        if prev["tipo"] == tipo:
            self._mostrar_panel_contenido(tipo)
            return
        # Solo actualizar el estado interno. NO crear objetos en el documento
        # aquí: la creación ocurre exclusivamente al presionar "Aceptar"
        # en CocoUnifiedTaskPanel.accept() -> _construir_insertos().
        self._contenido_por_celda[(col, row)] = {"tipo": tipo}
        self._guardar_config_actual(col, row)
        self._mostrar_panel_contenido(tipo)
        cell = data.get("cell")
        if cell is None:
            return
        resuelto = self._resolved_map.get(cell.label)
        if resuelto is None:
            return
        if tipo == "subdivision":
            if not (cell.axis and cell.children):
                try:
                    self.layout.set_split(cell, AXIS_X, 2)
                except LayoutError:
                    App.Console.PrintWarning(
                        "[VDO] No se pudo dividir la celda del layout")
                self._rebuild_y_avisar()
        else:
            # vacio / puerta / cajon: limpiar subdivisiones si las hay
            if cell.axis and cell.children:
                self.layout.disable_split(cell)
                self._rebuild_y_avisar()

    def _guardar_config_actual(self, col, row):
        """Lee los valores de los paneles reactivos y los guarda en
        _contenido_por_celda[(col, row)] para persistencia posterior."""
        datos = self._contenido_por_celda.get((col, row), {"tipo": "vacio"})
        tipo = datos.get("tipo", "vacio")
        cfg = dict(datos.get("config", {}))

        if tipo == "puerta":
            cfg.update({
                "nombre": f"Puerta_{(col, row)}",
                "tipo_sistema": self.combo_puerta_familia.currentText(),
                "tipo_montaje": self.combo_puerta_montaje.currentText(),
                "sentido_apertura": "Izquierda",
                "sistema_apertura": {
                    "Tirador": APERTURA_TIRADOR,
                    "Gola": APERTURA_GOLA,
                    "45°": APERTURA_45_GRADOS,
                    "Push Open": APERTURA_PUSH_OPEN,
                }.get(self.combo_puerta_apertura.currentText(), APERTURA_TIRADOR),
                "hardware_sku": self.combo_puerta_herraje.currentText(),
                "vdo_vano_id": f"({col},{row})",
                "ancho": 0.0,  # Se rellena en construir_insertos desde el resolved
                "alto": 0.0,
                "espesor": 18,
                "pos_x": 0.0,
                "pos_y": 0.0,
                "pos_z": 0.0,
                "anclaje": "inferior_izquierda_frente",
            })
        elif tipo == "cajon":
            cfg.update({
                "nombre": f"Cajon_{(col, row)}",
                "tipo": "cajon",
                "cantidad": self.spin_cajon_cantidad.value(),
                "corredera": self.combo_cajon_corredera.currentText(),
                "apertura": self.combo_cajon_apertura.currentText(),
                "vdo_vano_id": f"({col},{row})",
                "ancho": 0.0,
                "alto": 0.0,
                "espesor": 18,
                "pos_x": 0.0,
                "pos_y": 0.0,
                "pos_z": 0.0,
            })

        self._contenido_por_celda[(col, row)] = {"tipo": tipo, "config": cfg}
