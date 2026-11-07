# =====================================================================
# zocalo.py
# Aplicación FreeCAD del zócalo: ZocaloFeature (Part::FeaturePython)
# y make_zocalo. El cálculo vive en core/zocalo_core.py.
# =====================================================================

import json
from typing import Any

from freecad.vdo.cad.propiedades import add_common_props, rotacion_z
from freecad.vdo.core import defaults as VDO_D
from freecad.vdo.core import module_props as VDO_MOD
from freecad.vdo.core.helpers import _get_app, _get_part
from freecad.vdo.core.zocalo_core import calcular_geometria_zocalo
from freecad.vdo.datos.valores import MELAMINA_ESTANDAR


class ZocaloFeature:
    """FeaturePython que genera la geometría de un zócalo."""

    def __init__(self, obj: Any) -> None:  # objeto FreeCAD, sin tipo estatico
        obj.addProperty("App::PropertyLength", "Ancho", "Dimensiones",
                        "Ancho total del mueble (mm)").Ancho = 600.0
        obj.addProperty("App::PropertyLength", "Fondo", "Dimensiones",
                        "Fondo total del mueble (mm)").Fondo = 580.0
        obj.addProperty("App::PropertyLength", "AltoZocalo", "Dimensiones",
                        "Alto del zócalo (mm)").AltoZocalo = 100.0
        obj.addProperty("App::PropertyLength", "EspesorTablero", "Dimensiones",
                        "Espesor del tablero del zócalo (mm)"
                        ).EspesorTablero = VDO_D.ESPESOR_DEFAULT

        obj.addProperty("App::PropertyLength", "DistanciaFrente", "Separación",
                        "Distancia desde el frente del mueble (mm)"
                        ).DistanciaFrente = 50.0
        obj.addProperty("App::PropertyLength", "DistanciaCostados",
                        "Separación",
                        "Distancia desde los costados (mm)"
                        ).DistanciaCostados = 0.0
        obj.addProperty("App::PropertyLength", "DistanciaTrasera", "Separación",
                        "Distancia desde el fondo del mueble (mm)"
                        ).DistanciaTrasera = 20.0
        obj.addProperty("App::PropertyBool", "TieneTrasera", "Estructura",
                        "Cierra el cajón del zócalo por detrás"
                        ).TieneTrasera = True
        obj.addProperty("App::PropertyInteger", "AmarresIntermedios",
                        "Estructura",
                        "Costillas de refuerzo entre frente y trasera"
                        ).AmarresIntermedios = 0

        obj.addProperty("App::PropertyString", "VDO_Tipo", "VDO",
                        "Tipo de objeto").VDO_Tipo = "contenedor"
        obj.addProperty("App::PropertyString", "VDO_Subtipo", "VDO",
                        "Subtipo").VDO_Subtipo = "zocalo"
        obj.addProperty("App::PropertyString", "VDO_Material_Ref", "VDO",
                        "Material de las piezas"
                        ).VDO_Material_Ref = MELAMINA_ESTANDAR
        obj.addProperty("App::PropertyString", "VDO_Paneles_JSON", "VDO",
                        "Descripción JSON de las piezas del zócalo")
        obj.addProperty("App::PropertyString", "VDO_ResumenDespiece", "VDO",
                        "Resumen legible del despiece (solo lectura)")

        add_common_props(obj)

        obj.Proxy = self

    def _config(self, fp: Any) -> dict[str, Any]:  # fp: objeto FreeCAD, sin tipo estatico
        return {
            "ancho": float(fp.Ancho),
            "fondo": float(fp.Fondo),
            "alto_zocalo": float(fp.AltoZocalo),
            "espesor_tablero": float(fp.EspesorTablero),
            "distancia_frente": float(fp.DistanciaFrente),
            "distancia_costados": float(fp.DistanciaCostados),
            "distancia_trasera": float(fp.DistanciaTrasera),
            "tiene_trasera": bool(fp.TieneTrasera),
            "amarres_intermedios": int(fp.AmarresIntermedios),
            "material_ref": fp.VDO_Material_Ref,
        }

    def execute(self, fp: Any) -> None:  # fp: objeto FreeCAD, sin tipo estatico
        try:
            geo = calcular_geometria_zocalo(**self._config(fp))
        except ValueError as exc:
            _get_app().Console.PrintError(f"[VDO] Zócalo inválido: {exc}\n")
            fp.Shape = _get_part().Shape()
            fp.VDO_Paneles_JSON = "[]"
            fp.VDO_ResumenDespiece = f"Zócalo inválido: {exc}"
            return

        alto = float(fp.AltoZocalo)
        solidos: list[Any] = []  # solidos FreeCAD, sin tipo estatico
        for tira in geo["tiras"]:
            solidos.append(_get_part().makeBox(
                tira["w"], tira["h"], alto,
                _get_app().Vector(tira["x"], tira["y"], 0.0)))
        for amarre in geo["amarres"]:
            solidos.append(_get_part().makeBox(
                amarre["w"], amarre["h"], alto,
                _get_app().Vector(amarre["x"], amarre["y"], 0.0)))

        fp.Shape = _get_part().makeCompound(solidos)

        piezas: list[dict[str, Any]] = []
        for pieza in geo["piezas"]:
            dato = dict(pieza)
            dato["grupo"] = fp.Label
            dato["material_ref"] = fp.VDO_Material_Ref
            piezas.append(dato)
        fp.VDO_Paneles_JSON = json.dumps(piezas, ensure_ascii=False)
        fp.VDO_ResumenDespiece = geo["resumen"]

    def dumps(self) -> None:
        return None

    def loads(self, state: Any) -> None:  # estado de FreeCAD, sin tipo estatico
        return None


# doc y retorno: objetos FreeCAD, sin tipo estatico
def make_zocalo(doc: Any, configuracion: dict[str, Any]) -> Any | None:
    """Crea un zócalo paramétrico (FeaturePython).

    Args:
        doc: Documento de FreeCAD activo (proporcionado por app/cad, no
             buscado desde core).
        configuracion (dict): claves ancho, fondo, alto_zocalo,
            espesor_tablero, distancia_frente, distancia_costados,
            distancia_trasera, tiene_trasera, amarres_intermedios,
            material_ref, rotacion/anclaje/nombre.

    Returns:
        _get_app().DocumentObject: el objeto creado o None.
    """
    if doc is None:
        _get_app().Console.PrintError("[VDO] No hay documento activo.\n")
        return None

    nombre = configuracion.get("nombre", "Zocalo")
    obj = doc.addObject("Part::FeaturePython", nombre)
    ZocaloFeature(obj)

    if _get_app().GuiUp:
        # La vista se adjunta desde app/ (F5/F6), no desde core.
        pass

    obj.Ancho = configuracion.get("ancho", 600.0)
    obj.Fondo = configuracion.get("fondo", 580.0)
    obj.AltoZocalo = configuracion.get("alto_zocalo", 100.0)
    obj.EspesorTablero = configuracion.get(
        "espesor_tablero", VDO_D.ESPESOR_DEFAULT)
    obj.DistanciaFrente = configuracion.get("distancia_frente", 50.0)
    obj.DistanciaCostados = configuracion.get("distancia_costados", 0.0)
    obj.DistanciaTrasera = configuracion.get("distancia_trasera", 20.0)
    obj.TieneTrasera = configuracion.get("tiene_trasera", True)
    obj.AmarresIntermedios = configuracion.get("amarres_intermedios", 0)
    obj.VDO_Material_Ref = configuracion.get(
        "material_ref", MELAMINA_ESTANDAR)

    rotacion = float(configuracion.get("rotacion", 0.0))
    obj.VDO_RotacionZ = rotacion
    obj.VDO_Anclaje = configuracion.get(
        "anclaje", VDO_MOD.ANCLAJE_DEFAULT)
    if rotacion:
        obj.Placement = _get_app().Placement(
            obj.Placement.Base, rotacion_z(rotacion))

    doc.recompute()
    _get_app().Console.PrintMessage(
        f"[VDO] Zócalo '{nombre}' creado "
        f"({float(obj.Ancho):.0f} × {float(obj.Fondo):.0f} × "  # noqa: RUF001 - etiqueta de interfaz: signo tipografico visible (x o -) que el usuario ve; cambiarlo altera el texto
        f"{float(obj.AltoZocalo):.0f} mm).\n")
    return obj
