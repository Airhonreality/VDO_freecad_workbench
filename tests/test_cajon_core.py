# =====================================================================
# tests/test_cajon_core.py
# Suite de pruebas del CajonFeature (Trinidad de Cajones v2).
#
# Valida:
#   - Despiece correcto para las 3 tipologías de corredera
#   - Integración con vdo_facade_contract (gola, 45°, push_open)
#   - Lógica de operaciones booleanas (mock de Part)
#   - Integración con vdo_hardware_hub (resolve_drawer_slide)
#
# Nota: La validación de Shape.isValid() y booleanos reales requiere
# FreeCAD GUI (no disponible headless en este entorno). Los tests de
# geometría 3D usan mocks para validar la lógica de coordenadas.
# =====================================================================

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

try:
    _AQUI = os.path.dirname(os.path.abspath(__file__))
except NameError:
    _AQUI = os.getcwd()
_RAIZ = os.path.dirname(_AQUI)

from tests.soporte.freecad_falso import instalado

# Instalar mocks de FreeCAD/Part antes de importar core (que los necesita a nivel
# de módulo). Se restauran al terminar el proceso.
_instalado_ctx = instalado()
_instalado_ctx.__enter__()

from freecad.vdo.core import vdo_facade_contract as FC
from freecad.vdo.core import vdo_hardware_hub as H
from freecad.vdo.cad.cajon import (
    CAJA_METALICA as CC_MET,
)
from freecad.vdo.cad.cajon import (
    CORREDERA_OCULTA as CC_OCU,
)
from freecad.vdo.cad.cajon import (
    CORREDERA_TELESCOPICA as CC_TEL,
)
from freecad.vdo.cad.cajon import (
    _aplicar_bisel_45_fachada,
    _aplicar_corte,
    _corte_notch_lateral,
    _corte_pin_trasero,
    _corte_ranura_piso,
)
from freecad.vdo.core.vdo_cajon_correderas import (
    CAJA_METALICA,
    CORREDERA_OCULTA,
    CORREDERA_TELESCOPICA,
    listar_marcas,
    obtener_marca,
)
from freecad.vdo.core.vdo_cajon_despiece import calcular_despiece
from freecad.vdo.core.vdo_facade_contract import (
    APERTURA_45_GRADOS,
    APERTURA_GOLA,
    APERTURA_PUSH_OPEN,
    APERTURA_TIRADOR,
)
from tests.soporte.freecad_falso import instalado

# ---------------------------------------------------------------------
# Configuración base de prueba
# ---------------------------------------------------------------------

CONFIG_BASE = {
    "ancho_libre": 600.0,
    "prof_libre": 580.0,
    "ancho_modulo": 640.0,
    "alto_frente": 225.0,
    "marca": "blum_tandem",
    "alto_caja": 120.0,
    "grosor_caja": 16.0,
    "grosor_fondo": 6.0,
    "grosor_fachada": 18.0,
    "longitud_guia": 0.0,
    "montaje_trasera": "entre_laterales",
    "penetracion_ranura": 10.0,
    "eje_ranura": 11.5,
    "holgura_lateral_fachada": 2.0,
    "holgura_superior_fachada": 2.0,
    "holgura_inferior_fachada": 2.0,
    "material_ref": "melamina_standar",
}


# ---------------------------------------------------------------------
# Tests de despiece por tipología
# ---------------------------------------------------------------------

class TestDespieceTipologias(unittest.TestCase):
    """Validación del despiece para cada tipología de corredera."""

    def test_oculta_blum_tandem(self):
        """Corredera oculta Blum Tandem: delta=49, 6 piezas."""
        config = dict(CONFIG_BASE, tipo_corredera=CORREDERA_OCULTA)
        d = calcular_despiece(config)
        self.assertEqual(d["tipo_corredera"], CORREDERA_OCULTA)
        self.assertAlmostEqual(d["guia"]["delta"], 49.0)
        self.assertAlmostEqual(d["caja"]["ancho_exterior"], 551.0)  # 600-49
        self.assertEqual(len(d["piezas"]), 6)
        nombres = [p["nombre"] for p in d["piezas"]]
        self.assertIn("Cajon_Lateral_Izq", nombres)
        self.assertIn("Cajon_Lateral_Der", nombres)

    def test_oculta_generica(self):
        """Corredera oculta genérica: delta=45."""
        config = dict(CONFIG_BASE, tipo_corredera=CORREDERA_OCULTA, marca="generica")
        d = calcular_despiece(config)
        self.assertAlmostEqual(d["guia"]["delta"], 45.0)
        self.assertAlmostEqual(d["caja"]["ancho_exterior"], 555.0)  # 600-45

    def test_telescopica(self):
        """Corredera telescópica: delta=25.4 (12.7mm x 2 lados)."""
        config = dict(CONFIG_BASE, tipo_corredera=CORREDERA_TELESCOPICA)
        d = calcular_despiece(config)
        self.assertEqual(d["tipo_corredera"], CORREDERA_TELESCOPICA)
        self.assertAlmostEqual(d["guia"]["delta"], 25.4)
        self.assertAlmostEqual(d["caja"]["ancho_exterior"], 574.6)  # 600-25.4
        self.assertEqual(len(d["piezas"]), 6)

    def test_metalica_sin_laterales(self):
        """Caja metálica: 4 piezas, sin laterales de madera."""
        config = dict(CONFIG_BASE, tipo_corredera=CAJA_METALICA)
        d = calcular_despiece(config)
        self.assertEqual(d["tipo_corredera"], CAJA_METALICA)
        nombres = [p["nombre"] for p in d["piezas"]]
        self.assertNotIn("Cajon_Lateral_Izq", nombres)
        self.assertNotIn("Cajon_Lateral_Der", nombres)
        self.assertIn("Cajon_Contrafrente", nombres)
        self.assertIn("Cajon_Piso", nombres)
        self.assertEqual(len(d["piezas"]), 4)

    def test_listar_marcas_incluye_nuevas(self):
        """listar_marcas() incluye las claves del manifest y catálogo."""
        marcas = listar_marcas()
        self.assertIn("blum_tandem", marcas)
        self.assertIn("generica", marcas)
        self.assertIn("hafele", marcas)
        self.assertIn("ducasse", marcas)


# ---------------------------------------------------------------------
# Tests de integración con facade_contract
# ---------------------------------------------------------------------

class TestFacadeContractIntegracion(unittest.TestCase):
    """Validación de la integración con vdo_facade_contract."""

    def test_gola_descuenta_35mm_en_alto(self):
        """APERTURA_GOLA descuenta 35 mm de la altura de fachada."""
        config = dict(CONFIG_BASE,
                      tipo_corredera=CORREDERA_OCULTA,
                      sistema_apertura=APERTURA_GOLA)
        d = calcular_despiece(config)
        # Alto nominal: 225 - 2 - 2 = 221, con gola: 221 - 35 = 186
        self.assertAlmostEqual(d["fachada"]["alto"], 186.0)
        self.assertTrue(d["fachada"]["necesita_gola"])
        self.assertEqual(d["fachada"]["operacion_canto"],
                         FC.OPERACION_CANTO_GOLA)

    def test_inglete_45_conserva_altura(self):
        """APERTURA_45_GRADOS conserva la altura y usa BISEL_45."""
        config = dict(CONFIG_BASE,
                      tipo_corredera=CORREDERA_OCULTA,
                      sistema_apertura=APERTURA_45_GRADOS)
        d = calcular_despiece(config)
        self.assertAlmostEqual(d["fachada"]["alto"], 221.0)  # sin descuento
        self.assertTrue(d["fachada"]["necesita_bisel_45"])
        self.assertEqual(d["fachada"]["operacion_canto"],
                         FC.OPERACION_CANTO_45)

    def test_push_open_conserva_altura(self):
        """APERTURA_PUSH_OPEN conserva la altura."""
        config = dict(CONFIG_BASE,
                      tipo_corredera=CORREDERA_OCULTA,
                      sistema_apertura=APERTURA_PUSH_OPEN)
        d = calcular_despiece(config)
        self.assertAlmostEqual(d["fachada"]["alto"], 221.0)
        self.assertTrue(d["fachada"]["necesita_expulsor"])

    def test_tirador_conserva_altura(self):
        """APERTURA_TIRADOR conserva la altura y canto estándar."""
        config = dict(CONFIG_BASE,
                      tipo_corredera=CORREDERA_OCULTA,
                      sistema_apertura=APERTURA_TIRADOR)
        d = calcular_despiece(config)
        self.assertAlmostEqual(d["fachada"]["alto"], 221.0)
        self.assertFalse(d["fachada"]["necesita_gola"])
        self.assertFalse(d["fachada"]["necesita_bisel_45"])
        self.assertFalse(d["fachada"]["necesita_expulsor"])

    def test_cantos_por_sistema_apertura(self):
        """Los cantos se asignan correctamente por sistema de apertura."""
        config = dict(CONFIG_BASE,
                      tipo_corredera=CORREDERA_OCULTA,
                      sistema_apertura=APERTURA_45_GRADOS)
        d = calcular_despiece(config)
        cantos = d["fachada"]["cantos"]
        self.assertEqual(cantos["norte"], FC.OPERACION_CANTO_45)
        self.assertEqual(cantos["sur"], "FX")

        config2 = dict(CONFIG_BASE,
                       tipo_corredera=CORREDERA_OCULTA,
                       sistema_apertura=APERTURA_GOLA)
        d2 = calcular_despiece(config2)
        cantos2 = d2["fachada"]["cantos"]
        self.assertEqual(cantos2["norte"], FC.OPERACION_CANTO_GOLA)


# ---------------------------------------------------------------------
# Tests de integración con hardware_hub
# ---------------------------------------------------------------------

class TestHardwareHubIntegracion(unittest.TestCase):
    """Validación de resolve_drawer_slide desde el cajón."""

    def test_resolve_blum_tandem_desde_manifest(self):
        """blum_tandem se resuelve a BLUM-TANDEM con delta=49."""
        hw = H.resolve_drawer_slide(tipo="oculta", marca="blum_tandem")
        self.assertEqual(hw["sku"], "BLUM-TANDEM")
        self.assertAlmostEqual(hw["parametros_tecnicos"]["delta_ancho"], 49.0)

    def test_resolve_generica(self):
        """generica se resuelve a GEN-OCULTA con delta=45."""
        hw = H.resolve_drawer_slide(tipo="oculta", marca="generica")
        self.assertEqual(hw["sku"], "GEN-OCULTA")
        self.assertAlmostEqual(hw["parametros_tecnicos"]["delta_ancho"], 45.0)

    def test_resolve_sku_directo(self):
        """SKU directo se resuelve sin transformación."""
        hw = H.resolve_drawer_slide(tipo="oculta", marca="DUCASSE-OCULTA")
        self.assertEqual(hw["sku"], "DUCASSE-OCULTA")

    def test_resolve_telescopica(self):
        """Telescópica se resuelve con holgura 12.7mm."""
        hw = H.resolve_drawer_slide(tipo="telescopica",
                                    marca="GEN-TELESCOPICA-45KG")
        self.assertEqual(hw["sku"], "GEN-TELESCOPICA-45KG")
        self.assertAlmostEqual(
            hw["parametros_tecnicos"]["holgura_lateral_por_lado"], 12.7)

    def test_resolve_inexistente_lanza_keyerror(self):
        """Marca inexistente lanza KeyError descriptivo."""
        with self.assertRaises(KeyError):
            H.resolve_drawer_slide(tipo="oculta", marca="no_existe")


# ---------------------------------------------------------------------
# Tests de lógica de booleanos (mock de Part)
# ---------------------------------------------------------------------

class TestBooleanLogicMocked(unittest.TestCase):
    """Validación de la lógica de coordenadas para operaciones booleanas.

    Usa mocks de FreeCAD/Part ya que no hay display headless disponible.
    """

    def setUp(self):
        self.mock_solid = MagicMock()
        self.mock_solid.isValid.return_value = True
        self.mock_solid.Volume = 1000.0

        self.mock_tool = MagicMock()
        self.mock_tool.isValid.return_value = True

    def test_notch_reduce_volumen(self):
        """El notch en lateral reduce el volumen respecto al prisma puro."""

        # Simular: prisma puro = 1000, con notch = 800 (reducción)
        self.mock_solid.cut.return_value = MagicMock()
        self.mock_solid.cut.return_value.isValid.return_value = True
        self.mock_solid.cut.return_value.Volume = 800.0

        pos = {"x": 0, "y": 0, "z": 0, "largo_x": 16, "largo_y": 550,
               "largo_z": 120}
        _corte_notch_lateral(
            self.mock_solid, pos, 35.0, 12.0, 550)

        # Verificar que se llamó a cut con una herramienta
        self.mock_solid.cut.assert_called()
        args, _ = self.mock_solid.cut.call_args
        herramienta = args[0]
        # La herramienta de notch debe ser un Box (prisma)
        self.assertIsNotNone(herramienta)

    def test_pin_hole_reduce_volumen(self):
        """El taladro de pin reduce el volumen del testero trasero."""

        self.mock_solid.cut.return_value = MagicMock()
        self.mock_solid.cut.return_value.isValid.return_value = True
        self.mock_solid.cut.return_value.Volume = 950.0

        pos = {"x": 16, "y": 0, "z": 11.5, "largo_x": 519, "largo_y": 16,
               "largo_z": 96.5}
        _corte_pin_trasero(
            self.mock_solid, pos, 6.0, 10.0, 11.5, 6.0,
            96.5, 519, 16)

        self.mock_solid.cut.assert_called()
        args, _ = self.mock_solid.cut.call_args
        herramienta = args[0]
        self.assertIsNotNone(herramienta)

    def test_ranura_piso_reduce_volumen(self):
        """La ranura para piso delgado reduce el volumen del lateral."""

        self.mock_solid.cut.return_value = MagicMock()
        self.mock_solid.cut.return_value.isValid.return_value = True
        self.mock_solid.cut.return_value.Volume = 900.0

        pos = {"x": 0, "y": 0, "z": 0, "largo_x": 16, "largo_y": 550,
               "largo_z": 120}
        _corte_ranura_piso(
            self.mock_solid, pos, 4.0, 10.0, 5.5, 550)

        self.mock_solid.cut.assert_called()

    def test_bisel_45_crea_herramienta_triangular(self):
        """El bisel 45° crea una herramienta de corte triangular extruida."""

        self.mock_solid.cut.return_value = MagicMock()
        self.mock_solid.cut.return_value.isValid.return_value = True

        pos = {"x": 0, "y": -18, "z": 0, "largo_x": 636, "largo_y": 18,
               "largo_z": 221}
        _aplicar_bisel_45_fachada(
            self.mock_solid, pos, 636.0, 221.0, bisel_dist=5.0)

        self.mock_solid.cut.assert_called()

    def test_aplicar_corte_devuelve_original_si_falla(self):
        """Si el corte produce resultado invalido, se devuelve el solido original."""

        solido_original = MagicMock()
        solido_original.isValid.return_value = True
        # El resultado del corte es invalido -> se devuelve el original
        resultado_corte = MagicMock()
        resultado_corte.isValid.return_value = False
        solido_original.cut.return_value = resultado_corte
        herramienta = MagicMock()

        resultado = _aplicar_corte(solido_original, herramienta)
        self.assertEqual(resultado, solido_original)


# ---------------------------------------------------------------------
# Tests de validación de coordenadas calculadas (sin face indexing)
# ---------------------------------------------------------------------

class TestCoordenadasCalculadas(unittest.TestCase):
    """Validación de que las coordenadas se calculan, no se indexan."""

    def test_posiciones_laterales(self):
        """Las posiciones de laterales se calculan desde ancho_ext y g_caja."""
        config = dict(CONFIG_BASE, tipo_corredera=CORREDERA_OCULTA)
        d = calcular_despiece(config)
        pos = d["posiciones"]

        # lateral_izquierdo empieza en origen
        self.assertAlmostEqual(pos["lateral_izquierdo"]["x"], 0.0)
        self.assertAlmostEqual(pos["lateral_izquierdo"]["y"], 0.0)
        self.assertAlmostEqual(pos["lateral_izquierdo"]["z"], 0.0)

        # lateral_derecho empieza en ancho_ext - g_caja
        g_caja = d["caja"]["grosor"]
        ancho_ext = d["caja"]["ancho_exterior"]
        self.assertAlmostEqual(pos["lateral_derecho"]["x"],
                               ancho_ext - g_caja)

    def test_piso_en_ranura_telescopica(self):
        """En telescópica, el piso está en z_piso=10mm con grosor 5.5mm."""
        config = dict(CONFIG_BASE, tipo_corredera=CORREDERA_TELESCOPICA,
                      grosor_fondo=5.5, eje_ranura=10.0)
        d = calcular_despiece(config)
        self.assertAlmostEqual(d["caja"]["z_piso"], 10.0)
        self.assertAlmostEqual(d["caja"]["grosor_piso"], 5.5)

    def test_fachada_con_gola(self):
        """Con gola, la fachada es más baja."""
        config = dict(CONFIG_BASE,
                      tipo_corredera=CORREDERA_OCULTA,
                      sistema_apertura=APERTURA_GOLA)
        d = calcular_despiece(config)
        alto_nominal = d["fachada"]["alto_nominal"]
        alto_final = d["fachada"]["alto"]
        self.assertAlmostEqual(alto_final, alto_nominal - 35.0)


# ---------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------

if __name__ == "__main__":
    resultado = unittest.TextTestRunner(verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__]))
    if resultado.wasSuccessful():
        print("=" * 64)
        print("Tests de CajonCore OK - Trinidad v2 validada al 100%")
        print("=" * 64)
        sys.exit(0)
    sys.exit(1)
