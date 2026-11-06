"""
chassis_widget.py

Widget de Corte Transversal Interactivo 2D para la Envolvente / Chasis Paramétrico (Capa 1).
Parte del Sistema VDO (Ergonomía Cognitiva, Semiótica Espacial y Poka-Yoke para CAD/CAM).

Axioma:
    El COCO no es una primitiva; es solo un arquetipo de una envolvente paramétrica
    donde las caras pueden estar Activas o Ausentes, los encuentros de esquina conmutan
    entre las uniones de taller reales (tapa_domina, lateral_domina, inglete_45),
    y la base soporta múltiples estrategias (zócalo, suspendido, patas).

Compatible con PySide, PySide2 y PySide6 mediante qt.py.
"""

import logging
import sys

from freecad.vdo.qt_compat import QtCore, QtGui, QtSvg, QtWidgets
from freecad.vdo.ui.chassis_config import ChassisConfigMixin
from freecad.vdo.ui.chassis_construccion import ChassisConstruccionMixin
from freecad.vdo.ui.chassis_estado import ChassisEstadoMixin
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
    ChassisEstadoMixin,
    ChassisConfigMixin,
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
