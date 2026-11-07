from freecad.vdo.ui import tema_colores, tema_estilos

"""Hoja de estilos del chasis. Parte de ui/chassis_widget.py (M7, D-45)."""



_ESTILO_CHASSIS = f"""
            QWidget {{
                background-color: {tema_colores.FONDO};
                color: {tema_colores.TEXTO};
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
            }}
            #frameMatriz {{
                background-color: {tema_colores.COLOR_FONDO_CANVAS};
                border: 1px solid {tema_colores.COLOR_BORDE_OSCURO};
                border-radius: 6px;
            }}
            .arquetipo-chip {{
                background-color: {tema_colores.COLOR_FONDO_BOTON};
                border: 1px solid {tema_colores.BORDE};
                border-radius: 4px;
                padding: 2px 8px;
                font-size: 9px;
                color: {tema_colores.TEXTO_SUAVE2};
            }}
            .arquetipo-chip:hover {{
                background-color: {tema_colores.COLOR_FONDO_SECUNDARIO};
                border-color: {tema_colores.ACEINTO};
                color: {tema_colores.TEXTO_CLARO};
            }}
            .btn-cara-horiz {{
                background-color: {tema_colores.COLOR_FONDO_CHASIS};
                border: 1.5px solid {tema_colores.ACEINTO};
                border-radius: 4px;
                font-size: 10px;
                font-weight: bold;
                color: {tema_colores.TEXTO_CLARO};
            }}
            .btn-cara-horiz:!checked {{
                background-color: {tema_colores.COLOR_FONDO_CHASIS_OSCURO};
                border: 1px dashed {tema_colores.COLOR_BORDE_MEDIO};
                color: {tema_colores.COLOR_TEXTO_MUTED};
            }}
            .btn-cara-vert {{
                background-color: {tema_colores.COLOR_FONDO_CHASIS};
                border: 1.5px solid {tema_colores.ACEINTO};
                border-radius: 4px;
                font-size: 8px;
                font-weight: bold;
                color: {tema_colores.TEXTO_CLARO};
                line-height: 10px;
            }}
            .btn-cara-vert:!checked {{
                background-color: {tema_colores.COLOR_FONDO_CHASIS_OSCURO};
                border: 1px dashed {tema_colores.COLOR_BORDE_MEDIO};
                color: {tema_colores.COLOR_TEXTO_MUTED};
            }}
            .btn-esquina {{
                background-color: {tema_colores.FONDO2};
                border: 1px solid {tema_colores.BORDE};
                border-radius: 5px;
            }}
            .btn-esquina:hover {{
                background-color: {tema_colores.FONDO3};
                border-color: {tema_colores.ACEINTO};
            }}
            .btn-esquina:pressed {{
                background-color: {tema_colores.ACEINTO};
            }}
            .grupo-base {{
                border: 1px solid {tema_colores.FONDO3};
                border-radius: 5px;
                margin-top: 6px;
                padding-top: 8px;
                font-size: 9px;
                font-weight: bold;
                color: {tema_colores.TEXTO_SUAVE};
            }}
            .estrategia-btn {{
                background-color: {tema_colores.COLOR_FONDO_MEDIO};
                border: 1px solid {tema_colores.COLOR_BORDE_MEDIO_OSCURO};
                border-radius: 4px;
                font-size: 10px;
                color: {tema_colores.TEXTO_SUAVE2};
            }}
            .estrategia-btn:checked {{
                background-color: {tema_colores.ACEINTO};
                border-color: {tema_colores.ACEINTO};
                color: {tema_colores.TEXTO_CLARO};
                font-weight: bold;
            }}
            .estrategia-btn:hover:!checked {{
                background-color: {tema_colores.FONDO3};
                color: {tema_colores.TEXTO_CLARO};
            }}
            QComboBox {{
                background-color: {tema_colores.COLOR_FONDO_BASE};
                border: 1px solid {tema_colores.BORDE};
                border-radius: 4px;
                padding: 3px 6px;
                font-size: 10px;
            }}
            QComboBox:hover {{
                border-color: {tema_colores.ACEINTO};
            }}
            QDoubleSpinBox {{
                background-color: {tema_colores.COLOR_FONDO_BASE};
                border: 1px solid {tema_colores.BORDE};
                border-radius: 4px;
                padding: 2px 4px;
                font-size: 10px;
                color: {tema_colores.TEXTO_CLARO};
            }}
            QDoubleSpinBox:focus {{
                border-color: {tema_colores.ACEINTO};
            }}
        """


class ChassisEstilosMixin:
    """Mixin de VDOChassisControllerWidget: hoja de estilos. Sin cambios de codigo (D-45)."""

    def _aplicar_estilos(self):
        tema_estilos.aplicar_estilo(self, _ESTILO_CHASSIS)
