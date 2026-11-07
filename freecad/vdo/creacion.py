"""coordinación de creación de módulos (entrada), D-24.

Reúne el caso de uso interactivo (crear_modulo_interactivo) y los coordinadores
crear_hoja, crear_panel, crear_zocalo, crear_cajon, crear_puerta y crear_coco.
Cada uno recibe el documento y un DTO, llama al plano puro de core/ y devuelve
un resultado. La interfaz llega por parámetro desde commands.py.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from typing import Any

from freecad.vdo.cad.cajon import make_cajon
from freecad.vdo.cad.coco import make_coco
from freecad.vdo.cad.guardian import vdo_guard
from freecad.vdo.cad.panel import crear_pieza
from freecad.vdo.cad.propiedades import add_common_props as _cad_add_common_props
from freecad.vdo.cad.propiedades import ocultar_vista as _cad_ocultar_vista
from freecad.vdo.cad.puerta import make_puerta
from freecad.vdo.cad.zocalo import make_zocalo
from freecad.vdo.core.dto import (
    CajonDTO,
    CajonResultado,
    CocoDTO,
    CocoResultado,
    HojaDTO,
    HojaResultado,
    PanelDTO,
    PanelResultado,
    PuertaDTO,
    PuertaResultado,
    ZocaloDTO,
    ZocaloResultado,
)
from freecad.vdo.core.module_specs import get_spec
from freecad.vdo.core.view_base import diagnostico_viewprovider


def _sanitizar_nombre(nombre: str) -> str:
    nombre = re.sub(r"[^A-Za-z0-9_]", "_", str(nombre or "Modulo"))
    if not nombre or nombre[0].isdigit():
        nombre = "Modulo_" + nombre
    return nombre


def _nombre_unico(doc: Any, base: str) -> str:
    base = _sanitizar_nombre(base)
    if doc.getObject(base) is None:
        return base
    i = 1
    while doc.getObject(f"{base}_{i:03d}") is not None:
        i += 1
    return f"{base}_{i:03d}"


def crear_modulo_interactivo(
    module_key: str,
    config: dict[str, Any] | None = None,
    *,
    abrir_panel: Callable[..., None] | None = None,
    colocar: Callable[..., None] | None = None,
) -> Any:
    """Crea un módulo VDO, abre su panel y, al aceptarlo, lo coloca con clic.

    abrir_panel(spec, obj, on_accept, on_cancel): muestra el panel de configuración.
    colocar(obj, on_done, on_cancel): inicia la colocación con el mouse.
    Si no se pasan (FreeCADCmd, pruebas), el módulo se confirma en el origen.
    """
    spec = get_spec(module_key)

    doc = vdo_guard()
    if doc is None:
        import FreeCAD as App
        App.Console.PrintError(
            "[VDO] No hay documento activo para crear el módulo.\n")
        return None

    cfg = _config_creacion(spec, doc, config, module_key)
    tx_propia = _abrir_transaccion(doc, spec, module_key)

    obj = spec["factory_fn"](doc, cfg)
    if obj is None:
        raise RuntimeError("La factory no devolvió un objeto")

    def cancelar() -> None:
        if tx_propia:
            doc.abortTransaction()
        if doc.getObject(obj.Name) is not None:
            doc.removeObject(obj.Name)
        doc.recompute()

    def confirmar() -> None:
        doc.recompute()
        if tx_propia:
            doc.commitTransaction()

    _cad_add_common_props(obj)

    if abrir_panel is None or colocar is None:
        confirmar()
        return obj

    _colocar_interactivo(obj, spec, abrir_panel, colocar, confirmar, cancelar)
    return obj


def _config_creacion(spec: dict[str, Any], doc: Any, config: dict[str, Any] | None,
                     module_key: str) -> dict[str, Any]:
    cfg = dict(spec.get("config", {}))
    if config:
        cfg.update(config)
    cfg["nombre"] = _nombre_unico(
        doc, cfg.get("nombre") or spec.get("label", module_key))
    return cfg


def _abrir_transaccion(doc: Any, spec: dict[str, Any], module_key: str) -> bool:
    """Abre transacción propia si no hay una pendiente; devuelve si es propia."""
    if doc.HasPendingTransaction:
        return False
    doc.openTransaction(
        f"Crear y colocar {spec.get('label', module_key)}")
    return True


def _colocar_interactivo(obj: Any, spec: dict[str, Any], abrir_panel: Callable[..., None],
                         colocar: Callable[..., None], confirmar: Callable[[], None],
                         cancelar: Callable[[], None]) -> None:
    import FreeCAD as App
    App.Console.PrintMessage("[VDO] " + diagnostico_viewprovider(obj) + "\n")
    _cad_ocultar_vista(obj)

    estado = {"aceptado": False}

    def on_accept() -> None:
        # Un panel puede disparar Aceptar dos veces: solo la primera cuenta.
        if estado["aceptado"]:
            return
        estado["aceptado"] = True
        colocar(obj, on_done=confirmar, on_cancel=cancelar)

    def on_cancel() -> None:
        if estado["aceptado"]:
            return
        estado["aceptado"] = True
        cancelar()

    try:
        abrir_panel(spec, obj, on_accept, on_cancel)
    except (RuntimeError, ValueError, TypeError, KeyError):
        # Error de la interfaz: se deshace lo creado y se propaga (no se oculta).
        cancelar()
        raise


def crear_hoja(doc, dto: HojaDTO) -> HojaResultado:
    """Asegura el entorno Guardián en el documento recibido."""
    if doc is None:
        raise ValueError("Documento requerido para crear la hoja.")
    vdo_guard(doc)
    return HojaResultado(nombre=doc.Name or dto.nombre)


def crear_panel(doc, dto: PanelDTO) -> PanelResultado:
    """Crea un panel en el documento usando el plano puro de core/."""
    if doc is None:
        raise ValueError("Documento requerido para crear el panel.")
    cfg = {
        "nombre": dto.nombre,
        "etiqueta": dto.etiqueta,
        "orientacion": dto.orientacion,
        "largo": dto.largo,
        "ancho": dto.ancho,
        "espesor": dto.espesor,
        "cantos": dto.cantos,
        "material_ref": dto.material_ref,
        "usar_params": dto.usar_params,
        "rotacion": dto.rotacion,
        "anclaje": dto.anclaje,
    }
    obj = crear_pieza(doc, cfg)
    if obj is None:
        return PanelResultado(nombre=dto.nombre, volumen=0.0)
    return PanelResultado(nombre=obj.Name, volumen=float(obj.Shape.Volume))


def crear_zocalo(doc, dto: ZocaloDTO) -> ZocaloResultado:
    """Crea un zócalo en el documento usando el plano puro de core/."""
    if doc is None:
        raise ValueError("Documento requerido para crear el zócalo.")
    cfg = {
        "nombre": dto.nombre,
        "ancho": dto.ancho,
        "fondo": dto.fondo,
        "alto_zocalo": dto.alto_zocalo,
        "espesor_tablero": dto.espesor_tablero,
        "distancia_frente": dto.distancia_frente,
        "distancia_costados": dto.distancia_costados,
        "distancia_trasera": dto.distancia_trasera,
        "tiene_trasera": dto.tiene_trasera,
        "amarres_intermedios": dto.amarres_intermedios,
        "material_ref": dto.material_ref,
        "rotacion": dto.rotacion,
        "anclaje": dto.anclaje,
    }
    obj = make_zocalo(doc, cfg)
    if obj is None:
        return ZocaloResultado(nombre=dto.nombre, volumen=0.0)
    return ZocaloResultado(nombre=obj.Name, volumen=float(obj.Shape.Volume))


def crear_cajon(doc, dto: CajonDTO) -> CajonResultado:
    """Crea un cajón en el documento usando el plano puro de core/."""
    if doc is None:
        raise ValueError("Documento requerido para crear el cajón.")
    cfg = {
        "nombre": dto.nombre,
        "ancho_libre": dto.ancho_libre,
        "prof_libre": dto.prof_libre,
        "ancho_modulo": dto.ancho_modulo,
        "alto_frente": dto.alto_frente,
        "alto_caja": dto.alto_caja,
        "grosor_caja": dto.grosor_caja,
        "grosor_fondo": dto.grosor_fondo,
        "grosor_fachada": dto.grosor_fachada,
        "marca": dto.marca,
        "longitud_guia": dto.longitud_guia,
        "montaje_trasera": dto.montaje_trasera,
        "tipo_corredera": dto.tipo_corredera,
        "sistema_apertura": dto.sistema_apertura,
        "tipo_montaje": dto.tipo_montaje,
        "material_ref": dto.material_ref,
        "rotacion": dto.rotacion,
        "anclaje": dto.anclaje,
    }
    obj = make_cajon(doc, cfg)
    if obj is None:
        return CajonResultado(nombre=dto.nombre, tipo_corredera="")
    return CajonResultado(nombre=obj.Name, tipo_corredera=str(obj.TipoCorredera))


def crear_puerta(doc, dto: PuertaDTO) -> PuertaResultado:
    """Crea una puerta en el documento usando el plano puro de core/."""
    if doc is None:
        raise ValueError("Documento requerido para crear la puerta.")
    cfg = {
        "nombre": dto.nombre,
        "tipo_sistema": "Batiente Vertical",
        "tipo_montaje": dto.tipo_montaje,
        "sentido_apertura": "Izquierda",
        "sistema_apertura": dto.sistema_apertura,
        "hardware_sku": "",
        "vdo_vano_id": "",
        "ancho": dto.ancho,
        "alto": dto.alto,
        "espesor": dto.espesor,
        "pos_x": 0.0,
        "pos_y": 0.0,
        "pos_z": 0.0,
        "anclaje": dto.anclaje,
    }
    obj = make_puerta(doc, cfg)
    if obj is None:
        return PuertaResultado(nombre=dto.nombre, alto=0.0)
    return PuertaResultado(nombre=obj.Name, alto=float(obj.Alto))


def crear_coco(doc, dto: CocoDTO) -> CocoResultado:
    """Crea un COCO en el documento usando el plano puro de core/."""
    if doc is None:
        raise ValueError("Documento requerido para crear el COCO.")
    cfg = {
        "nombre": dto.nombre,
        "alto": dto.alto,
        "ancho": dto.ancho,
        "fondo_modulo": dto.fondo_modulo,
        "espesor": dto.espesor,
        "tiene_fondo": dto.tiene_fondo,
        "calibre_fondo": dto.calibre_fondo,
        "divisiones": dto.divisiones,
        "reengroses": dto.reengroses or {},
        "rotacion": dto.rotacion,
        "anclaje": dto.anclaje,
        "lados_vistos": dto.lados_vistos or ["frente"],
        "lados_apoyados": dto.lados_apoyados or ["fondo"],
    }
    obj = make_coco(doc, cfg)
    if obj is None:
        return CocoResultado(nombre=dto.nombre, volumen=0.0)
    return CocoResultado(nombre=obj.Name, volumen=float(obj.Shape.Volume))
