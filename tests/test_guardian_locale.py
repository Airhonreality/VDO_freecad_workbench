"""Nivel 2: el guardián escribe números que FreeCAD lee igual en cualquier locale (D-11).

Escribe valores con ``_asegurar_parametros``, relee las celdas y compara con el valor
original. Se repite con LC_NUMERIC=es_CO.UTF-8 (coma decimal) y con LC_NUMERIC=C.
El locale se fuerza con setlocale: Python no lo cambia por sí solo al arrancar.
"""

from __future__ import annotations

import locale
import unittest

from tests.soporte.requisitos import requiere_freecad

_LOCALES_PRUEBA = ("es_CO.UTF-8", "C")


def _valores_del_manifiesto() -> dict:
    """Todos los parámetros que escribe el guardián, leídos del manifiesto (D-13)."""
    from freecad.vdo.core import vdo_manifest as VM

    valores = {}
    valores.update(VM.VDO_MANIFEST["parametros_globales"])
    valores.update(VM.VDO_MANIFEST["parametros_locales"])
    return valores


_VALORES = _valores_del_manifiesto()


def _locale_disponible(nombre: str) -> bool:
    actual = locale.setlocale(locale.LC_NUMERIC)
    try:
        locale.setlocale(locale.LC_NUMERIC, nombre)
    except locale.Error:
        return False
    finally:
        locale.setlocale(locale.LC_NUMERIC, actual)
    return True


@requiere_freecad
class GuardianLocaleTests(unittest.TestCase):

    def _escribir_y_leer(self, nombre_locale: str, fila_valor: str) -> dict:
        import FreeCAD as App

        from freecad.vdo.cad import vdo_guardian as G

        actual = locale.setlocale(locale.LC_NUMERIC)
        locale.setlocale(locale.LC_NUMERIC, nombre_locale)
        doc = App.newDocument("GuardianLocale")
        try:
            hoja = doc.addObject("Spreadsheet::Sheet", "Params")
            G._asegurar_parametros(
                hoja, fila_inicio=2, fila_valor=fila_valor,
                fila_descripcion="C", parametros=_VALORES,
            )
            doc.recompute()
            leidos = {}
            for fila, nombre in enumerate(_VALORES, start=2):
                celda = f"{fila_valor}{fila}"
                leidos[nombre] = hoja.get(celda)
            return leidos
        finally:
            App.closeDocument(doc.Name)
            locale.setlocale(locale.LC_NUMERIC, actual)

    def test_valores_se_releen_igual_en_cada_locale(self):
        for nombre_locale in _LOCALES_PRUEBA:
            if not _locale_disponible(nombre_locale):
                self.skipTest(f"locale {nombre_locale} no instalado en este equipo")
            for fila_valor in ("A", "B"):
                with self.subTest(locale=nombre_locale, columna=fila_valor):
                    leidos = self._escribir_y_leer(nombre_locale, fila_valor)
                    for nombre, info in _VALORES.items():
                        self.assertEqual(
                            leidos[nombre], float(info["valor"]),
                            f"{nombre} con {nombre_locale}: leído {leidos[nombre]!r}",
                        )

    def test_valor_que_desborda_2_53_lanza_error(self):
        from freecad.vdo.cad import vdo_guardian as G
        from freecad.vdo.core.errores import ParametroInvalido

        with self.assertRaises(ParametroInvalido):
            G._celda_numerica(1e16)

    def test_mismo_resultado_en_ambos_locales(self):
        if not all(_locale_disponible(n) for n in _LOCALES_PRUEBA):
            self.skipTest("faltan locales de prueba en este equipo")
        por_locale = {n: self._escribir_y_leer(n, "B") for n in _LOCALES_PRUEBA}
        self.assertEqual(por_locale["es_CO.UTF-8"], por_locale["C"])


if __name__ == "__main__":
    unittest.main()
