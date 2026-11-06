"""Nivel 2: flujo de creación con panel y colocación (regresión F5).

Antes de F19.2-ter, app/vdo_creacion.crear_modulo_interactivo no abría el panel
ni llamaba a la colocación: el módulo quedaba oculto en el origen. Estos tests
fijan el flujo: crear -> abrir panel -> aceptar -> colocar -> confirmar, y
crear -> cancelar -> deshacer. La interfaz gráfica se sustituye por funciones
que registran las llamadas; la colocación real (ui/vdo_placement) se ejecuta
sin GUI, donde debe cancelar y devolver False.
"""

from __future__ import annotations

import unittest

import FreeCAD as App

import math

from freecad.vdo.creacion import crear_modulo_interactivo
from freecad.vdo.core.vdo_coco_core import make_coco
from freecad.vdo.core.vdo_panel_core import crear_pieza
from freecad.vdo.cad.zocalo import make_zocalo
from freecad.vdo.ui.vdo_placement import iniciar_colocacion
from tests.soporte.requisitos import requiere_freecad, requiere_qt


@requiere_freecad
class FlujoCreacionColocacionTests(unittest.TestCase):
    def setUp(self):
        self.doc = App.newDocument("TestFlujoColocacion")
        App.setActiveDocument(self.doc.Name)

    def tearDown(self):
        App.closeDocument(self.doc.Name)

    def _interfaz_falsa(self):
        llamadas = {"panel": None, "colocados": [], "colocar_on_done": None}

        def abrir_panel(spec, obj, on_accept, on_cancel):
            llamadas["panel"] = (spec["panel_ref"], obj.Name, on_accept, on_cancel)

        def colocar(obj, on_done, on_cancel):
            llamadas["colocados"].append(obj.Name)
            llamadas["colocar_on_done"] = on_done
            llamadas["colocar_on_cancel"] = on_cancel

        return llamadas, abrir_panel, colocar

    def test_sin_interfaz_confirma_en_origen(self):
        obj = crear_modulo_interactivo("panel_estandar", {"nombre": "Panel_Headless"})
        self.assertIsNotNone(obj)
        self.assertIsNotNone(self.doc.getObject(obj.Name))
        self.assertFalse(self.doc.HasPendingTransaction)

    def test_aceptar_abre_panel_y_coloca_el_modulo(self):
        llamadas, abrir_panel, colocar = self._interfaz_falsa()
        obj = crear_modulo_interactivo(
            "panel_estandar", {"nombre": "Panel_Flujo"},
            abrir_panel=abrir_panel, colocar=colocar)

        self.assertIsNotNone(llamadas["panel"], "el panel debe abrirse")
        panel_ref, nombre_panel, on_accept, _on_cancel = llamadas["panel"]
        self.assertEqual(panel_ref, "panel.panel")
        self.assertEqual(nombre_panel, obj.Name)

        on_accept()
        self.assertEqual(llamadas["colocados"], [obj.Name],
                         "al aceptar el panel debe iniciarse la colocación")

        # HasPendingTransaction es siempre False en freecadcmd: no se afirma sobre él.
        llamadas["colocar_on_done"]()
        self.assertIsNotNone(self.doc.getObject(obj.Name),
                             "confirmar debe conservar el módulo colocado")

    def test_aceptar_dos_veces_coloca_una_sola(self):
        llamadas, abrir_panel, colocar = self._interfaz_falsa()
        crear_modulo_interactivo(
            "panel_estandar", {"nombre": "Panel_Doble"},
            abrir_panel=abrir_panel, colocar=colocar)
        _ref, _nombre, on_accept, _on_cancel = llamadas["panel"]
        on_accept()
        on_accept()
        self.assertEqual(len(llamadas["colocados"]), 1)

    def test_cancelar_panel_borra_el_modulo(self):
        llamadas, abrir_panel, colocar = self._interfaz_falsa()
        obj = crear_modulo_interactivo(
            "panel_estandar", {"nombre": "Panel_Cancelado"},
            abrir_panel=abrir_panel, colocar=colocar)
        _ref, nombre, _on_accept, on_cancel = llamadas["panel"]
        on_cancel()
        self.assertEqual(llamadas["colocados"], [])
        self.assertIsNone(self.doc.getObject(nombre))
        self.assertIsNotNone(obj)

    def test_colocacion_real_sin_gui_cancela_y_devuelve_falso(self):
        # Sin FreeCADGui, ColocadorModulo no puede iniciar: debe cancelar, no fallar.
        obj = crear_modulo_interactivo("panel_estandar", {"nombre": "Panel_Real"})
        cancelado = []
        resultado = iniciar_colocacion(
            obj, on_done=lambda: None, on_cancel=lambda: cancelado.append(True))
        self.assertFalse(resultado)
        self.assertEqual(cancelado, [True])


@requiere_freecad
class RotacionCreacionTests(unittest.TestCase):
    """Regresión: con rotación ≠ 0, la creación fallaba con AttributeError
    (core llamaba a VDO_MOD.rotacion_z, que no existe)."""

    def setUp(self):
        self.doc = App.newDocument("TestRotacionCreacion")

    def tearDown(self):
        App.closeDocument(self.doc.Name)

    def _angulo_grados(self, obj):
        return math.degrees(obj.Placement.Rotation.Angle)

    def test_coco_con_rotacion(self):
        obj = make_coco(self.doc, {"nombre": "C_Rot", "alto": 700.0,
                                   "ancho": 600.0, "fondo_modulo": 580.0,
                                   "rotacion": 90.0})
        self.assertAlmostEqual(self._angulo_grados(obj), 90.0, places=6)

    def test_panel_con_rotacion(self):
        obj = crear_pieza(self.doc, {"nombre": "P_Rot", "etiqueta": "P",
                                     "orientacion": "horizontal", "largo": 600.0,
                                     "ancho": 400.0, "espesor": 18.0,
                                     "usar_params": False, "rotacion": 90.0})
        self.assertAlmostEqual(self._angulo_grados(obj), 90.0, places=6)

    def test_zocalo_con_rotacion(self):
        obj = make_zocalo(self.doc, {"nombre": "Z_Rot", "rotacion": 90.0})
        self.assertAlmostEqual(self._angulo_grados(obj), 90.0, places=6)


@requiere_freecad
@requiere_qt
class PanelesResuelvenTests(unittest.TestCase):
    """Cada módulo creable debe tener clase de panel real (regresión: panel.puerta
    fallaba con ImportError porque SISTEMAS_APERTURA se había movido)."""

    def test_todas_las_specs_tienen_clase_de_panel(self):
        from freecad.vdo.core.vdo_module_specs import MODULE_SPECS, get_spec
        from freecad.vdo.ui import vdo_interfaz

        fallos = []
        for clave in MODULE_SPECS:
            ref = get_spec(clave)["panel_ref"]
            try:
                vdo_interfaz._clase_panel(ref)
            except (ImportError, AttributeError, KeyError) as exc:
                fallos.append(f"{clave} -> {ref}: {exc}")
        self.assertEqual(fallos, [])


if __name__ == "__main__":
    unittest.main()
