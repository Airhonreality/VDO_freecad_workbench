# -*- coding: utf-8 -*-
"""Fase visual del workbench VDO.

FreeCAD ejecuta este archivo solo cuando hay interfaz gráfica (FreeCAD.GuiUp).
Aquí solo se declara la clase del workbench; el trabajo pesado se hace en
Initialize(), la primera vez que el usuario activa el workbench (carga diferida).
"""

import os
import sys

import FreeCADGui as Gui


def _module_dir():
    """Devuelve la carpeta raíz del módulo VDO.

    FreeCAD ejecuta InitGui.py sin la variable __file__; en ese caso buscamos la
    carpeta que está en sys.path y contiene el package.xml de VDO.
    """
    try:
        return os.path.dirname(os.path.abspath(__file__))
    except NameError:
        for entrada in sys.path:
            manifiesto = os.path.join(entrada, "package.xml")
            if os.path.isfile(manifiesto) and "<name>VDO</name>" in open(manifiesto, encoding="utf-8").read():
                return os.path.abspath(entrada)
        raise RuntimeError("No se encontró la carpeta del módulo VDO en sys.path")


_MODULE_DIR = _module_dir()
_ICON = os.path.join(_MODULE_DIR, "Resources", "icons", "vdo_workbench.svg")


def _registrar_gui():
    """Registra comandos e integración BIM al cargar la GUI (no al activar el workbench).

    Los comandos deben existir antes de que BIM monte sus menús: por eso se registran aquí
    y no en Initialize(). Los imports son ligeros; el motor y la UI se cargan al usarlos.
    """
    from freecad.vdo.commands import register_all
    from freecad.vdo.ui.bim_bridge import registrar_integracion_bim
    from freecad.vdo.ui.registro import registrar_piezas

    registrar_piezas()  # piezas de interfaz para el motor (D24)
    register_all()
    registrar_integracion_bim()


class VDOWorkbench(Gui.Workbench):
    """Workbench VDO: muebles paramétricos."""

    MenuText = "VDO"
    ToolTip = "Muebles paramétricos VDO"

    def Initialize(self):
        """Se ejecuta una vez, al activar el workbench por primera vez: barras y menú."""
        from freecad.vdo.commands import BARRAS

        for barra, comandos in BARRAS.items():
            self.appendToolbar(barra, comandos)
        self.appendMenu("VDO", [c for comandos in BARRAS.values() for c in comandos])

    def Activated(self):
        """Asegura documento y vista 3D, y muestra el Inspector Universal lateral."""
        try:
            from freecad.vdo.commands import asegurar_documento_activo
            asegurar_documento_activo()
        except Exception as exc:
            import FreeCAD
            FreeCAD.Console.PrintWarning(f"[VDO] No se pudo crear el documento: {exc}\n")
        try:
            from freecad.vdo.ui.plano_cero import mostrar_plano_cero
            mostrar_plano_cero()
        except Exception as exc:
            import FreeCAD
            FreeCAD.Console.PrintWarning(f"[VDO] Malla del plano 0 no disponible: {exc}\n")
        try:
            from freecad.vdo.ui.inspector_dock import obtener_o_crear_dock_inspector
            dock = obtener_o_crear_dock_inspector()
            if dock is not None:
                dock.show()
                dock.raise_()
        except Exception as exc:  # no bloquear la activación del workbench
            import FreeCAD
            FreeCAD.Console.PrintWarning(f"[VDO] Aviso al activar el Inspector: {exc}\n")

    def Deactivated(self):
        pass

    def GetClassName(self):
        return "Gui::PythonWorkbench"


# El icono se asigna en la instancia (no en el cuerpo de la clase): FreeCAD ejecuta
# este archivo en un espacio de nombres donde la clase no ve las variables del módulo.
try:
    _registrar_gui()
except Exception as exc:  # si falla el registro, el workbench igual debe aparecer
    import FreeCAD
    FreeCAD.Console.PrintError(f"[VDO] Error al registrar comandos: {exc}\n")

_workbench = VDOWorkbench()
_workbench.Icon = _ICON
Gui.addWorkbench(_workbench)
