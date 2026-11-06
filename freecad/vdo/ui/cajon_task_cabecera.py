# =====================================================================
# cajon_task_cabecera.py
# Cabecera de cotas y cantos de la fachada del panel de cajón.
# =====================================================================

from freecad.vdo.qt_compat import QtWidgets


# ---------------------------------------------------------------------
# PanelHeaderWidget: cabecera con cotas y cantos de la fachada
# ---------------------------------------------------------------------
class PanelHeaderWidget(QtWidgets.QGroupBox):
    """Cabecera informativa que muestra cotas y cantos de la fachada
    y las piezas del cajón seleccionado. Tema oscuro."""

    def __init__(self, parent=None):
        super().__init__("Fachada — Cotas y Cantos", parent)
        self.setStyleSheet(
            "QGroupBox { font-weight: bold; color: #e0e0e0; "
            "border: 1px solid #555555; border-radius: 6px; "
            "margin-top: 10px; padding-top: 8px; }"
            "QGroupBox::title { subcontrol-origin: margin; left: 10px; "
            "padding: 0 4px; }")

        self._layout = QtWidgets.QGridLayout(self)
        self._layout.setHorizontalSpacing(12)
        self._layout.setVerticalSpacing(4)

        self._labels = {}
        filas = [
            ("ancho_fachada", "Ancho fachada (mm):"),
            ("alto_fachada", "Alto fachada (mm):"),
            ("espesor_fachada", "Espesor (mm):"),
            ("sistema_apertura", "Sistema apertura:"),
            ("operacion_canto", "Operación canto sup.:"),
            ("canto_norte", "Canto Norte:"),
            ("canto_sur", "Canto Sur:"),
            ("canto_este", "Canto Este:"),
            ("canto_oeste", "Canto Oeste:"),
        ]
        for i, (clave, texto) in enumerate(filas):
            lbl_key = QtWidgets.QLabel(texto)
            lbl_key.setStyleSheet("color: #b0b0b0; font-size: 11px;")
            lbl_val = QtWidgets.QLabel("-")
            lbl_val.setStyleSheet("color: #e0e0e0; font-size: 11px;")
            lbl_val.setMinimumWidth(120)
            self._layout.addWidget(lbl_key, i, 0)
            self._layout.addWidget(lbl_val, i, 1)
            self._labels[clave] = lbl_val

    def actualizar(self, datos_fachada):
        """Actualiza los valores mostrados con los datos de la fachada."""
        if not datos_fachada:
            return
        self._labels["ancho_fachada"].setText(
            f"{float(datos_fachada.get('ancho', 0)):.1f}")
        self._labels["alto_fachada"].setText(
            f"{float(datos_fachada.get('alto', 0)):.1f}")
        self._labels["espesor_fachada"].setText(
            f"{float(datos_fachada.get('espesor', 0)):.1f}")
        self._labels["sistema_apertura"].setText(
            str(datos_fachada.get("sistema_apertura", "-")))
        self._labels["operacion_canto"].setText(
            str(datos_fachada.get("operacion_canto", "-")))
        cantos = datos_fachada.get("cantos", {})
        for lado in ("norte", "sur", "este", "oeste"):
            self._labels[f"canto_{lado}"].setText(
                str(cantos.get(lado, "-")))
