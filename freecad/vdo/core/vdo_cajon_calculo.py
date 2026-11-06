# =====================================================================
# vdo_cajon_calculo.py
# Cálculo del despiece del cajón con corredera oculta (Blum Tandem etc).
# Separado de vdo_cajon_despiece.py (M7, D-36).
#
# Datos de partida:
#   LI       = ancho libre interior del mueble (pared a pared)
#   ProfInt  = profundidad libre interior del mueble
#   LG       = largo nominal de la guía (auto: max(comerciales ≤ ProfInt))
#   Delta    = reducción por herraje (ej. Blum Tandem 16mm → 49 mm)
#   Gcaja    = grosor de laterales/trasera/frente interior (15-16 mm)
#   Gfondo   = grosor del piso (6-12 mm)
#   Gfrente  = grosor de la fachada (18 mm)
#
# Salida de calcular_despiece:
#   dict con:
#   "guia":        {lg, delta, marca, prof_int}
#   "caja":        medidas de las 5 piezas de la caja
#   "fachada":     medidas de la fachada
#   "posiciones":  coordenadas 3D (X=ancho, Y=prof, Z=alto)
#   "piezas":      lista de corte (para VDO_Paneles_JSON)
#   "mecanizados": cotas de mecanizado usadas
#   "avisos":      lista de advertencias (str)
# =====================================================================

from freecad.vdo.core.vdo_cajon_correderas import (
    _MANIFEST,
    CAJA_METALICA,
    CORREDERA_OCULTA,
    CORREDERA_TELESCOPICA,
    obtener_marca,
    seleccionar_guia,
)
from freecad.vdo.core.vdo_facade_contract import (
    APERTURA_TIRADOR,
    GOLA_DESCUENTO_ALTURA_DEFAULT,
    MONTAJE_PARCHE,
    SOLAPE_PARCHE_NOMINAL,
    aplicar_sistema_apertura,
    calcular_fachada_base,
    cantos_por_sistema_apertura,
    necesita_bisel_45,
    necesita_descuento_gola,
    necesita_expulsor_magnetico,
)
from freecad.vdo.datos.valores import BLUM_TANDEM, MELAMINA_ESTANDAR


def _leer_entradas(config):
    """Lee las entradas obligatorias, la marca y el tipo de corredera.

    Args:
        config (dict): claves obligatorias:
            ancho_libre (LI), prof_libre (ProfInt), ancho_modulo,
            alto_frente, marca (str)
          opcionales:
            alto_caja, grosor_caja, grosor_fondo, grosor_fachada,
            longitud_guia (0 = auto), montaje_trasera
            ("entre_laterales" | "testa"),
            penetracion_ranura, eje_ranura,
            holgura_lateral_fachada, holgura_superior_fachada,
            holgura_inferior_fachada, material_ref
    """
    li = float(config["ancho_libre"])
    prof_int = float(config["prof_libre"])
    float(config["ancho_modulo"])
    alto_frente = float(config["alto_frente"])
    marca_id = config.get("marca", BLUM_TANDEM)

    marca = obtener_marca(marca_id)
    delta = float(marca["delta_ancho"])
    mecanizado = dict(marca.get("mecanizado", {}))

    # --- Tipo de corredera: ajusta delta para telescópica ---
    tipo_corredera = str(config.get("tipo_corredera", CORREDERA_OCULTA)).strip().lower()
    if tipo_corredera == CORREDERA_TELESCOPICA:
        # Telescópica: holgura lateral 12.7 mm por lado → delta = 25.4 mm
        delta = 25.4

    # Añadir tipo_corredera al resultado para el generador 3D
    _tipo_corredera_result = tipo_corredera
    return (li, prof_int, alto_frente, marca_id, marca, delta, mecanizado,
            _tipo_corredera_result)


def _leer_defectos(config):
    """Lee los valores por defecto del manifest y las opciones de montaje."""
    # --- Defaults desde manifest (parametros_cajon) ---
    pc = _MANIFEST.get("parametros_cajon", {})

    def _p(clave, fallback):
        return float(pc.get(clave, {}).get("valor", fallback))

    alto_caja = float(config.get("alto_caja") or _p("alto_caja", 120))
    g_caja = float(config.get("grosor_caja") or _p("grosor_caja", 16))
    g_fondo = float(config.get("grosor_fondo") or _p("grosor_fondo", 6))
    g_fachada = float(config.get("grosor_fachada") or _p("grosor_fachada", 18))
    pen_ranura = float(config.get("penetracion_ranura")
                        or _p("penetracion_ranura_piso", 10))
    eje_ranura = float(config.get("eje_ranura")
                       or _p("eje_ranura_piso", 11.5))
    holg_lat = float(config.get("holgura_lateral_fachada")
                     or _p("holgura_lateral_fachada", 2))
    holg_sup = float(config.get("holgura_superior_fachada")
                     or _p("holgura_superior_fachada", 2))
    holg_inf = float(config.get("holgura_inferior_fachada")
                     or _p("holgura_inferior_fachada", 2))
    montaje = config.get("montaje_trasera", "entre_laterales")
    material_ref = config.get("material_ref", MELAMINA_ESTANDAR)
    tipo_montaje_fachada = str(
        config.get("tipo_montaje_fachada", MONTAJE_PARCHE)).strip().lower()
    return (alto_caja, g_caja, g_fondo, g_fachada, pen_ranura, eje_ranura,
            holg_lat, holg_sup, holg_inf, montaje, material_ref,
            tipo_montaje_fachada)


def _validar_entradas(g_caja, g_fondo, montaje):
    """Valida grosores y montaje. Devuelve los avisos; lanza ValueError si el montaje es inválido."""
    avisos = []

    # --- Validaciones ---
    if g_caja not in (15.0, 16.0):
        avisos.append(
            f"Grosor de caja {g_caja} mm: las correderas ocultas estándar "
            f"están pensadas para 15/16 mm (con 18 mm hay que rebajar el "
            f"canto inferior del lateral).")
    if g_fondo > g_caja:
        avisos.append("El grosor del piso no puede superar el de la caja.")
    if montaje not in ("entre_laterales", "testa"):
        raise ValueError(
            f"montaje_trasera inválido: '{montaje}' "
            f"(use 'entre_laterales' o 'testa')")
    return avisos


def _resolver_guia(config, prof_int, marca):
    """Resuelve la longitud de guía: manual si es > 0, si no automática."""
    # --- 1. Guía (LG) ---
    lg_manual = float(config.get("longitud_guia") or 0)
    lg = lg_manual if lg_manual > 0 else seleccionar_guia(prof_int, marca["longitudes_comerciales"])
    return lg, lg_manual


def _ancho_exterior(li, delta):
    """Ancho exterior de la caja (LI - Delta). Lanza ValueError si no es positivo."""
    # --- 2. Ancho exterior de la caja ---
    ancho_ext = li - delta
    if ancho_ext <= 0:
        raise ValueError(
            f"Ancho exterior de caja inválido: LI({li}) - Delta({delta}) "
            f"= {ancho_ext}. Revise LI o la marca de corredera.")
    return ancho_ext


def _geometria_caja(montaje, ancho_ext, g_caja, lg, alto_caja, alto_lateral, eje_ranura, g_fondo, pen_ranura):
    """Contra-frente, frente interior, piso y su altura; lanza ValueError si la caja es demasiado baja."""
    # --- 4. Contra-frente y frente interior ---
    if montaje == "entre_laterales":
        ancho_contra = ancho_ext - (2 * g_caja)
        y_trasera = lg - g_caja
    else:  # testa: trasera detrás de los laterales
        ancho_contra = ancho_ext
        y_trasera = lg

    z_piso = eje_ranura
    alto_contra = alto_lateral - (z_piso + g_fondo)  # sobre el piso
    if alto_contra <= 0:
        raise ValueError(
            f"Alto de caja ({alto_caja} mm) demasiado pequeño: "
            f"debe superar eje_ranura({eje_ranura}) + "
            f"grosor_fondo({g_fondo}) = {z_piso + g_fondo} mm.")
    alto_frente_int = alto_contra

    # --- 5. Piso ---
    if montaje == "entre_laterales":
        anchoEntre = ancho_contra  # = ancho_ext - 2*g_caja
    else:
        anchoEntre = ancho_ext - (2 * g_caja)
    ancho_piso = anchoEntre + (2 * pen_ranura)
    largo_piso = lg  # fórmula del usuario (largo = LG)
    return ancho_contra, y_trasera, z_piso, alto_contra, alto_frente_int, ancho_piso, largo_piso


def _fachada_base(alto_frente, holg_sup, holg_inf, ancho_ext, tipo_montaje_fachada, holg_lat):
    """Medidas base de la fachada; lanza ValueError si no son positivas."""
    # --- 6. Fachada ---
    alto_fachada_nominal = alto_frente - holg_sup - holg_inf
    ancho_fachada, _alto_fachada_contract = calcular_fachada_base(
        ancho_ext, alto_fachada_nominal, tipo_montaje_fachada,
        holgura=holg_lat, solape=SOLAPE_PARCHE_NOMINAL)
    if ancho_fachada <= 0 or alto_fachada_nominal <= 0:
        raise ValueError(
            f"Fachada inválida: {ancho_fachada} x {alto_fachada_nominal} mm "
            f"(holguras demasiado grandes).")
    return ancho_fachada, alto_fachada_nominal


def _sistema_apertura(config, alto_fachada_nominal):
    """Aplica el sistema de apertura a la fachada y devuelve sus cantos y operacion."""
    # --- Aplicar sistema de apertura (contrato universal de fachadas) ---
    sistema_apertura = config.get("sistema_apertura", APERTURA_TIRADOR)
    alto_fachada, operacion_canto = aplicar_sistema_apertura(
        alto_fachada_nominal, sistema_apertura,
        descuento_gola=GOLA_DESCUENTO_ALTURA_DEFAULT)
    cantos_fachada = cantos_por_sistema_apertura(sistema_apertura)
    return sistema_apertura, alto_fachada, operacion_canto, cantos_fachada


def _posiciones(ancho_ext, g_caja, lg, alto_lateral, ancho_contra, montaje, y_trasera,
    z_piso, g_fondo, alto_contra, alto_frente_int, pen_ranura, ancho_piso,
    largo_piso, g_fachada, ancho_fachada, alto_fachada):
    """Coordenadas 3D locales de las piezas de la caja y de la fachada."""
    # --- 7. Posiciones 3D (origen = esquina frontales-inferior-izquierda
    #        exterior de la caja, coordenadas puramente locales al cajón) ---
    # Nota: el centrado del cajón dentro del vano se resuelve exclusivamente
    # mediante LocalPlacement en _construir_cajones(); aquí no hay offset
    # de centrado X para evitar el doble desplazamiento.
    posiciones = {
        "lateral_izquierdo": {"x": 0.0, "y": 0.0, "z": 0.0,
                              "largo_x": g_caja, "largo_y": lg,
                              "largo_z": alto_lateral},
        "lateral_derecho": {"x": ancho_ext - g_caja, "y": 0.0, "z": 0.0,
                            "largo_x": g_caja, "largo_y": lg,
                            "largo_z": alto_lateral},
        "contra_frente": {"x": g_caja if montaje == "entre_laterales" else 0.0,
                          "y": y_trasera, "z": z_piso + g_fondo,
                          "largo_x": ancho_contra, "largo_y": g_caja,
                          "largo_z": alto_contra},
        "frente_interior": {"x": g_caja, "y": 0.0, "z": z_piso + g_fondo,
                            "largo_x": ancho_contra,
                            "largo_y": g_caja,
                            "largo_z": alto_frente_int},
        "piso": {"x": g_caja - pen_ranura, "y": 0.0, "z": z_piso,
                 "largo_x": ancho_piso, "largo_y": largo_piso,
                 "largo_z": g_fondo},
        "fachada": {"x": (ancho_ext - ancho_fachada) / 2.0, "y": -g_fachada,
                    "z": 0.0,
                    "largo_x": ancho_fachada, "largo_y": g_fachada,
                    "largo_z": alto_fachada},
    }
    return posiciones


def _cotas_mecanizado(mecanizado, marca_id, z_piso, g_fondo):
    """Cotas de mecanizado de la ficha técnica y su resumen."""
    # --- 8. Mecanizados (cotas de la ficha técnica) ---
    diam_t = float(mecanizado.get("diam_taladro", 6))
    prof_t = float(mecanizado.get("prof_taladro", 12))
    dist_t_tras = float(mecanizado.get("dist_taladro_borde_trasero", 8))
    prof_ranura = float(mecanizado.get("prof_ranura_lateral", 4))
    notch_ancho = float(mecanizado.get("notch_ancho", 25))
    notch_alto = float(mecanizado.get("notch_alto", 20))

    mecanizados_resumen = {
        "marca": marca_id,
        "diam_taladro": diam_t,
        "prof_taladro": prof_t,
        "dist_taladro_borde_trasero": dist_t_tras,
        "prof_ranura_lateral": prof_ranura,
        "notch_ancho": notch_ancho,
        "notch_alto": notch_alto,
        "eje_ranura": z_piso,
        "grosor_fondo": g_fondo,
    }
    return mecanizados_resumen, diam_t, prof_t, dist_t_tras, prof_ranura, notch_ancho, notch_alto


def _piezas_laterales(largo_lateral, alto_lateral, g_caja, material_ref, z_piso, g_fondo, lg,
    prof_ranura, diam_t, prof_t, dist_t_tras):
    """Paneles laterales izquierdo y derecho de la caja, para la lista de corte."""
    piezas = [
        {
            "nombre": "Cajon_Lateral_Izq",
            "tipo": "panel",
            "largo": largo_lateral,
            "ancho": alto_lateral,
            "espesor": g_caja,
            "cantidad": 1,
            "material_ref": material_ref,
            "mecanizados": [
                {"tipo": "ranura_piso", "cara": "interna",
                 "z_base": z_piso, "ancho": g_fondo,
                 "prof": prof_ranura, "largo": lg},
                {"tipo": "taladro_fondo", "ø": diam_t, "prof": prof_t,
                 "y_desde_trasero": dist_t_tras, "x_centrada": True},
            ],
        },
        {
            "nombre": "Cajon_Lateral_Der",
            "tipo": "panel",
            "largo": largo_lateral,
            "ancho": alto_lateral,
            "espesor": g_caja,
            "cantidad": 1,
            "material_ref": material_ref,
            "mecanizados": [
                {"tipo": "ranura_piso", "cara": "interna",
                 "z_base": z_piso, "ancho": g_fondo,
                 "prof": prof_ranura, "largo": lg},
                {"tipo": "taladro_fondo", "ø": diam_t, "prof": prof_t,
                 "y_desde_trasero": dist_t_tras, "x_centrada": True},
            ],
        },
    ]
    return piezas


def _piezas_restantes(ancho_contra, alto_contra, g_caja, material_ref, notch_ancho,
    notch_alto, alto_frente_int, ancho_piso, largo_piso, g_fondo, ancho_fachada,
    alto_fachada, g_fachada, sistema_apertura, operacion_canto, cantos_fachada):
    """Paneles de contrafrente, frente interior, piso y fachada."""
    return [
        {
            "nombre": "Cajon_Contrafrente",
            "tipo": "panel",
            "largo": ancho_contra,
            "ancho": alto_contra,
            "espesor": g_caja,
            "cantidad": 1,
            "material_ref": material_ref,
            "mecanizados": [
                {"tipo": "notch_inferior", "lados": "ambos",
                 "ancho": notch_ancho, "alto": notch_alto},
            ],
        },
        {
            "nombre": "Cajon_Frente_Interior",
            "tipo": "panel",
            "largo": ancho_contra,
            "ancho": alto_frente_int,
            "espesor": g_caja,
            "cantidad": 1,
            "material_ref": material_ref,
            "mecanizados": [
                {"tipo": "zona_locking_device", "cara": "inferior",
                 "nota": "Gancho de acople (locking device) según ficha"},
            ],
        },
        {
            "nombre": "Cajon_Piso",
            "tipo": "panel",
            "largo": largo_piso,
            "ancho": ancho_piso,
            "espesor": g_fondo,
            "cantidad": 1,
            "material_ref": material_ref,
            "mecanizados": [],
        },
        {
            "nombre": "Cajon_Fachada",
            "tipo": "panel",
            "largo": ancho_fachada,
            "ancho": alto_fachada,
            "espesor": g_fachada,
            "cantidad": 1,
            "material_ref": material_ref,
            "sistema_apertura": sistema_apertura,
            "operacion_canto": operacion_canto,
            "cantos": cantos_fachada,
            "mecanizados": [
                {"tipo": "canto", "caras": 4,
                 "nota": "Fachada: 4 cantos (convención VDO)"},
                {"tipo": operacion_canto, "cara": "superior",
                 "nota": f"Sistema de apertura: {sistema_apertura}"},
            ],
        },
    ]


def _resumen_caja(ancho_ext, largo_lateral, alto_lateral, g_caja,
                  ancho_contra, alto_contra, montaje, ancho_piso,
                  largo_piso, g_fondo, z_piso):
    """Medidas de la caja para el resultado de calcular_despiece."""
    return {
        "ancho_exterior": ancho_ext,
        "largo_lateral": largo_lateral,
        "alto_lateral": alto_lateral,
        "grosor": g_caja,
        "ancho_contra": ancho_contra,
        "alto_contra": alto_contra,
        "montaje_trasera": montaje,
        "ancho_piso": ancho_piso,
        "largo_piso": largo_piso,
        "grosor_piso": g_fondo,
        "z_piso": z_piso,
    }


def _resumen_fachada(ancho_fachada, alto_fachada, alto_fachada_nominal,
                     g_fachada, sistema_apertura, tipo_montaje_fachada,
                     operacion_canto, cantos_fachada):
    """Medidas y reglas de la fachada para el resultado."""
    return {
        "ancho": ancho_fachada,
        "alto": alto_fachada,
        "alto_nominal": alto_fachada_nominal,
        "espesor": g_fachada,
        "sistema_apertura": sistema_apertura,
        "tipo_montaje": tipo_montaje_fachada,
        "operacion_canto": operacion_canto,
        "cantos": cantos_fachada,
        "necesita_gola": necesita_descuento_gola(sistema_apertura),
        "necesita_bisel_45": necesita_bisel_45(sistema_apertura),
        "necesita_expulsor": necesita_expulsor_magnetico(sistema_apertura),
    }


def _filtrar_piezas(piezas, tipo_corredera):
    """Quita los laterales en caja metalica (van en el perfil)."""
    if tipo_corredera != CAJA_METALICA:
        return piezas
    return [p for p in piezas
            if p["nombre"] not in ("Cajon_Lateral_Izq", "Cajon_Lateral_Der")]


def calcular_despiece(config):
    """Calcula el despiece del cajón (corredera oculta, telescópica o metálica).

    Entradas y valores por defecto: ver _leer_entradas y _leer_defectos.
    Salida: ver la cabecera de este módulo.
    """
    # --- Entradas obligatorias, marca y tipo de corredera ---
    (li, prof_int, alto_frente, marca_id, marca, delta, mecanizado,
     _tipo_corredera_result) = _leer_entradas(config)
    (alto_caja, g_caja, g_fondo, g_fachada, pen_ranura, eje_ranura,
     holg_lat, holg_sup, holg_inf, montaje, material_ref,
     tipo_montaje_fachada) = _leer_defectos(config)
    avisos = _validar_entradas(g_caja, g_fondo, montaje)
    lg, lg_manual = _resolver_guia(config, prof_int, marca)
    ancho_ext = _ancho_exterior(li, delta)
    # --- 3. Laterales ---
    largo_lateral = lg
    alto_lateral = alto_caja
    (ancho_contra, y_trasera, z_piso, alto_contra, alto_frente_int,
     ancho_piso, largo_piso) = _geometria_caja(montaje, ancho_ext, g_caja,
     lg, alto_caja, alto_lateral, eje_ranura, g_fondo, pen_ranura)
    ancho_fachada, alto_fachada_nominal = _fachada_base(
        alto_frente, holg_sup, holg_inf, ancho_ext, tipo_montaje_fachada, holg_lat)
    (sistema_apertura, alto_fachada, operacion_canto,
     cantos_fachada) = _sistema_apertura(config, alto_fachada_nominal)
    posiciones = _posiciones(
        ancho_ext, g_caja, lg, alto_lateral, ancho_contra, montaje, y_trasera,
        z_piso, g_fondo, alto_contra, alto_frente_int, pen_ranura, ancho_piso,
        largo_piso, g_fachada, ancho_fachada, alto_fachada)
    (mecanizados_resumen, diam_t, prof_t, dist_t_tras, prof_ranura,
     notch_ancho, notch_alto) = _cotas_mecanizado(mecanizado, marca_id,
     z_piso, g_fondo)
    # --- 9. Piezas para cutting list (VDO_Paneles_JSON) ---
    piezas = _piezas_laterales(largo_lateral, alto_lateral, g_caja,
                               material_ref, z_piso, g_fondo, lg, prof_ranura,
                               diam_t, prof_t, dist_t_tras) + _piezas_restantes(
        ancho_contra, alto_contra, g_caja, material_ref, notch_ancho,
        notch_alto, alto_frente_int, ancho_piso, largo_piso, g_fondo,
        ancho_fachada, alto_fachada, g_fachada, sistema_apertura,
        operacion_canto, cantos_fachada)
    return {
        "guia": {"lg": lg, "delta": delta, "marca": marca_id,
                 "prof_int": prof_int,
                 "auto": lg_manual <= 0},
        "tipo_corredera": _tipo_corredera_result,
        "caja": _resumen_caja(ancho_ext, largo_lateral, alto_lateral, g_caja,
                              ancho_contra, alto_contra, montaje, ancho_piso,
                              largo_piso, g_fondo, z_piso),
        "fachada": _resumen_fachada(ancho_fachada, alto_fachada,
                                    alto_fachada_nominal, g_fachada,
                                    sistema_apertura, tipo_montaje_fachada,
                                    operacion_canto, cantos_fachada),
        "posiciones": posiciones,
        "piezas": _filtrar_piezas(piezas, _tipo_corredera_result),
        "mecanizados": mecanizados_resumen,
        "avisos": avisos,
    }