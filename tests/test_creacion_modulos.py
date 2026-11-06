"""Tests de nivel 2: creación de módulos (H1, H2, H3).

Cada test crea su propio documento, llama a la función de creación pasándole
el documento, y verifica que el objeto devuelto tiene Shape válido.
"""

from __future__ import annotations

import unittest

import FreeCAD as App

from freecad.vdo.cad.cajon import make_cajon
from freecad.vdo.cad.coco import make_coco
from freecad.vdo.cad.panel import crear_pieza
from freecad.vdo.cad.zocalo import make_zocalo
from tests.soporte.requisitos import requiere_freecad


@requiere_freecad
class CreacionModulosTests(unittest.TestCase):
    def setUp(self):
        self.doc = App.newDocument("TestCreacionModulos")

    def tearDown(self):
        App.closeDocument(self.doc.Name)

    def test_crear_pieza_devuelve_panel_con_shape(self):
        obj = crear_pieza(
            self.doc,
            {
                "nombre": "Panel_Test",
                "etiqueta": "Panel Test",
                "orientacion": "horizontal",
                "largo": 600.0,
                "ancho": 400.0,
                "espesor": 18.0,
                "usar_params": False,
            },
        )
        self.assertIsNotNone(obj)
        self.assertIsNotNone(obj.Shape)
        self.assertGreater(obj.Shape.Volume, 0)

    def test_make_coco_devuelve_objeto_con_shape(self):
        obj = make_coco(
            self.doc,
            {"nombre": "COCO_Test", "alto": 700.0, "ancho": 600.0, "fondo_modulo": 580.0},
        )
        self.assertIsNotNone(obj)
        self.assertIsNotNone(obj.Shape)

    def test_make_zocalo_devuelve_objeto_con_shape(self):
        obj = make_zocalo(
            self.doc,
            {"nombre": "Zocalo_Test", "ancho": 600.0, "fondo": 580.0, "alto_zocalo": 100.0},
        )
        self.assertIsNotNone(obj)
        self.assertIsNotNone(obj.Shape)

    def test_make_cajon_devuelve_objeto_con_shape(self):
        obj = make_cajon(
            self.doc,
            {"nombre": "Cajon_Test", "ancho_libre": 564.0, "prof_libre": 560.0, "ancho_modulo": 600.0},
        )
        self.assertIsNotNone(obj)
        self.assertIsNotNone(obj.Shape)

    def test_crear_pieza_sin_doc_devuelve_none(self):
        obj = crear_pieza(None, {"nombre": "X", "orientacion": "horizontal"})
        self.assertIsNone(obj)


if __name__ == "__main__":
    unittest.main()
