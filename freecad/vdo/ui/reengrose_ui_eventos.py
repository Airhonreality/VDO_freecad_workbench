"""Manejadores de eventos del editor de reengrose y sincronizacion de bordes/esquinas."""

from freecad.vdo.core import reengrose_modelo as VDO_RE_MODELO
from freecad.vdo.ui.qt import seleccionar_por_dato


class ReengroseEventosMixin:
    """Manejadores de eventos del editor de reengrose y sincronizacion de bordes/esquinas."""

    def _emitir(self, *args):
        if self._cargando:
            return
        self._actualizar_preview()
        self._actualizar_resumen()
        self.changed.emit()

    def _bordes_activos(self):
        return [b for b in VDO_RE_MODELO.BORDES_2D
                if self.btn_borde[b].isChecked()]

    def _esquinas_actuales(self):
        return {
            esquina: combo.currentData()
            for esquina, combo in self.combo_esquina.items()
        }

    def _on_activo(self, activo):
        if self._cargando:
            return
        if activo and not self._bordes_activos():
            self._cargando = True
            self.btn_borde["frente"].setChecked(True)
            self._cargando = False
        self._actualizar_estado()
        self._emitir()

    def _on_borde(self, borde, estado):
        if self._cargando:
            return
        self._actualizar_estado_all()
        self._emitir()

    def _actualizar_estado_all(self):
        """Sincroniza el botón [All] con el estado de los 4 bordes."""
        if self._cargando:
            return
        todos = all(self.btn_borde[b].isChecked()
                    for b in VDO_RE_MODELO.BORDES_2D)
        self.btn_all.blockSignals(True)
        self.btn_all.setChecked(todos)
        self.btn_all.blockSignals(False)

    def _on_all(self):
        objetivo = len(self._bordes_activos()) < len(VDO_RE_MODELO.BORDES_2D)
        self._cargando = True
        self.btn_all.blockSignals(True)
        self.btn_all.setChecked(objetivo)
        self.btn_all.blockSignals(False)
        for btn in self.btn_borde.values():
            btn.blockSignals(True)
            btn.setChecked(objetivo)
            btn.blockSignals(False)
        self._cargando = False
        self._emitir()

    def _on_uniforme(self, uniforme):
        if self._cargando:
            return
        if uniforme:
            self._replicar_uniforme()
        self._actualizar_estado()
        self._emitir()

    def _on_uniforme_spin(self, *args):
        if self._cargando:
            return
        if self.chk_uniforme.isChecked():
            self._replicar_uniforme()
        self._emitir()

    def _replicar_uniforme(self):
        """Copia ancho y offset globales a todos los bordes sin disparar los manejadores de cada spin."""
        self._cargando = True
        for borde in VDO_RE_MODELO.BORDES_2D:
            self.spin_ancho_borde[borde].setValue(
                self.spin_ancho.value())
            self.spin_offset_borde[borde].setValue(
                self.spin_offset.value())
        self._cargando = False

    def _on_custom_spin(self, *args):
        if self._cargando or self.chk_uniforme.isChecked():
            return
        self._emitir()

    def _on_esquina_changed(self, esquina):
        if self._cargando:
            return
        if self.chk_sync_esquinas.isChecked():
            valor = self.combo_esquina[esquina].currentData()
            self._cargando = True
            for otra, combo in self.combo_esquina.items():
                if otra == esquina:
                    continue
                combo.blockSignals(True)
                seleccionar_por_dato(combo, valor)
                combo.blockSignals(False)
            self._cargando = False
        self._emitir()

    def _on_sync_toggled(self, activo):
        if self._cargando:
            return
        if activo:
            valor = self.combo_esquina["frente_izquierda"].currentData()
            self._cargando = True
            for combo in self.combo_esquina.values():
                combo.blockSignals(True)
                seleccionar_por_dato(combo, valor)
                combo.blockSignals(False)
            self._cargando = False
        self._emitir()
