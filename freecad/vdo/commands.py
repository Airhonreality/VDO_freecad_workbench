"""Comandos de FreeCAD del workbench VDO.

Cada comando es una clase con GetResources / IsActive / Activated (patrón Command de FreeCAD).
Sin lógica de negocio: delegan en core/ (motor) y ui/ (paneles y diálogos).
Sustituyen a los antiguos .FCMacro, que se cargaban leyendo el archivo y ejecutándolo.
Aquí cada comando llama directamente a funciones importadas: no se ejecuta ningún archivo.

Los imports pesados (core, ui, Qt) se hacen dentro de Activated(), así que importar este
módulo es barato y no carga GUI.
"""

import FreeCAD as App

from freecad.vdo.core.vdo_paths import ruta_icono


def _gui_activa():
    """True si FreeCAD tiene interfaz gráfica."""
    return bool(getattr(App, "GuiUp", False))


def _error_sin_gui(nombre):
    App.Console.PrintError(f"[VDO] «{nombre}» necesita la interfaz gráfica de FreeCAD.\n")


class _ComandoBase:
    """Base: recursos (texto e icono) y estado. Las subclases definen Activated()."""

    MENU = ""
    TOOLTIP = ""
    ICONO = "vdo_workbench.svg"

    def GetResources(self):
        return {
            "Pixmap": str(ruta_icono(self.ICONO)),
            "MenuText": self.MENU,
            "ToolTip": self.TOOLTIP,
        }

    def IsActive(self):
        return True


# ---------------------------------------------------------------------
# Creación de módulos paramétricos (flujo: crear oculto → panel → colocar con clic)
# ---------------------------------------------------------------------

class _ComandoCreacion(_ComandoBase):
    """Crea un módulo con crear_modulo_interactivo(module_key, configuracion)."""

    MODULE_KEY = None
    CONFIG = {}

    def Activated(self):
        # Entrada (commands.py) = composición: aquí se inyecta la interfaz en app/.
        from freecad.vdo.app.vdo_creacion import crear_modulo_interactivo
        # Sin GUI no hay panel ni colocación: el caso de uso confirma en el origen.
        interfaz = {}
        if _gui_activa():
            from freecad.vdo.ui.vdo_interfaz import abrir_panel, colocar
            interfaz = {"abrir_panel": abrir_panel, "colocar": colocar}
        crear_modulo_interactivo(self.MODULE_KEY, dict(self.CONFIG), **interfaz)


class CmdCrearHoja(_ComandoBase):
    MENU = "Crear Hoja"
    TOOLTIP = "Crear hoja de melamina (Params_Melamina y Params)"
    ICONO = "vdo_workbench.svg"

    def Activated(self):
        from freecad.vdo.app.puertos import crear_documento
        doc = crear_documento()
        from freecad.vdo.cad.vdo_guardian import vdo_guard
        vdo_guard(doc)
        App.Console.PrintMessage(
            "[VDO] Entorno listo: [Params_Melamina] y [Params] garantizados por el Guardián.\n")


class CmdPanelEstandar(_ComandoCreacion):
    MENU = "Panel Estándar"
    TOOLTIP = "Panel estándar paramétrico"
    ICONO = "vdo_panel_estandar.svg"
    MODULE_KEY = "panel_estandar"
    CONFIG = {
        "nombre": "Panel_Base",
        "etiqueta": "Panel Estándar",
        "orientacion": "horizontal",
        "cantos": {"norte": "FX", "sur": "FX", "este": "RIG", "oeste": "FX"},
        "material_ref": "melamina_standar",
    }


class CmdPanelFachada(_ComandoCreacion):
    MENU = "Panel Fachada"
    TOOLTIP = "Panel fachada paramétrico"
    ICONO = "vdo_panel_fachada.svg"
    MODULE_KEY = "panel_fachada"
    CONFIG = {
        "nombre": "Fachada_Principal",
        "etiqueta": "Fachada",
        "orientacion": "vertical",
        "cantos": {"norte": "RIG", "sur": "RIG", "este": "RIG", "oeste": "RIG"},
        "material_ref": "melamina_standar",
    }


class CmdCoco4C(_ComandoCreacion):
    MENU = "COCO 4C"
    TOOLTIP = "Cajón 4 caras paramétrico"
    ICONO = "vdo_coco.svg"
    MODULE_KEY = "coco_4c"
    CONFIG = {"nombre": "COCO_4C"}  # resto de valores: vdo_module_specs


class CmdPanelDivision(_ComandoCreacion):
    MENU = "Panel División"
    TOOLTIP = "Panel divisor vertical paramétrico"
    ICONO = "vdo_panel.svg"
    MODULE_KEY = "panel_division"
    CONFIG = {
        "nombre": "Division_1",
        "etiqueta": "División",
        "orientacion": "vertical",
        "cantos": {"norte": "FX", "sur": "FX", "este": "FX", "oeste": "FX"},
        "material_ref": "melamina_standar",
    }


class CmdZocalo(_ComandoCreacion):
    MENU = "Zócalo"
    TOOLTIP = "Zócalo paramétrico de base"
    ICONO = "vdo_zocalo.svg"
    MODULE_KEY = "zocalo"
    CONFIG = {"nombre": "Zocalo"}


class CmdPuerta(_ComandoCreacion):
    MENU = "Puerta"
    TOOLTIP = "Puerta paramétrica (batiente, parche)"
    ICONO = "vdo_puerta.svg"
    MODULE_KEY = "puerta"
    CONFIG = {
        "nombre": "Puerta",
        "tipo_sistema": "Batiente Vertical",
        "tipo_montaje": "Parche",
        "sentido_apertura": "Izquierda",
        "sistema_apertura": "Tirador Tradicional",
        "hardware_sku": "",
        "vdo_vano_id": "",
        "ancho": 400.0,
        "alto": 700.0,
        "espesor": 18,
        "pos_x": 0.0,
        "pos_y": 0.0,
        "pos_z": 0.0,
        "anclaje": "inferior_izquierda_frente",
    }

    def Activated(self):
        # Guarda de seguridad: cerrar un diálogo activo antes de crear (lo que hacía el antiguo macro).
        if _gui_activa():
            try:
                import FreeCADGui as Gui
                if hasattr(Gui.Control, "activeDialog") and Gui.Control.activeDialog():
                    Gui.Control.closeDialog()
            except Exception:
                App.Console.PrintWarning(
                    "[VDO] No se pudo cerrar el diálogo activo")
        super().Activated()


class CmdCajonOculta(_ComandoCreacion):
    MENU = "Cajón con corredera oculta"
    TOOLTIP = "Cajón con corredera oculta"
    ICONO = "vdo_cajon.svg"
    MODULE_KEY = "cajon_oculta"
    CONFIG = {"nombre": "Cajon_Oculta"}


# ---------------------------------------------------------------------
# Herramientas (requieren GUI)
# ---------------------------------------------------------------------

class CmdEditarVDO(_ComandoBase):
    MENU = "Propiedades VDO"
    TOOLTIP = "Abrir el panel del módulo VDO seleccionado"
    ICONO = "vdo_workbench.svg"

    def Activated(self):
        if not _gui_activa():
            return _error_sin_gui(self.MENU)
        import FreeCADGui as Gui

        from freecad.vdo.core.vdo_view_base import diagnostico_viewprovider
        from freecad.vdo.ui.vdo_view_providers import (
            abrir_panel_objeto,
            enfocar_inspector_universal,
        )
        seleccion = Gui.Selection.getSelection()
        if not seleccion:
            App.Console.PrintWarning("[VDO] Selecciona un módulo VDO en el árbol o en la vista 3D.\n")
            return
        for obj in seleccion:
            App.Console.PrintMessage(diagnostico_viewprovider(obj) + "\n")
        enfocar_inspector_universal(seleccion[0])
        abrir_panel_objeto(seleccion[0])


class CmdInspectorVDO(_ComandoBase):
    MENU = "Inspector VDO"
    TOOLTIP = "Mostrar / ocultar el Inspector Universal VDO lateral"
    ICONO = "vdo_workbench.svg"

    def Activated(self):
        if not _gui_activa():
            return _error_sin_gui(self.MENU)
        from freecad.vdo.ui.vdo_inspector_dock import obtener_o_crear_dock_inspector
        dock = obtener_o_crear_dock_inspector()
        if dock is not None:
            dock.setVisible(not dock.isVisible())
            if dock.isVisible():
                dock.raise_()


class CmdListaCorte(_ComandoBase):
    MENU = "Lista de corte"
    TOOLTIP = "Exportar lista de corte (CSV) con preview de piezas"
    ICONO = "vdo_herrajes.svg"

    def Activated(self):
        if not _gui_activa():
            return _error_sin_gui(self.MENU)
        from freecad.vdo.ui.vdo_cutting_list_menu import abrir_lista_corte
        abrir_lista_corte()


class CmdOptimizador(_ComandoBase):
    MENU = "Optimizador de corte"
    TOOLTIP = "Optimizador 2D de corte sobre tableros"
    ICONO = "vdo_panel.svg"

    def Activated(self):
        if not _gui_activa():
            return _error_sin_gui(self.MENU)
        from freecad.vdo.ui.vdo_optimizer_dialog import abrir_optimizador
        abrir_optimizador()


class CmdNesting(_ComandoBase):
    MENU = "Nesting"
    TOOLTIP = "Optimizador de corte automático (requiere Nesting Workbench)"
    ICONO = "vdo_panel.svg"

    def Activated(self):
        if not _gui_activa():
            return _error_sin_gui(self.MENU)
        try:
            from freecad.vdo.ui import vdo_nesting_workflow
        except ImportError as exc:
            App.Console.PrintError(f"[VDO] Nesting no disponible: {exc}\n")
            return
        vdo_nesting_workflow.main()


class CmdHerrajes(_ComandoBase):
    MENU = "Herrajes"
    TOOLTIP = "Catálogo de herrajes VDO"
    ICONO = "vdo_herrajes.svg"

    def Activated(self):
        if not _gui_activa():
            return _error_sin_gui(self.MENU)
        import FreeCADGui as Gui

        from freecad.vdo.ui.vdo_hardware_manager import VDOHardwareManagerDialog
        dlg = VDOHardwareManagerDialog(Gui.getMainWindow())
        dlg.exec()


# ---------------------------------------------------------------------
# Entrada al workbench (documento + vista 3D)
# ---------------------------------------------------------------------

NOMBRE_WORKBENCH = "VDOWorkbench"  # nombre con que FreeCAD registra la clase de InitGui.py
NOMBRE_DOCUMENTO = "VDO"


def asegurar_documento_activo():
    """Devuelve el documento activo; si no hay ninguno, crea uno.

    Sin documento, FreeCAD muestra la página de inicio en lugar de la vista 3D, así que
    activar el workbench desde el desplegable no mostraba el canvas. Esto lo corrige.
    """
    if App.ActiveDocument is None:
        return App.newDocument(NOMBRE_DOCUMENTO)
    return App.ActiveDocument


class CmdAbrirVDO(_ComandoBase):
    """Entrada única al workbench: crea un documento y activa VDO con su vista 3D.

    Es la entrada equivalente a una tarjeta de la página de inicio. Esa página de FreeCAD
    tiene las tarjetas codificadas en C++ y no admite tarjetas de terceros, así que la
    entrada se ofrece en el menú Archivo de BIM (ver freecad/vdo/ui/vdo_bim_bridge.py).
    """
    MENU = "Nuevo proyecto VDO"
    TOOLTIP = "Crea un documento y abre el workbench VDO con su vista 3D"
    ICONO = "vdo_workbench.svg"

    def Activated(self):
        asegurar_documento_activo()
        if _gui_activa():
            import FreeCADGui as Gui
            Gui.activateWorkbench(NOMBRE_WORKBENCH)


# ---------------------------------------------------------------------
# Registro
# ---------------------------------------------------------------------

# Identificador de comando → clase. El identificador es el que usa FreeCAD en barras y menús.
COMANDOS = {
    "VDO_CrearHoja": CmdCrearHoja,
    "VDO_PanelEstandar": CmdPanelEstandar,
    "VDO_PanelFachada": CmdPanelFachada,
    "VDO_Coco4C": CmdCoco4C,
    "VDO_PanelDivision": CmdPanelDivision,
    "VDO_Zocalo": CmdZocalo,
    "VDO_Puerta": CmdPuerta,
    "VDO_CajonOculta": CmdCajonOculta,
    "VDO_Editar": CmdEditarVDO,
    "VDO_Inspector": CmdInspectorVDO,
    "VDO_ListaCorte": CmdListaCorte,
    "VDO_Optimizador": CmdOptimizador,
    "VDO_Nesting": CmdNesting,
    "VDO_Herrajes": CmdHerrajes,
    "VDO_AbrirVDO": CmdAbrirVDO,
}

# Barras del workbench: nombre de barra → comandos en orden.
BARRAS = {
    "VDO · Creación": [
        "VDO_CrearHoja", "VDO_PanelEstandar", "VDO_PanelFachada", "VDO_Coco4C",
        "VDO_PanelDivision", "VDO_Zocalo", "VDO_Puerta", "VDO_CajonOculta",
    ],
    "VDO · Herramientas": [
        "VDO_Editar", "VDO_Inspector", "VDO_ListaCorte", "VDO_Optimizador",
        "VDO_Nesting", "VDO_Herrajes",
    ],
}


def register_all():
    """Registra todos los comandos en FreeCAD. Requiere GUI (Gui.addCommand)."""
    import FreeCADGui as Gui
    for nombre, clase in COMANDOS.items():
        Gui.addCommand(nombre, clase())
    return list(COMANDOS)
