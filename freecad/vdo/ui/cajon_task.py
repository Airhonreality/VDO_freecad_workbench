# =====================================================================
# cajon_task.py
# Task Panel PySide para el cajón con corredera oculta (Trinidad v2).
# =====================================================================

import FreeCAD as App
import FreeCADGui as Gui

from freecad.vdo.cad.colocacion import aplicar_rotacion
from freecad.vdo.cad.documento import recalcular_activo
from freecad.vdo.cad.propiedades import add_common_props
from freecad.vdo.cad.transaccion import foto_propiedades, restaurar_propiedades
from freecad.vdo.core import hardware_hub, module_props
from freecad.vdo.core.cajon_correderas import (
    CAJA_METALICA,
    CORREDERA_OCULTA,
    CORREDERA_TELESCOPICA,
)
from freecad.vdo.core.facade_contract import (
    APERTURA_45_GRADOS,
    APERTURA_GOLA,
    APERTURA_PUSH_OPEN,
    APERTURA_TIRADOR,
    MONTAJE_EMBEBIDA,
    MONTAJE_PARCHE,
    MONTAJE_SEMIPARCHE,
    OPERACION_CANTO_45,
    OPERACION_CANTO_ESTANDAR,
    OPERACION_CANTO_GOLA,
    cantos_por_sistema_apertura,
    necesita_bisel_45,
    necesita_cantos_45,
    necesita_descuento_gola,
    necesita_expulsor_magnetico,
)
from freecad.vdo.core.facade_contract import (
    APERTURA_45_GRADOS as FA_45,
)
from freecad.vdo.core.facade_contract import (
    APERTURA_GOLA as FA_GOLA,
)
from freecad.vdo.core.facade_contract import (
    APERTURA_PUSH_OPEN as FA_PUSH,
)
from freecad.vdo.core.facade_contract import (
    APERTURA_TIRADOR as FA_TIRADOR,
)
from freecad.vdo.core.hardware_hub import (
    _FAMILIAS as _HW_FAMILIAS,
)
from freecad.vdo.core.hardware_hub import (
    get_family,
    resolve_drawer_slide,
)
from freecad.vdo.core.module_props import ANCLAJE_DEFAULT
from freecad.vdo.datos.valores import BLUM_TANDEM, MELAMINA_ESTANDAR
from freecad.vdo.qt_compat import QtCore, QtGui
from freecad.vdo.ui.cajon_task_construccion import CajonTaskConstruccionMixin
from freecad.vdo.ui.task_base import VDOTransactionMixin, cerrar_dialogo


# ---------------------------------------------------------------------
# CajonTaskPanel
# ---------------------------------------------------------------------
class CajonTaskPanel(CajonTaskConstruccionMixin, VDOTransactionMixin):
    """Panel de tareas para editar un cajón con corredera (Trinidad v2)."""

    def __init__(self, obj=None, on_accept=None, on_cancel=None,
                 auto_transaction=True):
        self._init_panel_vdo(obj, on_accept, on_cancel, auto_transaction,
                             "Editar cajón oculta", (add_common_props,))
        self._actualizar_header()
    # -----------------------------------------------------------------
    # Selectores contextuales
    # -----------------------------------------------------------------
    def _on_tipo_cambiado(self, idx):
        """Actualiza el combo SKU según el tipo de corredera."""
        self.combo_sku.clear()
        tipo_map = {
            0: CORREDERA_OCULTA,
            1: CORREDERA_TELESCOPICA,
            2: CAJA_METALICA,
        }
        tipo = tipo_map.get(idx, CORREDERA_OCULTA)
        familia = "corredera_oculta" if tipo == CORREDERA_OCULTA else (
            "corredera_telescopica" if tipo == CORREDERA_TELESCOPICA else None)

        try:
            skus = get_family(familia) if familia else {}
        except Exception as exc:
            App.Console.PrintWarning(f"[VDO] cajon_task: catalogo de SKU no leido, lista vacia: {exc}\n")
            skus = {}

        for sku in sorted(skus.keys()):
            datos = skus[sku]
            label = f"{sku} — {datos.get('nombre', '')}"
            self.combo_sku.addItem(label, sku)

        # Si no hay SKUs en el catálogo, añadir opciones manuales
        if self.combo_sku.count() == 0:
            if tipo == CORREDERA_OCULTA:
                self.combo_sku.addItem("BLUM-TANDEM — Blum Tandem", BLUM_TANDEM)
                self.combo_sku.addItem("GEN-OCULTA — Genérica", "generica")
                self.combo_sku.addItem("HAFELE-OCULTA — Hafele", "hafele")
                self.combo_sku.addItem("DUCASSE-OCULTA — Ducasse", "ducasse")
            elif tipo == CORREDERA_TELESCOPICA:
                self.combo_sku.addItem(
                    "GEN-TELESCOPICA-45KG — Telescópica 45kg",
                    "GEN-TELESCOPICA-45KG")

    def _on_apertura_cambiado(self, idx):
        """Actualiza el header cuando cambia el sistema de apertura."""
        self._actualizar_header()

    # -----------------------------------------------------------------
    # Carga de valores
    # -----------------------------------------------------------------
    def _cargar_valores(self, obj):  # noqa: C901 - complejidad 20 (max 12): funcion con ramas por caso; dividirla cambia el flujo sin golden por rama (D-81)
        """Carga las propiedades del objeto en los controles."""
        if hasattr(obj, "AnchoLibre"):
            self.spin_li.setValue(float(obj.AnchoLibre))
        if hasattr(obj, "ProfLibre"):
            self.spin_prof.setValue(float(obj.ProfLibre))
        if hasattr(obj, "AnchoModulo"):
            self.spin_ancho_mod.setValue(float(obj.AnchoModulo))
        if hasattr(obj, "AltoFrente"):
            self.spin_alto_frente.setValue(float(obj.AltoFrente))
        if hasattr(obj, "AltoCaja"):
            self.spin_alto_caja.setValue(float(obj.AltoCaja))
        if hasattr(obj, "GrosorCaja"):
            self.spin_g_caja.setValue(round(float(obj.GrosorCaja)))
        if hasattr(obj, "GrosorFondo"):
            self.spin_g_fondo.setValue(round(float(obj.GrosorFondo)))
        if hasattr(obj, "GrosorFachada"):
            self.spin_g_fachada.setValue(round(float(obj.GrosorFachada)))
        if hasattr(obj, "MarcaCorredera"):
            idx = self.combo_marca.findText(obj.MarcaCorredera)
            if idx >= 0:
                self.combo_marca.setCurrentIndex(idx)
        if hasattr(obj, "LongitudGuia"):
            self.spin_guia.setValue(float(obj.LongitudGuia))
        if hasattr(obj, "MontajeTrasera"):
            idx = self.combo_montaje.findText(obj.MontajeTrasera)
            if idx >= 0:
                self.combo_montaje.setCurrentIndex(idx)
        if hasattr(obj, "TipoCorredera"):
            tipo_map_rev = {
                CORREDERA_OCULTA: 0,
                CORREDERA_TELESCOPICA: 1,
                CAJA_METALICA: 2,
            }
            idx = tipo_map_rev.get(obj.TipoCorredera, 0)
            self.combo_tipo.setCurrentIndex(idx)
        if hasattr(obj, "SistemaApertura"):
            apertura_map_rev = {
                APERTURA_TIRADOR: 0,
                APERTURA_GOLA: 1,
                APERTURA_45_GRADOS: 2,
                APERTURA_PUSH_OPEN: 3,
            }
            idx = apertura_map_rev.get(obj.SistemaApertura, 0)
            self.combo_apertura.setCurrentIndex(idx)
        if hasattr(obj, "TipoMontaje"):
            idx = self.combo_montaje_fachada.findData(obj.TipoMontaje)
            if idx >= 0:
                self.combo_montaje_fachada.setCurrentIndex(idx)
        if hasattr(obj, "VDO_Herraje_Ref"):
            sku = obj.VDO_Herraje_Ref
            sku_idx = self.combo_sku.findData(sku)
            if sku_idx >= 0:
                self.combo_sku.setCurrentIndex(sku_idx)

        self._cargar_rotacion_anclaje(obj)

    def _cargar_rotacion_anclaje(self, obj):
        self.spin_rotacion.setValue(
            float(getattr(obj, "VDO_RotacionZ", 0.0)))
        anclaje = getattr(obj, "VDO_Anclaje", ANCLAJE_DEFAULT)
        for i in range(self.combo_anclaje.count()):
            if self.combo_anclaje.itemData(i) == anclaje:
                self.combo_anclaje.setCurrentIndex(i)
                break

    def _actualizar_header(self):
        """Actualiza el PanelHeaderWidget con las cotas calculadas."""
        try:
            from freecad.vdo.core.cajon_calculo import calcular_despiece
            config = {
                "ancho_libre": self.spin_li.value(),
                "prof_libre": self.spin_prof.value(),
                "ancho_modulo": self.spin_ancho_mod.value(),
                "alto_frente": self.spin_alto_frente.value(),
                "marca": self.combo_marca.currentText(),
                "alto_caja": self.spin_alto_caja.value(),
                "grosor_caja": self.spin_g_caja.value(),
                "grosor_fondo": self.spin_g_fondo.value(),
                "grosor_fachada": self.spin_g_fachada.value(),
                "longitud_guia": self.spin_guia.value(),
                "montaje_trasera": self.combo_montaje.currentText(),
                "tipo_corredera": (
                    CORREDERA_OCULTA if self.combo_tipo.currentIndex() == 0
                    else CORREDERA_TELESCOPICA if self.combo_tipo.currentIndex() == 1
                    else CAJA_METALICA),
                "sistema_apertura": (
                    APERTURA_TIRADOR if self.combo_apertura.currentIndex() == 0
                    else APERTURA_GOLA if self.combo_apertura.currentIndex() == 1
                    else APERTURA_45_GRADOS if self.combo_apertura.currentIndex() == 2
                    else APERTURA_PUSH_OPEN),
                "tipo_montaje_fachada": self.combo_montaje_fachada.currentData(),
                "penetracion_ranura": 10.0,
                "eje_ranura": 11.5,
                "holgura_lateral_fachada": 2.0,
                "holgura_superior_fachada": 2.0,
                "holgura_inferior_fachada": 2.0,
                "material_ref": MELAMINA_ESTANDAR,
            }
            d = calcular_despiece(config)
            self.header.actualizar(d.get("fachada", {}))
        except Exception:
            App.Console.PrintWarning(
                "[VDO] No se pudo actualizar el header del cajón")

    # -----------------------------------------------------------------
    # Aceptar / Cancelar
    # -----------------------------------------------------------------
    def accept(self):
        if not self.obj:
            return True
        foto = foto_propiedades(self.obj)
        try:
            self._transaccion_cajon()
            return True
        except Exception as e:
            self._vdo_abort()
            restaurar_propiedades(self.obj, foto)
            App.Console.PrintError(f"[VDO] Error aceptando cambios: {e}\n")
            return False

    def _transaccion_cajon(self):
        self._vdo_begin()
        self._escribir_cajon()
        self._vdo_commit()
        self._vdo_aceptado = True
        self._vdo_call_accept()

    def _escribir_cajon(self):
        self._form_builder.interpretar_texto()
        self.obj.AnchoLibre = self.spin_li.value()
        self.obj.ProfLibre = self.spin_prof.value()
        self.obj.AnchoModulo = self.spin_ancho_mod.value()
        self.obj.AltoFrente = self.spin_alto_frente.value()
        self.obj.AltoCaja = self.spin_alto_caja.value()
        self.obj.GrosorCaja = self.spin_g_caja.value()
        self.obj.GrosorFondo = self.spin_g_fondo.value()
        self.obj.GrosorFachada = self.spin_g_fachada.value()
        self.obj.MarcaCorredera = self.combo_marca.currentText()
        self.obj.LongitudGuia = self.spin_guia.value()
        self.obj.MontajeTrasera = self.combo_montaje.currentText()
        self.obj.TipoCorredera = (
            CORREDERA_OCULTA if self.combo_tipo.currentIndex() == 0
            else CORREDERA_TELESCOPICA if self.combo_tipo.currentIndex() == 1
            else CAJA_METALICA)
        self.obj.SistemaApertura = (
            APERTURA_TIRADOR if self.combo_apertura.currentIndex() == 0
            else APERTURA_GOLA if self.combo_apertura.currentIndex() == 1
            else APERTURA_45_GRADOS if self.combo_apertura.currentIndex() == 2
            else APERTURA_PUSH_OPEN)
        self.obj.TipoMontaje = self.combo_montaje_fachada.currentData()
        sku_data = self.combo_sku.currentData()
        if sku_data:
            self.obj.VDO_Herraje_Ref = str(sku_data)
        else:
            self.obj.VDO_Herraje_Ref = self.combo_marca.currentText()
        anclaje = self.combo_anclaje.currentData()
        if anclaje:
            self.obj.VDO_Anclaje = anclaje
        aplicar_rotacion(self.obj, self.spin_rotacion.value())
        recalcular_activo()

