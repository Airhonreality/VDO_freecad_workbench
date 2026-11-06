from freecad.vdo.ui import tema

"""Hoja de estilos del chasis. Parte de ui/chassis_widget.py (M7, D-45)."""



_ESTILO_CHASSIS = f"""
            QWidget {{
                background-color: {tema.FONDO};
                color: {tema.TEXTO};
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
            }}
            #frameMatriz {{
                background-color: {tema.COLOR_FONDO_CANVAS};
                border: 1px solid {tema.COLOR_BORDE_OSCURO};
                border-radius: 6px;
            }}
            .arquetipo-chip {{
                background-color: {tema.COLOR_FONDO_BOTON};
                border: 1px solid {tema.BORDE};
                border-radius: 4px;
                padding: 2px 8px;
                font-size: 9px;
                color: {tema.TEXTO_SUAVE2};
            }}
            .arquetipo-chip:hover {{
                background-color: {tema.COLOR_FONDO_SECUNDARIO};
                border-color: {tema.ACEINTO};
                color: {tema.TEXTO_CLARO};
            }}
            .btn-cara-horiz {{
                background-color: {tema.COLOR_FONDO_CHASIS};
                border: 1.5px solid {tema.ACEINTO};
                border-radius: 4px;
                font-size: 10px;
                font-weight: bold;
                color: {tema.TEXTO_CLARO};
            }}
            .btn-cara-horiz:!checked {{
                background-color: {tema.COLOR_FONDO_CHASIS_OSCURO};
                border: 1px dashed {tema.COLOR_BORDE_MEDIO};
                color: {tema.COLOR_TEXTO_MUTED};
            }}
            .btn-cara-vert {{
                background-color: {tema.COLOR_FONDO_CHASIS};
                border: 1.5px solid {tema.ACEINTO};
                border-radius: 4px;
                font-size: 8px;
                font-weight: bold;
                color: {tema.TEXTO_CLARO};
                line-height: 10px;
            }}
            .btn-cara-vert:!checked {{
                background-color: {tema.COLOR_FONDO_CHASIS_OSCURO};
                border: 1px dashed {tema.COLOR_BORDE_MEDIO};
                color: {tema.COLOR_TEXTO_MUTED};
            }}
            .btn-esquina {{
                background-color: {tema.FONDO2};
                border: 1px solid {tema.BORDE};
                border-radius: 5px;
            }}
            .btn-esquina:hover {{
                background-color: {tema.FONDO3};
                border-color: {tema.ACEINTO};
            }}
            .btn-esquina:pressed {{
                background-color: {tema.ACEINTO};
            }}
            .grupo-base {{
                border: 1px solid {tema.FONDO3};
                border-radius: 5px;
                margin-top: 6px;
                padding-top: 8px;
                font-size: 9px;
                font-weight: bold;
                color: {tema.TEXTO_SUAVE};
            }}
            .estrategia-btn {{
                background-color: {tema.COLOR_FONDO_MEDIO};
                border: 1px solid {tema.COLOR_BORDE_MEDIO_OSCURO};
                border-radius: 4px;
                font-size: 10px;
                color: {tema.TEXTO_SUAVE2};
            }}
            .estrategia-btn:checked {{
                background-color: {tema.ACEINTO};
                border-color: {tema.ACEINTO};
                color: {tema.TEXTO_CLARO};
                font-weight: bold;
            }}
            .estrategia-btn:hover:!checked {{
                background-color: {tema.FONDO3};
                color: {tema.TEXTO_CLARO};
            }}
            QComboBox {{
                background-color: {tema.COLOR_FONDO_BASE};
                border: 1px solid {tema.BORDE};
                border-radius: 4px;
                padding: 3px 6px;
                font-size: 10px;
            }}
            QComboBox:hover {{
                border-color: {tema.ACEINTO};
            }}
            QDoubleSpinBox {{
                background-color: {tema.COLOR_FONDO_BASE};
                border: 1px solid {tema.BORDE};
                border-radius: 4px;
                padding: 2px 4px;
                font-size: 10px;
                color: {tema.TEXTO_CLARO};
            }}
            QDoubleSpinBox:focus {{
                border-color: {tema.ACEINTO};
            }}
        """


class ChassisEstilosMixin:
    """Mixin de VDOChassisControllerWidget: hoja de estilos. Sin cambios de codigo (D-45)."""

    def _aplicar_estilos(self):
        tema.aplicar_estilo(self, _ESTILO_CHASSIS)
