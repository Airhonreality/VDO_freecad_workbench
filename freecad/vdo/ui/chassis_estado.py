"""Sincronizacion visual del chasis con su estado. Parte de ui/chassis_widget.py (M7, D-45)."""


from freecad.vdo.ui.chassis_constantes import (
    ENCUENTRO_LABELS,
    ENCUENTRO_TOOLTIPS,
)
from freecad.vdo.ui.tema_iconos import obtener_svg_icon


class ChassisEstadoMixin:
    """Mixin de VDOChassisControllerWidget: sincronizacion visual con el estado. Sin cambios de codigo (D-45)."""

    # ------------------------------------------------------------------
    # Sincronización Visual
    # ------------------------------------------------------------------
    def _actualizar_ui(self):
        self._actualizar_botones_caras()
        self._actualizar_botones_esquinas()
        self._actualizar_combo_fondo()
        self._actualizar_estrategia_base()
        self.canvas.update_state(self._caras, self._encuentros, self._base)

    def _actualizar_botones_caras(self):
        act_sup = self._caras["superior"]["activa"]
        self.btn_cara_sup.blockSignals(True)
        self.btn_cara_sup.setChecked(act_sup)
        self.btn_cara_sup.setText("━━ TAPA SUPERIOR · Activa ━━" if act_sup else "┄ TAPA SUPERIOR · Ausente ┄")
        self.btn_cara_sup.blockSignals(False)

        act_inf = self._caras["inferior"]["activa"]
        self.btn_cara_inf.blockSignals(True)
        self.btn_cara_inf.setChecked(act_inf)
        self.btn_cara_inf.setText("━━ BASE INFERIOR · Activa ━━" if act_inf else "┄ BASE INFERIOR · Ausente ┄")
        self.btn_cara_inf.blockSignals(False)

        act_izq = self._caras["izquierda"]["activa"]
        self.btn_cara_izq.blockSignals(True)
        self.btn_cara_izq.setChecked(act_izq)
        self.btn_cara_izq.setText("◀ Lat Izq" if act_izq else "◀ Izq Aus.")
        self.btn_cara_izq.blockSignals(False)

        act_der = self._caras["derecha"]["activa"]
        self.btn_cara_der.blockSignals(True)
        self.btn_cara_der.setChecked(act_der)
        self.btn_cara_der.setText("Lat Der ▶" if act_der else "Der Aus. ▶")
        self.btn_cara_der.blockSignals(False)

    def _actualizar_botones_esquinas(self):
        for e, btn in self.btn_esquina.items():
            tipo = self._encuentros.get(e, "tapa_domina")
            btn.setIcon(obtener_svg_icon(tipo, 22))
            btn.setToolTip(f"<b>{ENCUENTRO_LABELS.get(tipo, tipo)}</b><br>{ENCUENTRO_TOOLTIPS.get(tipo, '')}")

    def _actualizar_combo_fondo(self):
        tipo = self._caras["fondo"].get("tipo", "ranurado_5mm")
        idx = self.combo_fondo.findData(tipo)
        if idx >= 0:
            self.combo_fondo.blockSignals(True)
            self.combo_fondo.setCurrentIndex(idx)
            self.combo_fondo.blockSignals(False)

    def _actualizar_estrategia_base(self):
        estrategia = self._base.get("estrategia", "zocalo")
        for k, btn in self.btn_estrategias.items():
            btn.blockSignals(True)
            btn.setChecked(k == estrategia)
            btn.blockSignals(False)

        idx_stack = {"zocalo": 0, "suspendido": 1, "patas": 2}.get(estrategia, 0)
        self.stack_params.setCurrentIndex(idx_stack)

        self.spin_altura_zocalo.blockSignals(True)
        self.spin_offset_zocalo.blockSignals(True)
        self.spin_despegue_piso.blockSignals(True)
        self.spin_altura_patas.blockSignals(True)
        self.spin_offset_patas.blockSignals(True)

        if estrategia == "zocalo":
            self.spin_altura_zocalo.setValue(float(self._base.get("altura", 100.0)))
            self.spin_offset_zocalo.setValue(float(self._base.get("separacion_frente", 50.0)))
        elif estrategia == "suspendido":
            self.spin_despegue_piso.setValue(float(self._base.get("altura", 300.0)))
        elif estrategia == "patas":
            self.spin_altura_patas.setValue(float(self._base.get("altura", 100.0)))
            self.spin_offset_patas.setValue(float(self._base.get("separacion_frente", 50.0)))

        self.spin_altura_zocalo.blockSignals(False)
        self.spin_offset_zocalo.blockSignals(False)
        self.spin_despegue_piso.blockSignals(False)
        self.spin_altura_patas.blockSignals(False)
        self.spin_offset_patas.blockSignals(False)
