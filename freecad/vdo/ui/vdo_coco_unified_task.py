# =====================================================================
# vdo_coco_unified_task.py
# Task Panel UNIFICADO para COCO: edita TODO (básico + espacios + pose).
# Se abre por clic derecho, doble clic o flujo de creación.
# =====================================================================

import json
import FreeCAD as App

from freecad.vdo.cad.colocacion import aplicar_rotacion
from freecad.vdo.cad.documento import (
    crear_objeto,
    eliminar_objeto,
    recalcular_activo,
)
from freecad.vdo.cad.propiedades import (
    add_common_props,
    anadir_propiedad_texto,
    asignar_placement_local,
    asignar_propiedades,
)
from freecad.vdo.core import vdo_frames as VDO_FR
from freecad.vdo.core.vdo_facade_contract import (
    APERTURA_45_GRADOS,
    APERTURA_GOLA,
    APERTURA_PUSH_OPEN,
    APERTURA_TIRADOR,
    CALLE_ENTRE_FRENTES_DEFAULT,
)
from freecad.vdo.core.vdo_module_props import ANCLAJE_DEFAULT
from freecad.vdo.core.vdo_spaces import (
    ESPACIO_FIJO,
    ESPACIO_IGUALES,
    ESPACIO_RESTANTE,
    SpaceNode,
)
from freecad.vdo.datos.valores import BLUM_TANDEM
from freecad.vdo.qt_compat import QtCore, QtWidgets
from freecad.vdo.ui.vdo_task_base import VDOTransactionMixin, cerrar_dialogo
from freecad.vdo.ui.coco_unified_tabla import (
    COL_ACCIONES,
    COL_RESUMEN,
    COL_TIPO,
    COL_VALOR,
    EspacioRow,
    ROLE_NODE_ID,
    TIPOS_LABELS,
)
from freecad.vdo.ui.coco_unified_construccion import (
    CocoUnifiedConstruccionMixin,
)
from freecad.vdo.ui.coco_unified_pestanas import CocoUnifiedPestanasMixin


class CocoUnifiedTaskPanel(
    CocoUnifiedConstruccionMixin,
    CocoUnifiedPestanasMixin,
    VDOTransactionMixin,
):
    """Task Panel UNIFICADO: Medidas + Estructura + Divisiones + Colocación."""

    def __init__(self, obj=None, on_accept=None, on_cancel=None,
                 auto_transaction=True):
        self.obj = obj
        self._vdo_aceptado = False
        self._current_axis = "X"
        self._rows_x = []
        self._rows_y = []
        self._selected_paths = {"X": [], "Y": []}
        self._building = False
        self.spin_dividir = {}
        self.spin_dividir_hijo = {}
        self._init_vdo_task(
            on_accept=on_accept,
            on_cancel=on_cancel,
            auto_transaction=auto_transaction,
            transaction_name="Editar COCO Completo",
        )
        self.form = self._crear_widget()
        if obj:
            add_common_props(obj)
            if not hasattr(obj, "VDO_Reengrose_JSON"):
                anadir_propiedad_texto(
                    obj, "VDO_Reengrose_JSON",
                    "Reengrose",
                    "Modificadores de reengrose por pieza (JSON)"
                ).VDO_Reengrose_JSON = "{}"
            if not hasattr(obj, "VDO_Contenido_JSON"):
                anadir_propiedad_texto(
                    obj, "VDO_Contenido_JSON",
                    "Contenido",
                    "Contenido de vanos (puertas, cajones) (JSON)"
                ).VDO_Contenido_JSON = "{}"
            self._cargar_valores(obj)

    def _cargar_valores(self, obj):
        """Carga todas las propiedades del objeto en el panel."""
        self._building = True

        self.spin_alto.setValue(float(obj.Alto))
        self.spin_ancho.setValue(float(obj.Ancho))
        self.spin_fondo.setValue(float(obj.FondoModulo))
        self.spin_espesor.setValue(int(obj.Espesor))

        if hasattr(self, "box_chassis") and self.box_chassis is not None:
            raw_cfg = getattr(obj, "VDO_Chassis_JSON", None)
            cfg = None
            if raw_cfg:
                try:
                    cfg = json.loads(raw_cfg) if isinstance(raw_cfg, str) else raw_cfg
                except Exception:
                    cfg = None
            if not cfg or not isinstance(cfg, dict):
                tapa = getattr(obj, "Tapa", "externo")
                base = getattr(obj, "Base", "interno")
                tiene_fondo = getattr(obj, "TieneFondo", True)
                cfg = {
                    "caras": {
                        "superior": {"activa": True, "tipo": "estructural"},
                        "inferior": {"activa": True, "tipo": "estructural"},
                        "izquierda": {"activa": True, "tipo": "estructural"},
                        "derecha": {"activa": True, "tipo": "estructural"},
                        "fondo": {"activa": bool(tiene_fondo), "tipo": "ranurado_5mm"},
                    },
                    "encuentros": {
                        "superior_izq": "tapa_domina" if tapa == "externo" else "lateral_domina",
                        "superior_der": "tapa_domina" if tapa == "externo" else "lateral_domina",
                        "inferior_izq": "base_domina" if base == "externo" else "lateral_domina",
                        "inferior_der": "base_domina" if base == "externo" else "lateral_domina",
                    },
                    "base": {
                        "estrategia": "zocalo" if getattr(obj, "AltoZocalo", None) else "zocalo",
                        "altura": float(getattr(obj, "AltoZocalo", 100.0) or 100.0),
                        "separacion_frente": float(getattr(obj, "DistanciaFrente", 50.0) or 50.0),
                    }
                }
            self.box_chassis.setChassisConfig(cfg)

        self.spin_rotacion.setValue(
            float(getattr(obj, "VDO_RotacionZ", 0.0)))
        anclaje = getattr(obj, "VDO_Anclaje", ANCLAJE_DEFAULT)
        for i in range(self.combo_anclaje.count()):
            if self.combo_anclaje.itemData(i) == anclaje:
                self.combo_anclaje.setCurrentIndex(i)
                break

        vistos, apoyados = VDO_FR.cargar_exposicion(obj)
        for lado, combo in self.combos_exposicion.items():
            estado = "oculto"
            if lado in vistos:
                estado = "visto"
            elif lado in apoyados:
                estado = "apoyado"
            idx = combo.findData(estado)
            if idx >= 0:
                combo.setCurrentIndex(idx)

        self._rows_x = []
        self._rows_y = []
        self._selected_paths = {"X": [], "Y": []}

        self.editor_divisiones.set_dimensions(
            self.spin_alto.value(), self.spin_ancho.value(),
            self.spin_espesor.value())
        self.editor_divisiones.cargar_desde_objeto(obj)

        self._actualizar_resumen()
        self._building = False

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
        except (IndexError, TypeError):
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
        except ValueError:
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

    def _leer_valores_ui(self):
        cfg = self.box_chassis.getChassisConfig() if hasattr(self, "box_chassis") and self.box_chassis else {}
        enc_sup = cfg.get("encuentros", {}).get("superior_izq", "tapa_domina")
        enc_inf = cfg.get("encuentros", {}).get("inferior_izq", "lateral_domina")
        tapa_val = "externo" if enc_sup == "tapa_domina" else "interno"
        base_val = "externo" if enc_inf == "base_domina" else "interno"
        return {
            "alto": self.spin_alto.value(),
            "ancho": self.spin_ancho.value(),
            "fondo": self.spin_fondo.value(),
            "espesor": self.spin_espesor.value(),
            "tapa": tapa_val,
            "base": base_val,
        }

    def _actualizar_resumen(self):
        valores = self._leer_valores_ui()
        espesor = float(valores["espesor"])
        ancho_util = valores["ancho"] - (espesor * 2)
        alto_util = valores["alto"] - (espesor * 2)
        texto = (
            f"COCO {valores['ancho']:.0f} × {valores['alto']:.0f} × "
            f"{valores['fondo']:.0f} mm\n"
            f"Cavidad interior: {ancho_util:.1f} × {alto_util:.1f} mm\n"
            f"Tapa: {valores['tapa']} · Base: {valores['base']} · "
            f"Espesor: {espesor:.0f} mm\n\n")
        texto += self.editor_divisiones.resumen()
        if self.editor_divisiones.tiene_overflow():
            texto += ("\n\n⚠ OVERFLOW: corrige las medidas fijas "
                      "antes de aplicar.")
        self.lbl_resumen.setText(texto)

    def _on_ok(self):
        if self.accept():
            cerrar_dialogo()

    def _on_cancel(self):
        self.reject()
        cerrar_dialogo()

    def _construir_insertos(self, coco_obj):
        """Crea o actualiza los objetos hijos (puertas, cajones) del COCO.

        Se llama solo al presionar "Aceptar". No muta el documento antes.
        Gestiona huérfanos: elimina hijos cuyo vano ya no tenga contenido.
        """
        doc = App.ActiveDocument
        if doc is None:
            return

        # Leer contenido persistido
        texto = getattr(coco_obj, "VDO_Contenido_JSON", "") or "{}"
        try:
            contenido = json.loads(texto) if isinstance(texto, str) else {}
        except (ValueError, TypeError):
            contenido = {}
        # Convertir claves "i,j" a tuplas (col, row)
        contenido_tuplas = {}
        for k, v in contenido.items():
            try:
                col, row = map(int, str(k).split(","))
                contenido_tuplas[(col, row)] = v
            except (ValueError, TypeError):
                continue

        # Resolved map para obtener cotas de celdas
        editor = self.editor_divisiones
        resolved_map = getattr(editor, "_resolved_map", {})
        layout = getattr(editor, "layout", None)

        hijos_nuevos = []
        celdas_procesadas = set()

        for (col, row), datos in contenido_tuplas.items():
            celdas_procesadas.add((col, row))
            tipo = datos.get("tipo", "vacio")
            cfg = datos.get("config", {})

            if layout is None:
                continue
            cell = layout.get_cell(col, row)
            if cell is None:
                continue
            resuelto = resolved_map.get(cell.label)
            if resuelto is None:
                continue

            x = float(getattr(resuelto, "nominal_x", 0.0))
            z = float(getattr(resuelto, "nominal_z", 0.0))
            w = float(resuelto.w)
            h = float(resuelto.h)

            if tipo == "puerta":
                self._construir_puerta(
                    doc, coco_obj, cfg, x, z, w, h, hijos_nuevos)
            elif tipo == "cajon" or tipo == "cajon_torre":
                self._construir_cajones(
                    doc, coco_obj, cfg, x, z, w, h, hijos_nuevos)

        # --- Gestión de huérfanos ---
        hijos_actuales = list(coco_obj.Hijos or [])
        claves_activas = set()
        for hijo in hijos_nuevos:
            claves_activas.add(hijo.Name)
        for hijo in hijos_actuales:
            if hijo.Name not in claves_activas:
                try:
                    eliminar_objeto(doc, hijo.Name)
                except Exception:
                    App.Console.PrintWarning(
                        f"[VDO] No se pudo remover el hijo {hijo.Name}")

        asignar_propiedades(coco_obj, {"Hijos": hijos_nuevos})

    def _construir_puerta(self, doc, coco_obj, cfg, x, z, w, h, hijos_nuevos):
        """Crea o actualiza una puerta como hijo del COCO."""
        nombre = cfg.get("nombre", f"Puerta_{coco_obj.Name}")
        # Buscar si ya existe
        existente = None
        for hijo in list(coco_obj.Hijos or []):
            if hijo.Name == nombre:
                existente = hijo
                break

        if existente is None:
            existente = crear_objeto(doc, "Part::FeaturePython", nombre)
            from freecad.vdo.cad.puerta import PuertaFeature
            PuertaFeature(existente)
            if App.GuiUp:
                from freecad.vdo.ui.vdo_view_providers import ViewProviderPuerta
                ViewProviderPuerta(existente.ViewObject)

        # Propiedades de la puerta
        asignar_propiedades(existente, {"TipoSistema": cfg.get("tipo_sistema", "Batiente Vertical")})
        asignar_propiedades(existente, {"TipoMontaje": cfg.get("tipo_montaje", "Parche")})
        asignar_propiedades(existente, {"SentidoApertura": cfg.get("sentido_apertura", "Izquierda")})
        asignar_propiedades(existente, {"SistemaApertura": cfg.get(
            "sistema_apertura", APERTURA_TIRADOR)})
        asignar_propiedades(existente, {"HardwareSKU": cfg.get("hardware_sku", "")})
        asignar_propiedades(existente, {"VDO_Vano_ID": cfg.get("vdo_vano_id", "")})
        asignar_propiedades(existente, {"Ancho": float(cfg.get("ancho", w))})
        asignar_propiedades(existente, {"Alto": float(cfg.get("alto", h))})
        asignar_propiedades(existente, {"Espesor": int(cfg.get("espesor", 18))})
        asignar_propiedades(existente, {"PosX": float(cfg.get("pos_x", x))})
        asignar_propiedades(existente, {"PosY": float(cfg.get("pos_y", 0.0))})
        asignar_propiedades(existente, {"PosZ": float(cfg.get("pos_z", z))})
        asignar_propiedades(existente, {"VDO_Anclaje": cfg.get("anclaje", "inferior_izquierda_frente")})

        # Vínculo padre-hijo
        asignar_propiedades(existente, {"ParentCOCO": coco_obj})
        asignar_placement_local(existente, App.Placement(
            App.Vector(
                float(cfg.get("pos_x", x)),
                float(cfg.get("pos_y", 0.0)),
                float(cfg.get("pos_z", z)),
            ), App.Rotation()))

        hijos_nuevos.append(existente)

    def _construir_cajones(self, doc, coco_obj, cfg, x, z, w, h, hijos_nuevos):
        """Crea o actualiza cajones (1 o más, torre apilada) como hijos del COCO."""
        cantidad = int(cfg.get("cantidad", 1))
        corredera = cfg.get("corredera", "Oculta")
        apertura = cfg.get("apertura", "Tirador")
        nombre_base = cfg.get("nombre", f"Cajon_{coco_obj.Name}")

        # Calcular altura individual de frente para torre N cajones
        h_frente = (h - (cantidad - 1) * CALLE_ENTRE_FRENTES_DEFAULT) / cantidad
        if h_frente <= 0:
            h_frente = max(10.0, h / max(cantidad, 1))

        from freecad.vdo.core.vdo_cajon_correderas import (
            CORREDERA_OCULTA,
            CORREDERA_TELESCOPICA,
        )
        tipo_corredera = CORREDERA_OCULTA if corredera == "Oculta" else CORREDERA_TELESCOPICA

        apertura_map = {
            "Tirador": APERTURA_TIRADOR,
            "Gola": APERTURA_GOLA,
            "45°": APERTURA_45_GRADOS,
            "Push": APERTURA_PUSH_OPEN,
        }
        sistema_apertura = apertura_map.get(apertura, APERTURA_TIRADOR)

        for i in range(cantidad):
            nombre = f"{nombre_base}_{i + 1:02d}"
            # Buscar si ya existe
            existente = None
            for hijo in list(coco_obj.Hijos or []):
                if hijo.Name == nombre:
                    existente = hijo
                    break

            if existente is None:
                existente = crear_objeto(doc, "Part::FeaturePython", nombre)
                from freecad.vdo.cad.cajon import CajonFeature
                CajonFeature(existente)
                if App.GuiUp:
                    from freecad.vdo.ui.vdo_view_providers import ViewProviderCajon
                    ViewProviderCajon(existente.ViewObject)

            # Propiedades del cajón
            asignar_propiedades(existente, {"AnchoLibre": w})
            asignar_propiedades(existente, {"ProfLibre": float(getattr(coco_obj, "FondoModulo", 580.0))})
            asignar_propiedades(existente, {"AnchoModulo": w})
            asignar_propiedades(existente, {"AltoFrente": h_frente})
            # default 90mm
            asignar_propiedades(existente, {"AltoCaja": float(getattr(coco_obj, "Espesor", 18)) * 5})
            asignar_propiedades(existente, {"GrosorCaja": 16.0})
            asignar_propiedades(existente, {"GrosorFondo": 6.0})
            asignar_propiedades(existente, {"GrosorFachada": 18.0})
            asignar_propiedades(existente, {"MarcaCorredera": BLUM_TANDEM})
            asignar_propiedades(existente, {"LongitudGuia": 0.0})
            asignar_propiedades(existente, {"MontajeTrasera": "entre_laterales"})
            asignar_propiedades(existente, {"TipoCorredera": tipo_corredera})
            asignar_propiedades(existente, {"SistemaApertura": sistema_apertura})

            # Vínculo padre-hijo con z escalonado
            z_local = z + i * (h_frente + CALLE_ENTRE_FRENTES_DEFAULT)
            asignar_propiedades(existente, {"ParentCOCO": coco_obj})
            asignar_placement_local(existente, App.Placement(
                App.Vector(x, 0.0, z_local), App.Rotation()))

            hijos_nuevos.append(existente)

    def accept(self):
        if not self.obj:
            return True
        try:
            self._vdo_begin()

            for spin in (self.spin_alto, self.spin_ancho,
                         self.spin_fondo, self.spin_espesor,
                         self.spin_rotacion):
                spin.interpretText()

            asignar_propiedades(self.obj, {"Alto": self.spin_alto.value()})
            asignar_propiedades(self.obj, {"Ancho": self.spin_ancho.value()})
            asignar_propiedades(self.obj, {"FondoModulo": self.spin_fondo.value()})
            asignar_propiedades(self.obj, {"Espesor": self.spin_espesor.value()})

            if hasattr(self, "box_chassis") and self.box_chassis is not None:
                cfg = self.box_chassis.getChassisConfig()
                enc_sup = cfg.get("encuentros", {}).get("superior_izq", "tapa_domina")
                enc_inf = cfg.get("encuentros", {}).get("inferior_izq", "lateral_domina")
                asignar_propiedades(self.obj, {"Tapa": "externo" if enc_sup == "tapa_domina" else "interno"})
                asignar_propiedades(self.obj, {"Base": "externo" if enc_inf == "base_domina" else "interno"})
                asignar_propiedades(self.obj, {"TieneFondo": bool(cfg.get("caras", {}).get("fondo", {}).get("activa", True))})

                base_info = cfg.get("base", {})
                if "altura" in base_info and hasattr(self.obj, "AltoZocalo"):
                    try:
                        asignar_propiedades(self.obj, {"AltoZocalo": float(base_info["altura"])})
                    except Exception:
                        App.Console.PrintWarning(
                            "[VDO] No se pudo establecer AltoZocalo")
                if "separacion_frente" in base_info and hasattr(self.obj, "DistanciaFrente"):
                    try:
                        asignar_propiedades(self.obj, {"DistanciaFrente": float(base_info["separacion_frente"])})
                    except Exception:
                        App.Console.PrintWarning(
                            "[VDO] No se pudo establecer DistanciaFrente")

                try:
                    if hasattr(self.obj, "VDO_Chassis_JSON"):
                        asignar_propiedades(self.obj, {"VDO_Chassis_JSON": json.dumps(cfg)})
                    elif hasattr(self.obj, "addProperty"):
                        anadir_propiedad_texto(self.obj, "VDO_Chassis_JSON", "VDO",
                                           "Configuración semiótica de Capa 1")
                        asignar_propiedades(self.obj, {"VDO_Chassis_JSON": json.dumps(cfg)})
                except Exception:
                    App.Console.PrintWarning(
                        "[VDO] No se pudo persistir VDO_Chassis_JSON")

            anclaje = self.combo_anclaje.currentData()
            if anclaje:
                asignar_propiedades(self.obj, {"VDO_Anclaje": anclaje})
            aplicar_rotacion(self.obj, self.spin_rotacion.value())

            if self.editor_divisiones.tiene_overflow():
                QtWidgets.QMessageBox.warning(
                    self.form, "Divisiones VDO",
                    "Las medidas fijas no caben en la cavidad interior.\n"
                    "Reduce alguna medida antes de aplicar.")
                self._vdo_abort()
                return False

            vistos = []
            apoyados = []
            for lado, combo in self.combos_exposicion.items():
                estado = combo.currentData()
                if estado == "visto":
                    vistos.append(lado)
                elif estado == "apoyado":
                    apoyados.append(lado)
            VDO_FR.guardar_exposicion(self.obj, vistos, apoyados)

            if not hasattr(self.obj, "VDO_Divisiones"):
                anadir_propiedad_texto(
                    self.obj, "VDO_Divisiones", "Divisiones",
                    "Matriz de vanos v2 (JSON)")
            asignar_propiedades(self.obj, {"VDO_Divisiones": self.editor_divisiones.dumps()})
            asignar_propiedades(self.obj, {"VDO_Reengrose_JSON": (
                self.editor_divisiones.dumps_reengroses())})
            asignar_propiedades(self.obj, {"VDO_Contenido_JSON": (
                self.editor_divisiones.dumps_contenido())})

            # --- Construir insertos solo al aceptar (ciclo transaccional) ---
            self._construir_insertos(self.obj)

            recalcular_activo()
            self._vdo_commit()
            self._vdo_aceptado = True
            self._vdo_call_accept()
            return True
        except Exception as exc:
            self._vdo_abort()
            App.Console.PrintError(
                f"[VDO] Error aceptando COCO: {exc}\n")
            import traceback
            App.Console.PrintError(traceback.format_exc())
            return False
