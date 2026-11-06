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

def _fixture(nombre: str) -> str:
    """Texto de un fixture de entrada (tests/fixtures/). Falla si falta."""
    return (ROOT / "tests" / "fixtures" / nombre).read_text(encoding="utf-8").strip()


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
    "module_props": [
        "rotacion_z",
    ],
    "guardian": [
        "asegurar_hoja_global",
        "asegurar_params_local",
        "vdo_guard",
    ],
    "zocalo_core": [
        "calcular_geometria_zocalo",
    ],
    "panel_core": [],
    "cajon_core": [],
    "puerta_core": [],
    "coco_core": [],
    "layout": [
        "cavidad_interior",
    ],
    "optimizer_core": [
        "expand_pieces",
        "optimize",
    ],
    "nesting_presets": [],
    "spaces": [
        "calcular_espacio_libre",
    ],
}


# Funciones que cambiaron de módulo después de b78de04. Solo se usa cuando el módulo de
# origen ya no tiene la función. Cada entrada debe quedar registrada en
# docs/metricas/goldens_origen.md y en docs/DEUDA_TECNICA.md.
RELOCALIZADAS: dict[tuple[str, str], str] = {
    ("module_props", "rotacion_z"): "freecad.vdo.core.helpers",
    ("coco_spaces", "generar_divisiones_matriz"): "freecad.vdo.cad.coco_espacios",
}

# Módulos que cambiaron de capa después de b78de04. Se importa el primero que exista.
UBICACIONES: dict[str, tuple[str, ...]] = {
    "guardian": ("freecad.vdo.core.guardian", "freecad.vdo.cad.guardian"),
}

# Módulos de dominio repartidos en varios archivos (M7, D-34). Su golden sigue siendo
# uno solo: cada función se busca en el primer módulo del grupo que la define.
AGREGADOS: dict[str, tuple[str, ...]] = {
    "layout": tuple(
        f"freecad.vdo.core.layout_{parte}"
        for parte in ("modelo", "matriz", "resuelto", "resolucion")),
    "optimizer_core": ("freecad.vdo.core.optimizer_core",
                       "freecad.vdo.core.optimizer_lista_corte"),
    "cajon_despiece": tuple(
        f"freecad.vdo.core.cajon_{parte}"
        for parte in ("correderas", "calculo")),
    "reengrose": tuple(
        f"freecad.vdo.core.reengrose_{parte}"
        for parte in ("modelo", "modificador", "tiras", "geometria",
                      "despiece", "encuentros", "interferencias")),
}


class _Agregado:
    """Vista de varios módulos: ``getattr`` devuelve la primera definición encontrada."""

    def __init__(self, nombres: tuple[str, ...]):
        self._modulos = [importlib.import_module(n) for n in nombres]

    def __getattr__(self, nombre: str):
        for modulo in self._modulos:
            if hasattr(modulo, nombre):
                return getattr(modulo, nombre)
        raise AttributeError(nombre)

# Hoja y celdas que los escenarios "editada" del guardián modifican (fuera de la lógica probada).
_GUARDIAN_HOJA_GLOBAL = "Params_Melamina"
_GUARDIAN_HOJA_LOCAL = "Params"
_GUARDIAN_CELDA_GLOBAL = ("B2", "espesor_default", "1234")
_GUARDIAN_CELDA_LOCAL = ("A1", "alto", "999")


def _modulo_para_funcion(modulo: str, mod, nombre_func: str):
    """Módulo que expone la función. Usa la reubicación conocida si el original no la tiene."""
    if hasattr(mod, nombre_func):
        return mod
    destino = RELOCALIZADAS.get((modulo, nombre_func))
    if destino is None:
        return mod
    return importlib.import_module(destino)


def _ruta_golden_json(modulo: str) -> Path:
    return GOLDEN_DIR / f"{modulo}.json"


def _ruta_golden_py(modulo: str) -> Path:
    return GOLDEN_DIR / f"{modulo}.py"


_PROFUNDIDAD_MAX = 8


def _serializar(obj, _prof=0):
    """Serializa un valor a JSON, convirtiendo tuples a listas y sets a listas.

    Los objetos de dominio (sin tipo JSON) se representan por sus atributos públicos,
    con profundidad acotada para no entrar en ciclos.
    """
    if isinstance(obj, dict):
        return {str(k): _serializar(v, _prof + 1) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_serializar(v, _prof + 1) for v in obj]
    if isinstance(obj, set):
        return sorted(_serializar(v, _prof + 1) for v in obj)
    if isinstance(obj, float):
        return round(obj, 6)
    if obj is None or isinstance(obj, (int, str, bool)):
        return obj
    if hasattr(obj, "Axis") and hasattr(obj, "Angle") and hasattr(obj, "Matrix"):
        # App.Rotation de FreeCAD: eje y ángulo en radianes, redondeados.
        eje = obj.Axis
        return {"Rotation": {"axis": [round(eje.x, 6), round(eje.y, 6), round(eje.z, 6)],
                             "angle": round(obj.Angle, 6)}}
    if hasattr(obj, "__dict__") and _prof < _PROFUNDIDAD_MAX:
        atributos = {k: v for k, v in vars(obj).items() if not k.startswith("_")}
        return {type(obj).__name__: _serializar(atributos, _prof + 1)}
    return type(obj).__name__


def _normalizar(salida):
    """Normaliza una salida para comparación: convierte a JSON estable."""
    return json.dumps(_serializar(salida), sort_keys=True, ensure_ascii=False)


def _cargar_modulo(modulo: str):
    """Importa el módulo de dominio freecad.vdo.core.<modulo> (o su ubicación conocida).

    """
    if modulo in AGREGADOS:
        return _Agregado(AGREGADOS[modulo])
    if modulo in UBICACIONES:
        ultimo_error: Exception | None = None
        mod = None
        for nombre in UBICACIONES[modulo]:
            try:
                mod = importlib.import_module(nombre)
                break
            except ModuleNotFoundError as exc:
                ultimo_error = exc
        if mod is None:
            raise ultimo_error  # type: ignore[misc]
        return mod
    return importlib.import_module(f"freecad.vdo.core.{modulo}")


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
            {"valor": '["frente", "fondo"]', "por_defecto": ["izquierda"]},
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
            {"panel_base": {"nombre": "P", "largo": 800.0, "ancho": 450.0, "espesor": 18.0},
             "modifier": {"activo": True, "orientacion": "transversal", "ancho": 50.0}},
        ]
        entradas["calcular_geometria_caja"] = [
            {"caja": {"nombre": "C", "x": 0, "y": 0, "z": 0, "w": 600, "h": 500, "d": 18},
             "modifier": {"activo": False}},
            {"caja": {"nombre": "C", "x": 0, "y": 0, "z": 0, "w": 600, "h": 500, "d": 18},
             "modifier": {"activo": True, "orientacion": "paralela", "ancho": 70.0}},
            {"caja": {"nombre": "C", "x": 0, "y": 0, "z": 0, "w": 800, "h": 450, "d": 18},
             "modifier": {"activo": True, "orientacion": "transversal", "ancho": 50.0}},
        ]
        entradas["despiece_panel"] = [
            {"nombre": "Panel", "largo": 600.0, "ancho": 500.0, "espesor": 18.0,
             "modifier": {"activo": False}},
            {"nombre": "Panel", "largo": 600.0, "ancho": 500.0, "espesor": 18.0,
             "modifier": {"activo": True, "orientacion": "paralela", "ancho": 70.0}},
            {"nombre": "Panel", "largo": 800.0, "ancho": 450.0, "espesor": 18.0,
             "modifier": {"activo": True, "orientacion": "transversal", "ancho": 50.0}},
        ]
        entradas["despiece_caja"] = [
            {"caja": {"nombre": "C", "x": 0, "y": 0, "z": 0, "w": 600, "h": 500, "d": 18},
             "modifier": {"activo": False}, "ejes": {"largo": "x", "ancho": "y", "espesor": "z"}},
            {"caja": {"nombre": "C", "x": 0, "y": 0, "z": 0, "w": 600, "h": 500, "d": 18},
             "modifier": {"activo": True, "orientacion": "paralela", "ancho": 70.0},
             "ejes": {"largo": "x", "ancho": "y", "espesor": "z"}},
            {"caja": {"nombre": "C", "x": 0, "y": 0, "z": 0, "w": 800, "h": 450, "d": 18},
             "modifier": {"activo": True, "orientacion": "transversal", "ancho": 50.0},
             "ejes": {"largo": "y", "ancho": "x", "espesor": "z"}},
        ]
        entradas["resolver_politica_cantos"] = [
            {"panel_base": {"cantos": {}}, "modifier": {"activo": False}},
            {"panel_base": {"cantos": {}}, "modifier": {"activo": True, "modo_fabricacion": "independiente"}},
            {"panel_base": {"cantos": {"frente": "FX"}},
             "modifier": {"activo": True, "modo_fabricacion": "pacha"}},
        ]
        entradas["detectar_colision"] = [
            {"a": {"x": 0, "y": 0, "z": 0, "w": 10, "h": 10, "d": 10},
             "b": {"x": 20, "y": 0, "z": 0, "w": 10, "h": 10, "d": 10}},
            {"a": {"x": 0, "y": 0, "z": 0, "w": 10, "h": 10, "d": 10},
             "b": {"x": 5, "y": 0, "z": 0, "w": 10, "h": 10, "d": 10}},
            {"a": {"x": 0, "y": 0, "z": 0, "w": 10, "h": 10, "d": 10},
             "b": {"x": 10, "y": 0, "z": 0, "w": 10, "h": 10, "d": 10}},
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
            dict(base, tipo_corredera=mod.CAJA_METALICA,
                 sistema_apertura=importlib.import_module(
                     "freecad.vdo.core.facade_contract").APERTURA_GOLA),
        ]

    elif modulo == "puerta_despiece":
        # Firmas de b78de04: calcular_dimensiones_batiente(W_neto, H_neto, tipo_montaje, ...),
        # cantidad_bisagras(H), posiciones_cazoleta(H, n_bisagras=None, ...).
        entradas["calcular_dimensiones_batiente"] = [
            {"W_neto": 600, "H_neto": 800, "tipo_montaje": "parche"},
            {"W_neto": 600, "H_neto": 800, "tipo_montaje": "semiparche"},
            {"W_neto": 600, "H_neto": 800, "tipo_montaje": "embebida"},
        ]
        entradas["cantidad_bisagras"] = [
            {"H": 900},
            {"H": 1000},
            {"H": 1500},
        ]
        entradas["posiciones_cazoleta"] = [
            {"H": 800, "n_bisagras": 2},
            {"H": 1200, "n_bisagras": 3},
            {"H": 1500},
        ]

    elif modulo == "coco_spaces":
        # Firma de b78de04: generar_divisiones_matriz(divisiones_json, ancho_cavidad,
        # alto_cavidad, fondo, espesor, ..., espacios_x, espacios_y). Con divisiones_json
        # vacío usa el camino legado (espacios_x/espacios_y).
        entradas["generar_divisiones_matriz"] = [
            {"divisiones_json": _fixture("layout_2x2.json"), "ancho_cavidad": 600.0,
             "alto_cavidad": 700.0, "fondo": 580.0, "espesor": 18.0},
            {"divisiones_json": _fixture("layout_3x1.json"), "ancho_cavidad": 1000.0,
             "alto_cavidad": 2000.0, "fondo": 560.0, "espesor": 18.0},
            {"divisiones_json": _fixture("layout_1x2.json"), "ancho_cavidad": 400.0,
             "alto_cavidad": 500.0, "fondo": 580.0, "espesor": 16.0},
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
            {"tipo_mueble": "alacena"},
        ]
        entradas["resolve_drawer_slide"] = [
            {"tipo": "oculta", "marca": "blum_tandem"},
            {"tipo": "oculta", "marca": "generica"},
            {"tipo": "oculta", "marca": "HAFELE-OCULTA"},
        ]
        entradas["calculate_sliding_doors"] = [
            {"inner_w": 1000.0, "inner_h": 2000.0, "sku": "DUC-KIT-D52", "n_hojas": 2},
            {"inner_w": 1200.0, "inner_h": 2200.0, "sku": "DUC-AL-1535-MAD", "n_hojas": 3},
            {"inner_w": 1500.0, "inner_h": 2100.0, "sku": "DUC-AL-1535-VID", "n_hojas": 2},
        ]

    elif modulo == "module_props":
        entradas["rotacion_z"] = [
            {"grados": 0.0},
            {"grados": 90.0},
            {"grados": 45.0},
        ]

    elif modulo == "zocalo_core":
        entradas["calcular_geometria_zocalo"] = [
            {"ancho": 600.0, "fondo": 580.0, "alto_zocalo": 100.0, "espesor_tablero": 18.0},
            {"ancho": 900.0, "fondo": 560.0, "alto_zocalo": 80.0, "espesor_tablero": 18.0,
             "tiene_trasera": False},
            {"ancho": 450.0, "fondo": 580.0, "alto_zocalo": 100.0, "espesor_tablero": 16.0,
             "amarres_intermedios": 2},
        ]

    elif modulo == "layout":
        entradas["cavidad_interior"] = [
            {"alto": 720.0, "ancho": 600.0, "espesor": 18.0},
            {"alto": 2100.0, "ancho": 900.0, "espesor": 18.0},
            {"alto": 500.0, "ancho": 400.0, "espesor": 16.0},
        ]

    elif modulo == "spaces":
        entradas["calcular_espacio_libre"] = [
            {"espacios_json": "", "espacio_total": 600.0, "espesor": 18.0},
            {"espacios_json": "", "espacio_total": 1000.0, "espesor": 16.0},
            {"espacios_json": "", "espacio_total": 300.0, "espesor": 18.0},
        ]

    elif modulo == "optimizer_core":
        piezas_a = [{"name": "A", "w": 600.0, "h": 700.0, "thickness": 18.0,
                     "material": "melamina_standar", "cantos": {}}]
        piezas_b = [
            {"name": "Lateral", "w": 580.0, "h": 720.0, "thickness": 18.0,
             "material": "melamina_standar", "cantos": {}},
            {"name": "Estante #1", "w": 560.0, "h": 600.0, "thickness": 18.0,
             "material": "melamina_standar", "cantos": {"frente": "FX"}},
            {"name": "Estante #2", "w": 560.0, "h": 600.0, "thickness": 18.0,
             "material": "melamina_standar", "cantos": {"frente": "FX"}},
            {"name": "Fondo", "w": 600.0, "h": 700.0, "thickness": 6.0,
             "material": "fondo_mdf", "cantos": {}},
        ]
        # Pieza mayor que el tablero: debe quedar sin colocar, no excepción.
        piezas_c = [{"name": "Grande", "w": 2500.0, "h": 1900.0, "thickness": 18.0,
                     "material": "melamina_standar", "cantos": {}}]
        entradas["expand_pieces"] = [
            [{"name": "Lateral", "qty": 2, "width": 580.0, "length": 720.0,
              "thickness": 18.0, "material": "melamina_standar"}],
            [{"name": "Estante", "qty": 3, "width": 560.0, "length": 600.0,
              "thickness": 18.0, "material": "melamina_standar", "cantos": {"frente": "FX"}},
             {"name": "Tapa", "qty": 1, "width": 600.0, "length": 600.0,
              "thickness": 18.0, "material": "melamina_standar"}],
            [{"name": "Fondo", "qty": 1, "width": 600.0, "length": 700.0,
              "thickness": 6.0, "material": "fondo_mdf"}],
        ]
        entradas["optimize"] = [
            {"pieces": piezas_a, "board_w": 2440.0, "board_h": 1830.0},
            {"pieces": piezas_b, "board_w": 2440.0, "board_h": 1830.0},
            {"pieces": piezas_c, "board_w": 2440.0, "board_h": 1830.0},
        ]

    elif modulo == "guardian":
        # Escenario = estado del documento antes de llamar (ver _ejecutar_guardian).
        entradas["asegurar_hoja_global"] = [
            {"preexistente": "vacio"},
            {"preexistente": "hoja_global_vacia"},
            {"preexistente": "hoja_global_editada"},
        ]
        entradas["asegurar_params_local"] = [
            {"preexistente": "vacio"},
            {"preexistente": "hoja_local_vacia"},
            {"preexistente": "hoja_local_editada"},
        ]
        entradas["vdo_guard"] = [
            {"preexistente": "vacio"},
            {"preexistente": "hoja_global_vacia"},
            {"preexistente": "ambas_editadas"},
        ]

    return entradas


def _preparar_guardian(doc, estado: str) -> None:
    """Estado previo del documento.

    Las ediciones se hacen con la API de FreeCAD, no con el guardián.
    """
    if estado == "vacio":
        return
    crear_global = estado in ("hoja_global_vacia", "hoja_global_editada", "ambas_editadas")
    crear_local = estado in ("hoja_local_vacia", "hoja_local_editada", "ambas_editadas")
    editar_global = estado in ("hoja_global_editada", "ambas_editadas")
    editar_local = estado in ("hoja_local_editada", "ambas_editadas")
    if crear_global:
        hoja = doc.addObject("Spreadsheet::Sheet", _GUARDIAN_HOJA_GLOBAL)
        hoja.Label = _GUARDIAN_HOJA_GLOBAL
        if editar_global:
            celda, alias, valor = _GUARDIAN_CELDA_GLOBAL
            hoja.set(celda, valor)
            hoja.setAlias(celda, alias)
    if crear_local:
        hoja = doc.addObject("Spreadsheet::Sheet", _GUARDIAN_HOJA_LOCAL)
        hoja.Label = _GUARDIAN_HOJA_LOCAL
        if editar_local:
            celda, alias, valor = _GUARDIAN_CELDA_LOCAL
            hoja.set(celda, valor)
            hoja.setAlias(celda, alias)


def _volcar_hojas(doc) -> dict:
    """Contenido y alias de las celdas A1:D60 de cada hoja del documento."""
    salida = {}
    for obj in doc.Objects:
        if obj.TypeId != "Spreadsheet::Sheet":
            continue
        celdas = {}
        for fila in range(1, 61):
            for columna in "ABCD":
                ref = f"{columna}{fila}"
                contenido = obj.getContents(ref)
                alias = obj.getAlias(ref)
                if contenido or alias:
                    celdas[ref] = {"contenido": contenido, "alias": alias}
        salida[obj.Name] = {"label": obj.Label, "celdas": celdas}
    return salida


def _ejecutar_guardian(mod, nombre_func: str, entrada: dict):
    """Crea un documento con el estado previo, llama a la función y vuelca las hojas."""
    import FreeCAD as App

    doc = App.newDocument("VDO_GUARDIAN_GOLDEN")
    nombre_doc = doc.Name
    try:
        _preparar_guardian(doc, entrada["preexistente"])
        retorno = getattr(mod, nombre_func)(doc)
        return {
            "retorno": getattr(retorno, "Name", None) or str(retorno),
            "hojas": _volcar_hojas(doc),
        }
    finally:
        App.closeDocument(nombre_doc)


def _ejecutar_funcion(mod, nombre_func: str, entrada: dict):
    """Ejecuta una función de dominio con una entrada y devuelve la salida."""
    if mod.__name__.endswith("guardian"):
        return _ejecutar_guardian(mod, nombre_func, entrada)
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
                salida = _serializar(_ejecutar_funcion(_modulo_para_funcion(modulo, mod, fn_name), fn_name, entrada))
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
    resultado_global = True
    for mod_name in modulos:
        todo_ok = True  # estado de ESTE módulo; un fallo previo no debe silenciar el siguiente
        path = _ruta_golden_json(mod_name)
        if not path.exists():
            print(f"FALTA golden: {path}")
            resultado_global = False
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
                    salida = _ejecutar_funcion(_modulo_para_funcion(mod_name, mod, fn_name), fn_name, entrada)
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
        else:
            resultado_global = False
    return resultado_global


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
