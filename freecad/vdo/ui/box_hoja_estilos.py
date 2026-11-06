"""Hoja de estilos oscura. Parte de ui/box_controller.py (M7, D-44)."""


# ----------------------------------------------------------------------
# Hoja de estilos oscura (Figma Dark Theme)
# ----------------------------------------------------------------------
ESTILO_WIDGET = """
QWidget#VDOBoxRoot {
    background-color: #1e1e1e;
    color: #e0e0e0;
}

QFrame#canvas_container {
    background-color: #141414;
    border: 1px solid #333333;
    border-radius: 8px;
}

QPushButton.borde-btn {
    background-color: #262626;
    border: 1px solid #444444;
    border-radius: 4px;
    color: #888888;
    font-size: 10px;
    font-weight: bold;
    padding: 2px 4px;
}
QPushButton.borde-btn:hover {
    background-color: #333333;
    border-color: #666666;
    color: #cccccc;
}
QPushButton.borde-btn:checked {
    background-color: #0d4a75;
    border: 1px solid #007acc;
    color: #ffffff;
}
QPushButton.borde-btn[selected="true"] {
    border: 1.5px solid #00b4d8;
}

QPushButton.esquina-btn {
    background-color: #202020;
    border: 1px solid #444444;
    border-radius: 4px;
    padding: 2px;
}
QPushButton.esquina-btn:hover {
    background-color: #303030;
    border-color: #007acc;
}
QPushButton.esquina-btn:pressed {
    background-color: #161616;
}

QPushButton.centro-btn {
    background-color: #1b1b1b;
    border: 1px solid #3a3a3a;
    border-radius: 6px;
    color: #cccccc;
    font-size: 10px;
    font-weight: bold;
    padding: 3px 6px;
}
QPushButton.centro-btn:hover {
    background-color: #252525;
    border-color: #555555;
    color: #ffffff;
}
QPushButton.centro-btn:checked {
    background-color: #192a3a;
    border: 1px solid #007acc;
    color: #4da3ff;
}

QPushButton.all-btn {
    background-color: #2b2b2b;
    border: 1px solid #444444;
    border-radius: 4px;
    color: #cccccc;
    font-weight: bold;
    font-size: 11px;
    padding: 2px 8px;
}
QPushButton.all-btn:hover {
    background-color: #383838;
    border-color: #666666;
}
QPushButton.all-btn:checked {
    background-color: #007acc;
    border-color: #007acc;
    color: #ffffff;
}

QPushButton.chip-btn {
    background-color: #252525;
    border: 1px solid #444444;
    border-radius: 3px;
    color: #aaaaaa;
    font-size: 10px;
    padding: 2px 6px;
}
QPushButton.chip-btn:hover {
    background-color: #333333;
    border-color: #007acc;
    color: #ffffff;
}
QPushButton.chip-btn:checked {
    background-color: #005a9e;
    border-color: #007acc;
    color: #ffffff;
    font-weight: bold;
}

QCheckBox {
    color: #d0d0d0;
    font-size: 11px;
}
QCheckBox::indicator {
    width: 14px;
    height: 14px;
}

QLabel {
    color: #cccccc;
    font-size: 11px;
}
"""
