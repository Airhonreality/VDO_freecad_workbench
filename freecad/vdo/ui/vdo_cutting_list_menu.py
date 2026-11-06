"""Menú de exportación de lista de corte (migrado de Macro/vdo_cutting_list.FCMacro).

Muestra el diálogo de modo (todo / selección / módulo) y, al confirmar, abre el preview
de piezas de melamina antes de exportar el CSV.
"""

import FreeCAD as App

from freecad.vdo.qt_compat import QtWidgets
from freecad.vdo.ui import vdo_cutting_list_preview
from freecad.vdo.ui import tema


def mostrar_menu():
    """Muestra diálogo para elegir modo de exportación"""

    dialog = QtWidgets.QDialog()
    dialog.setWindowTitle("📊 VDO - Exportar Lista de Corte")
    dialog.setMinimumWidth(400)

    layout = QtWidgets.QVBoxLayout()
    _agregar_titulo(layout)
    radio_todo, radio_seleccion, radio_grupo = _crear_opciones(layout)
    _agregar_info(layout)
    _agregar_botones(dialog, layout)

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


def _agregar_titulo(layout):
    # Título
    titulo = QtWidgets.QLabel("¿Qué piezas deseas exportar?")
    tema.aplicar_estilo(titulo, tema.ESTILO_TITULO_14PX)
    layout.addWidget(titulo)

    layout.addSpacing(10)


def _crear_opciones(layout):
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
    return radio_todo, radio_seleccion, radio_grupo


def _agregar_info(layout):
    # Info
    info = QtWidgets.QLabel(
        "ℹ️ Se exportarán SOLO paneles de melamina\n"
        "   (Se excluyen muros, paneles BIM, etc)\n\n"
        "El siguiente paso mostrará un PREVIEW\n"
        "con las piezas coloreadas en ROJO para confirmar"
    )
    tema.aplicar_estilo(info, tema.ESTILO_INFO_11PX)
    layout.addWidget(info)

    layout.addSpacing(15)


def _agregar_botones(dialog, layout):
    # Botones
    btn_layout = QtWidgets.QHBoxLayout()

    btn_cancelar = QtWidgets.QPushButton("Cancelar")
    btn_cancelar.clicked.connect(dialog.reject)
    btn_layout.addWidget(btn_cancelar)

    btn_ok = QtWidgets.QPushButton("Continuar →")
    tema.aplicar_estilo(btn_ok, tema.ESTILO_BOTON_AZUL)
    btn_ok.clicked.connect(dialog.accept)
    btn_layout.addWidget(btn_ok)

    layout.addLayout(btn_layout)


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
