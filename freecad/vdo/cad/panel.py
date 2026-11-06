# =====================================================================
# panel.py
# Capa cad: escritura FreeCAD del panel (PanelFeature, crear_pieza y
# expresiones de propiedades). El cálculo vive en core/panel_core.py.
# =====================================================================

from typing import Any

from freecad.vdo.cad.geometria import forma_ref
from freecad.vdo.cad.propiedades import add_common_props
from freecad.vdo.core import defaults as VDO_D
from freecad.vdo.core import module_props as VDO_MOD
from freecad.vdo.core import reengrose_geometria as VDO_RE_GEOMETRIA
from freecad.vdo.core import reengrose_modelo as VDO_RE_MODELO
from freecad.vdo.core import reengrose_modificador as VDO_RE_MODIFICADOR
from freecad.vdo.core.finish import CANTOS_VALIDOS
from freecad.vdo.core.helpers import _get_app, _get_part, rotacion_z
from freecad.vdo.core.panel_core import (
    _validar_orientacion,
    expresiones_orientacion,
)
from freecad.vdo.datos.valores import MELAMINA_ESTANDAR

# (nombre, tipo, descripción, valor por defecto, opciones o None)
_PROPS_REENGROSE = (
    ("VDO_Reengrose_Activo", "App::PropertyBool",
     "Activa una tira o duplicado de refuerzo sobre el panel", False, None),
    ("VDO_Reengrose_Orientacion", "App::PropertyEnumeration",
     "Paralela al largo del panel o transversal cruzando el ancho",
     "paralela", VDO_RE_MODELO.ORIENTACIONES),
    ("VDO_Reengrose_Ancho", "App::PropertyLength",
     "Ancho de la tira de refuerzo en mm", 70.0, None),
    ("VDO_Reengrose_Espesor", "App::PropertyLength",
     "Espesor de la tira; 0 usa el espesor del panel base", 0.0, None),
    ("VDO_Reengrose_Cara", "App::PropertyEnumeration",
     "Cara del tablero donde se adhiere el refuerzo",
     "cara_a", VDO_RE_MODELO.CARAS),
    ("VDO_Reengrose_Alineacion", "App::PropertyEnumeration",
     "Posicion de la tira hacia el frente, centro o fondo",
     "frente", VDO_RE_MODELO.ALINEACIONES),
    ("VDO_Reengrose_Modo", "App::PropertyEnumeration",
     "Tira independiente o pacha encolada y canteada en bloque",
     "pacha", VDO_RE_MODELO.MODOS),
    ("VDO_Reengrose_Alcance", "App::PropertyEnumeration",
     "Pacha parcial en tira o pacha total de toda la cara",
     "parcial", VDO_RE_MODELO.ALCANCES),
    ("VDO_Reengrose_PoliticaRepisa", "App::PropertyEnumeration",
     "Ante colision con repisa: retroceder o mochear en escuadra",
     "retroceder", VDO_RE_MODELO.POLITICAS_REPISA),
    ("VDO_Reengrose_PrioridadEncuentro", "App::PropertyEnumeration",
     "Prioridad al cruzar tiras: vertical, horizontal o inglete 45",
     "vertical_domina", VDO_RE_MODELO.PRIORIDADES_ENCUENTRO),
    ("VDO_Reengrose_ChoqueNucleo", "App::PropertyEnumeration",
     "Choque contra panel nucleo: retroceso, mocheo o interrumpir tira",
     "retroceso", VDO_RE_MODELO.MODOS_CHOQUE_NUCLEO),
    ("VDO_Reengrose_JSON", "App::PropertyString",
     "Instantanea JSON del modificador de reengrose", "", None),
)


def add_reengrose_props(obj: Any) -> None:
    """Anade las propiedades del motor de reengrose a un panel L1."""
    for nombre, tipo, descripcion, defecto, opciones in _PROPS_REENGROSE:
        if hasattr(obj, nombre):
            continue
        prop = obj.addProperty(tipo, nombre, "Reengrose", descripcion)
        if opciones is not None:
            setattr(prop, nombre, list(opciones))
        setattr(obj, nombre, defecto)


def _limpiar_expresion(obj: Any, prop: str) -> None:
    """Limpia la expresión de una propiedad si existe."""
    obj.clearExpression(prop)


def aplicar_mapeo_orientacion(obj: Any, orientacion: str) -> None:
    """Aplica las expresiones de Params según la orientación.

    `Largo`/`Ancho` son siempre las caras del tablero y `Espesor` su grosor
    (semántica de despiece), NO los ejes locales de la caja. El mapeo lo
    calcula core/panel_core.expresiones_orientacion.
    """
    param_largo, param_ancho, param_espesor = expresiones_orientacion(orientacion)

    _limpiar_expresion(obj, "Largo")
    _limpiar_expresion(obj, "Ancho")
    _limpiar_expresion(obj, "Espesor")
    obj.setExpression("Largo", f"<<Params>>.{param_largo}")
    obj.setExpression("Ancho", f"<<Params>>.{param_ancho}")
    obj.setExpression("Espesor", f"<<Params>>.{param_espesor}")


class PanelFeature:
    """FeaturePython que genera la geometría de un tablero VDO."""

    def __init__(self, obj: Any) -> None:
        obj.addProperty(
            "App::PropertyLength", "Largo", "Dimensiones",
            "Largo del tablero (mm)").Largo = VDO_D.ANCHO_DEFAULT
        obj.addProperty(
            "App::PropertyLength", "Ancho", "Dimensiones",
            "Ancho del tablero (mm)").Ancho = VDO_D.FONDO_DEFAULT
        obj.addProperty(
            "App::PropertyLength", "Espesor", "Dimensiones",
            "Espesor del tablero (mm)").Espesor = VDO_D.ESPESOR_DEFAULT

        obj.addProperty(
            "App::PropertyString", "VDO_Tipo", "VDO",
            "Tipo de objeto").VDO_Tipo = "panel"

        prop_orient = obj.addProperty(
            "App::PropertyEnumeration", "VDO_Orientacion", "VDO",
            "Orientación del panel")
        prop_orient.VDO_Orientacion = VDO_D.ORIENTACIONES_VALIDAS
        if VDO_D.ORIENTACIONES_VALIDAS:
            obj.VDO_Orientacion = VDO_D.ORIENTACION_DEFAULT

        obj.addProperty(
            "App::PropertyString", "VDO_Etiqueta", "VDO",
            "Etiqueta libre de la pieza").VDO_Etiqueta = "Panel"

        obj.addProperty(
            "App::PropertyString", "VDO_Material_Ref", "VDO",
            "Material de la pieza"
        ).VDO_Material_Ref = MELAMINA_ESTANDAR

        for direccion in ["Norte", "Sur", "Este", "Oeste"]:
            prop_name = f"VDO_Canto_{direccion}"
            obj.addProperty(
                "App::PropertyEnumeration", prop_name, "Cantos",
                f"Canto {direccion}")
            setattr(obj, prop_name, list(CANTOS_VALIDOS))
            setattr(obj, prop_name, "FX")

        add_reengrose_props(obj)
        add_common_props(obj)

        obj.Proxy = self

    def execute(self, fp: Any) -> None:
        largo = float(fp.Largo)
        ancho = float(fp.Ancho)
        espesor = float(fp.Espesor)
        if largo <= 0 or ancho <= 0 or espesor <= 0:
            fp.Shape = _get_part().Shape()
            return

        base = _get_part().makeBox(largo, ancho, espesor)
        mod = VDO_RE_MODIFICADOR.desde_objeto(fp)
        if hasattr(fp, "VDO_Reengrose_JSON"):
            fp.VDO_Reengrose_JSON = mod.to_json()
        if not mod.activo:
            fp.Shape = base
            return
        geo = VDO_RE_GEOMETRIA.calcular_geometria_reengrose(
            {"nombre": fp.Label or fp.Name,
             "largo": largo, "ancho": ancho, "espesor": espesor},
            mod)
        shapes = [base]
        for pieza in geo["refuerzos"]:
            forma = forma_ref(pieza)
            if forma is not None:
                shapes.append(forma)
        fp.Shape = _get_part().makeCompound(shapes)

    def dumps(self) -> None:
        return None

    def loads(self, state: Any) -> None:
        return None


def _obtener_o_crear_panel(doc: Any, nombre: str) -> tuple[Any, bool]:
    """Devuelve (panel, es_nuevo): reutiliza un panel VDO existente o crea uno."""
    panel = doc.getObject(nombre)
    if panel is not None and not isinstance(
            getattr(panel, "Proxy", None), PanelFeature):
        if panel.TypeId != "Part::Box":
            raise ValueError(
                f"Ya existe un objeto '{nombre}' ({panel.TypeId}) que no es "
                "un panel VDO. Usa otro nombre.")
        # Migración: un Part::Box viejo no puede tener ViewProvider Python.
        doc.removeObject(panel.Name)
        panel = None

    if panel:
        _get_app().Console.PrintMessage(f"⚠️ '{nombre}' ya existe. Actualizando...")
        add_reengrose_props(panel)
        return panel, False
    panel = doc.addObject("Part::FeaturePython", nombre)
    PanelFeature(panel)
    return panel, True


def _aplicar_cantos(panel: Any, cantos: dict[str, str]) -> None:
    """Valida y asigna los cuatro cantos (Norte, Sur, Este, Oeste)."""
    for direccion in ["Norte", "Sur", "Este", "Oeste"]:
        prop_name = f"VDO_Canto_{direccion}"
        canto_value = cantos.get(direccion.lower(), "FX")
        if canto_value not in CANTOS_VALIDOS:
            raise ValueError(
                f"Canto inválido en '{direccion}': '{canto_value}'. "
                f"Debe ser uno de: {', '.join(CANTOS_VALIDOS)}.")
        setattr(panel, prop_name, canto_value)


def _aplicar_dimensiones(panel: Any, configuracion: dict[str, Any], orientacion: str) -> None:
    """Dimensiones por expresiones de Params o por valores explícitos."""
    usar_params = configuracion.get(
        "usar_params",
        not any(k in configuracion for k in ("largo", "ancho", "espesor")))
    if usar_params:
        aplicar_mapeo_orientacion(panel, orientacion)
        return
    for prop in ("Largo", "Ancho", "Espesor"):
        _limpiar_expresion(panel, prop)
    if "largo" in configuracion:
        panel.Largo = configuracion["largo"]
    if "ancho" in configuracion:
        panel.Ancho = configuracion["ancho"]
    if "espesor" in configuracion:
        panel.Espesor = configuracion["espesor"]


def _aplicar_rotacion_anclaje(panel: Any, configuracion: dict[str, Any], es_nuevo: bool) -> None:
    """Rotación Z, anclaje y Placement del panel."""
    rotacion = float(configuracion.get("rotacion", 0.0))
    panel.VDO_RotacionZ = rotacion
    panel.VDO_Anclaje = configuracion.get(
        "anclaje", VDO_MOD.ANCLAJE_DEFAULT)

    if rotacion:
        panel.Placement = _get_app().Placement(
            panel.Placement.Base, rotacion_z(rotacion))
    elif es_nuevo:
        panel.Placement = _get_app().Placement()


def crear_pieza(doc: Any, configuracion: dict[str, Any]) -> Any | None:
    """Función principal del motor de paneles (agnóstica de semántica).

    Args:
        doc: Documento de FreeCAD activo (proporcionado por app/cad, no
             buscado desde core).
        configuracion (dict): {
            "nombre": str,
            "etiqueta": str,      # tag libre, NO dirige geometría
            "orientacion": "horizontal" | "vertical",   # OBLIGATORIO
            "cantos": {"norte": str, "sur": str, "este": str, "oeste": str},
            "material_ref": str,  # opcional
            "largo"/"ancho"/"espesor": float,  # opcional
            "usar_params": bool,  # opcional (default True)
            "rotacion": float, "anclaje": str  # opcionales
        }

    Returns:
        _get_app().DocumentObject: El panel FeaturePython creado.
    """
    orientacion = _validar_orientacion(configuracion)

    if doc is None:
        _get_app().Console.PrintMessage("❌ [VDO Error] No hay documento activo.")
        return None

    nombre = configuracion.get("nombre", "Panel")
    cantos = configuracion.get("cantos", {})
    etiqueta = configuracion.get("etiqueta", nombre)
    material_ref = configuracion.get(
        "material_ref", MELAMINA_ESTANDAR)

    panel, es_nuevo = _obtener_o_crear_panel(doc, nombre)

    if _get_app().GuiUp:
        # La vista se adjunta desde app/ (F5/F6), no desde core.
        pass

    panel.VDO_Orientacion = orientacion
    panel.VDO_Etiqueta = etiqueta
    panel.VDO_Material_Ref = material_ref
    _aplicar_cantos(panel, cantos)
    _aplicar_dimensiones(panel, configuracion, orientacion)

    if "reengrose" in configuracion:
        VDO_RE_MODIFICADOR.aplicar_a_objeto(panel, configuracion.get("reengrose"))

    _aplicar_rotacion_anclaje(panel, configuracion, es_nuevo)

    doc.recompute()
    _get_app().Console.PrintMessage(f"✅ Panel '{nombre}' configurado: orientacion='{orientacion}'")
    return panel
