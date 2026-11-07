"""Pintado del arbol de la matriz COCO: vanos, estructura y items de piezas.

Extraido de coco_arbol_widgets.py (M7, D-66). Sin cambios de codigo."""

from freecad.vdo.core.simbolos import SIMBOLO_MULTIPLICAR
from freecad.vdo.datos.valores import TIRADOR
from freecad.vdo.qt_compat import QtCore, QtWidgets

ROLE_DATA = QtCore.Qt.UserRole + 1
ROLE_KIND = QtCore.Qt.UserRole + 2
ROLE_KEY = QtCore.Qt.UserRole + 3


class ArbolPintadoMixin:
    """Mixin de pintado del arbol; lo hereda ArbolDivisionesMixin."""

    def _pintar_arbol(self):
        self.tree.blockSignals(True)
        self.tree.clear()
        if self.mode == "estructura":
            self.tree.setHeaderLabels(
                ["Pieza", "Largo", "Ancho", "Espesor"])
            self._pintar_estructura()
        else:
            self.tree.setHeaderLabels(
                ["Vano", "X libre", "Y libre", "Subdivisión"])
            self._pintar_vanos()
        self.tree.expandAll()
        self.tree.blockSignals(False)

    def _pintar_vanos(self):
        root = self._crear_raiz_vanos()
        self._pintar_filas_vanos(root)
        self._agregar_piezas_ocultas(root)

    def _crear_raiz_vanos(self):
        root = QtWidgets.QTreeWidgetItem([
            f"COCO — Matriz {len(self.layout.columns)} {SIMBOLO_MULTIPLICAR} "
            f"{len(self.layout.rows)}", "", "", ""])
        root.setFlags(root.flags() & ~QtCore.Qt.ItemIsSelectable)
        self.tree.addTopLevelItem(root)
        return root

    def _pintar_filas_vanos(self, root):
        for j, row in enumerate(self._resolved.rows):
            row_item = QtWidgets.QTreeWidgetItem([
                f"Y{j + 1}", "", f"{row.size:.1f}",
                "fijo" if row.fixed is not None else "libre"])
            row_item.setData(0, ROLE_DATA, {
                "kind": "row", "row_index": j, "row": row})
            row_item.setToolTip(
                0, f"Fila Y{j + 1}: alto libre {row.size:.1f} mm")
            root.addChild(row_item)
            self._items_by_key[("row", j)] = row_item

            for i, _col in enumerate(self._resolved.columns):
                cell = self.layout.get_cell(i, j)
                resuelto = self._resolved_map.get(cell.label) if cell else None
                if resuelto is None:
                    continue
                item = self._crear_item_celda(
                    resuelto, row_item, kind="cell",
                    col_index=i, row_index=j, parent_axis=None)
                self._items_by_key[
                    ("cell", self.layout.columns[i].id,
                     self.layout.rows[j].id)] = item
                self._hijos_contenido_vano(item, i, j, cell)

    def _hijos_contenido_vano(self, item, i, j, cell):
        # Hijos del vano: puertas, cajones, torres
        contenido = self._contenido_por_celda.get((i, j))
        if contenido:
            tipo = contenido.get("tipo", "vacio")
            if tipo == "puerta":
                cfg = contenido.get("config", {})
                cfg.get("nombre", f"Puerta_{cell.label}")
                montaje = cfg.get("tipo_montaje", "Parche")
                apertura = cfg.get("sistema_apertura", TIRADOR)
                child = QtWidgets.QTreeWidgetItem([
                    f"🚪 Puerta ({montaje} · {apertura})", "", "", ""])
                child.setData(0, ROLE_DATA, {
                    "kind": "contenido_hijo",
                    "tipo": "puerta",
                    "celda": (i, j),
                    "config": cfg,
                })
                item.addChild(child)
            elif tipo == "cajon":
                cfg = contenido.get("config", {})
                cantidad = cfg.get("cantidad", 1)
                corredera = cfg.get("corredera", "Oculta")
                apertura = cfg.get("apertura", "Tirador")
                child = QtWidgets.QTreeWidgetItem([
                    f"🗄️ Cajón {SIMBOLO_MULTIPLICAR}{cantidad} ({corredera} · {apertura})",
                    "", "", ""])
                child.setData(0, ROLE_DATA, {
                    "kind": "contenido_hijo",
                    "tipo": "cajon",
                    "celda": (i, j),
                    "config": cfg,
                })
                item.addChild(child)

    def _agregar_piezas_ocultas(self, root):
        for pieza in self._piezas_fisicas():
            item = QtWidgets.QTreeWidgetItem([
                pieza["nombre"], "", "", ""])
            item.setData(0, ROLE_DATA, {
                "kind": "elemento_reengrose",
                "clave": pieza["key"],
                "pieza": pieza,
            })
            item.setHidden(True)
            root.addChild(item)
            self._items_by_key[("elemento", pieza["key"])] = item

    def _pintar_estructura(self):
        root = QtWidgets.QTreeWidgetItem([
            "COCO — Estructura física", "", "", ""])
        root.setFlags(root.flags() & ~QtCore.Qt.ItemIsSelectable)
        self.tree.addTopLevelItem(root)

        grupos = (
            ("Horizontales", "horizontal"),
            ("Verticales", "vertical"),
        )
        piezas = self._piezas_fisicas()
        for titulo, grupo in grupos:
            grupo_item = QtWidgets.QTreeWidgetItem([
                f"▾ {titulo}", "", "", ""])
            grupo_item.setFlags(
                grupo_item.flags() & ~QtCore.Qt.ItemIsSelectable)
            root.addChild(grupo_item)
            for pieza in piezas:
                if pieza["grupo"] != grupo:
                    continue
                item = self._crear_item_pieza(pieza, grupo_item)
                self._items_by_key[("piece", pieza["key"])] = item
                self._items_by_key[("elemento", pieza["key"])] = item
                if pieza["key"] in self.reengroses:
                    self._crear_item_reengrose(pieza, item)

    def _crear_item_pieza(self, pieza, parent):
        item = QtWidgets.QTreeWidgetItem([
            pieza["nombre"],
            f"{pieza['largo']:.1f}",
            f"{pieza['ancho']:.1f}",
            f"{pieza['espesor']:.1f}",
        ])
        item.setData(0, ROLE_DATA, {
            "kind": "piece",
            "clave": pieza["key"],
            "pieza": pieza,
        })
        item.setToolTip(
            0, f"{pieza['nombre']}\n"
               f"{pieza['largo']:.1f} {SIMBOLO_MULTIPLICAR} {pieza['ancho']:.1f} {SIMBOLO_MULTIPLICAR} "
               f"{pieza['espesor']:.1f} mm")
        parent.addChild(item)
        return item

    def _crear_item_reengrose(self, pieza, parent):
        item = QtWidgets.QTreeWidgetItem([
            "🪵 Reengrose · tira", "", "", ""])
        item.setData(0, ROLE_DATA, {
            "kind": "reengrose_piece",
            "clave": pieza["key"],
            "pieza": pieza,
        })
        item.setToolTip(
            0, f"Tira de reengrose de {pieza['nombre']}")
        parent.addChild(item)
        self._items_by_key[("reengrose", pieza["key"])] = item
        return item
