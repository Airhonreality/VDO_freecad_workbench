# =====================================================================
# puerta.py
# Capa 2 - PuertaFeature (Part::FeaturePython) con mecanizados booleanos
# y chaflanes para el submódulo de Puertas y Cierres (L2).
# =====================================================================



from freecad.vdo.core.facade_contract import (
    APERTURA_45_GRADOS,
    APERTURA_GOLA,
    APERTURA_PUSH_OPEN,
    APERTURA_TIRADOR,
    HOLGURA_PERIMETRAL_DEFAULT,
    MONTAJE_PARCHE,
    SOLAPE_PARCHE_NOMINAL,
    calcular_fachada_base,
)
from freecad.vdo.core.helpers import _get_app, _get_part
from freecad.vdo.cad.propiedades import add_common_props
from freecad.vdo.core.puerta_despiece import (
    CAZALETA_DIAMETRO,
    CAZALETA_PROFUNDIDAD,
    ajuste_altura_apertura,
    bisagras_para_puerta,
    calcular_corrediza,
    descripcion_piston,
    necesita_cantos_45,
)

# ---------------------------------------------------------------------
# Utilidades de geometría
# ---------------------------------------------------------------------

def _arista_borde(shape, coord_fijo, valor_fijo, coord_var, tol=1e-6):
    """Arista donde todos los vértices tienen coord_fijo == valor_fijo."""
    for arista in shape.Edges:
        pts = [v.Point for v in arista.Vertexes]
        if all(abs(p[coord_fijo] - valor_fijo) < tol for p in pts):
            return arista
    return None


def _cilindro_cazoleta(cup_x, cup_z, espesor, radio=None, profundidad=None):
    """Cilindro ciego de cazoleta taladrado desde la cara trasera (Y=espesor)."""
    radio = radio or CAZALETA_DIAMETRO / 2.0
    profundidad = profundidad or CAZALETA_PROFUNDIDAD
    base = _get_app().Vector(cup_x, espesor - profundidad, cup_z)
    direccion = _get_app().Vector(0.0, 1.0, 0.0)
    return _get_part().makeCylinder(radio, profundidad, base, direccion)


def _asignar_forma(fp, piezas, pos):
    """Fija Shape con los sólidos válidos y LocalPlacement en la pose recibida."""
    solidos = [s for s in piezas if not s.isNull() and s.Volume > 1e-9]
    fp.Shape = _get_part().makeCompound(solidos) if solidos else _get_part().Shape()
    # LocalPlacement: geometría ya está en origen local (0,0,0).
    # La posición relativa al vano del COCO se combina con ParentCOCO
    # en CocoFeature.execute().
    fp.LocalPlacement = _get_app().Placement(
        _get_app().Vector(*pos), _get_app().Rotation())


def _fachada_parche(dims, pos, montaje):
    """Devuelve (w_fach, h_fach, pos) con la fachada centrada sobre el hueco."""
    W, H, t = dims
    px, py, pz = pos
    if montaje != MONTAJE_PARCHE:
        return W, H, pos
    w_fach, h_fach = calcular_fachada_base(
        W, H, montaje,
        holgura=HOLGURA_PERIMETRAL_DEFAULT,
        solape=SOLAPE_PARCHE_NOMINAL)
    # Centrar la fachada sobre el hueco del vano
    px = px - (w_fach - W) / 2.0
    pz = pz - (h_fach - H) / 2.0
    # Panel apoyado en el plano exterior de la carcasa (Y=-t)
    py = py - t
    return w_fach, h_fach, (px, py, pz)


# Posiciones X de las cazoletas según el sentido de apertura
_CUP_XS_POR_SENTIDO = {
    "Derecha": lambda cota, w: [w - cota],
    "Doble": lambda cota, w: [cota, w - cota],
}


def _taladrar_cazoletas(shape, sentido, dims_fach, montaje, sku):
    """Resta del panel las cazoletas de bisagra (solo batiente vertical)."""
    w_fach, h_fach, t = dims_fach
    bis = bisagras_para_puerta(h_fach, montaje, prefer_sku=sku or None)
    radio = bis["diametro_cazoleta"] / 2.0
    prof = bis["profundidad_cazoleta"]
    cota_x = bis["cota_x"]
    cup_xs = _CUP_XS_POR_SENTIDO.get(
        sentido, lambda cota, w: [cota])(cota_x, w_fach)
    for cup_z in bis["posiciones_z"]:
        for cup_x in cup_xs:
            if 0 < cup_x < w_fach and 0 < cup_z < h_fach:
                cyl = _cilindro_cazoleta(cup_x, cup_z, t, radio, prof)
                shape = shape.cut(cyl)
    return shape


def _construir_batiente(fp, dims, pos, sistema, montaje, sentido, apertura):
    """Panel de batiente (vertical o basculante) con chaflán y cazoletas."""
    t = dims[2]
    w_fach, h_fach, pos = _fachada_parche(dims, pos, montaje)
    # Ajuste de altura por sistema de apertura (gola)
    H_efectiva, _descuento = ajuste_altura_apertura(apertura, h_fach)
    shape = _get_part().makeBox(w_fach, t, H_efectiva)
    # Chaflán 45° en el canto de agarre (borde superior delantero)
    if necesita_cantos_45(apertura):
        arista = _arista_borde(shape, 2, H_efectiva, 0)
        if arista is None:
            arista = _arista_borde(shape, 2, H_efectiva, 1)
        if arista is not None:
            shape = shape.makeChamfer(3.0, 3.0, [arista])
    if sistema == "Batiente Vertical":
        shape = _taladrar_cazoletas(
            shape, sentido, (w_fach, h_fach, t), montaje, fp.HardwareSKU)
    _asignar_forma(fp, [shape] if shape is not None else [], pos)


def _avisar_intersecciones(hojas):
    """Avisa si dos hojas de corredera comparten volumen."""
    for a in range(len(hojas)):
        for b in range(a + 1, len(hojas)):
            if hojas[a].common(hojas[b]).Volume > 1e-6:
                _get_app().Console.PrintWarning(
                    f"[VDO Puerta] Hojas {a+1} y {b+1} se "
                    f"intersectan (common > 0).\n")


def _construir_corrediza(fp, dims, pos, sentido, apertura):
    """Hojas de puerta corredera con traslape y paso de riel."""
    W, H, t = dims
    n_hojas = 3 if sentido == "Doble" else 2
    res = calcular_corrediza(W, H, tipo_mueble="closet", n_hojas=n_hojas,
                             prefer_sku=fp.HardwareSKU or None)
    w_hoja = float(res["ancho_hoja"])
    h_hoja = float(res["alto_hoja"])
    traslape = float(res["traslape_minimo"])

    # Paso en profundidad según el riel del catálogo
    tecnicos = res.get("parametros_tecnicos", {})
    paso_y = float(tecnicos.get("ancho_piso_riel_doble", t + 4.0))
    if paso_y <= 0:
        paso_y = t + 4.0

    hojas = []
    for i in range(n_hojas):
        hoja = _get_part().makeBox(w_hoja, t, h_hoja)
        # Desfasar en X con traslape y en Y con el paso del riel
        x_i = i * (w_hoja - traslape)
        y_i = i * paso_y
        hoja.Placement = _get_app().Placement(
            _get_app().Vector(x_i, y_i, 0), _get_app().Rotation())
        hojas.append(hoja.transformShape(hoja.Placement.toMatrix()))

    # Chaflán 45° si aplica (solo en la hoja delantera)
    if necesita_cantos_45(apertura) and hojas:
        arista = _arista_borde(hojas[0], 2, h_hoja, 0)
        if arista is not None:
            hojas[0] = hojas[0].makeChamfer(3.0, 3.0, [arista])

    # Validar que no haya intersección de volúmenes (common == 0)
    _avisar_intersecciones(hojas)
    _asignar_forma(fp, hojas, pos)
    fp.FuerzaPistonRecomendada = ""


# ---------------------------------------------------------------------
# FeaturePython
# ---------------------------------------------------------------------

class PuertaFeature:
    """Proxy de PuertaFeature para Part::FeaturePython."""

    def __init__(self, obj):
        obj.addProperty("App::PropertyEnumeration", "TipoSistema", "Sistema",
                        "Tipo de sistema de puerta").TipoSistema = [
            "Batiente Vertical", "Basculante Horizontal", "Corrediza"]
        obj.addProperty("App::PropertyEnumeration", "TipoMontaje", "Montaje",
                        "Tipo de montaje (batiente)").TipoMontaje = [
            "Parche", "Semiparche", "Embebida"]
        obj.addProperty("App::PropertyEnumeration", "SentidoApertura",
                        "Apertura", "Sentido de apertura").SentidoApertura = [
            "Izquierda", "Derecha", "Doble",
            "Hacia Arriba", "Hacia Abajo", "2 hojas", "3 hojas"]
        obj.addProperty("App::PropertyEnumeration", "SistemaApertura",
                        "Sistema de Apertura", "Sistema de apertura/fachada").SistemaApertura = [
            APERTURA_TIRADOR, APERTURA_GOLA, APERTURA_45_GRADOS, APERTURA_PUSH_OPEN]
        obj.addProperty("App::PropertyString", "HardwareSKU", "Herraje",
                        "SKU comercial del herraje activo").HardwareSKU = ""
        obj.addProperty("App::PropertyString", "VDO_Vano_ID", "Vinculación",
                        "Identificador del vano vinculado (ej. '(x1,y1)')").VDO_Vano_ID = ""
        obj.addProperty("App::PropertyString", "FuerzaPistonRecomendada",
                        "Físico", "Fuerza de pistón recomendada (solo lectura)").FuerzaPistonRecomendada = ""

        # Geometría
        obj.addProperty("App::PropertyLength", "Ancho", "Dimensiones",
                        "Ancho de la puerta (mm)").Ancho = 400.0
        obj.addProperty("App::PropertyLength", "Alto", "Dimensiones",
                        "Alto de la puerta (mm)").Alto = 700.0
        obj.addProperty("App::PropertyInteger", "Espesor", "Dimensiones",
                        "Espesor del panel (mm)").Espesor = 18
        obj.addProperty("App::PropertyLength", "PosX", "Posición",
                        "Posición X de la puerta (mm)").PosX = 0.0
        obj.addProperty("App::PropertyLength", "PosY", "Posición",
                        "Posición Y de la puerta (mm)").PosY = 0.0
        obj.addProperty("App::PropertyLength", "PosZ", "Posición",
                        "Posición Z de la puerta (mm)").PosZ = 0.0

        # VDO comunes
        add_common_props(obj)

        # Vínculo padre-hijo (kinematics de Placement)
        obj.addProperty("App::PropertyLink", "ParentCOCO", "VDO",
                        "Módulo COCO padre")
        obj.addProperty("App::PropertyPlacement", "LocalPlacement", "VDO",
                        "Pose relativa al vano del COCO").LocalPlacement = _get_app().Placement()

        obj.Proxy = self

    def execute(self, fp):
        """Reconstruir la geometría de la puerta."""

        sistema = str(fp.TipoSistema)
        montaje = str(fp.TipoMontaje)
        sentido = str(fp.SentidoApertura)
        apertura = str(fp.SistemaApertura)

        W = float(fp.Ancho)
        H = float(fp.Alto)
        t = float(fp.Espesor)
        px = float(fp.PosX)
        py = float(fp.PosY)
        pz = float(fp.PosZ)

        if W <= 0 or H <= 0 or t <= 0:
            fp.Shape = _get_part().Shape()
            return

        # Fuerza de pistón (basculante)
        if sistema == "Basculante Horizontal":
            texto, _comercial, _F = descripcion_piston(W, H)
            fp.FuerzaPistonRecomendada = texto
        else:
            fp.FuerzaPistonRecomendada = ""

        dims = (W, H, t)
        pos = (px, py, pz)
        if sistema in ("Batiente Vertical", "Basculante Horizontal"):
            _construir_batiente(fp, dims, pos, sistema, montaje, sentido, apertura)
        elif sistema == "Corrediza":
            _construir_corrediza(fp, dims, pos, sentido, apertura)
        else:
            fp.Shape = _get_part().Shape()

        # --- Vínculo rígido padre-hijo ---
        # No escribir fp.Placement aquí: solo CocoFeature.execute() es
        # la fuente de verdad del placement mundial del hijo.
        # LocalPlacement almacena la pose relativa al vano del COCO.


# ---------------------------------------------------------------------
# ViewProvider
# ---------------------------------------------------------------------


def make_puerta(doc, configuracion):
    """Crea un PuertaFeature en el documento recibido."""
    if doc is None:
        _get_app().Console.PrintError("[VDO Puerta] No hay documento activo.\n")
        return None

    nombre = configuracion.get("nombre", "Puerta")
    obj = doc.addObject("Part::FeaturePython", nombre)
    PuertaFeature(obj)

    if _get_app().GuiUp:
        # La vista se adjunta desde app/ (F5/F6), no desde core.
        pass

    obj.TipoSistema = configuracion.get("tipo_sistema", "Batiente Vertical")
    obj.TipoMontaje = configuracion.get("tipo_montaje", "Parche")
    obj.SentidoApertura = configuracion.get("sentido_apertura", "Izquierda")
    obj.SistemaApertura = configuracion.get("sistema_apertura",
                                            APERTURA_TIRADOR)
    obj.HardwareSKU = configuracion.get("hardware_sku", "")
    obj.VDO_Vano_ID = configuracion.get("vdo_vano_id", "")
    obj.Ancho = configuracion.get("ancho", 400.0)
    obj.Alto = configuracion.get("alto", 700.0)
    obj.Espesor = configuracion.get("espesor", 18)
    obj.PosX = configuracion.get("pos_x", 0.0)
    obj.PosY = configuracion.get("pos_y", 0.0)
    obj.PosZ = configuracion.get("pos_z", 0.0)
    obj.VDO_Anclaje = configuracion.get(
        "anclaje", "inferior_izquierda_frente")

    # Vínculo padre-hijo: LocalPlacement y ParentCOCO se establecen aquí.
    # La geometría interna se construye en origen local (0,0,0) dentro de
    # execute(); LocalPlacement lleva la posición relativa al vano del COCO.
    local_placement = configuracion.get("local_placement")
    if local_placement is not None:
        obj.LocalPlacement = local_placement
    parent_coco = configuracion.get("parent_coco")
    if parent_coco is not None:
        obj.ParentCOCO = parent_coco

    doc.recompute()
    _get_app().Console.PrintMessage(
        f"[VDO Puerta] '{nombre}' creado con FeaturePython.\n")
    return obj


__all__ = ["PuertaFeature", "make_puerta"]
