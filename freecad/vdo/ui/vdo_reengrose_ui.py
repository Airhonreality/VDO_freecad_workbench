"""Editor Qt del modificador universal de bordes de reengrose."""

from freecad.vdo.core import vdo_reengrose_modelo as VDO_RE_MODELO
from freecad.vdo.core import vdo_reengrose_modificador as VDO_RE_MODIFICADOR
from freecad.vdo.qt_compat import QtCore, QtWidgets
from freecad.vdo.ui.reengrose_ui_constantes import LABEL_BORDE
from freecad.vdo.ui.reengrose_ui_construccion import ReengroseConstruccionMixin


class ReengroseBorderEditor(
    ReengroseConstruccionMixin,
    QtWidgets.QGroupBox):
    """Seccion Figma-like: bordes, distancia al canto, largos y esquinas."""

    changed = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__("Reengrose / Refuerzo", parent)
        self._cargando = False
        self._construir()
        self._conectar()
        self._actualizar_estado()

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
            self._cargando = True
            for borde in VDO_RE_MODELO.BORDES_2D:
                self.spin_ancho_borde[borde].setValue(
                    self.spin_ancho.value())
                self.spin_offset_borde[borde].setValue(
                    self.spin_offset.value())
            self._cargando = False
        self._actualizar_estado()
        self._emitir()

    def _on_uniforme_spin(self, *args):
        if self._cargando:
            return
        if self.chk_uniforme.isChecked():
            self._cargando = True
            for borde in VDO_RE_MODELO.BORDES_2D:
                self.spin_ancho_borde[borde].setValue(
                    self.spin_ancho.value())
                self.spin_offset_borde[borde].setValue(
                    self.spin_offset.value())
            self._cargando = False
        self._emitir()

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
                self._set_combo_data(combo, valor)
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
                self._set_combo_data(combo, valor)
                combo.blockSignals(False)
            self._cargando = False
        self._emitir()

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

    # -----------------------------------------------------------------
    # API para paneles/editor
    # -----------------------------------------------------------------
    def cargar(self, modifier):
        if isinstance(modifier, VDO_RE_MODELO.ReengroseDTO):
            mod = VDO_RE_MODIFICADOR.ReengroseModifier(modifier)
        elif isinstance(modifier, VDO_RE_MODIFICADOR.ReengroseModifier):
            mod = modifier
        else:
            mod = VDO_RE_MODIFICADOR.ReengroseModifier(modifier)

        bordes = {}
        if getattr(mod, "usa_bordes", False):
            for borde in VDO_RE_MODELO.BORDES_2D:
                cfg = mod.bordes.get(borde)
                if isinstance(cfg, VDO_RE_MODELO.BordeConfig):
                    bordes[borde] = cfg
                else:
                    bordes[borde] = VDO_RE_MODELO.BordeConfig.from_dict(cfg)
        else:
            activo_legacy = None
            if mod.activo and mod.orientacion == "paralela":
                if mod.alineacion_profundidad in ("frente", "fondo"):
                    activo_legacy = mod.alineacion_profundidad
            if mod.activo and activo_legacy is None:
                activo_legacy = "frente"
            for borde in VDO_RE_MODELO.BORDES_2D:
                bordes[borde] = VDO_RE_MODELO.BordeConfig(
                    activo=(borde == activo_legacy),
                    ancho=mod.ancho,
                    offset_borde=0.0,
                    espesor=mod.espesor)

        activos = [b for b in VDO_RE_MODELO.BORDES_2D
                   if bordes[b].activo]
        primero = bordes[activos[0]] if activos else None
        ancho = primero.ancho if primero else mod.ancho
        offset = primero.offset_borde if primero else 0.0
        largo_tira = (primero.largo_tira if primero
                      else VDO_RE_MODELO.LARGO_TIRA_DEFAULT)
        uniforme = True
        if activos:
            uniforme = all(
                abs(bordes[b].ancho - ancho) <= 1e-6
                and abs(bordes[b].offset_borde - offset) <= 1e-6
                and bordes[b].largo_tira == largo_tira
                for b in activos)

        esquinas_raw = getattr(
            mod, "esquinas", VDO_RE_MODELO.ENCUENTRO_ESQUINAS_DEFAULT)
        if not esquinas_raw:
            esquinas_raw = VDO_RE_MODELO.ENCUENTRO_ESQUINAS_DEFAULT
        esquinas = VDO_RE_MODIFICADOR._normalizar_encuentro(esquinas_raw)
        uniforme_esq = len(set(esquinas.values())) == 1

        self._cargando = True
        self.chk_activo.setChecked(bool(mod.activo))
        for borde in VDO_RE_MODELO.BORDES_2D:
            cfg = bordes[borde]
            self.btn_borde[borde].setChecked(bool(cfg.activo))
            self.spin_ancho_borde[borde].setValue(float(cfg.ancho))
            self.spin_offset_borde[borde].setValue(
                float(cfg.offset_borde))
        self.spin_ancho.setValue(float(ancho))
        self.spin_offset.setValue(float(offset))
        self._set_combo_data(self.combo_largo_tira, largo_tira)
        self.spin_espesor.setValue(
            0.0 if mod.espesor is None else float(mod.espesor))
        self.chk_uniforme.setChecked(uniforme)
        for esquina in VDO_RE_MODELO.ESQUINAS_2D:
            self._set_combo_data(
                self.combo_esquina[esquina], esquinas[esquina])
        self.chk_sync_esquinas.setChecked(uniforme_esq)
        self._set_combo_data(self.combo_fabricacion, mod.fabricacion)
        self._set_combo_data(self.combo_choque, mod.choque_nucleo)
        self._set_combo_data(self.combo_cara, mod.cara)
        self._cargando = False
        self._actualizar_estado()

    @staticmethod
    def _set_combo_data(combo, valor):
        idx = combo.findData(valor)
        if idx >= 0:
            combo.setCurrentIndex(idx)

    def _datos_bordes(self):
        espesor = self.spin_espesor.value()
        espesor = espesor if espesor > 0 else None
        largo_tira = self.combo_largo_tira.currentData()
        bordes = {}
        for borde in VDO_RE_MODELO.BORDES_2D:
            if self.chk_uniforme.isChecked():
                ancho = self.spin_ancho.value()
                offset = self.spin_offset.value()
            else:
                ancho = self.spin_ancho_borde[borde].value()
                offset = self.spin_offset_borde[borde].value()
            bordes[borde] = {
                "activo": self.btn_borde[borde].isChecked(),
                "ancho": ancho,
                "distancia_al_canto": offset,
                "largo_tira": largo_tira,
                "offset_borde": offset,
                "espesor": espesor,
            }
        return bordes

    def leer_modificador(self):
        return VDO_RE_MODIFICADOR.ReengroseModifier({
            "activo": self.chk_activo.isChecked(),
            "bordes": self._datos_bordes(),
            "esquinas": self._esquinas_actuales(),
            "fabricacion": self.combo_fabricacion.currentData(),
            "choque_nucleo": self.combo_choque.currentData(),
            "cara": self.combo_cara.currentData(),
            "usa_bordes": True,
        })

    def set_activar_si_vacio(self):
        if not self._bordes_activos():
            self._cargando = True
            self.btn_borde["frente"].setChecked(True)
            self._cargando = False
            self._actualizar_estado()
