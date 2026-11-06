# =====================================================================
# vdo_panel_task.py
# Panel de configuración del módulo Panel VDO (orientación, cantos y pose).
# Los campos se describen en datos/formularios.py (M6, MN-08, D-71).
# =====================================================================

import FreeCAD as App

from freecad.vdo.cad.colocacion import aplicar_rotacion
from freecad.vdo.cad.propiedades import add_common_props
from freecad.vdo.cad.documento import recalcular_activo
from freecad.vdo.core import vdo_reengrose_geometria as VDO_RE_GEOMETRIA
from freecad.vdo.core import vdo_reengrose_modelo as VDO_RE_MODELO
from freecad.vdo.core import vdo_reengrose_modificador as VDO_RE_MODIFICADOR
from freecad.vdo.core.vdo_module_props import ANCLAJE_DEFAULT
from freecad.vdo.cad.panel import add_reengrose_props
from freecad.vdo.datos.formularios import PANEL_GRUPOS_ANTES, PANEL_GRUPOS_DESPUES
from freecad.vdo.datos.valores import MELAMINA_ESTANDAR
from freecad.vdo.qt_compat import QtWidgets
from freecad.vdo.ui.vdo_form_builder import FormBuilder
from freecad.vdo.ui.vdo_task_base import VDOTransactionMixin, cerrar_dialogo

DIRECCIONES_CANTO = ("Norte", "Sur", "Este", "Oeste")


class PanelTaskPanel(VDOTransactionMixin):
    """Configuración de un panel VDO (orientación, cantos y pose)."""

    def __init__(self, obj=None, on_accept=None, on_cancel=None,
                 auto_transaction=True):
        self.obj = obj
        self._vdo_aceptado = False
        self._init_vdo_task(
            on_accept=on_accept,
            on_cancel=on_cancel,
            auto_transaction=auto_transaction,
            transaction_name="Editar panel VDO",
        )
        self.form = self._crear_widget()
        if obj:
            add_reengrose_props(obj)
            add_common_props(obj)
            self._cargar_valores(obj)

    def _crear_widget(self):
        widget = QtWidgets.QWidget()
        main_layout = QtWidgets.QVBoxLayout(widget)

        self._form_builder = FormBuilder(widget)
        for titulo, filas in PANEL_GRUPOS_ANTES:
            self._form_builder.construir_grupo(main_layout, titulo, filas)

        main_layout.addWidget(self._crear_grupo_reengrose())

        for titulo, filas in PANEL_GRUPOS_DESPUES:
            self._form_builder.construir_grupo(main_layout, titulo, filas)
        main_layout.addStretch()

        self._crear_botones(main_layout)
        self._enlazar_widgets()
        self.re_editor.changed.connect(self._on_reengrose_modo_changed)
        return widget

    def _enlazar_widgets(self):
        """Nombres cortos de los widgets del formulario, usados por la carga y la escritura."""
        fb = self._form_builder
        self.edit_etiqueta = fb.widget("etiqueta")
        self.combo_orientacion = fb.widget("orientacion")
        self.edit_material = fb.widget("material")
        self.combo_modo = fb.widget("modo")
        self.spin_largo = fb.widget("largo")
        self.spin_ancho = fb.widget("ancho")
        self.spin_espesor = fb.widget("espesor")
        self.combo_cantos = {
            d: fb.widget(f"canto_{d.lower()}") for d in DIRECCIONES_CANTO}
        self.spin_rotacion = fb.widget("rotacion")
        self.combo_anclaje = fb.widget("anclaje")

    def _crear_botones(self, main_layout):
        botones = QtWidgets.QDialogButtonBox()
        btn_ok = botones.addButton(
            "Crear y colocar" if not self.auto_transaction else "Aplicar",
            QtWidgets.QDialogButtonBox.AcceptRole)
        btn_cancelar = botones.addButton(
            "Cancelar", QtWidgets.QDialogButtonBox.RejectRole)
        botones.accepted.connect(self._on_ok)
        botones.rejected.connect(self._on_cancel)
        btn_ok.setToolTip(
            "Guarda los cambios en el panel y recalcula la geometría.")
        btn_cancelar.setToolTip("Cierra sin aplicar los cambios.")
        main_layout.addWidget(botones)

    def _crear_grupo_reengrose(self):
        from freecad.vdo.ui.vdo_reengrose_ui import ReengroseBorderEditor
        self.re_editor = ReengroseBorderEditor()
        self.chk_reengrose = self.re_editor.chk_activo
        self.spin_re_ancho = self.re_editor.spin_ancho
        self.spin_re_espesor = self.re_editor.spin_espesor
        self.combo_re_cara = self.re_editor.combo_cara
        self.combo_re_modo = self.re_editor.combo_fabricacion
        self.combo_re_politica = self.re_editor.combo_choque
        self.combo_re_prioridad = self.re_editor.combo_esquinas
        self.combo_re_esquinas = self.re_editor.combo_esquinas
        self.combo_re_choque = self.re_editor.combo_choque
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
        self.lbl_re_resumen = self.re_editor.lbl_resumen
        self.chk_sync_esquinas = self.re_editor.chk_sync_esquinas
        self.combo_esquina = self.re_editor.combo_esquina
        self.preview_reengrose = self.re_editor.preview

        # Controles legacy ocultos para compatibilidad de API.
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
        return self.re_editor

    def _tiene_expresiones(self, obj):
        try:
            return bool(dict(obj.ExpressionEngine or []).get("Largo"))
        except Exception:
            return True

    def _cargar_valores(self, obj):
        self.edit_etiqueta.setText(getattr(obj, "VDO_Etiqueta", ""))
        self.edit_material.setText(
            getattr(obj, "VDO_Material_Ref", MELAMINA_ESTANDAR))
        idx = self.combo_orientacion.findText(
            getattr(obj, "VDO_Orientacion", "horizontal"))
        if idx >= 0:
            self.combo_orientacion.setCurrentIndex(idx)

        for direccion in DIRECCIONES_CANTO:
            valor = getattr(obj, f"VDO_Canto_{direccion}", "FX")
            idx = self.combo_cantos[direccion].findText(valor)
            if idx >= 0:
                self.combo_cantos[direccion].setCurrentIndex(idx)

        self.spin_rotacion.setValue(
            float(getattr(obj, "VDO_RotacionZ", 0.0)))
        anclaje = getattr(obj, "VDO_Anclaje", ANCLAJE_DEFAULT)
        for i in range(self.combo_anclaje.count()):
            if self.combo_anclaje.itemData(i) == anclaje:
                self.combo_anclaje.setCurrentIndex(i)
                break

        usar_expr = self._tiene_expresiones(obj)
        self.combo_modo.setCurrentIndex(1 if usar_expr else 0)
        if usar_expr:
            expr_engine = dict(obj.ExpressionEngine or [])
            self.spin_largo.setText(expr_engine.get("Largo", ""))
            self.spin_ancho.setText(expr_engine.get("Ancho", ""))
            self.spin_espesor.setText(expr_engine.get("Espesor", ""))
        else:
            self.spin_largo.setValue(float(getattr(obj, "Largo", 0.0)))
            self.spin_ancho.setValue(float(getattr(obj, "Ancho", 0.0)))
            self.spin_espesor.setValue(float(getattr(obj, "Espesor", 0.0)))

        self._cargar_reengrose(obj)

    def _leer_reengrose(self):
        return self.re_editor.leer_modificador()

    def _actualizar_resumen_reengrose(self):
        self.re_editor._actualizar_resumen()

    def _on_reengrose_toggled(self, activo):
        self._on_reengrose_modo_changed()

    def _on_reengrose_modo_changed(self, *args):
        self.re_editor._actualizar_estado()

    def _cargar_reengrose(self, obj):
        mod = VDO_RE_MODIFICADOR.desde_objeto(obj)
        self.re_editor.cargar(mod)
        self.re_editor._actualizar_estado()

    def _on_ok(self):
        if self.accept():
            cerrar_dialogo()

    def _on_cancel(self):
        self.reject()
        cerrar_dialogo()

    def _aplicar_datos_basicos(self):
        self._form_builder.interpretar_texto()
        for spin in (self.spin_re_ancho, self.spin_re_espesor):
            spin.interpretText()

        self.obj.VDO_Etiqueta = self.edit_etiqueta.text().strip()
        self.obj.VDO_Orientacion = self.combo_orientacion.currentText()
        self.obj.VDO_Material_Ref = self.edit_material.text().strip()

        for direccion in DIRECCIONES_CANTO:
            self.obj.__setattr__(
                f"VDO_Canto_{direccion}",
                self.combo_cantos[direccion].currentText())

    def _aplicar_medidas(self):
        if self.combo_modo.currentIndex() == 1:
            for prop, spin in (("Largo", self.spin_largo),
                               ("Ancho", self.spin_ancho),
                               ("Espesor", self.spin_espesor)):
                self.obj.setExpression(prop, spin.value())
        else:
            for prop, spin in (("Largo", self.spin_largo),
                               ("Ancho", self.spin_ancho),
                               ("Espesor", self.spin_espesor)):
                try:
                    self.obj.clearExpression(prop)
                except Exception:
                    App.Console.PrintWarning(
                        f"[VDO] No se pudo limpiar expresión de {prop}")
                setattr(self.obj, prop, spin.value_float())

    def _aplicar_anclaje_rotacion(self):
        anclaje = self.combo_anclaje.currentData()
        if anclaje:
            self.obj.VDO_Anclaje = anclaje
        aplicar_rotacion(self.obj, self.spin_rotacion.value())

    def _calcular_reengrose(self, mod):
        """Calcula la geometría del reengrose. False si la configuración no es válida."""
        try:
            VDO_RE_GEOMETRIA.calcular_geometria_reengrose({
                "nombre": self.obj.Label,
                "largo": self.spin_largo.value_float(),
                "ancho": self.spin_ancho.value_float(),
                "espesor": self.spin_espesor.value_float(),
            }, mod)
            return True
        except VDO_RE_MODELO.ReengroseError as exc:
            QtWidgets.QMessageBox.warning(
                self.form, "Reengrose / Pacha", str(exc))
            return False

    def _escribir_panel(self):
        self._aplicar_datos_basicos()
        self._aplicar_medidas()
        mod_reengrose = self._leer_reengrose()
        if mod_reengrose.activo and not self._calcular_reengrose(mod_reengrose):
            return False
        VDO_RE_MODIFICADOR.aplicar_a_objeto(self.obj, mod_reengrose)
        self._aplicar_anclaje_rotacion()
        recalcular_activo()
        return True

    def _transaccion_panel(self):
        try:
            self._vdo_begin()
            if not self._escribir_panel():
                self._vdo_abort()
                return False
            self._vdo_commit()
            self._vdo_aceptado = True
            self._vdo_call_accept()
            return True
        except Exception as exc:
            self._vdo_abort()
            App.Console.PrintError(
                f"[VDO] Error aceptando panel: {exc}\n")
            import traceback
            App.Console.PrintError(traceback.format_exc())
            return False

    def accept(self):
        if not self.obj:
            return True
        return self._transaccion_panel()
