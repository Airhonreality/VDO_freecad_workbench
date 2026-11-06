"""Hoja de estilos del chasis. Parte de ui/vdo_chassis_widget.py (M7, D-45)."""



_ESTILO_CHASSIS = """
            QWidget {
                background-color: #1e1e1e;
                color: #e0e0e0;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
            }
            #frameMatriz {
                background-color: #161616;
                border: 1px solid #2d2d2d;
                border-radius: 6px;
            }
            .arquetipo-chip {
                background-color: #2b2b2b;
                border: 1px solid #444444;
                border-radius: 4px;
                padding: 2px 8px;
                font-size: 9px;
                color: #cccccc;
            }
            .arquetipo-chip:hover {
                background-color: #383838;
                border-color: #007acc;
                color: #ffffff;
            }
            .btn-cara-horiz {
                background-color: #25282c;
                border: 1.5px solid #007acc;
                border-radius: 4px;
                font-size: 10px;
                font-weight: bold;
                color: #ffffff;
            }
            .btn-cara-horiz:!checked {
                background-color: #1a1a1a;
                border: 1px dashed #555555;
                color: #777777;
            }
            .btn-cara-vert {
                background-color: #25282c;
                border: 1.5px solid #007acc;
                border-radius: 4px;
                font-size: 8px;
                font-weight: bold;
                color: #ffffff;
                line-height: 10px;
            }
            .btn-cara-vert:!checked {
                background-color: #1a1a1a;
                border: 1px dashed #555555;
                color: #777777;
            }
            .btn-esquina {
                background-color: #262626;
                border: 1px solid #444444;
                border-radius: 5px;
            }
            .btn-esquina:hover {
                background-color: #333333;
                border-color: #007acc;
            }
            .btn-esquina:pressed {
                background-color: #007acc;
            }
            .grupo-base {
                border: 1px solid #333333;
                border-radius: 5px;
                margin-top: 6px;
                padding-top: 8px;
                font-size: 9px;
                font-weight: bold;
                color: #888888;
            }
            .estrategia-btn {
                background-color: #282828;
                border: 1px solid #3d3d3d;
                border-radius: 4px;
                font-size: 10px;
                color: #cccccc;
            }
            .estrategia-btn:checked {
                background-color: #007acc;
                border-color: #007acc;
                color: #ffffff;
                font-weight: bold;
            }
            .estrategia-btn:hover:!checked {
                background-color: #333333;
                color: #ffffff;
            }
            QComboBox {
                background-color: #252525;
                border: 1px solid #444444;
                border-radius: 4px;
                padding: 3px 6px;
                font-size: 10px;
            }
            QComboBox:hover {
                border-color: #007acc;
            }
            QDoubleSpinBox {
                background-color: #252525;
                border: 1px solid #444444;
                border-radius: 4px;
                padding: 2px 4px;
                font-size: 10px;
                color: #ffffff;
            }
            QDoubleSpinBox:focus {
                border-color: #007acc;
            }
        """


class ChassisEstilosMixin:
    """Mixin de VDOChassisControllerWidget: hoja de estilos. Sin cambios de codigo (D-45)."""

    def _aplicar_estilos(self):
        self.setStyleSheet(_ESTILO_CHASSIS)
