"""Geometria de refuerzos de reengrose sobre paneles y cajas de modulo."""

from freecad.vdo.core.reengrose_modelo import _EJES, ReengroseError
from freecad.vdo.core.reengrose_modificador import espesor_efectivo, normalizar_modificador
from freecad.vdo.core.reengrose_tiras import generar_geometria_tiras_perimetrales


def _inicio_alineado(total, tamano, alineacion):
    total = float(total)
    tamano = float(tamano)
    alineacion = str(alineacion or "centrado").lower()
    if alineacion == "frente":
        inicio = 0.0
    elif alineacion == "fondo":
        inicio = total - tamano
    else:
        inicio = (total - tamano) / 2.0
    return max(0.0, inicio)


def _refuerzos_bordes_reengrose(largo, ancho, espesor, nombre, mod):
    tiras = generar_geometria_tiras_perimetrales(
        ancho, largo, mod, espesor)
    caras = ["cara_a", "cara_b"] if mod["cara"] == "ambos" else [mod["cara"]]
    refuerzos = []
    for cara in caras:
        sufijo_cara = ""
        if len(caras) > 1:
            sufijo_cara = "_A" if cara == "cara_a" else "_B"
        for tira in tiras:
            esp_ref = float(tira["d"])
            z0 = espesor if cara == "cara_a" else -esp_ref
            ref = {
                "nombre": (
                    f"{nombre}_Tira_{tira['nombre_sufijo']}{sufijo_cara}"),
                "rol": "refuerzo",
                "largo": float(tira.get("largo", tira["w"])),
                "ancho": float(tira.get("ancho", tira["h"])),
                "espesor": esp_ref,
                "x": float(tira["x"]),
                "y": float(tira["y"]),
                "z": float(z0),
                "borde": tira["borde"],
                "cara": cara,
                "eje_extrusion": "z",
            }
            if tira.get("poligono"):
                ref["poligono"] = [
                    (float(px), float(py), float(z0))
                    for px, py in tira["poligono"]
                ]
            refuerzos.append(ref)
    return refuerzos, tiras


def _posicion_refuerzo(largo, ancho, mod):
    """Devuelve largo, ancho, x0 e y0 de un refuerzo sin pacha total."""
    ancho_ref = mod["ancho"]
    if mod["orientacion"] == "paralela":
        if ancho_ref > ancho + 1e-6:
            raise ReengroseError(
                "El ancho del reengrose paralelo no cabe en la pieza.")
        y0 = _inicio_alineado(
            ancho, ancho_ref, mod["alineacion_profundidad"])
        return largo, ancho_ref, 0.0, y0
    if ancho_ref > largo + 1e-6:
        raise ReengroseError(
            "El ancho del reengrose transversal no cabe en la pieza.")
    x0 = _inicio_alineado(largo, ancho_ref, "centrado")
    return ancho, ancho_ref, x0, 0.0


def _refuerzo_pieza(nombre, largo, ancho, esp_ref, z0, sufijo, mod):
    """Construye la pieza de refuerzo de una cara."""
    if mod["modo_fabricacion"] == "pacha" and mod["alcance"] == "total":
        return {
            "nombre": f"{nombre}_Pacha{sufijo}",
            "rol": "refuerzo",
            "largo": largo,
            "ancho": ancho,
            "espesor": esp_ref,
            "x": 0.0,
            "y": 0.0,
            "z": z0,
        }
    largo_ref, ancho_ref, x0, y0 = _posicion_refuerzo(largo, ancho, mod)
    return {
        "nombre": f"{nombre}_Reengrose{sufijo}",
        "rol": "refuerzo",
        "largo": largo_ref,
        "ancho": ancho_ref,
        "espesor": esp_ref,
        "x": x0,
        "y": y0,
        "z": z0,
    }


def calcular_geometria_reengrose(panel_base, modifier):
    """Calcula la pieza base y los refuerzos en coordenadas del tablero."""
    mod = normalizar_modificador(modifier)
    largo = float(panel_base.get("largo", 0.0))
    ancho = float(panel_base.get("ancho", 0.0))
    espesor = float(panel_base.get("espesor", 0.0))
    nombre = str(panel_base.get("nombre", "Panel"))

    resultado = {
        "base": {
            "nombre": nombre,
            "rol": "base",
            "largo": largo,
            "ancho": ancho,
            "espesor": espesor,
            "x": 0.0,
            "y": 0.0,
            "z": 0.0,
        },
        "refuerzos": [],
        "grupo_pacha": "",
        "modificador": mod,
    }
    if not mod["activo"]:
        return resultado

    if largo <= 0 or ancho <= 0 or espesor <= 0:
        raise ReengroseError("El panel base debe tener dimensiones positivas.")

    if mod["usa_bordes"]:
        refuerzos, tiras = _refuerzos_bordes_reengrose(
            largo, ancho, espesor, nombre, mod)
        resultado["refuerzos"] = refuerzos
        resultado["tiras"] = tiras
        if mod["fabricacion"] == "pacha" and refuerzos:
            resultado["grupo_pacha"] = f"Pacha_{nombre}"
        return resultado

    esp_ref = espesor_efectivo(panel_base, mod)
    caras = ["cara_a", "cara_b"] if mod["cara"] == "ambos" else [mod["cara"]]

    for cara in caras:
        z0 = espesor if cara == "cara_a" else -esp_ref
        sufijo = ""
        if len(caras) > 1:
            sufijo = "_A" if cara == "cara_a" else "_B"
        resultado["refuerzos"].append(_refuerzo_pieza(
            nombre, largo, ancho, esp_ref, z0, sufijo, mod))
    if mod["modo_fabricacion"] == "pacha":
        resultado["grupo_pacha"] = f"Pacha_{nombre}"
    return resultado


def _refuerzos_bordes_caja(base, ejes, largo, ancho, espesor,
                           nombre, mod):
    tiras = generar_geometria_tiras_perimetrales(
        ancho, largo, mod, espesor)
    dim_key = {"x": "w", "y": "h", "z": "d"}
    cara_lista = (
        ["cara_a", "cara_b"] if mod["cara"] == "ambos"
        else [mod["cara"]])
    refuerzos = []
    for cara in cara_lista:
        sufijo_cara = ""
        if len(cara_lista) > 1:
            sufijo_cara = "_A" if cara == "cara_a" else "_B"
        for tira in tiras:
            esp_ref = float(tira["d"])
            z_local = espesor if cara == "cara_a" else -esp_ref
            ref = dict(base)
            ref[ejes["largo"]] = base[ejes["largo"]] + float(tira["x"])
            ref[dim_key[ejes["largo"]]] = float(tira["w"])
            ref[ejes["ancho"]] = base[ejes["ancho"]] + float(tira["y"])
            ref[dim_key[ejes["ancho"]]] = float(tira["h"])
            ref[ejes["espesor"]] = base[ejes["espesor"]] + z_local
            ref[dim_key[ejes["espesor"]]] = esp_ref
            ref["nombre"] = (
                f"{nombre}_Tira_{tira['nombre_sufijo']}{sufijo_cara}")
            ref["rol"] = "refuerzo"
            ref["borde"] = tira["borde"]
            ref["cara"] = cara
            ref["eje_extrusion"] = ejes["espesor"]
            if tira.get("poligono"):
                puntos = []
                for px, py in tira["poligono"]:
                    coords = {
                        eje: float(base[eje]) for eje in _EJES
                    }
                    coords[ejes["largo"]] = (
                        base[ejes["largo"]] + float(px))
                    coords[ejes["ancho"]] = (
                        base[ejes["ancho"]] + float(py))
                    coords[ejes["espesor"]] = (
                        base[ejes["espesor"]] + z_local)
                    puntos.append((
                        coords["x"], coords["y"], coords["z"]))
                ref["poligono"] = puntos
            refuerzos.append(ref)
    return refuerzos, tiras


_CLAVE_DIMENSION = {"x": "w", "y": "h", "z": "d"}


def _validar_ejes(ejes):
    """Normaliza a minusculas y valida los ejes largo, ancho y espesor."""
    for clave in ("largo", "ancho", "espesor"):
        eje = str(ejes.get(clave, "")).lower()
        if eje not in ("x", "y", "z"):
            raise ReengroseError(f"Eje invalido para '{clave}': {eje!r}.")
        ejes[clave] = eje
    if len(set(ejes.values())) != 3:
        raise ReengroseError("Los ejes largo/ancho/espesor deben ser distintos.")
    return ejes


def _dimensiones_caja(base, ejes):
    """Devuelve largo, ancho y espesor de la caja segun los ejes."""
    dims = {eje: base[_CLAVE_DIMENSION[eje]] for eje in ("x", "y", "z")}
    largo = dims[ejes["largo"]]
    ancho = dims[ejes["ancho"]]
    espesor = dims[ejes["espesor"]]
    if largo <= 0 or ancho <= 0 or espesor <= 0:
        raise ReengroseError("La caja base debe tener dimensiones positivas.")
    return largo, ancho, espesor


def _intervalos_cara(mod, ejes, largo, ancho):
    """Intervalos (inicio, tamano) en largo y ancho del refuerzo de una cara."""
    intervalos = {}
    if mod["modo_fabricacion"] == "pacha" and mod["alcance"] == "total":
        intervalos[ejes["largo"]] = (0.0, largo)
        intervalos[ejes["ancho"]] = (0.0, ancho)
    elif mod["orientacion"] == "paralela":
        if mod["ancho"] > ancho + 1e-6:
            raise ReengroseError(
                "El ancho del reengrose paralelo no cabe en la pieza.")
        intervalos[ejes["largo"]] = (0.0, largo)
        intervalos[ejes["ancho"]] = (
            _inicio_alineado(
                ancho, mod["ancho"], mod["alineacion_profundidad"]),
            mod["ancho"])
    else:
        if mod["ancho"] > largo + 1e-6:
            raise ReengroseError(
                "El ancho del reengrose transversal no cabe en la pieza.")
        intervalos[ejes["largo"]] = (
            (largo - mod["ancho"]) / 2.0, mod["ancho"])
        intervalos[ejes["ancho"]] = (0.0, ancho)
    return intervalos


def _intervalo_espesor(cara, espesor, esp_ref):
    """Intervalo del espesor del refuerzo y sufijo de nombre de la cara."""
    if cara == "cara_a":
        return (espesor, esp_ref), "_A"
    return (-esp_ref, esp_ref), "_B"


def _refuerzo_cara(base, nombre, mod, intervalos, cara, sufijo):
    """Construye la pieza de refuerzo de una cara."""
    ref = dict(base)
    for eje, (inicio, tamano) in intervalos.items():
        ref[eje] = base[eje] + inicio
        ref[_CLAVE_DIMENSION[eje]] = tamano
    ref["nombre"] = (
        f"{nombre}_Pacha{sufijo}"
        if mod["modo_fabricacion"] == "pacha"
        and mod["alcance"] == "total"
        else f"{nombre}_Reengrose{sufijo}")
    ref["rol"] = "refuerzo"
    ref["cara"] = cara
    return ref


def _refuerzos_caras(base, ejes, largo, ancho, espesor, nombre, mod):
    """Refuerzos del modo sin bordes: una pieza por cara activa."""
    esp_ref = float(mod["espesor"] or espesor)
    caras = ["cara_a", "cara_b"] if mod["cara"] == "ambos" else [mod["cara"]]
    refuerzos = []
    for cara in caras:
        intervalos = _intervalos_cara(mod, ejes, largo, ancho)
        intervalo_espesor, sufijo = _intervalo_espesor(cara, espesor, esp_ref)
        intervalos[ejes["espesor"]] = intervalo_espesor
        if len(caras) == 1:
            sufijo = ""
        refuerzos.append(
            _refuerzo_cara(base, nombre, mod, intervalos, cara, sufijo))
    return refuerzos


def calcular_geometria_caja(caja, modifier, ejes=None):
    """Calcula refuerzos de una pieza en coordenadas de modulo.

    ``caja`` usa x/y/z como origen y w/h/d como dimensiones (w=X, h=Y, d=Z).
    ``ejes`` indica que eje de la caja actua como largo, ancho y espesor:
        vertical:  {"largo": "z", "ancho": "y", "espesor": "x"}
        horizontal:{"largo": "x", "ancho": "y", "espesor": "z"}
        fondo:     {"largo": "x", "ancho": "z", "espesor": "y"}
    """
    mod = normalizar_modificador(modifier)
    base = {clave: float(caja.get(clave, 0.0))
            for clave in ("x", "y", "z", "w", "h", "d")}
    nombre = str(caja.get("nombre", "Pieza"))
    ejes = _validar_ejes(
        dict(ejes or {"largo": "x", "ancho": "y", "espesor": "z"}))
    resultado = {
        "base": dict(base),
        "refuerzos": [],
        "grupo_pacha": "",
        "modificador": mod,
    }
    if not mod["activo"]:
        return resultado

    largo, ancho, espesor = _dimensiones_caja(base, ejes)
    if mod["usa_bordes"]:
        refuerzos, tiras = _refuerzos_bordes_caja(
            base, ejes, largo, ancho, espesor, nombre, mod)
        resultado["refuerzos"] = refuerzos
        resultado["tiras"] = tiras
        if mod["fabricacion"] == "pacha" and refuerzos:
            resultado["grupo_pacha"] = f"Pacha_{nombre}"
        return resultado

    resultado["refuerzos"] = _refuerzos_caras(
        base, ejes, largo, ancho, espesor, nombre, mod)
    if mod["modo_fabricacion"] == "pacha":
        resultado["grupo_pacha"] = f"Pacha_{nombre}"
    return resultado


def extras_por_cara(modifier, espesor_panel):
    """Devuelve el espesor extra que invade cada cara (+/-) del panel."""
    mod = normalizar_modificador(modifier)
    if not mod["activo"]:
        return (0.0, 0.0)
    extra = float(mod["espesor"] or espesor_panel)
    if mod["cara"] == "ambos":
        return (extra, extra)
    if mod["cara"] == "cara_a":
        return (extra, 0.0)
    return (0.0, extra)
