# =====================================================================
# module_props.py
# Constantes y lecturas puras de propiedades de colocación VDO.
#
# add_common_props escribe atributos en objetos FreeCAD recibidos como
# parametro (no importa FreeCAD a nivel de modulo). Este modulo es puro:
# no importa FreeCAD ni Qt a nivel de modulo.
# =====================================================================


import json
import os

# Tabla de anclajes: datos en freecad/vdo/datos/anclajes.json (MN-04).
# Se carga aquí y en cad/propiedades.py. Unificar el cargador cuando core deje de
# importar cad (M5, ver DEUDA_TECNICA.md D-10).
_RUTA_ANCLAJES = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "datos", "anclajes.json")
with open(_RUTA_ANCLAJES, encoding="utf-8") as _fh:
    _DATOS_ANCLAJES = json.load(_fh)

ANCLAJES = list(_DATOS_ANCLAJES["anclajes"])
ANCLAJE_DEFAULT = _DATOS_ANCLAJES["defecto"]
ANCLAJE_LABELS = dict(_DATOS_ANCLAJES["etiquetas"])
ANCLAJE_IDS = {label: idx for idx, label in ANCLAJE_LABELS.items()}

