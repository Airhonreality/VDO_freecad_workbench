# -*- coding: utf-8 -*-
# =====================================================================
# vdo_guardian.py
# Guardián de Dependencias VDO — PARTE PURA (core/).
#
# Define qué parámetros asegurar en cada hoja de cálculo y valida el
# entorno. La escritura efectiva en el documento FreeCAD se hace en
# cad/vdo_guardian.py (capa cad/). Este modulo no importa FreeCAD ni Qt.
# =====================================================================

from __future__ import annotations

from freecad.vdo.core import vdo_manifest as VM

HOJA_GLOBAL = "Params_Melamina"
HOJA_LOCAL = "Params"


def planificar_guardian(manifest: dict | None = None) -> dict:
    """Devuelve el plan de qué asegurar en cada hoja (datos puros).

    Args:
        manifest: dict del manifiesto. Si None, se carga fresco por llamada.

    Returns:
        {
          "hoja_global": {"nombre": str, "cabeceras": [...], "parametros": {...}},
          "hoja_local": {"nombre": str, "cabeceras": [...], "parametros": {...}},
          "version": str,
        }
    """
    if manifest is None:
        from freecad.vdo.core.vdo_manifest import _obtener_json as _cargar
        manifest = _cargar()

    capa_global = manifest.get("capa_global", {})
    capa_local = manifest.get("capa_local", {})
    nombre_global = capa_global.get("hoja", HOJA_GLOBAL)
    nombre_local = capa_local.get("hoja", HOJA_LOCAL)

    return {
        "hoja_global": {
            "nombre": nombre_global,
            "cabeceras": ["'Parametro", "'Valor", "'Descripcion"],
            "parametros": manifest.get("parametros_globales", {}),
        },
        "hoja_local": {
            "nombre": nombre_local,
            "cabeceras": ["'Parametro", "'Valor", "'Descripcion"],
            "parametros": manifest.get("parametros_locales", {}),
        },
        "version": manifest.get("version", "1.0.0"),
    }


def asegurar_hoja_global(doc) -> object:
    """Escribe la hoja global en el documento recibido (no importa FreeCAD).

    ``doc`` es un objeto documento de FreeCAD (proporcionado por cad/ o app/).
    """
    from freecad.vdo.core.vdo_manifest import _obtener_json as _cargar
    manifest = _cargar()
    nombre = manifest.get("capa_global", {}).get("hoja", HOJA_GLOBAL)
    hoja = doc.getObject(nombre)
    if hoja is None:
        hoja = doc.addObject("Spreadsheet::Sheet", nombre)
        hoja.Label = nombre

    if not hoja.getContents("A1"):
        hoja.set("A1", "'Parametro")
        hoja.set("B1", "'Valor")
        hoja.set("C1", "'Descripcion")

    _asegurar_parametros(
        hoja,
        fila_inicio=2,
        fila_valor="B",
        fila_descripcion="C",
        parametros=manifest.get("parametros_globales", {}),
    )
    return hoja


def asegurar_params_local(doc) -> object:
    """Escribe la hoja local en el documento recibido (no importa FreeCAD)."""
    from freecad.vdo.core.vdo_manifest import _obtener_json as _cargar
    manifest = _cargar()
    nombre = manifest.get("capa_local", {}).get("hoja", HOJA_LOCAL)
    hoja = doc.getObject(nombre)
    if hoja is None:
        hoja = doc.addObject("Spreadsheet::Sheet", nombre)
        hoja.Label = nombre

    _asegurar_parametros(
        hoja,
        fila_inicio=1,
        fila_valor="A",
        fila_descripcion="B",
        parametros=manifest.get("parametros_locales", {}),
    )
    return hoja


def _asegurar_parametros(hoja, fila_inicio, fila_valor, fila_descripcion,
                         parametros):
    for fila, (nombre, info) in enumerate(parametros.items(), start=fila_inicio):
        celda_valor = f"{fila_valor}{fila}"
        if hoja.getAlias(celda_valor) is not None:
            continue
        if fila_valor == "A":
            hoja.set(f"A{fila}", str(info["valor"]))
            hoja.setAlias(f"A{fila}", nombre)
        else:
            hoja.set(f"A{fila}", f"'{nombre}")
            hoja.set(f"{fila_valor}{fila}", str(info["valor"]))
            hoja.setAlias(f"{fila_valor}{fila}", nombre)
        if "descripcion" in info and info["descripcion"]:
            hoja.set(f"{fila_descripcion}{fila}", f"'{info['descripcion']}")


def vdo_guard(doc=None):
    """Asegura el entorno en el documento recibido.

    Si doc es None, no se puede crear un documento desde core/ (eso es
    responsabilidad de cad/ o app/). Devuelve doc tal cual.
    """
    if doc is None:
        return None
    asegurar_hoja_global(doc)
    asegurar_params_local(doc)
    doc.recompute()
    plan = planificar_guardian()
    return doc
