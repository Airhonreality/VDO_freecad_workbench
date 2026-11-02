"""Menú de exportación de lista de corte (migrado de Macro/vdo_cutting_list.FCMacro).

Muestra el diálogo de modo (todo / selección / módulo) y, al confirmar, abre el preview
de piezas de melamina antes de exportar el CSV.
"""

import FreeCAD as App

from freecad.vdo.qt_compat import QtWidgets
from freecad.vdo.ui import vdo_cutting_list_preview


def mostrar_menu():
    """Muestra diálogo para elegir modo de exportación"""

    dialog = QtWidgets.QDialog()
    dialog.setWindowTitle("📊 VDO - Exportar Lista de Corte")
    dialog.setMinimumWidth(400)

    layout = QtWidgets.QVBoxLayout()

    # Título
    titulo = QtWidgets.QLabel("¿Qué piezas deseas exportar?")
    titulo.setStyleSheet("font-size: 14px; font-weight: bold;")
    layout.addWidget(titulo)

    layout.addSpacing(10)

    # Opciones
    radio_todo = QtWidgets.QRadioButton("📋 EXPORTAR TODO el documento")
    radio_seleccion = QtWidgets.QRadioButton("✋ EXPORTAR SELECCIÓN (objetos marcados)")
    radio_grupo = QtWidgets.QRadioButton("📦 EXPORTAR MÓDULO actual")

    # Preseleccionar SELECCIÓN si hay objetos marcados en el árbol/3D
    import FreeCADGui as Gui
    if Gui.Selection.getSelection():
        radio_seleccion.setChecked(True)
    else:
        radio_todo.setChecked(True)

    layout.addWidget(radio_todo)
    layout.addWidget(radio_seleccion)
    layout.addWidget(radio_grupo)

    layout.addSpacing(15)

    # Info
    info = QtWidgets.QLabel(
        "ℹ️ Se exportarán SOLO paneles de melamina\n"
        "   (Se excluyen muros, paneles BIM, etc)\n\n"
        "El siguiente paso mostrará un PREVIEW\n"
        "con las piezas coloreadas en ROJO para confirmar"
    )
    info.setStyleSheet("color: #666; font-size: 11px;")
    layout.addWidget(info)

    layout.addSpacing(15)

    # Botones
    btn_layout = QtWidgets.QHBoxLayout()

    btn_cancelar = QtWidgets.QPushButton("Cancelar")
    btn_cancelar.clicked.connect(dialog.reject)
    btn_layout.addWidget(btn_cancelar)

    btn_ok = QtWidgets.QPushButton("Continuar →")
    btn_ok.setStyleSheet("background-color: #0066cc; color: white; font-weight: bold;")
    btn_ok.clicked.connect(dialog.accept)
    btn_layout.addWidget(btn_ok)

    layout.addLayout(btn_layout)

    dialog.setLayout(layout)

    # Mostrar y obtener resultado
    if dialog.exec() != QtWidgets.QDialog.Accepted:
        App.Console.PrintMessage("❌ Cancelado")
        return None

    # Determinar modo seleccionado
    if radio_seleccion.isChecked():
        return "seleccion"
    elif radio_grupo.isChecked():
        return "grupo"
    else:
        return "todo"


def abrir_lista_corte():
    """Punto de entrada del comando: menú de modo y preview. Requiere GUI."""
    import FreeCADGui as Gui

    App.Console.PrintMessage("=" * 70)
    App.Console.PrintMessage("VDO CUTTING LIST - Exportador con Preview")
    App.Console.PrintMessage("=" * 70)
    if not App.ActiveDocument:
        App.Console.PrintMessage("No hay documento activo")
        return
    modo = mostrar_menu()
    if not modo:
        return
    App.Console.PrintMessage(f"\nModo seleccionado: {modo.upper()}")
    vdo_cutting_list_preview.main(modo=modo)
