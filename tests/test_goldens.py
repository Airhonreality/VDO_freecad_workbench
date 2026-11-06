"""Golden masters de dominio dentro del runner (nivel 1 y nivel 2).

Comprueba, por módulo de tools/auditoria/golden.py:
- el golden existe, tiene al menos 3 entradas por función y ninguna entrada en error;
- la salida del código actual coincide con el golden (golden.verificar).

Un módulo que importa FreeCAD (AST, no ejecución) se omite en el nivel 1 con motivo
explícito, y se ejecuta en el nivel 2. Los puros se ejecutan en ambos niveles.
Ningún golden se regenera desde aquí.
"""

from __future__ import annotations

import ast
import importlib.util
import json
import unittest
from pathlib import Path

from tests.soporte.requisitos import _freecad_real

ROOT = Path(__file__).resolve().parent.parent
_GOLDEN_PY = ROOT / "tools" / "auditoria" / "golden.py"
GOLDEN_DIR = ROOT / "tests" / "golden"

# Módulos sin funciones con golden, con motivo registrado en docs/metricas/goldens_origen.md.
# Decisión P-10 (DECISIONES_DELEGADAS.md): N/A con motivo y deuda con responsable.
NA_JUSTIFICADOS = {"nesting_presets"}

# Flujos de creación cubiertos por golden_creacion (creacion_modulos.json): 3 entradas cada uno.
FLUJOS_CREACION = ("crear_pieza", "make_coco", "make_zocalo", "make_cajon", "make_puerta")


def _cargar_golden():
    spec = importlib.util.spec_from_file_location("golden_auditoria", _GOLDEN_PY)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


golden = _cargar_golden()


def _ruta_modulo(nombre: str) -> Path:
    """'freecad.vdo.core.vdo_x' -> ruta del fichero .py dentro del repo."""
    return ROOT / Path(*nombre.split(".")).with_suffix(".py")


def _necesita_freecad(modulo: str) -> bool:
    """True si importar el módulo necesita FreeCAD o Part (directa o transitivamente).

    Análisis AST de imports de nivel de módulo dentro de freecad.vdo. No ejecuta nada.
    """
    origenes = golden.AGREGADOS.get(modulo) or (
        golden.UBICACIONES.get(modulo, (f"freecad.vdo.core.vdo_{modulo}",))[-1],)
    pendientes = list(origenes)
    visitados: set[str] = set()
    while pendientes:
        nombre = pendientes.pop()
        if nombre in visitados:
            continue
        visitados.add(nombre)
        ruta = _ruta_modulo(nombre)
        if not ruta.exists():
            continue
        arbol = ast.parse(ruta.read_text(encoding="utf-8"), filename=str(ruta))
        # Solo imports de nivel de módulo: los diferidos dentro de funciones no impiden importar.
        for nodo in arbol.body:
            if isinstance(nodo, ast.Import):
                nombres = [a.name for a in nodo.names]
            elif isinstance(nodo, ast.ImportFrom) and nodo.module:
                nombres = [nodo.module] + [f"{nodo.module}.{a.name}" for a in nodo.names]
            else:
                continue
            for n in nombres:
                if n.split(".")[0] in ("FreeCAD", "Part"):
                    return True
                if n.startswith("freecad.vdo."):
                    pendientes.append(n)
    return False


class GoldensEstructuraTests(unittest.TestCase):
    """No depende de FreeCAD: lee los ficheros JSON."""

    def test_cada_modulo_con_funciones_tiene_golden_con_3_entradas(self):
        for modulo, funciones in golden.MODULOS_FUNCIONES.items():
            if not funciones:
                continue
            with self.subTest(modulo=modulo):
                ruta = GOLDEN_DIR / f"{modulo}.json"
                self.assertTrue(ruta.exists(), f"falta {ruta}")
                datos = json.loads(ruta.read_text(encoding="utf-8"))
                for fn in funciones:
                    entradas = datos.get(fn, [])
                    self.assertGreaterEqual(len(entradas), 3, f"{modulo}.{fn}: {len(entradas)} entradas")

    def test_ninguna_entrada_de_golden_esta_en_error(self):
        for ruta in sorted(GOLDEN_DIR.glob("*.json")):
            datos = json.loads(ruta.read_text(encoding="utf-8"))
            if ruta.stem == "creacion_modulos":
                entradas_por_fn = {fn: lista for fn, lista in datos.items()}
            else:
                entradas_por_fn = datos
            for fn, lista in entradas_por_fn.items():
                for i, entrada in enumerate(lista):
                    with self.subTest(golden=ruta.stem, funcion=fn, indice=i):
                        self.assertNotIn("error", entrada)

    def test_flujos_de_creacion_tienen_3_entradas(self):
        datos = json.loads((GOLDEN_DIR / "creacion_modulos.json").read_text(encoding="utf-8"))
        for flujo in FLUJOS_CREACION:
            with self.subTest(flujo=flujo):
                self.assertGreaterEqual(len(datos.get(flujo, [])), 3)

    def test_na_justificados_no_tienen_funciones_registradas(self):
        for modulo in NA_JUSTIFICADOS:
            with self.subTest(modulo=modulo):
                self.assertEqual(golden.MODULOS_FUNCIONES.get(modulo), [])


# Módulos cuyo golden necesita FreeCAD al ejecutarse, aunque su import sea puro.
# Medido en el nivel 1 del runner: module_props falla con "False is not true" sin FreeCAD real.
# Causa: rotacion_z reubicada a core/vdo_helpers construye App.Rotation en tiempo de llamada.
SOLO_NIVEL_2_POR_EJECUCION = {"module_props"}

# Goldens que comparan formas OCC grabadas con FreeCAD real. Requisito declarado (D-30).
GOLDEN_FORMAS_OCC = {"coco_spaces"}


def _crear_test_verificacion(modulo: str):
    def test(self):
        if modulo in GOLDEN_FORMAS_OCC and _freecad_real() is None:
            raise unittest.SkipTest(f"{modulo} requiere FreeCAD real (formas OCC)")
        necesita = _necesita_freecad(modulo) or modulo in SOLO_NIVEL_2_POR_EJECUCION
        if _freecad_real() is None and necesita:
            if modulo in SOLO_NIVEL_2_POR_EJECUCION:
                motivo = f"{modulo} necesita FreeCAD al ejecutarse (rotacion_z); requiere FreeCAD real"
            else:
                motivo = f"{modulo} importa FreeCAD a nivel de módulo; requiere FreeCAD real"
            raise unittest.SkipTest(motivo)
        self.assertTrue(golden.verificar(modulo), f"golden {modulo} con diferencias")

    test.__doc__ = f"Golden {modulo} contra el código actual."
    return test


class GoldensVerificacionTests(unittest.TestCase):
    pass


for _modulo in golden.MODULOS_FUNCIONES:
    if golden.MODULOS_FUNCIONES[_modulo]:
        setattr(GoldensVerificacionTests, f"test_{_modulo}", _crear_test_verificacion(_modulo))
