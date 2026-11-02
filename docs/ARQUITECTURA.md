# Arquitectura VDO

Documento vivo de la arquitectura del workbench VDO tras la refactorización
(`docs/PLAN_REFACTOR_VDO.md`, fases F1–F8). Reemplaza a los documentos
archivados en `docs/archivo/` (BASELINE_*, RESULTADOS_*, SESION_*,
PLAN_CONVERSION_*, `workbench investigation.txt`,
`Arquitectura de capas espacios a modulos.txt`).

---

## 1. Objetivo y alcance

VDO es un workbench de FreeCAD para diseño de mobiliario de carpintería
(paramétrico: cajones, puertas, zócalos, paneles y contenedores COCO). La
arquitectura separa estrictamente la lógica de dominio (sin FreeCAD ni Qt) de
la capa de interfaz (Qt/FreeCADGui).

## 2. Capas

```
freecad/vdo/
├── __init__.py            # Paquete y registro de comandos/vista
├── commands.py            # Comandos de Workbench (toolbar)
├── qt_compat.py           # UNICO punto de importacion de PySide (PySide6->2->PySide)
├── qt_compat.py expone:   QtCore, QtGui, QtWidgets, QtSvg
├── ui/                    # Capa UI (Qt). Importa solo desde qt_compat.
│   ├── vdo_theme.py       # Tokens de color + get_svg_icon unificado (D-10, D-24)
│   ├── vdo_form_builder.py# Constructor declarativo de formularios (D-15)
│   ├── vdo_task_base.py   # Base unica de Task Panels (VDOTransactionMixin) (D-12)
│   ├── vdo_qt.py          # Controles Qt (VDO_DoubleSpinBox, VDO_ExpressionInput)
│   ├── vdo_*.task.py      # Task Panels: cajon, panel, puerta, zocalo, coco_unified, widgets_coco
│   └── ... (utilidades UI: inspector, docking, listas de corte, etc.)
└── core/                  # Capa pura (SIN FreeCAD, SIN Qt, SIN ui/)
    ├── vdo_manifest.py    # UNICO cargador del manifiesto JSON (funciones de acceso)
    ├── vdo_facade_contract.py  # Contrato unificado de aperturas/fachadas (D-13)
    ├── vdo_defaults.py    # Valores por defecto (usa vdo_manifest)
    ├── vdo_reengrose.py   # Motor de reengrose (incluye forma_ref, D-21)
    ├── vdo_reengrose_solids.py  # BORRADO (fusionado en vdo_reengrose)
    ├── vdo_loader.py      # BORRADO (absorbido en vdo_manifest)
    ├── vdo_cajon_despiece.py
    ├── vdo_puerta_despiece.py
    └── ... (resto de logica pura)
```

- **Core agnóstico** (`freecad/vdo/core/`): no importa Qt, `FreeCADGui` ni
  `ui/`. Solo lógica pura, decimales y enums. `vdo_reengrose.py` importa
  `FreeCAD`/`Part` solo para `forma_ref` (construcción de `Part.Shape`), por
  decisión explícita de D-21.
- **Qt solo en una capa**: únicamente
  `freecad/vdo/qt_compat.py` importa PySide. Todo el resto (`core/`, `ui/`,
  tests) importa desde `qt_compat`.
- **UI**: `ui/` importa Qt exclusivamente a través de `qt_compat`.

## 3. Reglas de diseño (decisiones cerradas, §2 del plan)

| ID | Regla |
|----|-------|
| D-02 | Identificadores de dominio en español; API de FreeCAD/Qt en inglés; docstrings y mensajes al usuario en español. |
| D-03 / D-05 / D-06 | Un único módulo de datos: `core/vdo_manifest.py`. Se eliminó `vdo_loader.py`, `jsonschema` y el esquema JSON. Carga fresca del JSON (sin caché de módulo). |
| D-07 / D-08 | Panel COCO único: `ui/vdo_coco_unified_task.py`. Borrados `vdo_coco_task.py` y `vdo_coco_spaces_task.py` (sin importadores). |
| D-09 | `ui/vdo_coco_divisions_task.py` → `ui/vdo_widgets_coco.py` (no es panel; contiene `PanelHeaderWidget` y `DivisionesEditor`). |
| D-10 | Tema único: `ui/vdo_theme.py` con tokens; acento `#007acc`. |
| D-11 | Solo `qt_compat.py` importa PySide. |
| D-12 | `ui/vdo_task_base.py` es la base única de Task Panels. |
| D-13 | Reglas de apertura (`necesita_expulsor_magnetico`, `necesita_cantos_45`, `APERTURA_*`) viven en `core/vdo_facade_contract.py`. |
| D-16 | Prohibido `except: pass` y `except:` desnudo; errores visibles. |
| D-17 | Prohibido `print(` en `freecad/`; usar `App.Console`. |
| D-18 | `sys.path` eliminado de `tests/` (el runner fija la ruta). |

## 4. Flujo de datos

1. El manifiesto (`core/vdo_manifest.json`) se lee fresco vía
   `core/vdo_manifest.py` (funciones `get_material`, `get_hardware`,
   `calcular_costo_material`, etc.).
2. Los cálculos de dominio (despiece, reengrose, fachada) viven en `core/`
   y son testables con `python3` sin FreeCAD.
3. Los Task Panels (`ui/*_task.py`) heredan de `VDOTransactionMixin` y
   construyen su formulario (cuando migrado) con `FormBuilder`.
4. La vista 3D y los `ViewProvider` usan `Part::FeaturePython`; `execute()`
   nunca modifica `Placement` (la pose vive en propiedades `VDO_*`).

## 5. Cómo añadir un módulo

1. Lógica pura → `freecad/vdo/core/` (sin imports de Qt/FreeCADGui).
2. Si necesita Qt → `freecad/vdo/ui/` importando solo de `qt_compat`.
3. Si es un Task Panel → heredar de `VDOTransactionMixin` en
   `ui/vdo_task_base.py`.
4. Nunca importar `PySide` fuera de `qt_compat.py` (verificado por test
   `test_qt_compat_solo_punto_entrada_pyside`).
5. Nunca usar `print(` en `freecad/` (verificado por test
   `test_no_print_en_freecad`).

## 6. Cómo correr los tests

Modo puro (sin FreeCAD):
```
VDO_TEST_DIR=tests VDO_TEST_OUT=/tmp/t.txt python3 tools/run_tests.py
```
Línea de aceptación: ≥ 91 OK, 0 fallos. Los errores de importación
(PySide/FreeCAD ausentes) son esperables fuera de FreeCAD.

Modo FreeCAD (si hay `freecadcmd`):
```
VDO_TEST_DIR=tests VDO_TEST_OUT=/tmp/tf.txt freecadcmd tools/run_tests.py
```

## 7. Documentación relacionada (mantenida en `docs/`)

- `DEUDA_TECNICA_VDO.md`: deuda técnica conocida y no resuelta.
- `CONTEXTO_TECNICO_VDO.md`, `REVISION_ARQUITECTURA_CAPAS.md`,
  `MANIFIESTO_DISENO_INTERFAZ_VDO.md`, `vdo_diccionario_semantico.md`,
  `VDO_NESTING_README.md`, `MATRIZ_MAPEO.md`, `PROGRESO_VDO.md/.yaml`.
- `docs/archivo/`: documentos históricos movidos en F1 (BASELINE_*,
  RESULTADOS_*, SESION_*, PLAN_CONVERSION_*, etc.).
- `docs/PROGRESO_REFACTOR.md`: registro fase a fase de la refactorización.

## 8. Fuera de alcance de la refactorización (F1–F8)

- Fusión de inspector, optimizador, lista de corte y herrajes (D-23).
- Resto de la fusión de `vdo_box_controller` / `vdo_chassis_widget` (D-24).
- `Init.py`/`InitGui.py` no reescritos (D-19).
- Descomposición de funciones > 150 líneas pendiente de snapshots dedicados
  (D-20, diferida para preservar paridad de comportamiento).
- Motor compartido de despiece cajón/puerta pendiente de evidencia de
  solapamiento (D-14, diferido).
