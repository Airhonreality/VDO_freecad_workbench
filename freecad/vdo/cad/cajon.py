# =====================================================================
# cajon.py
# Motor del cajón con corredera oculta VDO (FeaturePython).
# Trinidad de Cajones v2: geometría paramétrica pura con booleanos.
#
# Tipologías soportadas:
#   CORREDERA_OCULTA   - Blum Tandem / Genérica: notch + pin + piso grueso
#   CORREDERA_TELESCOPICA - Piso delgado 5.5mm en ranura, holgura 12.7mm/lado
#   CAJA_METALICA      - Sin laterales de madera (solo piso + trasera)
#
# Sistemas de apertura (facade_contract):
#   APERTURA_TIRADOR, APERTURA_GOLA, APERTURA_45_GRADOS, APERTURA_PUSH_OPEN
#
# Axioma: booleanos generados por prismas en coordenadas calculadas.
# Prohibido indexar caras volátiles (Shape.Faces[n]).
# =====================================================================

import json

from freecad.vdo.cad.cajon_geometria import _solidos_cajon
from freecad.vdo.cad.propiedades import add_common_props
from freecad.vdo.core import defaults as VDO_D
from freecad.vdo.core import module_props as VDO_MOD
from freecad.vdo.core.cajon_calculo import calcular_despiece
from freecad.vdo.core.cajon_correderas import (
    CAJA_METALICA,
    CORREDERA_OCULTA,
    CORREDERA_TELESCOPICA,
    listar_marcas,
)
from freecad.vdo.core.facade_contract import (
    APERTURA_45_GRADOS,
    APERTURA_GOLA,
    APERTURA_PUSH_OPEN,
    APERTURA_TIRADOR,
    MONTAJE_EMBEBIDA,
    MONTAJE_PARCHE,
    MONTAJE_SEMIPARCHE,
)
from freecad.vdo.core.helpers import _get_app, _get_part
from freecad.vdo.datos.valores import BLUM_TANDEM, MELAMINA_ESTANDAR

# =====================================================================
# CajonFeature
# =====================================================================

def _props_entrada_cajon(obj):
    """Propiedades de entrada: espacio interior del mueble."""
    obj.addProperty("App::PropertyLength", "AnchoLibre", "Dimensiones",
                    "Ancho libre interior del mueble LI (mm)"
                    ).AnchoLibre = 564.0
    obj.addProperty("App::PropertyLength", "ProfLibre", "Dimensiones",
                    "Profundidad libre interior del mueble (mm)"
                    ).ProfLibre = 560.0
    obj.addProperty("App::PropertyLength", "AnchoModulo", "Dimensiones",
                    "Ancho total del módulo (para la fachada, mm)"
                    ).AnchoModulo = 600.0
    obj.addProperty("App::PropertyLength", "AltoFrente", "Dimensiones",
                    "Alto total asignado a la fachada (mm)"
                    ).AltoFrente = 225.0


def _props_caja_cajon(obj):
    """Propiedades de la caja: alto y espesores del tablero."""
    obj.addProperty("App::PropertyLength", "AltoCaja", "Caja",
                    "Alto de los laterales de la caja (85/120/150)"
                    ).AltoCaja = VDO_D.CAJON_ALTO_DEFAULT
    obj.addProperty("App::PropertyLength", "GrosorCaja", "Caja",
                    "Espesor del tablero de la caja (15/16 mm)"
                    ).GrosorCaja = VDO_D.CAJON_GROSOR_DEFAULT
    obj.addProperty("App::PropertyLength", "GrosorFondo", "Caja",
                    "Espesor del piso del cajón (6/12 mm)"
                    ).GrosorFondo = VDO_D.CAJON_FONDO_DEFAULT
    obj.addProperty("App::PropertyLength", "GrosorFachada", "Fachada",
                    "Espesor de la fachada decorativa (18 mm)"
                    ).GrosorFachada = VDO_D.CAJON_FACHADA_DEFAULT


def _props_herraje_cajon(obj):
    """Propiedades de herraje: marca de corredera, guía y montaje de la trasera."""
    marcas = listar_marcas()
    obj.addProperty("App::PropertyEnumeration", "MarcaCorredera",
                    "Herraje", "Marca de corredera oculta (delta y cotas)"
                    ).MarcaCorredera = marcas
    obj.MarcaCorredera = BLUM_TANDEM if BLUM_TANDEM in marcas else marcas[0]
    obj.addProperty("App::PropertyLength", "LongitudGuia", "Herraje",
                    "Largo nominal de la guía (0 = auto según ProfLibre)"
                    ).LongitudGuia = 0.0
    obj.addProperty("App::PropertyEnumeration", "MontajeTrasera",
                    "Herraje", "Montaje de la contra-frente"
                    ).MontajeTrasera = ["entre_laterales", "testa"]
    obj.MontajeTrasera = "entre_laterales"


def _props_tipologia_cajon(obj):
    """Propiedad de tipologia de corredera."""
    obj.addProperty("App::PropertyEnumeration", "TipoCorredera",
                    "Herraje",
                    "Tipo de corredera: oculta / telescópica / metálica"
                    ).TipoCorredera = [
                        CORREDERA_OCULTA, CORREDERA_TELESCOPICA, CAJA_METALICA]
    obj.TipoCorredera = CORREDERA_OCULTA


def _props_fachada_cajon(obj):
    """Propiedades de fachada: sistema de apertura y tipo de montaje."""
    obj.addProperty("App::PropertyEnumeration", "SistemaApertura",
                    "Fachada",
                    "Sistema de apertura del frente del cajón"
                    ).SistemaApertura = [
                        APERTURA_TIRADOR, APERTURA_GOLA,
                        APERTURA_45_GRADOS, APERTURA_PUSH_OPEN]
    obj.SistemaApertura = APERTURA_TIRADOR

    obj.addProperty("App::PropertyEnumeration", "TipoMontaje",
                    "Fachada",
                    "Tipo de montaje de la fachada frente al vano"
    ).TipoMontaje = [MONTAJE_PARCHE, MONTAJE_SEMIPARCHE, MONTAJE_EMBEBIDA]
    obj.TipoMontaje = MONTAJE_PARCHE


def _props_vdo_cajon(obj):
    """Propiedades VDO de exportacion (cutting list) y de resumen del despiece."""
    obj.addProperty("App::PropertyString", "VDO_Tipo", "VDO",
                    "Tipo de objeto").VDO_Tipo = "contenedor"
    obj.addProperty("App::PropertyString", "VDO_Subtipo", "VDO",
                    "Subtipo").VDO_Subtipo = "cajon_oculta"
    obj.addProperty("App::PropertyString", "VDO_Material_Ref", "VDO",
                    "Material de las piezas"
                    ).VDO_Material_Ref = MELAMINA_ESTANDAR
    obj.addProperty("App::PropertyString", "VDO_Herraje_Ref", "VDO",
                    "Herraje de corredera oculta"
                    ).VDO_Herraje_Ref = obj.MarcaCorredera
    obj.addProperty("App::PropertyString", "VDO_Paneles_JSON", "VDO",
                    "Descripción JSON de las piezas del despiece")
    obj.addProperty("App::PropertyString", "VDO_ResumenDespiece", "VDO",
                    "Resumen legible del despiece (solo lectura)")


class CajonFeature:
    """FeaturePython que genera la geometría de un cajón (Trinidad v2)."""

    def __init__(self, obj):
        _props_entrada_cajon(obj)
        _props_caja_cajon(obj)
        _props_herraje_cajon(obj)
        _props_tipologia_cajon(obj)
        _props_fachada_cajon(obj)
        _props_vdo_cajon(obj)

        # Pose común VDO (rotación + anclaje). No altera la geometría.
        add_common_props(obj)

        # Vínculo padre-hijo (kinematics de Placement)
        obj.addProperty("App::PropertyLink", "ParentCOCO", "VDO",
                        "Módulo COCO padre")
        obj.addProperty("App::PropertyPlacement", "LocalPlacement", "VDO",
                        "Pose relativa al vano del COCO").LocalPlacement = _get_app().Placement()

        obj.Proxy = self

    # -----------------------------------------------------------------
    def _config(self, fp):
        """Construye el dict de entrada para calcular_despiece()."""
        # Para telescópica: grosor de piso 5.5 mm y eje de ranura a 10 mm
        grosor_fondo = float(fp.GrosorFondo)
        eje_ranura = VDO_D.CAJON_EJE_RANURA
        if fp.TipoCorredera == CORREDERA_TELESCOPICA:
            grosor_fondo = 5.5
            eje_ranura = 10.0

        return {
            "ancho_libre": float(fp.AnchoLibre),
            "prof_libre": float(fp.ProfLibre),
            "ancho_modulo": float(fp.AnchoModulo),
            "alto_frente": float(fp.AltoFrente),
            "marca": fp.MarcaCorredera,
            "alto_caja": float(fp.AltoCaja),
            "grosor_caja": float(fp.GrosorCaja),
            "grosor_fondo": grosor_fondo,
            "grosor_fachada": float(fp.GrosorFachada),
            "longitud_guia": float(fp.LongitudGuia),
            "montaje_trasera": fp.MontajeTrasera,
            "tipo_corredera": fp.TipoCorredera,
            "sistema_apertura": fp.SistemaApertura,
            "tipo_montaje_fachada": fp.TipoMontaje,
            "penetracion_ranura": VDO_D.CAJON_PENETRACION_RANURA,
            "eje_ranura": eje_ranura,
            "holgura_lateral_fachada": VDO_D.CAJON_HOLGURA_LAT_FACHADA,
            "holgura_superior_fachada": VDO_D.CAJON_HOLGURA_SUP_FACHADA,
            "holgura_inferior_fachada": VDO_D.CAJON_HOLGURA_INF_FACHADA,
            "material_ref": fp.VDO_Material_Ref,
        }

    # -----------------------------------------------------------------
    def execute(self, fp):
        """Reconstruir la geometría del cajón con booleanos limpios."""
        try:
            d = calcular_despiece(self._config(fp))
        except (ValueError, KeyError, TypeError) as e:
            _get_app().Console.PrintError(f"[VDO] Despiece inválido: {e}\n")
            fp.Shape = _get_part().Shape()
            return

        tipo_corredera = d.get("tipo_corredera", CORREDERA_OCULTA)
        sistema_apertura = d.get("sistema_apertura", APERTURA_TIRADOR)

        solids = _solidos_cajon(d, tipo_corredera, sistema_apertura)

        # Exportación: piezas del despiece y resumen legible
        fp.VDO_Paneles_JSON = _paneles_json(
            d["piezas"], tipo_corredera, fp.Label)
        fp.VDO_ResumenDespiece = _resumen_despiece(d)
        for aviso in d["avisos"]:
            _get_app().Console.PrintWarning(f"[VDO] ⚠️ {aviso}\n")

        fp.Shape = _get_part().makeCompound(solids)

        # --- Vínculo rígido padre-hijo ---
        # No escribir fp.Placement aquí: solo CocoFeature.execute() es
        # la fuente de verdad del placement mundial del hijo.
        # LocalPlacement almacena la pose relativa al vano del COCO.
        _normalizar_local_placement(fp)

    # -----------------------------------------------------------------
    def dumps(self):
        return None

    def loads(self, state):
        return None


def _paneles_json(piezas, tipo_corredera, label):
    """JSON de las piezas del despiece con nombre prefijado por el Label."""
    paneles = json.loads(json.dumps(piezas, ensure_ascii=False))
    if tipo_corredera == CAJA_METALICA:
        # Para caja metálica, no reportar madera en costados
        paneles = [p for p in paneles
                   if p["nombre"] not in ("Cajon_Lateral_Izq",
                                          "Cajon_Lateral_Der")]
    for pz in paneles:
        pz["nombre"] = f"{label}_{pz['nombre'].replace('Cajon_', '')}"
    return json.dumps(paneles, ensure_ascii=False)


def _resumen_despiece(d):
    """Resumen legible del despiece (texto de solo lectura)."""
    tipo_corredera = d.get("tipo_corredera", CORREDERA_OCULTA)
    sistema_apertura = d.get("sistema_apertura", APERTURA_TIRADOR)
    caja = d["caja"]
    guia = d["guia"]
    g_caja = caja["grosor"]
    g_fondo = caja["grosor_piso"]
    z_piso = caja["z_piso"]
    lg = caja["largo_lateral"]
    alto_lateral = caja["alto_lateral"]
    ancho_ext = caja["ancho_exterior"]
    ancho_contra = caja["ancho_contra"]
    alto_contra = caja["alto_contra"]
    return (
        f"Cajón Trinidad v2 ({tipo_corredera})\n"
        f"Guía {guia['marca']}: LG={guia['lg']:.0f} mm "
        f"({'auto' if guia['auto'] else 'manual'}, Δ={guia['delta']:.0f} mm)\n"
        f"Caja ext: {ancho_ext:.0f} x {lg:.0f} x {alto_lateral:.0f} mm "
        f"(G={g_caja:.0f})\n"
        f"Contra-frente: {ancho_contra:.0f} x {alto_contra:.1f} mm "
        f"({caja['montaje_trasera']})\n"
        f"Piso: {caja['ancho_piso']:.0f} x {caja['largo_piso']:.0f} x "
        f"{g_fondo:.0f} mm (z={z_piso:.1f})\n"
        f"Fachada: {d['fachada']['ancho']:.0f} x {d['fachada']['alto']:.0f} "
        f"x {d['fachada']['espesor']:.0f} mm ({sistema_apertura})\n"
        f"Tipo corredera: {tipo_corredera}"
    )


def _normalizar_local_placement(fp):
    """Restablece LocalPlacement si su base contiene valores no numéricos."""
    lp = fp.LocalPlacement
    base = lp.Base
    if any(
        not isinstance(v, (int, float))
        or v != v  # NaN check
        for v in (base.x, base.y, base.z)
    ):
        fp.LocalPlacement = _get_app().Placement(
            _get_app().Vector(0.0, 0.0, 0.0), _get_app().Rotation())


def make_cajon(doc, configuracion):
    """
    Crea un cajón con corredera (FeaturePython, Trinidad v2).
    """
    if doc is None:
        _get_app().Console.PrintError("[VDO] No hay documento activo.\n")
        return None

    nombre = configuracion.get("nombre", "Cajon_Oculta")
    obj = doc.addObject("Part::FeaturePython", nombre)
    CajonFeature(obj)

    if _get_app().GuiUp:
        # La vista se adjunta desde app/ (F5/F6), no desde core.
        pass

    obj.AnchoLibre = configuracion.get("ancho_libre", 564.0)
    obj.ProfLibre = configuracion.get("prof_libre", 560.0)
    obj.AnchoModulo = configuracion.get("ancho_modulo", 600.0)
    obj.AltoFrente = configuracion.get("alto_frente", 225.0)
    obj.AltoCaja = configuracion.get("alto_caja", VDO_D.CAJON_ALTO_DEFAULT)
    obj.GrosorCaja = configuracion.get("grosor_caja", VDO_D.CAJON_GROSOR_DEFAULT)
    obj.GrosorFondo = configuracion.get("grosor_fondo", VDO_D.CAJON_FONDO_DEFAULT)
    obj.GrosorFachada = configuracion.get("grosor_fachada", VDO_D.CAJON_FACHADA_DEFAULT)
    obj.MarcaCorredera = configuracion.get("marca", BLUM_TANDEM)
    obj.LongitudGuia = configuracion.get("longitud_guia", 0.0)
    obj.MontajeTrasera = configuracion.get("montaje_trasera", "entre_laterales")
    obj.TipoCorredera = configuracion.get("tipo_corredera", CORREDERA_OCULTA)
    obj.SistemaApertura = configuracion.get("sistema_apertura", APERTURA_TIRADOR)
    obj.TipoMontaje = configuracion.get("tipo_montaje_fachada", MONTAJE_PARCHE)
    if "material_ref" in configuracion:
        obj.VDO_Material_Ref = configuracion["material_ref"]
    obj.VDO_Herraje_Ref = obj.MarcaCorredera
    rotacion = float(configuracion.get("rotacion", 0.0))
    obj.VDO_RotacionZ = rotacion
    obj.VDO_Anclaje = configuracion.get(
        "anclaje", VDO_MOD.ANCLAJE_DEFAULT)

    # Vínculo padre-hijo: LocalPlacement y ParentCOCO se establecen aquí.
    # La geometría interna se construye en coordenadas locales del vano
    # dentro de execute(); LocalPlacement lleva la posición relativa al COCO.
    local_placement = configuracion.get("local_placement")
    if local_placement is not None:
        obj.LocalPlacement = local_placement
    parent_coco = configuracion.get("parent_coco")
    if parent_coco is not None:
        obj.ParentCOCO = parent_coco

    doc.recompute()
    _get_app().Console.PrintMessage(
        f"[VDO] Cajón '{nombre}' creado "
        f"(tipo={obj.TipoCorredera}, marca={obj.MarcaCorredera}, "
        f"LI={float(obj.AnchoLibre):.0f}, ProfLibre={float(obj.ProfLibre):.0f}).\n")
    return obj
