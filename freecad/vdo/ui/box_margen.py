"""Margenes de borde y chips de offset. Parte de ui/vdo_box_controller.py (M7, D-44)."""

from freecad.vdo.core import vdo_reengrose_modelo as VDO_RE_MODELO

from freecad.vdo.ui.box_constantes import obtener_svg_icon


class BoxMargenMixin:
    """Mixin de VDOBoxControllerWidget: Margenes de borde y chips de offset. Sin cambios de codigo (D-44)."""

    # ------------------------------------------------------------------
    # Lógica de Interacción (State Machine y Poka-Yoke)
    # ------------------------------------------------------------------
    def _on_activo_toggled(self, activo):
        if self._cargando:
            return
        if activo and not self._hay_bordes_activos():
            self._cargando = True
            self.btn_borde["frente"].setChecked(True)
            self._cargando = False
        self._actualizar_estado_habilitacion()
        self._actualizar_estado_all()
        self._actualizar_canvas_concentrico()
        self._emitir_cambio()

    def _hay_bordes_activos(self):
        return any(self.btn_borde[b].isChecked() for b in VDO_RE_MODELO.BORDES_2D)

    def _on_all_clicked(self):
        if self._cargando:
            return
        activos_actuales = sum(1 for b in VDO_RE_MODELO.BORDES_2D if self.btn_borde[b].isChecked())
        nuevo_estado = (activos_actuales < len(VDO_RE_MODELO.BORDES_2D))

        self._cargando = True
        for b in VDO_RE_MODELO.BORDES_2D:
            self.btn_borde[b].setChecked(nuevo_estado)
        self.btn_all.setChecked(nuevo_estado)
        if nuevo_estado and not self.chk_activo.isChecked():
            self.chk_activo.setChecked(True)
        self._cargando = False

        self._actualizar_estado_habilitacion()
        self._actualizar_canvas_concentrico()
        self._emitir_cambio()

    def _on_borde_clicked(self, borde):
        if self._cargando:
            return
        self._seleccionar_margen(borde)
        if self.btn_borde[borde].isChecked() and not self.chk_activo.isChecked():
            self._cargando = True
            self.chk_activo.setChecked(True)
            self._cargando = False
        self._actualizar_estado_all()
        self._actualizar_canvas_concentrico()
        self._emitir_cambio()

    def _seleccionar_margen(self, margen):
        self._margen_seleccionado = margen
        self._borde_seleccionado = margen

        # Actualizar estilo de chips de margen
        for b, btn in self.btn_margenes.items():
            btn.blockSignals(True)
            btn.setChecked(b == margen)
            btn.blockSignals(False)

        # Actualizar etiquetas de botones de borde
        for b, btn in self.btn_borde.items():
            btn.setProperty("selected", "true" if b == margen else "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)

        self.lbl_margen_tag.setText(f"Margen: <b>{margen.upper()}</b>")

        # Cargar valores en los spinboxes principales si estamos en modo individual
        if not self.btn_centro.isChecked():
            self._cargando = True
            w = self._valores_bordes[margen]["ancho"]
            d = self._valores_bordes[margen]["offset"]
            self.spin_ancho.setValue(w)
            self.spin_offset.setValue(d)
            self._cargando = False

        self._actualizar_canvas_concentrico()

    def _aplicar_chip_offset(self, val):
        self.spin_offset.setValue(float(val))

    def _on_spin_ancho_changed(self):
        if self._cargando:
            return
        w = self.spin_ancho.value()
        if self.btn_centro.isChecked():
            # Uniforme: replicar a todos los bordes
            for b in VDO_RE_MODELO.BORDES_2D:
                self._valores_bordes[b]["ancho"] = w
                self.spin_ancho_borde[b].setValue(w)
        else:
            # Individual: aplicar solo al margen seleccionado
            m = self._margen_seleccionado
            self._valores_bordes[m]["ancho"] = w
            self.spin_ancho_borde[m].setValue(w)

        self._actualizar_canvas_concentrico()
        self._emitir_cambio()

    def _on_spin_offset_changed(self):
        if self._cargando:
            return
        d = self.spin_offset.value()
        if self.btn_centro.isChecked():
            # Uniforme: replicar a todos los bordes
            for b in VDO_RE_MODELO.BORDES_2D:
                self._valores_bordes[b]["offset"] = d
                self.spin_offset_borde[b].setValue(d)
        else:
            # Individual: aplicar solo al margen seleccionado
            m = self._margen_seleccionado
            self._valores_bordes[m]["offset"] = d
            self.spin_offset_borde[m].setValue(d)

        self._actualizar_canvas_concentrico()
        self._emitir_cambio()

    def _on_uniforme_toggled(self):
        if self._cargando:
            return
        uniforme = self.btn_centro.isChecked()
        self._cargando = True
        if uniforme:
            self.btn_centro.setText(" Uniforme")
            self.btn_centro.setIcon(obtener_svg_icon("link"))
            ancho_u = self.spin_ancho.value()
            dist_u = self.spin_offset.value()
            for b in VDO_RE_MODELO.BORDES_2D:
                self._valores_bordes[b]["ancho"] = ancho_u
                self._valores_bordes[b]["offset"] = dist_u
                self.spin_ancho_borde[b].setValue(ancho_u)
                self.spin_offset_borde[b].setValue(dist_u)
        else:
            self.btn_centro.setText(" Individual")
            self.btn_centro.setIcon(obtener_svg_icon("unlink"))
            m = self._margen_seleccionado
            self.spin_ancho.setValue(self._valores_bordes[m]["ancho"])
            self.spin_offset.setValue(self._valores_bordes[m]["offset"])

        self._cargando = False
        self._actualizar_canvas_concentrico()
        self._emitir_cambio()

    seleccionar_margen = _seleccionar_margen
