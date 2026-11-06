# =====================================================================
# coco.py
# Capa cad: CocoFeature (Part::FeaturePython), make_coco y el recorte
# de formas. El cálculo de piezas vive en core/vdo_coco_core.py.
# =====================================================================

import json

from freecad.vdo.cad.coco_divisiones import aplicar_divisiones
from freecad.vdo.cad.coco_shell import (
    aplicar_carcasa,
    preparar_carcasa,
)
from freecad.vdo.cad.coco_carcasa import (
    caja_fondo,
    cajas_carcasa,
    leer_parametros,
)
from freecad.vdo.cad.coco_cortes import (
    cortar_shells_contra_nucleos,
    resolver_tiras_divisiones,
)
from freecad.vdo.cad.propiedades import add_common_props
from freecad.vdo.core import vdo_defaults as VDO_D
from freecad.vdo.core import vdo_finish as VDO_FINISH
from freecad.vdo.core import vdo_frames as VDO_FR
from freecad.vdo.core import vdo_module_props as VDO_MOD
from freecad.vdo.core.vdo_helpers import _get_app, _get_part, rotacion_z
from freecad.vdo.datos.valores import MELAMINA_ESTANDAR
from freecad.vdo.core.vdo_coco_core import (
    _expandir_reengrose,
)


class CocoFeature:
    """FeaturePython que genera la geometría de un cofre COCO."""

    def __init__(self, obj):
        obj.addProperty("App::PropertyLength", "Alto", "Dimensiones",
                        "Alto total del módulo (mm)").Alto = VDO_D.ALTO_DEFAULT
        obj.addProperty("App::PropertyLength", "Ancho", "Dimensiones",
                        "Ancho total del módulo (mm)").Ancho = VDO_D.ANCHO_DEFAULT
        obj.addProperty("App::PropertyLength", "FondoModulo", "Dimensiones",
                        "Profundidad total del módulo (mm)").FondoModulo = VDO_D.FONDO_DEFAULT
        obj.addProperty("App::PropertyInteger", "Espesor", "Dimensiones",
                        "Espesor del tablero (mm)").Espesor = VDO_D.ESPESOR_DEFAULT
        obj.addProperty("App::PropertyBool", "TieneFondo", "Estructura",
                        "Habilitar fondo/respaldo").TieneFondo = VDO_D.FONDO_HABILITADO
        obj.addProperty("App::PropertyInteger", "CalibreFondo", "Estructura",
                        "Espesor del fondo (mm)").CalibreFondo = VDO_D.FONDO_CALIBRE
        obj.addProperty("App::PropertyFloat", "ProfundidadRanura", "Estructura",
                        "Profundidad de ranura para fondo (mm)").ProfundidadRanura = VDO_D.FONDO_PROFUNDIDAD_RANURA
        obj.addProperty("App::PropertyFloat", "DistanciaBorde", "Estructura",
                        "Distancia del borde para fondo grueso (mm)").DistanciaBorde = VDO_D.FONDO_DISTANCIA_BORDE
        obj.addProperty("App::PropertyEnumeration", "Tapa", "Estructura",
                        "Configuración de la tapa").Tapa = ["externo", "interno"]
        obj.addProperty("App::PropertyEnumeration", "Base", "Estructura",
                        "Configuración de la base").Base = ["externo", "interno"]
        obj.addProperty("App::PropertyString", "VDO_Divisiones", "Divisiones",
                        "Matriz de vanos v2 (JSON)").VDO_Divisiones = ""
        obj.addProperty("App::PropertyString", "VDO_Reengrose_JSON", "Reengrose",
                        "Modificadores de reengrose por pieza (JSON)").VDO_Reengrose_JSON = "{}"
        obj.addProperty("App::PropertyString", "ResumenEspacios", "Divisiones",
                        "Resumen legible de espacios calculados (solo lectura)")

        # === PROPIEDADES DE EXPORTACIÓN (para cutting list) ===
        obj.addProperty("App::PropertyString", "VDO_Tipo", "VDO",
                        "Tipo de objeto").VDO_Tipo = "contenedor"
        obj.addProperty("App::PropertyString", "VDO_Subtipo", "VDO",
                        "Subtipo (COCO, módulo, etc)").VDO_Subtipo = "COCO_4C"
        obj.addProperty("App::PropertyString", "VDO_Material_Ref", "VDO",
                        "Material de los paneles").VDO_Material_Ref = MELAMINA_ESTANDAR

        # Paneles internos (propiedades de lectura para exportación)
        obj.addProperty("App::PropertyString", "VDO_Paneles_JSON", "VDO",
                        "Descripción JSON de los paneles internos")

        # Lista de insertos contenidos (puertas, cajones) para DAG limpio.
        obj.addProperty("App::PropertyLinkList", "Hijos", "VDO",
                        "Insertos contenidos (puertas, cajones)").Hijos = []

        # Pose común VDO (rotación + anclaje). No altera la geometría.
        add_common_props(obj)

        obj.Proxy = self

    def execute(self, fp):
        """Reconstruir la geometría del cofre."""

        (alto, ancho, fondo, espesor, tapa, base, tiene_fondo,
         calibre_fondo, prof_ranura, dist_borde) = leer_parametros(fp)

        boxes = []

        (lat_height, base_length, base_pos_x, base_pos_z, techo_length,
         techo_pos_x, techo_pos_z, lat_izq, lat_der, panel_base,
         panel_techo) = cajas_carcasa(alto, ancho, fondo, espesor, tapa, base)
        (lat_izq, lat_der, panel_base, panel_techo, fondo_box,
         fondo_es_delgado, f_len, f_alt, f_x, f_y, f_z) = caja_fondo(
            alto, ancho, fondo, espesor, tiene_fondo, calibre_fondo,
            prof_ranura, dist_borde, lat_izq, lat_der, panel_base,
            panel_techo, boxes)

        (reengroses, obstaculos, shell_tiras, shell_info, shell_refs,
         shell_cores) = preparar_carcasa(
            fp, lat_izq, lat_der, panel_base, panel_techo, fondo_box)
        aplicar_carcasa(
            fp, espesor, ancho, alto, fondo, base_pos_x, base_length,
            base_pos_z, techo_pos_x, techo_length, techo_pos_z, tiene_fondo,
            f_x, f_y, f_z, f_len, calibre_fondo, f_alt, reengroses,
            obstaculos, shell_tiras, shell_info, shell_refs, boxes)

        divs, divisiones_piezas, resuelto, indice_divs = aplicar_divisiones(
            fp, alto, ancho, espesor, fondo, tiene_fondo, f_y, reengroses,
            obstaculos, boxes)

        division_tiras = resolver_tiras_divisiones(
            resuelto, shell_tiras, divisiones_piezas, divs, boxes,
            indice_divs)
        cortar_shells_contra_nucleos(
            division_tiras, shell_refs, shell_cores, divs, boxes)

        # === GUARDAR DATOS DE LOS PANELES PARA EXPORTACIÓN ===
        # Convención: largo/ancho = caras del tablero, espesor = grosor.
        import json
        lados_vistos, lados_apoyados = VDO_FR.cargar_exposicion(fp)
        paneles_data = [
            {
                "nombre": f"{fp.Label}_Lateral_Izq",
                "tipo": "panel",
                "rol": "lateral_izquierdo",
                "largo": fondo,
                "ancho": lat_height,
                "espesor": espesor,
                "orientacion": "vertical",
                "cantidad": 1,
                "material_ref": fp.VDO_Material_Ref
            },
            {
                "nombre": f"{fp.Label}_Lateral_Der",
                "tipo": "panel",
                "rol": "lateral_derecho",
                "largo": fondo,
                "ancho": lat_height,
                "espesor": espesor,
                "orientacion": "vertical",
                "cantidad": 1,
                "material_ref": fp.VDO_Material_Ref
            },
            {
                "nombre": f"{fp.Label}_Base",
                "tipo": "panel",
                "rol": "base",
                "largo": base_length,
                "ancho": fondo,
                "espesor": espesor,
                "orientacion": "horizontal",
                "cantidad": 1,
                "material_ref": fp.VDO_Material_Ref
            },
            {
                "nombre": f"{fp.Label}_Techo",
                "tipo": "panel",
                "rol": "techo",
                "largo": techo_length,
                "ancho": fondo,
                "espesor": espesor,
                "orientacion": "horizontal",
                "cantidad": 1,
                "material_ref": fp.VDO_Material_Ref
            }
        ]

        if tiene_fondo:
            paneles_data.append({
                "nombre": f"{fp.Label}_Fondo",
                "tipo": "panel",
                "rol": "fondo",
                "largo": f_len,
                "ancho": f_alt,
                "espesor": calibre_fondo,
                "orientacion": "vertical",
                "cantidad": 1,
                "material_ref": fp.VDO_Material_Ref,
                "fondo_delgado": fondo_es_delgado
            })

        for pz in divisiones_piezas:
            pz["nombre"] = f"{fp.Label}_{pz['nombre']}"
            pz["material_ref"] = fp.VDO_Material_Ref
            paneles_data.append(pz)

        for pz in paneles_data:
            info = shell_info.get(pz.get("rol"))
            if info and info.get("reengrose"):
                pz["reengrose"] = info["reengrose"]
                pz["caja"] = info["caja"]
                pz["ejes"] = info["ejes"]
                pz["clave_reengrose"] = pz.get("rol", "")

        paneles_data = VDO_FINISH.aplicar_cantos(
            paneles_data, lados_vistos, lados_apoyados,
            tapa=tapa, base=base)

        paneles_expandidos = []
        for pz in paneles_data:
            paneles_expandidos.extend(_expandir_reengrose(pz))
        paneles_data = paneles_expandidos

        fp.VDO_Paneles_JSON = json.dumps(paneles_data, ensure_ascii=False)

        solidos = []
        for forma in boxes:
            if forma is None or forma.isNull():
                continue
            if forma.ShapeType == "Compound":
                solidos.extend(
                    solido for solido in forma.Solids
                    if solido.Volume > 1e-9)
            elif forma.Volume > 1e-9:
                solidos.append(forma)
        fp.Shape = _get_part().makeCompound(solidos)

        # --- Propagación de Placement a insertos (hijos) ---
        # Cuando el COCO se mueve o rota (su Placement cambia),
        # todos sus hijos se mueven rígidamente con él.
        hijos = list(fp.Hijos or [])
        for hijo in hijos:
            if hijo is not None and hasattr(hijo, "LocalPlacement"):
                hijo.Placement = fp.Placement.multiply(
                    hijo.LocalPlacement)


    def dumps(self):
        return None

    def loads(self, state):
        return None


def make_coco(doc, configuracion):
    """
    Crea un COCO FeaturePython con propiedades configurables.

    Args:
        doc: Documento de FreeCAD activo (proporcionado por app/cad, no
             buscado desde core).
        configuracion (dict): Parámetros del cofre.

    Returns:
        _get_app().DocumentObject: El objeto FeaturePython creado.
    """
    if doc is None:
        _get_app().Console.PrintError("[VDO] No hay documento activo.\n")
        return None

    nombre = configuracion.get("nombre", "COCO_4C")

    obj = doc.addObject("Part::FeaturePython", nombre)
    CocoFeature(obj)

    if _get_app().GuiUp:
        # La vista se adjunta desde app/ (F5/F6), no desde core.
        pass

    # Aplicar configuración (valores por defecto desde vdo_manifest.json)
    obj.Alto = configuracion.get("alto", VDO_D.ALTO_DEFAULT)
    obj.Ancho = configuracion.get("ancho", VDO_D.ANCHO_DEFAULT)
    obj.FondoModulo = configuracion.get("fondo_modulo", VDO_D.FONDO_DEFAULT)
    obj.Espesor = configuracion.get("espesor", VDO_D.ESPESOR_DEFAULT)
    obj.TieneFondo = configuracion.get("tiene_fondo", VDO_D.FONDO_HABILITADO)
    obj.CalibreFondo = configuracion.get("calibre_fondo", VDO_D.FONDO_CALIBRE)
    obj.ProfundidadRanura = configuracion.get("profundidad_ranura", VDO_D.FONDO_PROFUNDIDAD_RANURA)
    obj.DistanciaBorde = configuracion.get("distancia_borde", VDO_D.FONDO_DISTANCIA_BORDE)
    obj.Tapa = configuracion.get("tapa", VDO_D.TAPA_POSICION)
    obj.Base = configuracion.get("base", VDO_D.BASE_POSICION)
    obj.VDO_Divisiones = configuracion.get("divisiones", "")
    reengroses = configuracion.get("reengroses", {})
    if not isinstance(reengroses, str):
        reengroses = json.dumps(reengroses or {}, ensure_ascii=False)
    obj.VDO_Reengrose_JSON = reengroses or "{}"
    rotacion = float(configuracion.get("rotacion", 0.0))
    obj.VDO_RotacionZ = rotacion
    obj.VDO_Anclaje = configuracion.get(
        "anclaje", VDO_MOD.ANCLAJE_DEFAULT)
    VDO_FR.guardar_exposicion(
        obj,
        configuracion.get("lados_vistos", [VDO_FR.FRENTE]),
        configuracion.get("lados_apoyados", [VDO_FR.FONDO]))
    if rotacion:
        obj.Placement = _get_app().Placement(
            obj.Placement.Base, rotacion_z(rotacion))

    doc.recompute()
    _get_app().Console.PrintMessage(
        f"[VDO] COCO '{nombre}' creado con FeaturePython.\n")
    return obj
