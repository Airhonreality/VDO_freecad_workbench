"""Encuentros de esquina. Parte de ui/box_controller.py (M7, D-44)."""

from freecad.vdo.ui.box_constantes import (
    ENCUENTRO_TOOLTIPS,
    ESQUINAS,
    TIPOS_ENCUENTRO,
)
from freecad.vdo.ui.tema import obtener_svg_icon


class BoxEsquinasMixin:
    """Mixin de VDOBoxControllerWidget: Encuentros de esquina. Sin cambios de codigo (D-44)."""

    def _on_esquina_clicked(self, esquina):
        if self._cargando:
            return
        esquina = {
            "no": "fondo_izquierda", "ne": "fondo_derecha",
            "so": "frente_izquierda", "se": "frente_derecha"
        }.get(esquina.lower(), esquina)
        actual = self._esquinas[esquina]
        idx = (TIPOS_ENCUENTRO.index(actual) + 1) % len(TIPOS_ENCUENTRO)
        nuevo_tipo = TIPOS_ENCUENTRO[idx]

        self._cargando = True
        self.combo_esquina[esquina].blockSignals(True)
        idx_c = self.combo_esquina[esquina].findData(nuevo_tipo)
        if idx_c >= 0:
            self.combo_esquina[esquina].setCurrentIndex(idx_c)
        self.combo_esquina[esquina].blockSignals(False)
        self._cargando = False

        self._on_combo_esquina_changed(esquina)

    def _on_combo_esquina_changed(self, esquina):
        if self._cargando:
            return
        esquina = {
            "no": "fondo_izquierda", "ne": "fondo_derecha",
            "so": "frente_izquierda", "se": "frente_derecha"
        }.get(esquina.lower(), esquina)
        tipo = self.combo_esquina[esquina].currentData()
        if not tipo:
            return
        self._esquinas[esquina] = tipo

        if self.chk_sync_esquinas.isChecked():
            self._cargando = True
            for e in ESQUINAS:
                if e != esquina:
                    self._esquinas[e] = tipo
                    self._set_combo_silencioso(self.combo_esquina[e], tipo)
            self._cargando = False

        self._actualizar_iconos_esquinas()
        self._actualizar_canvas_concentrico()
        self._emitir_cambio()

    def _on_sync_esquinas_toggled(self, activo):
        if self._cargando:
            return
        if activo:
            tipo = self._esquinas["frente_izquierda"]
            self._cargando = True
            for e in ESQUINAS:
                self._esquinas[e] = tipo
                self._set_combo_silencioso(self.combo_esquina[e], tipo)
            self._cargando = False
            self._actualizar_iconos_esquinas()
            self._actualizar_canvas_concentrico()
            self._emitir_cambio()

    def _actualizar_iconos_esquinas(self):
        for e in ESQUINAS:
            tipo = self._esquinas[e]
            btn = self.btn_esquina[e]
            btn.setIcon(obtener_svg_icon(tipo, 20))
            btn.setToolTip(f"Esquina {e}:\n{ENCUENTRO_TOOLTIPS.get(tipo, tipo)}")
