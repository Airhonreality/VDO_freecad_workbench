"""Estado visual del editor de reengrose: habilitacion, vista previa y resumen."""

from freecad.vdo.ui.reengrose_ui_constantes import LABEL_BORDE


class ReengroseEstadoMixin:
    """Estado visual del editor de reengrose: habilitacion, vista previa y resumen."""

    def _actualizar_estado(self):
        activo = self.chk_activo.isChecked()
        self.btn_all.setEnabled(activo)
        for btn in self.btn_borde.values():
            btn.setEnabled(activo)
        self.chk_uniforme.setEnabled(activo)
        self.spin_ancho.setEnabled(activo and self.chk_uniforme.isChecked())
        self.spin_offset.setEnabled(
            activo and self.chk_uniforme.isChecked())
        self.spin_espesor.setEnabled(activo)
        self.combo_largo_tira.setEnabled(activo)
        self.widget_custom.setVisible(
            activo and not self.chk_uniforme.isChecked())
        self.chk_sync_esquinas.setEnabled(activo)
        for combo in self.combo_esquina.values():
            combo.setEnabled(activo)
        for combo in (self.combo_fabricacion, self.combo_choque,
                      self.combo_cara):
            combo.setEnabled(activo)
        self._actualizar_preview()
        self._actualizar_resumen()

    def _actualizar_preview(self):
        activos = self._bordes_activos() if self.chk_activo.isChecked() else []
        self.preview.set_estado(activos, self._esquinas_actuales())

    def _actualizar_resumen(self):
        if not self.chk_activo.isChecked():
            self.lbl_resumen.setText("Sin reengrose.")
            return
        activos = self._bordes_activos()
        if not activos:
            self.lbl_resumen.setText("Sin bordes activos.")
            return
        if self.chk_uniforme.isChecked():
            anchos = {f"{self.spin_ancho.value():.1f}"}
            offsets = {f"{self.spin_offset.value():.1f}"}
        else:
            anchos = {
                f"{self.spin_ancho_borde[b].value():.1f}"
                for b in activos}
            offsets = {
                f"{self.spin_offset_borde[b].value():.1f}"
                for b in activos}
        tipos = set(self._esquinas_actuales().values())
        if len(tipos) == 1:
            texto_esquinas = self.combo_esquina[
                "frente_izquierda"].currentText()
        else:
            texto_esquinas = "esquinas mixtas"
        ancho = "/".join(sorted(anchos))
        offset = "/".join(sorted(offsets))
        largo = self.combo_largo_tira.currentText()
        nombre = ", ".join(LABEL_BORDE[b] for b in activos)
        self.lbl_resumen.setText(
            f"{len(activos)} bordes ({nombre}) · ancho {ancho} mm · "
            f"distancia al canto {offset} mm · {largo} · "
            f"{texto_esquinas} · "
            f"{self.combo_fabricacion.currentText()}.")
