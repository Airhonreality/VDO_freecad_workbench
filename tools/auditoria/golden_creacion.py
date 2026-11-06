"""Golden de los flujos de creación de módulos (M0, plan de minimalismo).

Se ejecuta con FreeCAD (nivel 2). El código que se mide es el que FreeCAD carga
según el HOME con el que se lance. Para generar desde b78de04:

    H=/tmp/vdo_home_noche   # enlace Mod/VDO -> worktree de b78de04
    HOME=$H GOLDEN_MODO=regenerar freecadcmd tools/auditoria/golden_creacion.py

Para comparar el código actual contra el golden (sin escribir), sin GOLDEN_MODO
o con GOLDEN_MODO=verificar:

    freecadcmd tools/auditoria/golden_creacion.py

Cada flujo tiene 3 entradas. La salida registra volumen, caja envolvente, número de
sólidos y las propiedades VDO que el flujo escribe. No se usa la forma exacta del
Shape: solo cifras que deben ser iguales entre versiones.

El flujo crear_panel (app/casos_uso) no existe en b78de04: se omite aquí y se
documenta en docs/metricas/goldens_origen.md.
"""

import json
import os
import sys

import FreeCAD as App

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
GOLDEN = os.path.join(RAIZ, "tests", "golden", "creacion_modulos.json")

ENTRADAS = {
    "crear_pieza": [
        {"nombre": "P1", "etiqueta": "P1", "orientacion": "horizontal", "largo": 600.0,
         "ancho": 400.0, "espesor": 18.0, "usar_params": False},
        {"nombre": "P2", "etiqueta": "P2", "orientacion": "vertical", "largo": 800.0,
         "ancho": 300.0, "espesor": 16.0, "usar_params": False},
        {"nombre": "P3", "etiqueta": "P3", "orientacion": "horizontal", "largo": 1000.0,
         "ancho": 500.0, "espesor": 18.0, "usar_params": False},
    ],
    "make_coco": [
        {"nombre": "C1", "alto": 700.0, "ancho": 600.0, "fondo_modulo": 580.0},
        {"nombre": "C2", "alto": 720.0, "ancho": 450.0, "fondo_modulo": 560.0},
        {"nombre": "C3", "alto": 2100.0, "ancho": 900.0, "fondo_modulo": 580.0},
    ],
    "make_zocalo": [
        {"nombre": "Z1", "ancho": 600.0, "fondo": 580.0, "alto_zocalo": 100.0},
        {"nombre": "Z2", "ancho": 900.0, "fondo": 560.0, "alto_zocalo": 80.0},
        {"nombre": "Z3", "ancho": 450.0, "fondo": 580.0, "alto_zocalo": 100.0},
    ],
    "make_cajon": [
        {"nombre": "K1", "ancho_libre": 564.0, "prof_libre": 560.0, "ancho_modulo": 600.0},
        {"nombre": "K2", "ancho_libre": 864.0, "prof_libre": 520.0, "ancho_modulo": 900.0},
        {"nombre": "K3", "ancho_libre": 414.0, "prof_libre": 560.0, "ancho_modulo": 450.0},
    ],
    "make_puerta": [
        # Enteros: b78de04 rechaza float en make_puerta (TypeError) y los fixtures usan enteros.
        {"nombre": "D1", "ancho": 614, "alto": 814, "espesor": 18,
         "tipo_montaje": "Parche"},
        {"nombre": "D2", "ancho": 514, "alto": 1214, "espesor": 18,
         "tipo_montaje": "Embebida"},
        {"nombre": "D3", "ancho": 714, "alto": 2014, "espesor": 18,
         "tipo_montaje": "Semiparche"},
    ],
}

PROPS = ["VDO_Orientacion", "VDO_Etiqueta", "VDO_Material_Ref", "Largo", "Ancho",
         "Espesor", "Volumen", "Alto", "Fondo"]


def _fabrica(nombre_flujo):
    """Devuelve la función de creación de b78de04 para cada flujo."""
    if nombre_flujo == "crear_pieza":
        from freecad.vdo.core.vdo_panel_core import crear_pieza as f
    elif nombre_flujo == "make_coco":
        from freecad.vdo.core.vdo_coco_core import make_coco as f
    elif nombre_flujo == "make_zocalo":
        from freecad.vdo.cad.zocalo import make_zocalo as f
    elif nombre_flujo == "make_cajon":
        from freecad.vdo.core.vdo_cajon_core import make_cajon as f
    else:
        from freecad.vdo.core.vdo_puerta_core import make_puerta as f
    return f


def _invocar(fabrica, doc, entrada):
    """Llama a la función de creación según su firma de la versión cargada.

    b78de04: f(configuracion), usa App.ActiveDocument.
    Código actual: f(doc, configuracion). Se detecta por la firma; el resultado es el
    mismo objeto en ambos casos. El cambio de interfaz se registra en goldens_origen.md.
    """
    import inspect
    if len(inspect.signature(fabrica).parameters) >= 2:
        return fabrica(doc, entrada)
    App.setActiveDocument(doc.Name)
    return fabrica(entrada)


def _resumen(obj):
    """Cifras estables de un objeto creado: volumen, caja, sólidos y propiedades."""
    if obj is None:
        return None
    salida = {"label": obj.Label}
    shape = getattr(obj, "Shape", None)
    if shape is not None and not shape.isNull():
        bb = shape.BoundBox
        salida["volumen"] = round(shape.Volume, 3)
        salida["caja"] = [round(bb.XLength, 3), round(bb.YLength, 3), round(bb.ZLength, 3)]
        salida["n_solidos"] = len(shape.Solids)
    props = {}
    for p in PROPS:
        if hasattr(obj, p):
            v = getattr(obj, p)
            if isinstance(v, float):
                v = round(v, 3)
            elif not isinstance(v, (int, str, bool, type(None))):
                v = str(v)  # tipos de FreeCAD (vectores, placements): se comparan como texto
            props[p] = v
    salida["props"] = props
    return salida


def generar():
    import freecad.vdo as _paquete
    print("CODIGO_CARGADO", _paquete.__file__, flush=True)
    resultado = {}
    for flujo, entradas in ENTRADAS.items():
        fila = []
        for entrada in entradas:
            doc = App.newDocument("G_" + flujo)
            App.setActiveDocument(doc.Name)
            try:
                # En b78de04 todas las funciones de creación reciben solo `configuracion`
                # y escriben en App.ActiveDocument.
                obj = _invocar(_fabrica(flujo), doc, entrada)
                doc.recompute()
                fila.append({"entrada": entrada, "salida": _resumen(obj)})
            except Exception as exc:
                # Se registra como salida del golden, nunca se descarta.
                fila.append({"entrada": entrada, "error": f"{type(exc).__name__}: {exc}"})
            finally:
                App.closeDocument(doc.Name)
        resultado[flujo] = fila
    return resultado


def main():
    modo = os.environ.get("GOLDEN_MODO", "verificar")
    nuevo = generar()
    if modo == "regenerar":
        texto = json.dumps(nuevo, indent=2, ensure_ascii=False) + "\n"  # serializa antes de escribir
        with open(GOLDEN, "w", encoding="utf-8") as f:
            f.write(texto)
        print("GOLDEN_ESCRITO", GOLDEN, flush=True)
        return
    with open(GOLDEN, encoding="utf-8") as f:
        esperado = json.load(f)
    difs = 0
    for flujo, filas in nuevo.items():
        for i, fila in enumerate(filas):
            lista = esperado.get(flujo)
            exp = lista[i] if isinstance(lista, list) and i < len(lista) else None
            if exp != fila:
                difs += 1
                print("DIFERENCIA", flujo, i, "\n  golden:", exp, "\n  actual:", fila, flush=True)
    print("VERIFICAR diferencias=", difs, flush=True)


try:
    main()
except BaseException:
    import traceback
    traceback.print_exc(file=sys.stdout)
    sys.stdout.flush()
    raise
