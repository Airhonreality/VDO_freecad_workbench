# =====================================================================
# puerta_task_cabecera.py
# Cabecera universal de pieza (PanelHeaderWidget) para el panel de puerta.
# =====================================================================

from freecad.vdo.qt_compat import QtWidgets
from freecad.vdo.ui.puerta_task_constantes import (
    COLOR_BORDE,
    COLOR_FONDO,
    COLOR_TEXTO,
)


# ---------------------------------------------------------------------
# PanelHeaderWidget (encabezado universal de pieza física)
# ---------------------------------------------------------------------
class PanelHeaderWidget(QtWidgets.QGroupBox):
    """Cabecera obligatoria para toda pieza física del sistema VDO.

    Muestra: [ Identificador ] [ Largo × Ancho × Espesor mm ]
             [ Cantos: Norte, Sur, Este, Oeste ]
    """

    def __init__(self, parent=None):
        super().__init__("Cabecera de pieza", parent)
        self.setStyleSheet(
            f"QGroupBox {{ background: {COLOR_FONDO}; color: {COLOR_TEXTO}; "
            f"border: 1px solid {COLOR_BORDE}; border-radius: 4px; "
            f"margin-top: 8px; padding-top: 4px; }}"
            f"QGroupBox::title {{ subcontrol-origin: margin; left: 8px; }}")
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(2)

        self.lbl_id = QtWidgets.QLabel("Sin selección")
        self.lbl_id.setStyleSheet("font-weight: bold;")
        self.lbl_id.setWordWrap(True)
        layout.addWidget(self.lbl_id)

        self.lbl_dimensiones = QtWidgets.QLabel("—")
        self.lbl_dimensiones.setToolTip(
            "Dimensiones brutas de corte: Largo × Ancho × Espesor (mm).")
        layout.addWidget(self.lbl_dimensiones)

        self.lbl_cantos = QtWidgets.QLabel("")
        self.lbl_cantos.setWordWrap(True)
        self.lbl_cantos.setStyleSheet(
            f"QLabel {{ background: #2b2b2b; color: {COLOR_TEXTO}; "
            f"padding: 3px; border: 1px solid {COLOR_BORDE}; }}")
        layout.addWidget(self.lbl_cantos)

    def set_pieza(self, identificador, largo, ancho, espesor, cantos=None):
        self.lbl_id.setText(str(identificador or "Pieza"))
        self.lbl_dimensiones.setText(
            f"{float(largo):.1f} × {float(ancho):.1f} × "
            f"{float(espesor):.1f} mm")
        cantos = cantos or {}
        partes = []
        for borde in ("norte", "sur", "este", "oeste"):
            partes.append(f"{borde.title()}: {cantos.get(borde, 'FX')}")
        self.lbl_cantos.setText(" · ".join(partes))

    def clear(self):
        self.lbl_id.setText("Sin selección")
        self.lbl_dimensiones.setText("—")
        self.lbl_cantos.setText("")
