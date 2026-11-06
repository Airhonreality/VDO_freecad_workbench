"""API de carga y lectura del modificador de reengrose en el editor."""

from freecad.vdo.core import reengrose_modelo as VDO_RE_MODELO
from freecad.vdo.core import reengrose_modificador as VDO_RE_MODIFICADOR


class ReengroseConfigMixin:
    """API de carga y lectura del modificador de reengrose en el editor."""

    # -----------------------------------------------------------------
    # API para paneles/editor
    # -----------------------------------------------------------------
    def cargar(self, modifier):
        mod = self._modificador_de(modifier)
        bordes = self._bordes_de(mod)
        ancho, offset, largo_tira, uniforme = self._agregar_bordes(bordes, mod)
        esquinas, uniforme_esq = self._esquinas_de(mod)
        self._cargando = True
        self._aplicar_bordes_ui(mod, bordes, ancho, offset, largo_tira, uniforme)
        self._aplicar_esquinas_ui(esquinas, uniforme_esq)
        self._set_combo_data(self.combo_fabricacion, mod.fabricacion)
        self._set_combo_data(self.combo_choque, mod.choque_nucleo)
        self._set_combo_data(self.combo_cara, mod.cara)
        self._cargando = False
        self._actualizar_estado()

    def _modificador_de(self, modifier):
        if isinstance(modifier, VDO_RE_MODELO.ReengroseDTO):
            mod = VDO_RE_MODIFICADOR.ReengroseModifier(modifier)
        elif isinstance(modifier, VDO_RE_MODIFICADOR.ReengroseModifier):
            mod = modifier
        else:
            mod = VDO_RE_MODIFICADOR.ReengroseModifier(modifier)
        return mod

    def _bordes_de(self, mod):
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

        return bordes

    def _agregar_bordes(self, bordes, mod):
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

        return ancho, offset, largo_tira, uniforme

    def _esquinas_de(self, mod):
        esquinas_raw = getattr(
            mod, "esquinas", VDO_RE_MODELO.ENCUENTRO_ESQUINAS_DEFAULT)
        if not esquinas_raw:
            esquinas_raw = VDO_RE_MODELO.ENCUENTRO_ESQUINAS_DEFAULT
        esquinas = VDO_RE_MODIFICADOR._normalizar_encuentro(esquinas_raw)
        uniforme_esq = len(set(esquinas.values())) == 1
        return esquinas, uniforme_esq

    def _aplicar_bordes_ui(self, mod, bordes, ancho, offset, largo_tira, uniforme):
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

    def _aplicar_esquinas_ui(self, esquinas, uniforme_esq):
        for esquina in VDO_RE_MODELO.ESQUINAS_2D:
            self._set_combo_data(
                self.combo_esquina[esquina], esquinas[esquina])
        self.chk_sync_esquinas.setChecked(uniforme_esq)

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
