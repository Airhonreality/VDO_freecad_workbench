"""Estado, canvas y resumen. Parte de ui/box_controller.py (M7, D-44)."""

from freecad.vdo.core import reengrose_modelo as VDO_RE_MODELO
from freecad.vdo.ui.box_constantes import _TEXTO_BOTON_BORDE, ENCUENTRO_LABELS
from freecad.vdo.ui.qt import seleccionar_por_dato


class BoxEstadoMixin:
    """Mixin de VDOBoxControllerWidget: Estado, canvas y resumen. Sin cambios de codigo (D-44)."""

    def _actualizar_estado_all(self):
        todos = all(self.btn_borde[b].isChecked() for b in VDO_RE_MODELO.BORDES_2D)
        self.btn_all.blockSignals(True)
        self.btn_all.setChecked(todos)
        self.btn_all.blockSignals(False)

    def _actualizar_canvas_concentrico(self):
        activos = {b: self.btn_borde[b].isChecked() for b in VDO_RE_MODELO.BORDES_2D}
        self.canvas_concentrico.actualizar(
            activos, self._valores_bordes, self._esquinas, self._margen_seleccionado)

        # Actualizar texto explicativo en los 4 botones de borde
        for b in VDO_RE_MODELO.BORDES_2D:
            btn = self.btn_borde[b]
            w = self._valores_bordes[b]["ancho"]
            d = self._valores_bordes[b]["offset"]
            texto_offset = "0 mm (ras)" if d == 0.0 else f"⇥ {d:.0f} mm"

            plantilla = _TEXTO_BOTON_BORDE.get(b)
            if plantilla is not None:
                btn.setText(plantilla(w, texto_offset))

    def _actualizar_estado_habilitacion(self):
        activo = self.chk_activo.isChecked()
        self.container_canvas.setEnabled(activo)
        self.btn_all.setEnabled(activo)
        self.chk_sync_esquinas.setEnabled(activo)
        self.panel_medidas.setEnabled(activo)

    def _actualizar_estado(self):
        """Alias retrocompatible."""
        self._actualizar_estado_habilitacion()

    def _actualizar_resumen(self):
        if not self.chk_activo.isChecked():
            self.lbl_resumen.setText("Reengrose desactivado.")
            return
        activos = [b for b in VDO_RE_MODELO.BORDES_2D if self.btn_borde[b].isChecked()]
        if not activos:
            self.lbl_resumen.setText("Sin bordes perimetrales activos.")
            return

        nombres = [b.capitalize() for b in activos]
        if self.btn_centro.isChecked():
            offset_val = self.spin_offset.value()
            offset_txt = "al ras (offset 0)" if offset_val == 0 else f"offset {offset_val:.1f} mm"
            medidas = f"ancho {self.spin_ancho.value():.1f} mm · {offset_txt}"
        else:
            detalles = []
            for b in activos:
                w = self._valores_bordes[b]["ancho"]
                d = self._valores_bordes[b]["offset"]
                detalles.append(f"{b.capitalize()}: {w:.0f}mm @ {d:.0f}mm")
            medidas = " · ".join(detalles)

        tipos_esq = set(self._esquinas.values())
        if len(tipos_esq) == 1:
            texto_esq = ENCUENTRO_LABELS[next(iter(tipos_esq))]
        else:
            texto_esq = "Esquinas mixtas"

        esp = self.spin_espesor.value()
        texto_esp = f" · Espesor {esp:.1f} mm" if esp > 0 else ""

        self.lbl_resumen.setText(
            f"<b>{len(activos)} bordes</b> ({', '.join(nombres)})<br/>"
            f"{medidas}{texto_esp} · <i>{texto_esq}</i>"
        )

    def _emitir_cambio(self):
        if self._cargando:
            return
        self._actualizar_resumen()
        cfg = self.getConfig()
        self.sigConfigChanged.emit(cfg)
        self.changed.emit()

    @staticmethod
    def _set_combo_silencioso(combo, valor):
        combo.blockSignals(True)
        seleccionar_por_dato(combo, valor)
        combo.blockSignals(False)
