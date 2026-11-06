"""Inspector de la matriz COCO: cabecera de pieza y actualizacion del inspector.

Extraido de vdo_widgets_coco.py (M7, D-40). Sin cambios de codigo."""

import logging

from freecad.vdo.core import (
    finish as VDO_FIN,
)
from freecad.vdo.core import (
    reengrose_geometria as VDO_RE_GEOMETRIA,
)
from freecad.vdo.core import (
    reengrose_modificador as VDO_RE_MODIFICADOR,
)
from freecad.vdo.core.facade_contract import (
    APERTURA_45_GRADOS,
    APERTURA_GOLA,
    APERTURA_PUSH_OPEN,
    APERTURA_TIRADOR,
)
from freecad.vdo.core.layout_modelo import AXIS_X, AXIS_Y
from freecad.vdo.qt_compat import QtWidgets
from freecad.vdo.ui import tema

_LOG = logging.getLogger(__name__)

BORDE_LABELS = {
    "norte": "Norte", "sur": "Sur", "este": "Este", "oeste": "Oeste"}


class PanelHeaderWidget(QtWidgets.QGroupBox):
    """Encabezado universal para una pieza física o una tira de reengrose."""

    def __init__(self, parent=None):
        super().__init__("Encabezado de pieza", parent)
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(6, 4, 6, 4)
        layout.setSpacing(2)

        self.lbl_nombre = QtWidgets.QLabel("Sin selección")
        tema.aplicar_estilo(self.lbl_nombre, tema.ESTILO_NEGRITA)
        self.lbl_nombre.setWordWrap(True)
        layout.addWidget(self.lbl_nombre)

        self.lbl_dimensiones = QtWidgets.QLabel("—")
        self.lbl_dimensiones.setToolTip(
            "Dimensiones brutas de corte: Largo × Ancho × Espesor.")
        layout.addWidget(self.lbl_dimensiones)

        self.lbl_cantos = QtWidgets.QLabel("")
        self.lbl_cantos.setWordWrap(True)
        tema.aplicar_estilo(self.lbl_cantos, tema.ESTILO_ETIQUETA_OSCURA_COMPACTA)
        layout.addWidget(self.lbl_cantos)

        self._cantos_labels = {}
        self.set_panel("Sin selección", 0.0, 0.0, 0.0)

    def _normalizar_cantos(self, cantos):
        datos = {}
        for borde in VDO_FIN.BORDES:
            valor = str((cantos or {}).get(borde, "FX") or "FX").upper()
            datos[borde] = valor
        return datos

    def set_panel(self, nombre, largo, ancho, espesor, cantos=None,
                  sufijo=""):
        nombre = str(nombre or "Pieza")
        if sufijo:
            nombre = f"{nombre} {sufijo}"
        self.lbl_nombre.setText(nombre)
        self.lbl_dimensiones.setText(
            f"{float(largo):.1f} × {float(ancho):.1f} × "
            f"{float(espesor):.1f} mm")
        datos = self._normalizar_cantos(cantos)
        self.lbl_cantos.setText(" · ".join(
            f"{BORDE_LABELS[borde]}: {datos[borde]}" for borde in VDO_FIN.BORDES))

    def set_strip(self, nombre, largo, ancho, espesor, cantos=None):
        self.set_panel(nombre, largo, ancho, espesor, cantos,
                       sufijo="(tira de reengrose)")

    def clear(self):
        self.lbl_nombre.setText("Sin selección")
        self.lbl_dimensiones.setText("—")
        self.lbl_cantos.setText("")

    def cantos_texto(self):
        return self.lbl_cantos.text()


class InspectorDivisionesMixin:
    """Mixin de DivisionesEditor (ver coco_construccion_widgets.py)."""

    def _actualizar_inspector(self):
        data = self._selected_data
        if not data:
            self.header.setVisible(False)
            self.lbl_nominal_neto.setVisible(False)
            self.lbl_invasores.setVisible(False)
            self.lbl_sel.setText("Sin selección.")
            return
        self._building = True
        kind = data["kind"]
        es_pieza = kind in (
            "piece", "reengrose_piece", "elemento_reengrose")
        self._actualizar_visibilidad_base(kind, es_pieza)
        if kind in ("cell", "nested"):
            self._actualizar_contenido_celda(data)
        elif kind == "contenido_hijo":
            self._actualizar_contenido_hijo(data)
        if es_pieza:
            self._actualizar_pieza(data, kind)
            self._actualizar_aviso_overflow()
            return

        self.inspector.setTitle("Inspector del vano")
        cell = data.get("cell")
        if kind == "row":
            self._actualizar_fila(data)
        else:
            resuelto = self._resolved_map.get(cell.label)
            self._actualizar_vano_resumen(cell, resuelto)
            if kind == "cell":
                self._actualizar_celda_fija(data, cell, resuelto)
            else:
                self._actualizar_subdivision_fija(data, cell, resuelto)

        self._building = False
        self._actualizar_aviso_overflow()

    def _actualizar_visibilidad_base(self, kind, es_pieza):
        self.header.setVisible(es_pieza)
        self.grupo_reengrose.setVisible(es_pieza)
        self.lbl_nominal_neto.setVisible(
            kind in ("cell", "nested"))
        self.lbl_invasores.setVisible(kind in ("cell", "nested"))
        self.widget_col_fixed.setVisible(kind == "cell")
        self.widget_row_fixed.setVisible(kind in ("cell", "row"))
        self.widget_cell_fixed.setVisible(kind == "nested")
        self.lbl_contenido.setVisible(kind in ("cell", "nested"))
        self.combo_contenido.setVisible(kind in ("cell", "nested"))
        self.widget_split.setVisible(False)
        self.widget_puerta.setVisible(False)
        self.widget_cajon.setVisible(False)
        self.lbl_aviso.setText("")

    def _actualizar_contenido_celda(self, data):
        cell = data.get("cell")
        contenido = self._contenido_por_celda.get(
            (data.get("col_index"), data.get("row_index")), {"tipo": "vacio"})
        idx = self.combo_contenido.findData(contenido["tipo"])
        if idx >= 0:
            self.combo_contenido.blockSignals(True)
            self.combo_contenido.setCurrentIndex(idx)
            self.combo_contenido.blockSignals(False)
        self._mostrar_panel_contenido(contenido["tipo"])

    def _actualizar_contenido_hijo(self, data):
        tipo = data.get("tipo")
        cfg = data.get("config", {})
        celda = data.get("celda")
        celda_label = ""
        if celda:
            try:
                col, row = celda
                resuelto = self._resolved_map.get(
                    self.layout.get_cell(col, row).label
                )
                if resuelto is not None:
                    celda_label = resuelto.label
            except (ValueError, TypeError, AttributeError) as exc:
                _LOG.debug("coco_inspector_widgets: celda sin formato, usa texto plano: %s", exc)
                celda_label = f"{celda}"
        # Ocultar panel de pieza física
        self.header.setVisible(False)
        self.grupo_reengrose.setVisible(False)
        self.lbl_nominal_neto.setVisible(False)
        self.lbl_invasores.setVisible(False)
        self.widget_col_fixed.setVisible(False)
        self.widget_row_fixed.setVisible(False)
        self.widget_cell_fixed.setVisible(False)
        self.lbl_contenido.setVisible(False)
        self.combo_contenido.setVisible(False)
        self.widget_split.setVisible(False)
        self.lbl_aviso.setText("")
        if tipo == "cajon":
            self._actualizar_cajon(celda_label, cfg)
        elif tipo == "puerta":
            self._actualizar_puerta(celda_label, cfg)

    def _actualizar_cajon(self, celda_label, cfg):
        self.inspector.setTitle("Inspector de cajón")
        self.lbl_sel.setText(
            f"<b>Cajón en vano {celda_label}</b>")
        self.widget_cajon.setVisible(True)
        self.widget_puerta.setVisible(False)
        # Cargar valores actuales en los spinners/combos
        self._building = True
        self.spin_cajon_cantidad.setValue(
            int(cfg.get("cantidad", 1)))
        self._set_combo_data(
            self.combo_cajon_corredera,
            cfg.get("corredera", "Oculta"))
        self._set_combo_data(
            self.combo_cajon_apertura,
            cfg.get("apertura", "Tirador"))
        self._building = False

    def _actualizar_puerta(self, celda_label, cfg):
        self.inspector.setTitle("Inspector de puerta")
        self.lbl_sel.setText(
            f"<b>Puerta en vano {celda_label}</b>")
        self.widget_puerta.setVisible(True)
        self.widget_cajon.setVisible(False)
        # Cargar valores actuales en los combos
        self._building = True
        self._set_combo_data(
            self.combo_puerta_familia,
            cfg.get("tipo_sistema", "Batiente Vertical"))
        self._set_combo_data(
            self.combo_puerta_montaje,
            cfg.get("tipo_montaje", "Parche"))
        apertura_val = cfg.get("sistema_apertura", APERTURA_TIRADOR)
        apertura_label = {
            APERTURA_TIRADOR: "Tirador",
            APERTURA_GOLA: "Gola",
            APERTURA_45_GRADOS: "45°",
            APERTURA_PUSH_OPEN: "Push Open",
        }.get(apertura_val, "Tirador")
        self._set_combo_data(
            self.combo_puerta_apertura, apertura_label)
        self._set_combo_data(
            self.combo_puerta_herraje,
            cfg.get("hardware_sku", ""))
        self._building = False

    def _actualizar_pieza(self, data, kind):
        pieza = data.get("pieza")
        if pieza is None:
            pieza = self._pieza_por_clave(data["clave"])
        self.inspector.setTitle("Inspector de pieza")
        if pieza is not None:
            es_reengrose = kind != "piece"
            self._actualizar_header_pieza(pieza, es_reengrose)
            if es_reengrose:
                self.lbl_sel.setText(
                    f"🪵 Reengrose de {pieza['nombre']}")
            else:
                self.lbl_sel.setText(f"Pieza {pieza['nombre']}")
        else:
            self.header.clear()
            self.lbl_sel.setText("Pieza no disponible.")
        self.widget_split.setVisible(False)
        self.widget_puerta.setVisible(False)
        self.widget_cajon.setVisible(False)
        self.lbl_nominal_neto.setText("")
        self.lbl_invasores.setText("")
        self._building = False

    def _actualizar_fila(self, data):
        row = data["row"]
        self.lbl_sel.setText(f"Fila Y{data['row_index'] + 1}")
        self.chk_row_fixed.setChecked(row.fixed is not None)
        self.spin_row_fixed.setValue(
            row.fixed if row.fixed is not None else row.size)
        self.widget_split.setVisible(False)
        self.widget_puerta.setVisible(False)
        self.widget_cajon.setVisible(False)
        self.spin_row_fixed.setEnabled(row.fixed is not None)
        self.lbl_nominal_neto.setText("")
        self.lbl_invasores.setText("")

    def _actualizar_vano_resumen(self, cell, resuelto):
        self.lbl_sel.setText(
            f"Vano {cell.label}\nX libre: {resuelto.w:.1f} mm · "
            f"Y libre: {resuelto.h:.1f} mm")
        self.chk_col_fixed.setEnabled(True)
        if cell.axis and cell.children:
            idx = 0 if cell.axis == AXIS_X else 1
            self.combo_axis.setCurrentIndex(idx)
            self.spin_n.setValue(len(cell.children))
            self.combo_contenido.blockSignals(True)
            self.combo_contenido.setCurrentIndex(
                self.combo_contenido.findData("subdivision"))
            self.combo_contenido.blockSignals(False)
            self.widget_split.setVisible(True)
            self.widget_puerta.setVisible(False)
            self.widget_cajon.setVisible(False)
        else:
            self.combo_axis.setCurrentIndex(
                0 if self.combo_axis.currentData() != AXIS_Y else 1)
            self.spin_n.setValue(2)

        self.lbl_nominal_neto.setText(
            f"Nominal: {resuelto.nominal_w:.1f} × "
            f"{resuelto.nominal_h:.1f} mm\n"
            f"Neto: {resuelto.w:.1f} × {resuelto.h:.1f} mm")
        invasores = self._reengroses_invasores(resuelto)
        self.lbl_invasores.setText(
            ("Reengroses invasores: " + ", ".join(invasores))
            if invasores else "Sin reengroses invasores.")

    def _actualizar_celda_fija(self, data, cell, resuelto):
        col = self.layout.columns[data["col_index"]]
        row = self.layout.rows[data["row_index"]]
        self.lbl_sel.setText(
            f"Vano {cell.label} · columna X{data['col_index'] + 1} · "
            f"fila Y{data['row_index'] + 1}\n"
            f"X libre: {resuelto.w:.1f} mm · "
            f"Y libre: {resuelto.h:.1f} mm")
        self.chk_col_fixed.setChecked(col.fixed is not None)
        self.spin_col_fixed.setValue(
            col.fixed if col.fixed is not None else resuelto.w)
        self.spin_col_fixed.setEnabled(col.fixed is not None)
        self.chk_row_fixed.setChecked(row.fixed is not None)
        self.spin_row_fixed.setValue(
            row.fixed if row.fixed is not None else resuelto.h)
        self.spin_row_fixed.setEnabled(row.fixed is not None)
        self.widget_cell_fixed.setVisible(False)

    def _actualizar_subdivision_fija(self, data, cell, resuelto):
        axis = data.get("parent_axis")
        self.lbl_sel.setText(
            f"Vano {cell.label} · subdivisión local\n"
            f"X libre: {resuelto.w:.1f} mm · "
            f"Y libre: {resuelto.h:.1f} mm")
        self.chk_cell_fixed.setText(
            "Medida fija en X" if axis == AXIS_X
            else "Medida fija en Y")
        base = resuelto.w if axis == AXIS_X else resuelto.h
        self.chk_cell_fixed.setChecked(cell.fixed is not None)
        self.spin_cell_fixed.setValue(
            cell.fixed if cell.fixed is not None else base)
        self.spin_cell_fixed.setEnabled(
            cell.fixed is not None and not cell.axis)
        self.chk_cell_fixed.setEnabled(not cell.axis)
        if cell.axis:
            self.lbl_aviso.setText(
                "Vano subdividido: su medida exterior está "
                "congelada. Para cambiarla, edita el padre.")


    def _actualizar_header_pieza(self, pieza, es_reengrose):
        if pieza is None:
            self.header.clear()
            return
        if not es_reengrose:
            self.header.set_panel(
                pieza["nombre"], pieza["largo"], pieza["ancho"],
                pieza["espesor"], pieza["cantos"])
            return
        datos = self.reengroses.get(pieza["key"])
        cantos = self._cantos_pieza(
            pieza["rol"], pieza["key"], True)
        if not datos:
            self.header.set_panel(
                pieza["nombre"], pieza["largo"], pieza["ancho"],
                pieza["espesor"], cantos)
            return
        try:
            mod = VDO_RE_MODIFICADOR.ReengroseModifier(datos)
            geo = VDO_RE_GEOMETRIA.calcular_geometria_caja(
                pieza["caja"], mod, pieza["ejes"])
            refs = geo.get("refuerzos") or []
        except Exception as exc:
            _LOG.warning("coco_inspector_widgets: referencias de pieza no leidas: %s", exc)
            refs = []
        if not refs:
            self.header.set_panel(
                pieza["nombre"], pieza["largo"], pieza["ancho"],
                pieza["espesor"], cantos)
            return
        ref = refs[0]
        dim_key = {"x": "w", "y": "h", "z": "d"}
        largo = ref[dim_key[pieza["ejes"]["largo"]]]
        ancho = ref[dim_key[pieza["ejes"]["ancho"]]]
        espesor = ref[dim_key[pieza["ejes"]["espesor"]]]
        self.header.set_strip(
            pieza["nombre"], largo, ancho, espesor, cantos)
    def _actualizar_aviso_overflow(self):
        if self._resolved and self._resolved.overflow:
            self.lbl_aviso.setText(
                "⚠ Medidas fijas fuera de presupuesto. "
                "Reduce alguna medida o el número de vanos.")
        elif self._legacy_warnings:
            self.lbl_aviso.setText(self._legacy_warnings[0])
