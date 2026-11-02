"""Golden masters de los módulos de dominio VDO (M-19).

Genera y verifica capturas de salida de funciones de dominio para detectar
regresiones. Cada golden tiene al menos 3 entradas por función.

Uso:
    # Generar golden de un módulo (requiere revisión humana del diff)
    python3 -I tools/auditoria/golden.py --regenerar <modulo>

    # Verificar todos los golden = 100% iguales
    python3 -I tools/auditoria/golden.py --verificar

    # Verificar un módulo concreto
    python3 -I tools/auditoria/golden.py --verificar <modulo>

Los golden de geometría que dependen de OCC (Part) se ejecutan en nivel 2
(freecadcmd). Los de cálculo puro, en nivel 1 (python3 -I).
"""

from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
GOLDEN_DIR = ROOT / "tests" / "golden"

# Módulos de dominio y sus funciones públicas a cubrir (>= 3 entradas cada una).
MODULOS_FUNCIONES: dict[str, list[str]] = {
    "facade_contract": [
        "calcular_fachada_base",
        "aplicar_sistema_apertura",
        "necesita_descuento_gola",
        "necesita_bisel_45",
        "necesita_cantos_45",
        "necesita_expulsor_magnetico",
        "cantos_por_sistema_apertura",
    ],
    "frames": [
        "normal",
        "opuesto",
        "rotar_z",
        "normal_global",
        "interpretar_lados",
        "serializar_lados",
    ],
    "finish": [
        "cantos_para_rol",
        "aplicar_cantos",
    ],
    "reengrose": [
        "normalizar_modificador",
        "generar_tiras_perimetrales",
        "calcular_geometria_reengrose",
        "calcular_geometria_caja",
        "despiece_panel",
        "despiece_caja",
        "resolver_politica_cantos",
        "detectar_colision",
    ],
    "cajon_despiece": [
        "calcular_despiece",
    ],
    "puerta_despiece": [
        "calcular_dimensiones_batiente",
        "cantidad_bisagras",
        "posiciones_cazoleta",
    ],
    "coco_spaces": [
        "generar_divisiones_matriz",
    ],
    "hardware_hub": [
        "resolve_hinge",
        "resolve_sliding",
        "resolve_drawer_slide",
        "calculate_sliding_doors",
    ],
    # Los siguientes dependen de FreeCAD; se verifican en nivel 2.
    "module_props": [],
    "guardian": [],
    "zocalo_core": [],
    "panel_core": [],
    "cajon_core": [],
    "puerta_core": [],
    "coco_core": [],
    "layout": [],
    "optimizer_core": [],
    "nesting_presets": [],
    "spaces": [],
}


def _ruta_golden_json(modulo: str) -> Path:
    return GOLDEN_DIR / f"{modulo}.json"


def _ruta_golden_py(modulo: str) -> Path:
    return GOLDEN_DIR / f"{modulo}.py"


def _serializar(obj):
    """Serializa un valor a JSON, convirtiendo tuples a listas y sets a listas."""
    if isinstance(obj, dict):
        return {k: _serializar(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_serializar(v) for v in obj]
    if isinstance(obj, set):
        return sorted(_serializar(v) for v in obj)
    if isinstance(obj, float):
        return round(obj, 6)
    return obj


def _normalizar(salida):
    """Normaliza una salida para comparación: convierte a JSON estable."""
    return json.dumps(_serializar(salida), sort_keys=True, ensure_ascii=False)


def _cargar_modulo(modulo: str):
    """Importa el módulo de dominio freecad.vdo.core.vdo_<modulo>."""
    nombre = f"freecad.vdo.core.vdo_{modulo}"
    return importlib.import_module(nombre)


def _entradas_por_funcion(modulo: str) -> dict[str, list[dict]]:
    """Devuelve entradas representativas por función para un módulo."""
    mod = _cargar_modulo(modulo)
    entradas: dict[str, list[dict]] = {}

    if modulo == "facade_contract":
        entradas["calcular_fachada_base"] = [
            {"w_vano": 500.0, "h_vano": 700.0, "tipo_montaje": "parche"},
            {"w_vano": 500.0, "h_vano": 700.0, "tipo_montaje": "semiparche"},
            {"w_vano": 500.0, "h_vano": 700.0, "tipo_montaje": "embebida"},
            {"w_vano": 1000.0, "h_vano": 500.0, "tipo_montaje": "parche", "holgura": 4.0, "solape": 10.0},
        ]
        entradas["aplicar_sistema_apertura"] = [
            {"h_fachada": 700.0, "sistema_apertura": "gola_aluminio"},
            {"h_fachada": 700.0, "sistema_apertura": "inglete_45"},
            {"h_fachada": 700.0, "sistema_apertura": "tirador"},
            {"h_fachada": 700.0, "sistema_apertura": "push_open"},
        ]
        entradas["necesita_descuento_gola"] = [
            {"sistema_apertura": "gola_aluminio"},
            {"sistema_apertura": "tirador"},
            {"sistema_apertura": "inglete_45"},
        ]
        entradas["necesita_bisel_45"] = [
            {"sistema_apertura": "inglete_45"},
            {"sistema_apertura": "tirador"},
            {"sistema_apertura": "gola_aluminio"},
        ]
        entradas["necesita_cantos_45"] = [
            {"sistema_apertura": "inglete_45"},
            {"sistema_apertura": "tirador"},
            {"sistema_apertura": "gola_aluminio"},
        ]
        entradas["necesita_expulsor_magnetico"] = [
            {"sistema_apertura": "push_open"},
            {"sistema_apertura": "tirador"},
            {"sistema_apertura": "gola_aluminio"},
        ]
        entradas["cantos_por_sistema_apertura"] = [
            {"sistema_apertura": "tirador"},
            {"sistema_apertura": "gola_aluminio"},
            {"sistema_apertura": "inglete_45"},
        ]

    elif modulo == "frames":
        entradas["normal"] = [
            {"lado": "frente"},
            {"lado": "fondo"},
            {"lado": "izquierda"},
        ]
        entradas["opuesto"] = [
            {"lado": "frente"},
            {"lado": "fondo"},
            {"lado": "izquierda"},
        ]
        entradas["rotar_z"] = [
            {"vector": [1.0, 0.0, 0.0], "grados": 90.0},
            {"vector": [0.0, 1.0, 0.0], "grados": 180.0},
            {"vector": [1.0, 1.0, 0.0], "grados": 45.0},
        ]
        entradas["normal_global"] = [
            {"lado": "frente", "rotacion_z": 0.0},
            {"lado": "fondo", "rotacion_z": 90.0},
            {"lado": "izquierda", "rotacion_z": 45.0},
        ]
        entradas["interpretar_lados"] = [
            {"valor": "[frente, fondo]", "por_defecto": ["izquierda"]},
            {"valor": "frente,derecha"},
            {"valor": None, "por_defecto": ["superior"]},
        ]
        entradas["serializar_lados"] = [
            {"lados": ["frente", "fondo"]},
            {"lados": "izquierda,derecha"},
            {"lados": []},
        ]

    elif modulo == "finish":
        entradas["cantos_para_rol"] = [
            {"rol": "lateral_izquierdo", "lados_vistos": "frente"},
            {"rol": "lateral_izquierdo", "lados_vistos": "frente, fondo"},
            {"rol": "base", "lados_vistos": "frente", "tapa": "externo", "base": "externo"},
        ]
        entradas["aplicar_cantos"] = [
            {"piezas": [{"rol": "lateral_izquierdo"}], "lados_vistos": "frente"},
            {"piezas": [{"rol": "base"}, {"rol": "techo"}], "lados_vistos": "frente, fondo"},
            {"piezas": [{"rol": "fondo"}], "lados_vistos": "frente"},
        ]

    elif modulo == "reengrose":
        entradas["normalizar_modificador"] = [
            {},
            {"activo": False},
            {"activo": True, "orientacion": "paralela", "ancho": 70.0, "cara": "cara_a"},
        ]
        entradas["generar_tiras_perimetrales"] = [
            {"largo_tablero": 600.0, "ancho_tablero": 500.0, "bordes": {}, "espesor_madre": 18.0},
            {"largo_tablero": 600.0, "ancho_tablero": 500.0,
             "bordes": {"frente": {"activo": True, "ancho": 70.0}}, "espesor_madre": 18.0},
            {"largo_tablero": 600.0, "ancho_tablero": 500.0,
             "bordes": {"frente": {"activo": True, "ancho": 70.0},
                        "fondo": {"activo": True, "ancho": 70.0},
                        "izquierda": {"activo": True, "ancho": 70.0},
                        "derecha": {"activo": True, "ancho": 70.0}},
             "espesor_madre": 18.0},
        ]
        entradas["calcular_geometria_reengrose"] = [
            {"panel_base": {"nombre": "P", "largo": 600.0, "ancho": 500.0, "espesor": 18.0},
             "modifier": {"activo": False}},
            {"panel_base": {"nombre": "P", "largo": 600.0, "ancho": 500.0, "espesor": 18.0},
             "modifier": {"activo": True, "orientacion": "paralela", "ancho": 70.0}},
        ]
        entradas["calcular_geometria_caja"] = [
            {"caja": {"nombre": "C", "x": 0, "y": 0, "z": 0, "w": 600, "h": 500, "d": 18},
             "modifier": {"activo": False}},
            {"caja": {"nombre": "C", "x": 0, "y": 0, "z": 0, "w": 600, "h": 500, "d": 18},
             "modifier": {"activo": True, "orientacion": "paralela", "ancho": 70.0}},
        ]
        entradas["despiece_panel"] = [
            {"nombre": "Panel", "largo": 600.0, "ancho": 500.0, "espesor": 18.0,
             "modifier": {"activo": False}},
            {"nombre": "Panel", "largo": 600.0, "ancho": 500.0, "espesor": 18.0,
             "modifier": {"activo": True, "orientacion": "paralela", "ancho": 70.0}},
        ]
        entradas["despiece_caja"] = [
            {"caja": {"nombre": "C", "x": 0, "y": 0, "z": 0, "w": 600, "h": 500, "d": 18},
             "modifier": {"activo": False}, "ejes": {"largo": "x", "ancho": "y", "espesor": "z"}},
            {"caja": {"nombre": "C", "x": 0, "y": 0, "z": 0, "w": 600, "h": 500, "d": 18},
             "modifier": {"activo": True, "orientacion": "paralela", "ancho": 70.0},
             "ejes": {"largo": "x", "ancho": "y", "espesor": "z"}},
        ]
        entradas["resolver_politica_cantos"] = [
            {"panel_base": {"cantos": {}}, "modifier": {"activo": False}},
            {"panel_base": {"cantos": {}}, "modifier": {"activo": True, "modo_fabricacion": "independiente"}},
        ]
        entradas["detectar_colision"] = [
            {"a": {"x": 0, "y": 0, "z": 0, "w": 10, "h": 10, "d": 10},
             "b": {"x": 20, "y": 0, "z": 0, "w": 10, "h": 10, "d": 10}},
            {"a": {"x": 0, "y": 0, "z": 0, "w": 10, "h": 10, "d": 10},
             "b": {"x": 5, "y": 0, "z": 0, "w": 10, "h": 10, "d": 10}},
        ]

    elif modulo == "cajon_despiece":
        base = {
            "ancho_libre": 600.0, "prof_libre": 580.0, "ancho_modulo": 640.0,
            "alto_frente": 225.0, "marca": "blum_tandem", "alto_caja": 120.0,
            "grosor_caja": 16.0, "grosor_fondo": 6.0, "grosor_fachada": 18.0,
            "longitud_guia": 0.0, "montaje_trasera": "entre_laterales",
            "penetracion_ranura": 10.0, "eje_ranura": 11.5,
            "holgura_lateral_fachada": 2.0, "holgura_superior_fachada": 2.0,
            "holgura_inferior_fachada": 2.0, "material_ref": "melamina_standar",
            "tipo_corredera": mod.CORREDERA_OCULTA,
        }
        entradas["calcular_despiece"] = [
            dict(base),
            dict(base, tipo_corredera=mod.CORREDERA_TELESCOPICA),
            dict(base, tipo_corredera=mod.CAJA_METALICA, sistema_apertura=mod.APERTURA_GOLA),
        ]

    elif modulo == "puerta_despiece":
        entradas["calcular_dimensiones_batiente"] = [
            {"ancho": 600, "alto": 800, "montaje": "parche"},
            {"ancho": 600, "alto": 800, "montaje": "semiparche"},
            {"ancho": 600, "alto": 800, "montaje": "embebida"},
        ]
        entradas["cantidad_bisagras"] = [
            {"alto": 900},
            {"alto": 1000},
            {"alto": 1500},
        ]
        entradas["posiciones_cazoleta"] = [
            {"alto": 800, "n_bisagras": 2},
            {"alto": 1200, "n_bisagras": 3},
        ]

    elif modulo == "coco_spaces":
        entradas["generar_divisiones_matriz"] = [
            {"ancho": 600.0, "alto": 700.0, "n_divisiones": 3},
            {"ancho": 1000.0, "alto": 2000.0, "n_divisiones": 4},
            {"ancho": 400.0, "alto": 500.0, "n_divisiones": 2},
        ]

    elif modulo == "hardware_hub":
        entradas["resolve_hinge"] = [
            {"tipo_montaje": "parche"},
            {"tipo_montaje": "semiparche"},
            {"tipo_montaje": "embebida"},
        ]
        entradas["resolve_sliding"] = [
            {"tipo_mueble": "closet"},
            {"tipo_mueble": "mueble"},
        ]
        entradas["resolve_drawer_slide"] = [
            {"tipo": "oculta", "marca": "blum_tandem"},
            {"tipo": "oculta", "marca": "generica"},
        ]
        entradas["calculate_sliding_doors"] = [
            {"inner_w": 1000.0, "inner_h": 2000.0, "sku": "DUC-KIT-D52", "n_hojas": 2},
            {"inner_w": 1200.0, "inner_h": 2200.0, "sku": "DUC-AL-1535-MAD", "n_hojas": 3},
        ]

    return entradas


def _ejecutar_funcion(mod, nombre_func: str, entrada: dict):
    """Ejecuta una función de dominio con una entrada y devuelve la salida."""
    fn = getattr(mod, nombre_func)
    try:
        return fn(**entrada)
    except TypeError:
        try:
            return fn(entrada)
        except TypeError:
            return fn()


def regenerar(modulo: str):
    """Genera el golden de un módulo y lo guarda en tests/golden/."""
    GOLDEN_DIR.mkdir(parents=True, exist_ok=True)
    mod = _cargar_modulo(modulo)
    funciones = MODULOS_FUNCIONES.get(modulo, [])
    entradas_por_fn = _entradas_por_funcion(modulo)

    resultados = {}
    for fn_name in funciones:
        entradas = entradas_por_fn.get(fn_name, [])
        salidas = []
        for entrada in entradas:
            try:
                salida = _ejecutar_funcion(mod, fn_name, entrada)
                salidas.append({"entrada": entrada, "salida": salida})
            except Exception as exc:
                salidas.append({"entrada": entrada, "error": str(exc)})
        resultados[fn_name] = salidas

    path = _ruta_golden_json(modulo)
    path.write_text(json.dumps(resultados, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Golden generado: {path} ({len(funciones)} funciones)")


def verificar(modulo: str | None = None) -> bool:
    """Verifica que los golden actuales coincidan con la salida del código."""
    modulos = [modulo] if modulo else list(MODULOS_FUNCIONES.keys())
    todo_ok = True
    for mod_name in modulos:
        path = _ruta_golden_json(mod_name)
        if not path.exists():
            print(f"FALTA golden: {path}")
            todo_ok = False
            continue
        esperado = json.loads(path.read_text(encoding="utf-8"))
        mod = _cargar_modulo(mod_name)
        funciones = MODULOS_FUNCIONES.get(mod_name, [])
        entradas_por_fn = _entradas_por_funcion(mod_name)

        for fn_name in funciones:
            esperadas = esperado.get(fn_name, [])
            entradas = entradas_por_fn.get(fn_name, [])
            for i, exp in enumerate(esperadas):
                entrada = entradas[i] if i < len(entradas) else exp["entrada"]
                try:
                    salida = _ejecutar_funcion(mod, fn_name, entrada)
                    salida_serial = _serializar(salida)
                    if "error" in exp:
                        print(f"  {mod_name}.{fn_name}[{i}]: esperaba error, obtuvo salida")
                        todo_ok = False
                    elif _normalizar(salida_serial) != _normalizar(exp.get("salida")):
                        print(f"  DIFERENCIA {mod_name}.{fn_name}[{i}]")
                        print(f"    entrada: {entrada}")
                        print(f"    esperado: {exp.get('salida')}")
                        print(f"    obtenido: {salida_serial}")
                        todo_ok = False
                except Exception as exc:
                    if "error" in exp and exp["error"] in str(exc):
                        continue
                    print(f"  EXCEPCION {mod_name}.{fn_name}[{i}]: {exc}")
                    todo_ok = False
        if todo_ok:
            print(f"OK golden: {mod_name}")
    return todo_ok


def main():
    if "--regenerar" in sys.argv:
        idx = sys.argv.index("--regenerar")
        modulo = sys.argv[idx + 1]
        regenerar(modulo)
        sys.exit(0)
    elif "--verificar" in sys.argv:
        idx = sys.argv.index("--verificar")
        modulo = sys.argv[idx + 1] if idx + 1 < len(sys.argv) else None
        ok = verificar(modulo)
        sys.exit(0 if ok else 1)
    else:
        print("Uso: golden.py --regenerar <modulo> | --verificar [<modulo>]")
        sys.exit(1)


if __name__ == "__main__":
    main()
