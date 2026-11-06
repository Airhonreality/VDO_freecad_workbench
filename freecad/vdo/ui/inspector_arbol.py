"""Arbol maestro del inspector y sincronizacion con la seleccion y la vista previa."""

import FreeCAD as App

from freecad.vdo.qt_compat import QtCore, QtGui, QtWidgets
from freecad.vdo.ui.inspector_paginas import (
    _TARGET_TO_PAGE,
    PAGE_CHASIS,
    PAGE_CIERRE,
    PAGE_PIEZA,
    PAGE_VANO,
    _float_seguro,
)
from freecad.vdo.ui.selection_bridge import VDOSelectionBridge


class ArbolInspectorMixin:
    """Arbol maestro del inspector y sincronizacion con la seleccion y la vista previa."""

    def _regenerar_arbol_maestro(self, obj, piezas, resolved, contenido_por_celda):
        self.master_tree.blockSignals(True)
        self.master_tree.clear()

        nombre_raiz = getattr(obj, "Label", getattr(obj, "Name", "COCO")) if obj else "COCO"
        raiz = QtWidgets.QTreeWidgetItem([f"📦 {nombre_raiz}"])
        raiz.setData(0, QtCore.Qt.UserRole, {"tipo": "coco", "obj": obj})
        self.master_tree.addTopLevelItem(raiz)

        item_chasis = self._construir_rama_chasis(raiz, obj)

        # Rama 2: Piezas Físicas
        item_piezas = QtWidgets.QTreeWidgetItem(["🪵 Piezas Físicas"])
        item_piezas.setData(0, QtCore.Qt.UserRole, {"tipo": "piezas_header", "obj": obj})
        raiz.addChild(item_piezas)

        for p in piezas:
            it = QtWidgets.QTreeWidgetItem([f"🪵 {p['nombre']} [{p['largo']:.0f}×{p['ancho']:.0f}]"])  # noqa: RUF001 - etiqueta de interfaz: signo tipografico visible (x o -) que el usuario ve; cambiarlo altera el texto
            it.setData(0, QtCore.Qt.UserRole, {"tipo": "pieza", "clave": p["key"], "pieza": p})
            item_piezas.addChild(it)

        # Rama 3: Vanos y Cavidades
        item_vanos = QtWidgets.QTreeWidgetItem(["🔲 Vanos y Cavidades"])
        item_vanos.setData(0, QtCore.Qt.UserRole, {"tipo": "vanos_header", "obj": obj})
        raiz.addChild(item_vanos)

        if resolved is not None:
            for cell in resolved.walk_cells():
                lbl = getattr(cell, "label", "(x1, y1)")
                it_cell = QtWidgets.QTreeWidgetItem([f"🔲 {lbl} [{cell.w:.0f}×{cell.h:.0f}]"])  # noqa: RUF001 - etiqueta de interfaz: signo tipografico visible (x o -) que el usuario ve; cambiarlo altera el texto
                it_cell.setData(0, QtCore.Qt.UserRole, {"tipo": "vano", "label": lbl, "cell": cell})
                item_vanos.addChild(it_cell)

                # Insertos anidados bajo la celda
                ins_cfg = contenido_por_celda.get(lbl, {})
                tipo_ins = ins_cfg.get("tipo")
                if tipo_ins == "cajon":
                    it_ins = QtWidgets.QTreeWidgetItem([f"🗄️ Cajón ({ins_cfg.get('n_cajones', 1)}x)"])
                    it_ins.setData(0, QtCore.Qt.UserRole, {"tipo": "inserto_cajon", "cfg": ins_cfg, "cell": cell})
                    it_cell.addChild(it_ins)
                elif tipo_ins == "puerta":
                    it_ins = QtWidgets.QTreeWidgetItem([f"🚪 Puerta ({ins_cfg.get('sistema', 'Batiente')})"])
                    it_ins.setData(0, QtCore.Qt.UserRole, {"tipo": "inserto_puerta", "cfg": ins_cfg, "cell": cell})
                    it_cell.addChild(it_ins)

        raiz.setExpanded(True)
        item_chasis.setExpanded(True)
        item_vanos.setExpanded(True)
        self.master_tree.blockSignals(False)

    def _construir_rama_chasis(self, raiz, obj):
        # Rama 1: Chasis y Envolvente
        item_chasis = QtWidgets.QTreeWidgetItem(["🪵 Chasis y Envolvente"])
        item_chasis.setData(0, QtCore.Qt.UserRole, {"tipo": "chasis", "obj": obj})
        raiz.addChild(item_chasis)

        caras_chasis = [
            ("━━ Tapa Superior", "superior"),
            ("━━ Base Inferior", "inferior"),
            ("◀ Lateral Izquierdo", "izquierda"),
            ("Lateral Derecho ▶", "derecha"),
            ("▦ Fondo Trasero", "fondo"),
            ("⌸ Zócalo Base", "zocalo"),
        ]
        for nom, face_id in caras_chasis:
            it = QtWidgets.QTreeWidgetItem([nom])
            it.setData(0, QtCore.Qt.UserRole, {"tipo": "chasis_face", "face": face_id})
            item_chasis.addChild(it)
        return item_chasis

    def _on_tree_item_clicked(self, item, column):
        data = item.data(0, QtCore.Qt.UserRole)
        if not data or not isinstance(data, dict):
            return

        tipo = data.get("tipo")
        if tipo in ("coco", "chasis", "chasis_face"):
            self._ir_a_nivel(PAGE_CHASIS, VDOSelectionBridge.TARGET_COCO)
            if self.preview is not None:
                self.preview.set_selected(None)

        elif tipo == "pieza":
            p = data.get("pieza", {})
            self.pagina_pieza.cargar_pieza_dict(p)
            self._ir_a_nivel(PAGE_PIEZA, VDOSelectionBridge.TARGET_PANEL)
            if self.preview is not None:
                self.preview.set_selected_panel(p.get("key", ""))

        elif tipo == "piezas_header":
            self._ir_a_nivel(PAGE_PIEZA, VDOSelectionBridge.TARGET_PANEL)

        elif tipo == "vano":
            cell = data.get("cell")
            self.pagina_vano.cargar_vano_cell(cell, fondo=_float_seguro(getattr(self._obj_actual, "FondoModulo", 550.0)))
            self._ir_a_nivel(PAGE_VANO, getattr(VDOSelectionBridge, "TARGET_VANO", "VANO"))
            if self.preview is not None:
                self.preview.set_selected(data.get("label", ""))

        elif tipo in ("inserto_cajon", "inserto_puerta"):
            cfg = data.get("cfg", {})
            self.pagina_cierre.cargar_cierre_desde_config(tipo, cfg)
            self._ir_a_nivel(PAGE_CIERRE, "CAJON" if "cajon" in tipo else "PUERTA")


    # ------------------------------------------------------------------
    # Clics del Visor 2D (CocoPreview2D) -> Árbol y Páginas
    # ------------------------------------------------------------------
    def _on_preview_cell_clicked(self, label):
        self._seleccionar_item_en_arbol("label", label)
        if self._resolved_layout is not None:
            for cell in self._resolved_layout.walk_cells():
                if getattr(cell, "label", "") == label:
                    self.pagina_vano.cargar_vano_cell(cell, fondo=_float_seguro(getattr(self._obj_actual, "FondoModulo", 550.0)))
                    break
        self._ir_a_nivel(PAGE_VANO, getattr(VDOSelectionBridge, "TARGET_VANO", "VANO"))

    def _on_preview_panel_clicked(self, clave):
        self._seleccionar_item_en_arbol("clave", clave)
        for p in self._piezas_calculadas:
            if p.get("key") == clave:
                self.pagina_pieza.cargar_pieza_dict(p)
                break
        self._ir_a_nivel(PAGE_PIEZA, VDOSelectionBridge.TARGET_PANEL)

    def _on_preview_reengrose_clicked(self, clave):
        self._on_preview_panel_clicked(clave)

    def _seleccionar_item_en_arbol(self, campo, valor):
        """Busca y selecciona el elemento en el QTreeWidget Maestro."""
        it = QtWidgets.QTreeWidgetItemIterator(self.master_tree)
        while it.value():
            item = it.value()
            data = item.data(0, QtCore.Qt.UserRole)
            if isinstance(data, dict) and data.get(campo) == valor:
                self.master_tree.blockSignals(True)
                self.master_tree.setCurrentItem(item)
                self.master_tree.blockSignals(False)
                return
            it += 1


    # ------------------------------------------------------------------
    # Puente de selección nativa FreeCAD
    # ------------------------------------------------------------------
    def _inicializar_puente(self):
        self._puente = VDOSelectionBridge(
            on_target_changed=self._on_selection_changed)
        self._puente.attach()

    def _on_selection_changed(self, obj, target_type):
        """Reacción reactiva a un cambio de selección en FreeCAD."""
        try:
            self._obj_actual = obj
            self._tipo_actual = target_type

            if obj is None or target_type == VDOSelectionBridge.TARGET_UNKNOWN:
                self._ir_a_nivel(PAGE_CHASIS, VDOSelectionBridge.TARGET_UNKNOWN)
                return

            page = _TARGET_TO_PAGE.get(target_type, PAGE_CHASIS)

            if page == PAGE_CHASIS and target_type == VDOSelectionBridge.TARGET_COCO:
                self.cargar_coco(obj)
            elif page == PAGE_PIEZA and target_type == VDOSelectionBridge.TARGET_PANEL:
                self.pagina_pieza.cargar_panel(obj)
            elif page == PAGE_CIERRE:
                self.pagina_cierre.cargar_cierre(obj, target_type)
            elif page == PAGE_VANO:
                self.pagina_vano.cargar_vano(obj)
            else:
                self._ir_a_nivel(PAGE_CHASIS, VDOSelectionBridge.TARGET_UNKNOWN)
                return

            self._ir_a_nivel(page, target_type)

        except Exception:
            App.Console.PrintWarning(
                "[VDO] Error navegando a nivel de página")
            try:
                self._ir_a_nivel(PAGE_CHASIS, VDOSelectionBridge.TARGET_UNKNOWN)
            except Exception:
                App.Console.PrintWarning(
                    "[VDO] No se pudo navegar a la página de chasis")
