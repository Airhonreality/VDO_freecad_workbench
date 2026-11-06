"""Reengroses del COCO: panel contextual y API de datos (cargar y volcar el editor).

Extraido de vdo_widgets_coco.py (M7, D-40). Sin cambios de codigo."""

import json
import logging

from freecad.vdo.core import (
    reengrose_modelo as VDO_RE_MODELO,
)
from freecad.vdo.core import (
    reengrose_modificador as VDO_RE_MODIFICADOR,
)
from freecad.vdo.core.layout_matriz import Layout
from freecad.vdo.core.layout_modelo import cavidad_interior
from freecad.vdo.qt_compat import QtWidgets

_LOG = logging.getLogger(__name__)


class ReengroseDivisionesMixin:
    """Mixin de DivisionesEditor (ver coco_construccion_widgets.py)."""

    def _crear_grupo_reengrose(self):
        from freecad.vdo.ui.box_controller import VDOBoxControllerWidget
        grupo = QtWidgets.QGroupBox("Reengrose / Refuerzo")
        grid = QtWidgets.QGridLayout(grupo)
        grid.setContentsMargins(6, 6, 6, 6)
        grid.setVerticalSpacing(4)
        grid.setHorizontalSpacing(8)

        self._crear_combo_elemento(grid)

        # Controlador Espacial Figma Box Model (Cuadrado Paramétrico)
        self.box_controller = VDOBoxControllerWidget()
        self.re_editor = self.box_controller
        grid.addWidget(self.box_controller, 1, 0, 1, 4)

        self._crear_combos_fabricacion(grid)

        self._crear_aliases_reengrose()

        self._crear_controles_legacy()

        return grupo

    def _crear_combo_elemento(self, grid):
        grid.addWidget(QtWidgets.QLabel("Elemento:"), 0, 0)
        self.combo_elemento_reengrose = QtWidgets.QComboBox()
        self.combo_elemento_reengrose.setToolTip(
            "Elegí el lateral, la base, el techo o una división para "
            "configurar su refuerzo. Los vanos muestran la luz neta; el "
            "refuerzo pertenece a la pieza que lo lleva.")
        grid.addWidget(self.combo_elemento_reengrose, 0, 1, 1, 3)

    def _crear_combos_fabricacion(self, grid):
        # Parámetros globales de fabricación debajo del widget
        grid.addWidget(QtWidgets.QLabel("Fabricación:"), 2, 0)
        self.combo_fabricacion = QtWidgets.QComboBox()
        self.combo_fabricacion.addItem("Pacha (bloque unificado)", "pacha")
        self.combo_fabricacion.addItem("Independiente", "independiente")
        self.combo_fabricacion.setToolTip("Fabricación de las tiras y su canteado.")
        grid.addWidget(self.combo_fabricacion, 2, 1, 1, 3)

        grid.addWidget(QtWidgets.QLabel("Choque núcleo:"), 3, 0)
        self.combo_choque = QtWidgets.QComboBox()
        self.combo_choque.addItem("Retroceso (corte recto)", "retroceso")
        self.combo_choque.addItem("Mocheo / rebaje", "mocheo")
        self.combo_choque.addItem("Interrumpir tira", "interrumpir_tira")
        self.combo_choque.setToolTip("Comportamiento de la tira al chocar con el núcleo.")
        grid.addWidget(self.combo_choque, 3, 1, 1, 3)

        grid.addWidget(QtWidgets.QLabel("Cara de pegado:"), 4, 0)
        self.combo_cara = QtWidgets.QComboBox()
        self.combo_cara.addItem("Cara A (+)", "cara_a")
        self.combo_cara.addItem("Cara B (−)", "cara_b")
        self.combo_cara.addItem("Ambas caras", "ambos")
        self.combo_cara.setToolTip("Cara del tablero donde se pegan las tiras.")
        grid.addWidget(self.combo_cara, 4, 1, 1, 3)

    def _crear_aliases_reengrose(self):
        # Aliases y compatibilidad backward
        self.chk_reengrose = self.re_editor.chk_activo
        self.spin_re_ancho = self.re_editor.spin_ancho
        self.spin_re_espesor = self.re_editor.spin_espesor
        self.combo_re_cara = self.combo_cara
        self.combo_re_modo = self.combo_fabricacion
        self.combo_re_politica = self.combo_choque
        self.combo_re_prioridad = self.re_editor.combo_esquinas
        self.combo_re_esquinas = self.re_editor.combo_esquinas
        self.combo_re_choque = self.combo_choque
        self.spin_re_offset = self.re_editor.spin_offset
        self.chk_re_uniforme = self.re_editor.chk_uniforme
        self.btn_all = self.re_editor.btn_all
        self.btn_borde = self.re_editor.btn_borde
        self.btn_borde_frente = self.re_editor.btn_borde["frente"]
        self.btn_borde_fondo = self.re_editor.btn_borde["fondo"]
        self.btn_borde_izquierda = self.re_editor.btn_borde["izquierda"]
        self.btn_borde_derecha = self.re_editor.btn_borde["derecha"]
        self.spin_re_ancho_borde = self.re_editor.spin_ancho_borde
        self.spin_re_offset_borde = self.re_editor.spin_offset_borde
        self.lbl_reengrose = self.re_editor.lbl_resumen
        self.chk_sync_esquinas = self.re_editor.chk_sync_esquinas
        self.combo_esquina = self.re_editor.combo_esquina
        self.preview_reengrose = None

        self.re_editor.combo_choque = self.combo_choque
        self.re_editor.combo_cara = self.combo_cara
        self.re_editor.combo_fabricacion = self.combo_fabricacion
        self.re_editor._set_combo_data = self._set_combo_data

    def _crear_controles_legacy(self):
        # Controles legacy ocultos para compatibilidad de API
        self.combo_re_orientacion = QtWidgets.QComboBox()
        self.combo_re_orientacion.addItem("Paralela", "paralela")
        self.combo_re_orientacion.addItem("Transversal", "transversal")
        self.combo_re_alineacion = QtWidgets.QComboBox()
        self.combo_re_alineacion.addItem("Frente", "frente")
        self.combo_re_alineacion.addItem("Centrado", "centrado")
        self.combo_re_alineacion.addItem("Fondo", "fondo")
        self.combo_re_alcance = QtWidgets.QComboBox()
        self.combo_re_alcance.addItem("Parcial", "parcial")
        self.combo_re_alcance.addItem("Total", "total")
    @staticmethod
    def _spin_medida():
        spin = QtWidgets.QDoubleSpinBox()
        spin.setRange(0.0, 100000.0)
        spin.setDecimals(1)
        spin.setSuffix(" mm")
        return spin
    @staticmethod
    def _fila_check_spin(check, spin):
        widget = QtWidgets.QWidget()
        fila = QtWidgets.QHBoxLayout(widget)
        fila.setContentsMargins(0, 0, 0, 0)
        fila.addWidget(check)
        fila.addWidget(spin, 1)
        return widget

    # -----------------------------------------------------------------
    # API para el panel COCO
    # -----------------------------------------------------------------
    def set_dimensions(self, alto, ancho, espesor, fondo=None, tapa=None,
                       base=None, tiene_fondo=None):
        self.outer_w = float(ancho)
        self.outer_h = float(alto)
        self.thickness = float(espesor)
        if fondo is not None:
            self._fondo = float(fondo)
        if tapa is not None:
            self._tapa = str(tapa)
        if base is not None:
            self._base = str(base)
        if tiene_fondo is not None:
            self._tiene_fondo = bool(tiene_fondo)
        cavidad = cavidad_interior(alto, ancho, espesor)
        self.inner_w = cavidad["ancho"]
        self.inner_h = cavidad["alto"]
        self._rebuild()
    def cargar_desde_objeto(self, obj):
        texto = getattr(obj, "VDO_Divisiones", "") or ""
        self._legacy_warnings = []
        self.layout = Layout.loads(texto)
        self.reengroses = VDO_RE_MODIFICADOR.leer_reengroses(obj)
        self._obj = obj
        self._fondo = float(getattr(obj, "FondoModulo", self._fondo))
        self._tapa = str(getattr(obj, "Tapa", self._tapa))
        self._base = str(getattr(obj, "Base", self._base))
        self._tiene_fondo = bool(
            getattr(obj, "TieneFondo", self._tiene_fondo))
        self._selected_reengrose_key = None
        self._selected_key = ("cell",
                              self.layout.columns[0].id,
                              self.layout.rows[0].id)
        # Cargar contenido de vanos persistido
        texto_contenido = getattr(obj, "VDO_Contenido_JSON", "") or "{}"
        try:
            self._contenido_por_celda = json.loads(texto_contenido)
            # Convertir claves de string "i,j" a tuplas
            self._contenido_por_celda = {
                tuple(map(int, k.split(","))): v
                for k, v in self._contenido_por_celda.items()
            }
        except (ValueError, TypeError, AttributeError) as exc:
            _LOG.warning("coco_reengrose_widgets: contenido por celda no leido: %s", exc)
            self._contenido_por_celda = {}
        self._rebuild()
    def dumps(self):
        return self.layout.dumps()
    def dumps_reengroses(self):
        return json.dumps(self.reengroses, ensure_ascii=False)
    def dumps_contenido(self):
        serializable = {
            f"{i},{j}": v for (i, j), v in self._contenido_por_celda.items()
        }
        return json.dumps(serializable, ensure_ascii=False)
    def resumen(self):
        if self._resolved is None:
            return "Sin dimensiones."
        lineas = [self._resolved.summary()]
        if self._legacy_warnings:
            lineas.extend("⚠ " + w for w in self._legacy_warnings)
        return "\n".join(lineas)
    def tiene_overflow(self):
        return bool(self._resolved and self._resolved.overflow)

    # -----------------------------------------------------------------
    # Auxiliares
    # -----------------------------------------------------------------
    # -----------------------------------------------------------------
    # Reengrose contextual
    # -----------------------------------------------------------------
    def _elementos_reengrose(self):
        return [
            (pieza["key"], pieza["nombre"])
            for pieza in self._piezas_fisicas()
        ]
    def _poblar_elementos_reengrose(self):
        if self._resolved is None:
            return
        items = self._elementos_reengrose()
        claves = [clave for clave, _ in items]
        seleccion = self._selected_reengrose_key
        if seleccion not in claves:
            preferida = "division_x:x2"
            seleccion = (
                preferida if preferida in claves else claves[0])

        previo = self._building
        self._building = True
        self.combo_elemento_reengrose.blockSignals(True)
        self.combo_elemento_reengrose.clear()
        for clave, etiqueta in items:
            self.combo_elemento_reengrose.addItem(etiqueta, clave)
        idx = self.combo_elemento_reengrose.findData(seleccion)
        if idx >= 0:
            self.combo_elemento_reengrose.setCurrentIndex(idx)
        self.combo_elemento_reengrose.blockSignals(False)
        self._selected_reengrose_key = seleccion
        if not self._skip_cargar_reengrose:
            self._cargar_reengrose_controls(seleccion)
        self._building = previo
    def _cargar_reengrose_controls(self, clave):
        datos = self.reengroses.get(clave)
        try:
            mod = (
                VDO_RE_MODIFICADOR.ReengroseModifier(datos) if datos
                else VDO_RE_MODIFICADOR.ReengroseModifier())
        except VDO_RE_MODELO.ReengroseError as exc:
            _LOG.warning("coco_reengrose_widgets: reengrose invalido, usa modificador vacio: %s", exc)
            mod = VDO_RE_MODIFICADOR.ReengroseModifier()
        self.re_editor.cargar(mod)
        self._set_combo_data(
            self.combo_fabricacion, getattr(mod, "fabricacion", "pacha"))
        choque = getattr(mod, "choque_nucleo", "retroceso")
        if not datos and str(clave) in ("techo", "base"):
            choque = "mocheo"
        self._set_combo_data(self.combo_choque, choque)
        self._set_combo_data(
            self.combo_cara, getattr(mod, "cara", "cara_a"))
        self.re_editor._actualizar_resumen()
        self._actualizar_estado_reengrose()

    @staticmethod
    def _etiquetas_caras(clave):
        if clave == "lateral_izquierdo":
            return ("Interna (+)", "Externa (−)")
        if clave == "lateral_derecho":
            return ("Externa (+)", "Interna (−)")
        if clave == "base":
            return ("Superior / interna (+)", "Inferior / externa (−)")
        if clave == "techo":
            return ("Superior / externa (+)", "Inferior / interna (−)")
        if clave == "fondo":
            return ("Trasera (+)", "Delantera (−)")
        if str(clave).startswith("division_x:"):
            return ("Lado derecho (+)", "Lado izquierdo (−)")
        return ("Superior (+)", "Inferior (−)")

    @staticmethod
    def _set_combo_data(combo, valor):
        idx = combo.findData(valor)
        if idx >= 0:
            combo.setCurrentIndex(idx)

    def _leer_reengrose_ui(self):
        datos = self.re_editor.getConfig()
        datos["fabricacion"] = self.combo_fabricacion.currentData()
        datos["choque_nucleo"] = self.combo_choque.currentData()
        datos["cara"] = self.combo_cara.currentData()
        datos["activo"] = True
        return VDO_RE_MODIFICADOR.normalizar_modificador(datos)

    def _actualizar_estado_reengrose(self):
        activo = self.chk_reengrose.isChecked()
        self.re_editor._actualizar_estado_habilitacion()
        self.combo_fabricacion.setEnabled(activo)
        self.combo_choque.setEnabled(activo)
        self.combo_cara.setEnabled(activo)
    def _on_reengrose_element_changed(self, *args):
        if self._building:
            return
        clave = self.combo_elemento_reengrose.currentData()
        if not clave:
            return
        self._selected_reengrose_key = clave
        self._cargar_reengrose_controls(clave)
    def _on_reengrose_changed(self, *args):
        if self._building or self._en_reengrose:
            return
        clave = self.combo_elemento_reengrose.currentData()
        if not clave:
            return
        self._en_reengrose = True
        self._skip_cargar_reengrose = True
        try:
            if not self.chk_reengrose.isChecked():
                self.reengroses.pop(clave, None)
            else:
                self.reengroses[clave] = self._leer_reengrose_ui()
            self._selected_reengrose_key = clave
            self._rebuild_y_avisar()
        finally:
            self._skip_cargar_reengrose = False
            self._en_reengrose = False
