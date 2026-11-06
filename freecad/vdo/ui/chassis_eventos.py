"""Manejadores de eventos del chasis. Parte de ui/chassis_widget.py (M7, D-45)."""


from freecad.vdo.ui.chassis_constantes import (
    _ARQUETIPOS,
    TIPOS_ENCUENTRO,
)


class ChassisEventosMixin:
    """Mixin de VDOChassisControllerWidget: manejadores de eventos. Sin cambios de codigo (D-45)."""

    # ------------------------------------------------------------------
    # Manejadores de Eventos
    # ------------------------------------------------------------------
    def _on_cara_toggled(self, cara):
        if self._cargando:
            return
        if cara not in self._caras:
            return

        nueva_activa = not self._caras[cara]["activa"]
        self._caras[cara]["activa"] = nueva_activa

        self._actualizar_botones_caras()
        self.canvas.update_state(self._caras, self._encuentros, self._base)
        self._emitir_cambio()

    def _on_esquina_clicked(self, esquina):
        if self._cargando:
            return
        actual = self._encuentros.get(esquina, "tapa_domina")
        idx = (TIPOS_ENCUENTRO.index(actual) + 1) % len(TIPOS_ENCUENTRO)
        nuevo_tipo = TIPOS_ENCUENTRO[idx]

        self._encuentros[esquina] = nuevo_tipo
        self._actualizar_botones_esquinas()
        self.canvas.update_state(self._caras, self._encuentros, self._base)
        self._emitir_cambio()

    def _on_fondo_changed(self):
        if self._cargando:
            return
        tipo = self.combo_fondo.currentData()
        self._caras["fondo"]["tipo"] = tipo
        self._caras["fondo"]["activa"] = tipo != "abierto"
        self.canvas.update_state(self._caras, self._encuentros, self._base)
        self._emitir_cambio()

    def _on_estrategia_clicked(self, estrategia):
        if self._cargando:
            return
        self._base["estrategia"] = estrategia

        for k, btn in self.btn_estrategias.items():
            btn.blockSignals(True)
            btn.setChecked(k == estrategia)
            btn.blockSignals(False)

        idx_stack = {"zocalo": 0, "suspendido": 1, "patas": 2}.get(estrategia, 0)
        self.stack_params.setCurrentIndex(idx_stack)

        self._actualizar_valores_base_dict()
        self.canvas.update_state(self._caras, self._encuentros, self._base)
        self._emitir_cambio()

    def _on_param_base_changed(self):
        if self._cargando:
            return
        self._actualizar_valores_base_dict()
        self.canvas.update_state(self._caras, self._encuentros, self._base)
        self._emitir_cambio()

    def _actualizar_valores_base_dict(self):
        estrategia = self._base.get("estrategia", "zocalo")
        if estrategia == "zocalo":
            self._base["altura"] = float(self.spin_altura_zocalo.value())
            self._base["separacion_frente"] = float(self.spin_offset_zocalo.value())
        elif estrategia == "suspendido":
            self._base["altura"] = float(self.spin_despegue_piso.value())
            self._base["separacion_frente"] = 0.0
        elif estrategia == "patas":
            self._base["altura"] = float(self.spin_altura_patas.value())
            self._base["separacion_frente"] = float(self.spin_offset_patas.value())

    def _on_arquetipo_clicked(self, nombre):
        if self._cargando:
            return

        cfg = _ARQUETIPOS.get(nombre)
        if cfg is None:
            return

        self.setChassisConfig(cfg)
        self._emitir_cambio()
