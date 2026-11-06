"""
vdo_chassis_widget.py

Widget de Corte Transversal Interactivo 2D para la Envolvente / Chasis Paramétrico (Capa 1).
Parte del Sistema VDO (Ergonomía Cognitiva, Semiótica Espacial y Poka-Yoke para CAD/CAM).

Axioma:
    El COCO no es una primitiva; es solo un arquetipo de una envolvente paramétrica
    donde las caras pueden estar Activas o Ausentes, los encuentros de esquina conmutan
    entre las uniones de taller reales (tapa_domina, lateral_domina, inglete_45),
    y la base soporta múltiples estrategias (zócalo, suspendido, patas).

Compatible con PySide, PySide2 y PySide6 mediante vdo_qt.py.
"""

import logging
import sys

from freecad.vdo.qt_compat import QtCore, QtGui, QtSvg, QtWidgets

from freecad.vdo.ui.chassis_constantes import (
    CARAS,
    ENCUENTROS,
    ENCUENTRO_LABELS,
    ENCUENTRO_TOOLTIPS,
    obtener_svg_icon,
)
from freecad.vdo.ui.chassis_construccion import ChassisConstruccionMixin
from freecad.vdo.ui.chassis_estilos import ChassisEstilosMixin
from freecad.vdo.ui.chassis_eventos import ChassisEventosMixin

_LOG = logging.getLogger(__name__)



# ----------------------------------------------------------------------
# Widget Principal: VDOChassisControllerWidget
# ----------------------------------------------------------------------
class VDOChassisControllerWidget(
    ChassisConstruccionMixin,
    ChassisEstilosMixin,
    ChassisEventosMixin,
    QtWidgets.QWidget,
):
    """
    Controlador semiótico 2D para la Envolvente / Chasis Paramétrico (Capa 1).
    Permite conmutar caras activas/ausentes, ciclar uniones de esquina y
    definir la estrategia de base de forma interactiva y Poka-Yoke.
    """

    sigChassisChanged = QtCore.Signal(dict)
    sigConfigChanged = sigChassisChanged  # Alias de conveniencia

    def __init__(self, parent=None):
        super().__init__(parent)
        self._cargando = False

        # Estado del modelo de Capa 1
        self._caras = {
            "superior": {"activa": True, "tipo": "estructural"},
            "inferior": {"activa": True, "tipo": "estructural"},
            "izquierda": {"activa": True, "tipo": "estructural"},
            "derecha": {"activa": True, "tipo": "estructural"},
            "fondo": {"activa": True, "tipo": "ranurado_5mm"},
        }
        self._encuentros = {
            "superior_izq": "tapa_domina",
            "superior_der": "tapa_domina",
            "inferior_izq": "lateral_domina",
            "inferior_der": "lateral_domina",
        }
        self._base = {
            "estrategia": "zocalo",
            "altura": 100.0,
            "separacion_frente": 50.0,
        }

        self._init_ui()
        self._aplicar_estilos()
        self._actualizar_ui()

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

    def _emitir_cambio(self):
        if not self._cargando:
            self.sigChassisChanged.emit(self.getChassisConfig())

    # ------------------------------------------------------------------
    # Contrato Público API (Capa 1)
    # ------------------------------------------------------------------
    def setChassisConfig(self, cfg: dict):
        """Carga la configuración sin emitir señales redundantes."""
        if not isinstance(cfg, dict):
            return

        self._cargando = True
        try:
            # Caras
            caras_cfg = cfg.get("caras", {})
            for c in CARAS:
                if c in caras_cfg:
                    self._caras[c] = dict(caras_cfg[c])

            # Encuentros
            enc_cfg = cfg.get("encuentros", {})
            for e in ENCUENTROS:
                if e in enc_cfg:
                    self._encuentros[e] = enc_cfg[e]

            # Base
            base_cfg = cfg.get("base", {})
            if base_cfg:
                self._base.update(base_cfg)

            self._actualizar_ui()
        finally:
            self._cargando = False

    def getChassisConfig(self) -> dict:
        """Devuelve el diccionario canónico de Capa 1 para el chasis."""
        return {
            "caras": {
                c: dict(self._caras[c]) for c in CARAS
            },
            "encuentros": {
                e: self._encuentros[e] for e in ENCUENTROS
            },
            "base": {
                "estrategia": self._base.get("estrategia", "zocalo"),
                "altura": float(self._base.get("altura", 100.0)),
                "separacion_frente": float(self._base.get("separacion_frente", 50.0)),
            }
        }

    # Aliases de compatibilidad y estilo snake_case
    set_chassis_config = setChassisConfig
    get_chassis_config = getChassisConfig


# ----------------------------------------------------------------------
# Ejecución Standalone para Validación Visual Directa
# ----------------------------------------------------------------------
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")

    # Paleta oscura global coherente
    paleta = QtGui.QPalette()
    paleta.setColor(QtGui.QPalette.Window, QtGui.QColor("#1e1e1e"))
    paleta.setColor(QtGui.QPalette.WindowText, QtGui.QColor("#e0e0e0"))
    paleta.setColor(QtGui.QPalette.Base, QtGui.QColor("#252525"))
    paleta.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor("#1e1e1e"))
    paleta.setColor(QtGui.QPalette.Text, QtGui.QColor("#e0e0e0"))
    paleta.setColor(QtGui.QPalette.Button, QtGui.QColor("#2b2b2b"))
    paleta.setColor(QtGui.QPalette.ButtonText, QtGui.QColor("#ffffff"))
    paleta.setColor(QtGui.QPalette.Highlight, QtGui.QColor("#007acc"))
    paleta.setColor(QtGui.QPalette.HighlightedText, QtGui.QColor("#ffffff"))
    app.setPalette(paleta)

    ventana = QtWidgets.QMainWindow()
    ventana.setWindowTitle("VDO Chassis Controller - Corte Transversal Interactivo 2D")
    ventana.setMinimumSize(360, 480)

    widget = VDOChassisControllerWidget()

    def on_change(cfg):
        activas = [c for c, d in cfg["caras"].items() if d.get("activa")]
        _LOG.debug(f"[VDO Chassis Event] Caras activas: {activas} | Encuentros: {cfg['encuentros']} | Base: {cfg['base']['estrategia']}")

    widget.sigChassisChanged.connect(on_change)

    ventana.setCentralWidget(widget)
    ventana.show()
    exec_func = getattr(app, "exec", getattr(app, "exec_", None))
    sys.exit(exec_func())
