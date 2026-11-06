# =====================================================================
# vdo_puerta_task.py
# Capa 4 - Task Panel PySide para Puertas y Cierres (L2).
# Construido con VDOTransactionMixin y el Manifiesto de UI VDO.
# =====================================================================

import FreeCAD as App

from freecad.vdo.cad.propiedades import add_common_props, asignar_propiedades
from freecad.vdo.cad.documento import recalcular_activo
from freecad.vdo.core import vdo_hardware_hub as H
from freecad.vdo.core.aperturas import ETIQUETAS, SISTEMA_POR_ETIQUETA
from freecad.vdo.core.vdo_facade_contract import (
    APERTURA_45_GRADOS,
    APERTURA_GOLA,
    APERTURA_PUSH_OPEN,
    APERTURA_TIRADOR,
    OPERACION_CANTO_45,
    OPERACION_CANTO_ESTANDAR,
    OPERACION_CANTO_GOLA,
    cantos_por_sistema_apertura,
    necesita_cantos_45,
    necesita_expulsor_magnetico,
)
from freecad.vdo.core.vdo_puerta_despiece import (
    ajuste_altura_apertura,
    bisagras_para_puerta,
    calcular_corrediza,
    descripcion_piston,
)
from freecad.vdo.ui.puerta_task_constantes import (
    SENTIDOS_BASCULANTE,
    SENTIDOS_BATIENTE,
    SENTIDOS_CORREDIZA,
)
from freecad.vdo.ui.puerta_task_construccion import PuertaTaskConstruccionMixin
from freecad.vdo.ui.vdo_task_base import VDOTransactionMixin, cerrar_dialogo

# ---------------------------------------------------------------------
# Task Panel
# ---------------------------------------------------------------------
class PuertaTaskPanel(PuertaTaskConstruccionMixin, VDOTransactionMixin):
    """Panel de tareas para configurar una puerta VDO."""

    def __init__(self, obj=None, on_accept=None, on_cancel=None,
                 auto_transaction=True):
        self.obj = obj
        self._vdo_aceptado = False
        self._init_vdo_task(
            on_accept=on_accept,
            on_cancel=on_cancel,
            auto_transaction=auto_transaction,
            transaction_name="Editar puerta VDO",
        )
        self.form = self._crear_widget()
        if obj:
            add_common_props(obj)
            self._cargar_valores(obj)
        self._actualizar_visibilidad()

    # -----------------------------------------------------------------
    # Carga / aplicación de valores
    # -----------------------------------------------------------------
    def _cargar_valores(self, obj):
        idx = self.combo_sistema.findText(obj.TipoSistema)
        if idx >= 0:
            self.combo_sistema.setCurrentIndex(idx)
        idx = self.combo_montaje.findText(obj.TipoMontaje)
        if idx >= 0:
            self.combo_montaje.setCurrentIndex(idx)
        idx = self.combo_sentido.findText(obj.SentidoApertura)
        if idx >= 0:
            self.combo_sentido.setCurrentIndex(idx)
        label = ETIQUETAS.get(obj.SistemaApertura, obj.SistemaApertura)
        idx = self.combo_apertura.findText(label)
        if idx >= 0:
            self.combo_apertura.setCurrentIndex(idx)
        idx = self.combo_sku.findText(obj.HardwareSKU)
        if idx >= 0:
            self.combo_sku.setCurrentIndex(idx)
        self.spin_ancho.setValue(float(obj.Ancho))
        self.spin_alto.setValue(float(obj.Alto))
        self.spin_espesor.setValue(int(obj.Espesor))
        self.spin_pos_x.setValue(float(obj.PosX))
        self.spin_pos_y.setValue(float(obj.PosY))
        self.spin_pos_z.setValue(float(obj.PosZ))
        anclaje = getattr(obj, "VDO_Anclaje", "inferior_izquierda_frente")
        for i in range(self.combo_anclaje.count()):
            if self.combo_anclaje.itemData(i) == anclaje:
                self.combo_anclaje.setCurrentIndex(i)
                break

    def _poblar_skus(self, familia):
        """Puebla el dropdown de SKUs desde la familia de Capa H."""
        self.combo_sku.blockSignals(True)
        self.combo_sku.clear()
        try:
            skus = sorted(H.query_family(familia).keys())
        except KeyError:
            skus = []
        if skus:
            self.combo_sku.addItems(skus)
        self.combo_sku.blockSignals(False)

    def _actualizar_visibilidad(self):
        sistema = self.combo_sistema.currentText()
        es_batiente = sistema == "Batiente Vertical"
        es_basculante = sistema == "Basculante Horizontal"
        es_corrediza = sistema == "Corrediza"

        self.grp_montaje.setVisible(es_batiente)
        self.grp_herraje.setVisible(es_batiente or es_corrediza)
        self.grp_piston.setVisible(es_basculante)

        # Sentido según familia
        self.combo_sentido.blockSignals(True)
        self.combo_sentido.clear()
        if es_batiente:
            self.combo_sentido.addItems(SENTIDOS_BATIENTE)
            self._poblar_skus("bisagra_cazoleta")
        elif es_basculante:
            self.combo_sentido.addItems(SENTIDOS_BASCULANTE)
            self.combo_sku.clear()
        else:
            self.combo_sentido.addItems(SENTIDOS_CORREDIZA)
            self._poblar_skus("sistema_corredizo")
        self.combo_sentido.blockSignals(False)

        self._actualizar_herraje_info()
        self._actualizar_piston()
        self._actualizar_header()

    def _on_cambio_sistema(self, idx):
        self._actualizar_visibilidad()
        self._actualizar_todo()

    def _actualizar_todo(self):
        self._actualizar_herraje_info()
        self._actualizar_piston()
        self._actualizar_header()

    def _actualizar_header(self):
        """Actualiza la cabecera universal de pieza con los datos actuales."""
        try:
            W = self.spin_ancho.value()
            H = self.spin_alto.value()
            t = self.spin_espesor.value()
            sistema = self.combo_sistema.currentText()
            apertura_label = self.combo_apertura.currentText()
            apertura = SISTEMA_POR_ETIQUETA.get(apertura_label, apertura_label)

            # Usar el sistema de apertura para calcular la altura efectiva
            # y obtener los cantos para el header.
            H_efectiva, _desc = ajuste_altura_apertura(apertura, H)
            cantos = cantos_por_sistema_apertura(apertura)

            identificador = f"Puerta_{sistema.split()[0]}"
            if sistema == "Batiente Vertical":
                identificador += f"_{self.combo_montaje.currentText()}"
            self.header.set_pieza(identificador, W, H_efectiva, t, cantos)
        except Exception:
            self.header.clear()

    def _actualizar_herraje_info(self):
        sku = self.combo_sku.currentText()
        if not sku:
            self.lbl_herraje_info.setText("")
            return
        try:
            hw = H.get_hardware(sku)
            tecnicos = hw["parametros_tecnicos"]
            lineas = [
                f"{hw['nombre']}",
                f"Proveedor: {hw['proveedor']}  ·  Precio: "
                f"{hw['precio_unitario']} {hw['moneda']}",
            ]
            if "tipo_montaje" in tecnicos:
                lineas.append(f"Montaje: {tecnicos['tipo_montaje']}")
            if "diametro_cazoleta" in tecnicos:
                lineas.append(
                    f"Cazoleta: Ø{tecnicos['diametro_cazoleta']} mm × "
                    f"{tecnicos['profundidad_cazoleta']} mm profundo")
            if "descuento_altura_hoja" in tecnicos:
                lineas.append(
                    f"Descuento alto hoja: {tecnicos['descuento_altura_hoja']} mm  ·  "
                    f"Traslape: {tecnicos['traslape_minimo']} mm")
            self.lbl_herraje_info.setText(" · ".join(lineas))
        except KeyError:
            self.lbl_herraje_info.setText(f"SKU {sku} no encontrado en el catálogo.")

    def _actualizar_piston(self):
        if self.combo_sistema.currentText() != "Basculante Horizontal":
            self.lbl_piston.setText("")
            return
        try:
            W = self.spin_ancho.value()
            H = self.spin_alto.value()
            _texto, comercial, F = descripcion_piston(W, H)
            self.lbl_piston.setText(
                f"💡 Recomendación: Pistón a Gas de {comercial}N  "
                f"(fuerza teórica: {F:.0f} N)")
        except Exception as e:
            self.lbl_piston.setText(f"Error calculando pistón: {e}")

    # -----------------------------------------------------------------
    # Aceptar / Cancelar
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
        try:
            self._vdo_begin()
            for spin in (self.spin_ancho, self.spin_alto,
                         self.spin_pos_x, self.spin_pos_y,
                         self.spin_pos_z):
                spin.interpretText()
            label = self.combo_apertura.currentText()
            valores = {
                "TipoSistema": self.combo_sistema.currentText(),
                "TipoMontaje": self.combo_montaje.currentText(),
                "SentidoApertura": self.combo_sentido.currentText(),
                "SistemaApertura": SISTEMA_POR_ETIQUETA.get(label, label),
                "HardwareSKU": self.combo_sku.currentText(),
                "Ancho": self.spin_ancho.value(),
                "Alto": self.spin_alto.value(),
                "Espesor": self.spin_espesor.value(),
                "PosX": self.spin_pos_x.value(),
                "PosY": self.spin_pos_y.value(),
                "PosZ": self.spin_pos_z.value(),
            }
            anclaje = self.combo_anclaje.currentData()
            if anclaje:
                valores["VDO_Anclaje"] = anclaje
            asignar_propiedades(self.obj, valores)

            # Fuerza de pistón (solo lectura)
            if self.obj.TipoSistema == "Basculante Horizontal":
                texto, _, _ = descripcion_piston(self.obj.Ancho, self.obj.Alto)
                asignar_propiedades(self.obj, {"FuerzaPistonRecomendada": texto})
            else:
                asignar_propiedades(self.obj, {"FuerzaPistonRecomendada": ""})

            recalcular_activo()
            self._vdo_commit()
            self._vdo_aceptado = True
            self._vdo_call_accept()
            return True
        except Exception as e:
            self._vdo_abort()
            App.Console.PrintError(f"[VDO Puerta] Error aceptando: {e}\n")
            return False

