# =====================================================================
# zocalo_task.py
# Task Panel PySide del zócalo paramétrico VDO.
# =====================================================================

import FreeCAD as App

from freecad.vdo.cad.colocacion import aplicar_rotacion
from freecad.vdo.cad.documento import recalcular_activo
from freecad.vdo.cad.propiedades import add_common_props, asignar_propiedades
from freecad.vdo.cad.transaccion import foto_propiedades, restaurar_propiedades
from freecad.vdo.core import module_props
from freecad.vdo.core.module_props import ANCLAJE_DEFAULT
from freecad.vdo.core.zocalo_core import ZocaloError, calcular_geometria_zocalo
from freecad.vdo.datos.formularios import PROPIEDAD_ZOCALO, ZOCALO_GRUPOS
from freecad.vdo.qt_compat import QtGui, QtWidgets
from freecad.vdo.ui.coco_inspector_widgets import PanelHeaderWidget
from freecad.vdo.ui.form_builder import FormBuilder
from freecad.vdo.ui.task_base import VDOTransactionMixin, cerrar_dialogo

CANTOS_FRENTE = {
    "norte": "RIG", "sur": "RIG", "este": "RIG", "oeste": "RIG"}


class ZocaloTaskPanel(VDOTransactionMixin):
    """Panel de tareas para editar un zócalo."""

    def __init__(self, obj=None, on_accept=None, on_cancel=None,
                 auto_transaction=True):
        self.obj = obj
        self._vdo_aceptado = False
        self._init_vdo_task(
            on_accept=on_accept,
            on_cancel=on_cancel,
            auto_transaction=auto_transaction,
            transaction_name="Editar zócalo",
        )
        self.form = self._crear_widget()
        if obj:
            add_common_props(obj)
            self._cargar_valores(obj)
        self._actualizar_header()

    # -----------------------------------------------------------------
    def _crear_widget(self):
        widget = QtWidgets.QWidget()
        main_layout = QtWidgets.QVBoxLayout(widget)

        self.header = PanelHeaderWidget()
        main_layout.addWidget(self.header)

        self._form_builder = FormBuilder(widget)
        for titulo, filas in ZOCALO_GRUPOS:
            self._form_builder.construir_grupo(main_layout, titulo, filas)
        main_layout.addStretch()

        self._crear_botones(main_layout)
        self._enlazar_widgets()
        self._conectar_senales()

        return widget

    def _enlazar_widgets(self):
        """Nombres cortos de los widgets del formulario, usados por señales y carga."""
        fb = self._form_builder
        self.spin_ancho = fb.widget("ancho")
        self.spin_fondo = fb.widget("fondo")
        self.spin_alto = fb.widget("alto")
        self.spin_espesor = fb.widget("espesor")
        self.spin_frente = fb.widget("frente")
        self.spin_costados = fb.widget("costados")
        self.spin_trasera = fb.widget("trasera")
        self.chk_trasera = fb.widget("trasera_habilitada")
        self.spin_amarres = fb.widget("amarres")
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
            "Guarda los cambios del zócalo y recalcula la geometría.")
        btn_cancelar.setToolTip("Cierra sin aplicar los cambios.")
        main_layout.addWidget(botones)

    def _conectar_senales(self):
        for senal in (
                self.spin_ancho.valueChanged,
                self.spin_fondo.valueChanged,
                self.spin_alto.valueChanged,
                self.spin_espesor.valueChanged,
                self.spin_frente.valueChanged,
                self.spin_costados.valueChanged,
                self.spin_trasera.valueChanged):
            senal.connect(self._actualizar_header)
        self.chk_trasera.toggled.connect(self._on_trasera)
        self.chk_trasera.toggled.connect(self._actualizar_header)
        self.chk_trasera.setChecked(True)

    # -----------------------------------------------------------------
    def _on_trasera(self, activo):
        self.spin_trasera.setEnabled(bool(activo))

    def _actualizar_header(self, *_args):
        ancho = self.spin_ancho.value()
        alto = self.spin_alto.value()
        espesor = float(self.spin_espesor.value())
        self.header.set_panel(
            "Zocalo_Frente", ancho, alto, espesor, CANTOS_FRENTE)

    def _cargar_valores(self, obj):
        if hasattr(obj, "Ancho"):
            self.spin_ancho.setValue(float(obj.Ancho))
        if hasattr(obj, "Fondo"):
            self.spin_fondo.setValue(float(obj.Fondo))
        if hasattr(obj, "AltoZocalo"):
            self.spin_alto.setValue(float(obj.AltoZocalo))
        if hasattr(obj, "EspesorTablero"):
            self.spin_espesor.setValue(
                round(float(obj.EspesorTablero)))
        if hasattr(obj, "DistanciaFrente"):
            self.spin_frente.setValue(float(obj.DistanciaFrente))
        if hasattr(obj, "DistanciaCostados"):
            self.spin_costados.setValue(float(obj.DistanciaCostados))
        if hasattr(obj, "DistanciaTrasera"):
            self.spin_trasera.setValue(float(obj.DistanciaTrasera))
        if hasattr(obj, "TieneTrasera"):
            self.chk_trasera.setChecked(bool(obj.TieneTrasera))
        if hasattr(obj, "AmarresIntermedios"):
            self.spin_amarres.setValue(int(obj.AmarresIntermedios))
        self.spin_rotacion.setValue(
            float(getattr(obj, "VDO_RotacionZ", 0.0)))
        anclaje = getattr(obj, "VDO_Anclaje", ANCLAJE_DEFAULT)
        for i in range(self.combo_anclaje.count()):
            if self.combo_anclaje.itemData(i) == anclaje:
                self.combo_anclaje.setCurrentIndex(i)
                break

    # -----------------------------------------------------------------
    def _on_ok(self):
        if self.accept():
            cerrar_dialogo()

    def _on_cancel(self):
        self.reject()
        cerrar_dialogo()

    def accept(self):
        if not self.obj:
            return True
        return self._transaccion_zocalo()

    def _transaccion_zocalo(self):
        foto = foto_propiedades(self.obj)
        try:
            self._vdo_begin()
            self._escribir_zocalo()
            self._vdo_commit()
            self._vdo_aceptado = True
            self._vdo_call_accept()
            return True
        except ZocaloError as exc:
            self._vdo_abort()
            restaurar_propiedades(self.obj, foto)
            QtWidgets.QMessageBox.warning(
                self.form, "Zócalo", str(exc))
            return False
        except Exception as exc:
            self._vdo_abort()
            restaurar_propiedades(self.obj, foto)
            App.Console.PrintError(
                f"[VDO] Error aceptando el zócalo: {exc}\n")
            return False

    def _escribir_zocalo(self):
        fb = self._form_builder
        fb.interpretar_texto()
        v = fb.valores()
        calcular_geometria_zocalo(
            v["ancho"], v["fondo"], v["alto"], v["espesor"], v["frente"],
            v["costados"], v["trasera"], v["trasera_habilitada"], v["amarres"])
        valores = {PROPIEDAD_ZOCALO[c]: v[c] for c in PROPIEDAD_ZOCALO}
        if v["anclaje"]:
            valores["VDO_Anclaje"] = v["anclaje"]
        asignar_propiedades(self.obj, valores)
        aplicar_rotacion(self.obj, v["rotacion"])
        recalcular_activo()
