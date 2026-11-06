import os
import unittest

from freecad.vdo.core import vdo_reengrose_despiece as R_DESPIECE
from freecad.vdo.core import vdo_reengrose_geometria as R_GEOMETRIA
from freecad.vdo.core import vdo_reengrose_interferencias as R_INTERFERENCIAS
from freecad.vdo.core import vdo_reengrose_modelo as R_MODELO
from freecad.vdo.core import vdo_reengrose_modificador as R_MODIFICADOR


class ReengrosePureTests(unittest.TestCase):
    def setUp(self):
        self.panel = {
            "nombre": "P", "largo": 600.0, "ancho": 400.0,
            "espesor": 18.0, "cantos": {"norte": "RIG"},
        }

    def test_defaults_and_validation(self):
        mod = R_MODIFICADOR.ReengroseModifier()
        self.assertFalse(mod.activo)
        self.assertEqual(mod.orientacion, "paralela")
        self.assertEqual(mod.ancho, 70.0)
        self.assertIsNone(mod.espesor)
        with self.assertRaises(R_MODELO.ReengroseError):
            R_MODIFICADOR.ReengroseModifier({"ancho": 0})
        with self.assertRaises(R_MODELO.ReengroseError):
            R_MODIFICADOR.ReengroseModifier({"orientacion": "diagonal"})

    def test_paralela_cara_a(self):
        mod = R_MODIFICADOR.ReengroseModifier({
            "activo": True, "ancho": 70, "cara": "cara_a",
            "alineacion_profundidad": "frente"})
        geo = R_GEOMETRIA.calcular_geometria_reengrose(self.panel, mod)
        ref = geo["refuerzos"][0]
        self.assertEqual((ref["largo"], ref["ancho"]), (600.0, 70.0))
        self.assertEqual((ref["x"], ref["y"], ref["z"]), (0.0, 0.0, 18.0))

    def test_paralela_fondo_y_cara_b(self):
        mod = R_MODIFICADOR.ReengroseModifier({
            "activo": True, "ancho": 70, "cara": "cara_b",
            "alineacion_profundidad": "fondo"})
        ref = R_GEOMETRIA.calcular_geometria_reengrose(self.panel, mod)["refuerzos"][0]
        self.assertEqual((ref["y"], ref["z"]), (330.0, -18.0))

    def test_transversal(self):
        mod = R_MODIFICADOR.ReengroseModifier({
            "activo": True, "ancho": 70, "orientacion": "transversal"})
        ref = R_GEOMETRIA.calcular_geometria_reengrose(self.panel, mod)["refuerzos"][0]
        self.assertEqual((ref["largo"], ref["ancho"]), (400.0, 70.0))
        self.assertEqual(ref["x"], 265.0)

    def test_pacha_total(self):
        mod = R_MODIFICADOR.ReengroseModifier({
            "activo": True, "modo_fabricacion": "pacha",
            "alcance": "total"})
        ref = R_GEOMETRIA.calcular_geometria_reengrose(self.panel, mod)["refuerzos"][0]
        self.assertEqual((ref["largo"], ref["ancho"]), (600.0, 400.0))

    def test_politica_cantos(self):
        indep = R_MODIFICADOR.ReengroseModifier({
            "activo": True, "modo_fabricacion": "independiente"})
        plan = R_DESPIECE.resolver_politica_cantos(self.panel, indep)
        self.assertEqual(plan["base"]["norte"], "RIG")
        self.assertEqual(plan["tira"]["norte"], "RIG")
        pacha = R_MODIFICADOR.ReengroseModifier({
            "activo": True, "modo_fabricacion": "pacha"})
        plan = R_DESPIECE.resolver_politica_cantos(self.panel, pacha)
        self.assertEqual(plan["base"]["norte"], "FX")
        self.assertEqual(plan["bloque"]["norte"], "RIG")

    def test_colision_y_mocheo(self):
        repisa = {"x": 0, "y": 0, "z": 0, "w": 500, "h": 400, "d": 18}
        choque = {"x": 480, "y": 0, "z": 0, "w": 18, "h": 70, "d": 18}
        libre = {"x": 100, "y": 0, "z": 40, "w": 18, "h": 70, "d": 18}
        self.assertIsNone(R_INTERFERENCIAS.generar_mocheo_repisa(repisa, libre))
        retro = R_INTERFERENCIAS.generar_mocheo_repisa(repisa, choque)
        self.assertEqual(retro["modo"], "retroceder")
        self.assertEqual(retro["recorte_x"], 18.0)
        moche = R_INTERFERENCIAS.generar_mocheo_repisa(repisa, choque, "mochear")
        self.assertEqual(moche["modo"], "mochear")
        self.assertEqual(moche["moche"]["w"], 18.0)
        self.assertEqual(moche["moche"]["h"], 70.0)

    def test_vano_neto(self):
        resultado = R_INTERFERENCIAS.calcular_vano_neto_con_reengrose(
            {"ancho": 500, "alto": 700},
            {"lado_afectado": "izquierda", "espesor_extra": 18})
        self.assertEqual(resultado["ancho"], 482.0)
        self.assertEqual(resultado["desplazamiento_x"], 18.0)

    def test_despiece_pacha(self):
        mod = R_MODIFICADOR.ReengroseModifier({
            "activo": True, "modo_fabricacion": "pacha"})
        piezas = R_DESPIECE.despiece_panel("P", 600, 400, 18, mod, cantos={})
        self.assertEqual(len(piezas), 2)
        self.assertEqual(piezas[0]["grupo_pacha"], "Pacha_P")
        self.assertEqual(piezas[0]["cantos"]["norte"], "FX")
        self.assertEqual(piezas[0]["cantos_bloque"]["norte"], "RIG")


if __name__ == "__main__":
    unittest.main()
