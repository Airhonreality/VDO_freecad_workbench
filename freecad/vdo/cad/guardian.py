"""cad/guardian.py — Escritura del entorno Guardián en el documento FreeCAD.

Esta es la parte CAD (capa cad/) del Guardián. Crea y asegura hojas de
cálculo (Params_Melamina y Params) en el documento activo, inyectando los
parámetros del manifiesto.

No contiene lógica de dominio: solo escribe lo que core/planifica.
"""

from __future__ import annotations

from fractions import Fraction

import FreeCAD as App

from freecad.vdo.core import defaults as VDO_D
from freecad.vdo.core import manifest as VM
from freecad.vdo.core.errores import ParametroInvalido

HOJA_GLOBAL = "Params_Melamina"
HOJA_LOCAL = "Params"


def _obtener_hoja(doc, nombre):
    """Obtiene la hoja de cálculo ``nombre``; la crea si no existe."""
    hoja = doc.getObject(nombre)
    if hoja is None:
        hoja = doc.addObject("Spreadsheet::Sheet", nombre)
        hoja.Label = nombre
    return hoja


def _tiene_alias(hoja, celda):
    return hoja.getAlias(celda) is not None


# Por encima de 2^53 un entero no se representa exactamente como double.
LIMITE_EXACTO = 2 ** 53


def _celda_numerica(valor):
    """Contenido de celda que FreeCAD lee igual con cualquier LC_NUMERIC.

    Con locale de coma decimal, FreeCAD lee "0.4" como 0 (D-11). Las
    fracciones enteras "=N/D" no tienen separador decimal: se parsean igual
    en cualquier locale. Se redondea a 10 decimales (D-13) para que el
    denominador quede acotado. Si numerador o denominador superan 2^53, se
    lanza ParametroInvalido: no se escribe un valor incorrecto en silencio.
    """
    fraccion = Fraction(repr(round(float(valor), 10)))
    if max(abs(fraccion.numerator), fraccion.denominator) > LIMITE_EXACTO:
        raise ParametroInvalido(
            "valor no representable exactamente en una celda de hoja",
            {"valor": valor, "numerador": fraccion.numerator,
             "denominador": fraccion.denominator})
    if fraccion.denominator == 1:
        return str(fraccion.numerator)
    return f"={fraccion.numerator}/{fraccion.denominator}"


def _asegurar_parametros(hoja, fila_inicio, fila_valor, fila_descripcion,
                         parametros):
    """Inyecta etiqueta/valor+alias/descripcion en cada fila de parametros.

    Solo escribe celdas sin alias: respeta cualquier valor ya editado.
    """
    for fila, (nombre, info) in enumerate(parametros.items(), start=fila_inicio):
        celda_valor = f"{fila_valor}{fila}"
        if _tiene_alias(hoja, celda_valor):
            continue
        if fila_valor == "A":
            hoja.set(f"A{fila}", _celda_numerica(info["valor"]))
            hoja.setAlias(f"A{fila}", nombre)
        else:
            hoja.set(f"A{fila}", f"'{nombre}")
            hoja.set(f"{fila_valor}{fila}", _celda_numerica(info["valor"]))
            hoja.setAlias(f"{fila_valor}{fila}", nombre)
        if info.get("descripcion"):
            hoja.set(f"{fila_descripcion}{fila}", f"'{info['descripcion']}")
        App.Console.PrintMessage(
            f"[VDO Guardian] Parametro '{nombre}' = {info['valor']} mm")


def asegurar_hoja_global(doc):
    """Capa Global (Reglas de Taller): hoja Params_Melamina."""
    nombre = VM.VDO_MANIFEST.get("capa_global", {}).get("hoja", HOJA_GLOBAL)
    hoja = _obtener_hoja(doc, nombre)

    if not hoja.getContents("A1"):
        hoja.set("A1", "'Parametro")
        hoja.set("B1", "'Valor")
        hoja.set("C1", "'Descripcion")

    _asegurar_parametros(
        hoja,
        fila_inicio=2,
        fila_valor="B",
        fila_descripcion="C",
        parametros=VM.VDO_MANIFEST["parametros_globales"],
    )
    return hoja


def asegurar_params_local(doc):
    """Capa Local (Contenedores y Módulos): hoja Params del módulo."""
    nombre = VM.VDO_MANIFEST.get("capa_local", {}).get("hoja", HOJA_LOCAL)
    hoja = _obtener_hoja(doc, nombre)

    _asegurar_parametros(
        hoja,
        fila_inicio=1,
        fila_valor="A",
        fila_descripcion="B",
        parametros=VM.VDO_MANIFEST["parametros_locales"],
    )
    return hoja


def asegurar_documento():
    """Devuelve el documento activo, creando uno si no hay ninguno."""
    doc = App.ActiveDocument
    if doc is None:
        doc = App.newDocument("VDO")
        App.Console.PrintMessage(
            "[VDO Guardian] No había documento activo; se creó VDO.")
    return doc


def vdo_guard(doc=None):
    """Punto de entrada: valida el documento e inyecta el entorno completo."""
    if doc is None:
        doc = asegurar_documento()

    hoja_global = asegurar_hoja_global(doc)
    hoja_local = asegurar_params_local(doc)

    doc.recompute()
    version = VM.VDO_MANIFEST["version"]
    App.Console.PrintMessage(f"[VDO Guardian] Entorno asegurado v{version}: "
          f"{hoja_global.Name} + {hoja_local.Name}")
    return doc
