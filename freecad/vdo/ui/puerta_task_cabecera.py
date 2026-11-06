# =====================================================================
# puerta_task_cabecera.py
# Cabecera universal de pieza (PanelHeaderWidget) para el panel de puerta.
# =====================================================================

from freecad.vdo.qt_compat import QtWidgets
from freecad.vdo.ui import tema


# ---------------------------------------------------------------------
# PanelHeaderWidget (encabezado universal de pieza física)
# ---------------------------------------------------------------------
class PanelHeaderWidget(QtWidgets.QGroupBox):
    """Cabecera obligatoria para toda pieza física del sistema VDO.

    Muestra: [ Identificador ] [ Largo x Ancho x Espesor mm ]
             [ Cantos: Norte, Sur, Este, Oeste ]
    """

    def __init__(self, parent=None):
        super().__init__("Cabecera de pieza", parent)
        tema.aplicar_estilo(self, tema.ESTILO_PUERTA_GRUPO_CABECERA)
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(2)

        self.lbl_id = QtWidgets.QLabel("Sin selección")
        tema.aplicar_estilo(self.lbl_id, tema.ESTILO_NEGRITA)
        self.lbl_id.setWordWrap(True)
        layout.addWidget(self.lbl_id)

        self.lbl_dimensiones = QtWidgets.QLabel("—")
        self.lbl_dimensiones.setToolTip(
            "Dimensiones brutas de corte: Largo × Ancho × Espesor (mm).")  # noqa: RUF001 - etiqueta de interfaz: signo tipografico visible (x o -) que el usuario ve; cambiarlo altera el texto
        layout.addWidget(self.lbl_dimensiones)

        self.lbl_cantos = QtWidgets.QLabel("")
        self.lbl_cantos.setWordWrap(True)
        tema.aplicar_estilo(self.lbl_cantos, tema.ESTILO_ETIQUETA_OSCURA_COMPACTA)
        layout.addWidget(self.lbl_cantos)

    def set_pieza(self, identificador, largo, ancho, espesor, cantos=None):
        self.lbl_id.setText(str(identificador or "Pieza"))
        self.lbl_dimensiones.setText(
            f"{float(largo):.1f} × {float(ancho):.1f} × "  # noqa: RUF001 - etiqueta de interfaz: signo tipografico visible (x o -) que el usuario ve; cambiarlo altera el texto
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
