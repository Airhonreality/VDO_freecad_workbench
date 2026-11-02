# Plan de refactorización VDO

Documento ejecutable por un agente. Las decisiones de la sección 2 están **cerradas**: no se
rediscuten durante la ejecución. Si una decisión resulta imposible de cumplir, se registra en
`docs/PROGRESO_REFACTOR.md` con la evidencia y se propone una alternativa, sin cambiarla en silencio.

Origen: auditoría de arquitectura y calidad (ver sección 3 para la línea base medida).

---

## 0. Reglas de ejecución

1. **Ramas y commits.** Cada fase vive en `refactor/fN-<slug>` creada desde la rama anterior
   terminada (F1 desde `refactor/estabilizar-migracion`). Un commit por fase (puede haber más si
   se necesitan, pero el cierre de fase es un commit). **No hacer push. No hacer merge a `main`.**
2. **Atribución en commits:** terminar el mensaje con
   `Co-Authored-By: Claude Haiku 5.5 <noreply@anthropic.com>`.
3. **Idioma de commits:** español, formato `tipo(ámbito): resumen` (como los commits existentes).
4. **Paridad de comportamiento.** Ninguna fase cambia resultados numéricos (medidas de piezas,
   costos, cortes, BOM). Si un cambio de comportamiento es inevitable, va en una fase aparte y
   queda documentado. El único cambio visual permitido es el de la fase F3 (tema de color, D-10).
5. **Línea base de tests (no puede empeorar):** `VDO_TEST_DIR=tests VDO_TEST_OUT=/tmp/t.txt python3 tools/run_tests.py`
   debe dar **al menos 91 OK y 0 fallos**. Los 11 errores de importación (PySide/FreeCAD ausentes)
   son esperables fuera de FreeCAD. Si una fase añade tests, el número de OK sube, nunca baja.
6. **Verificación en FreeCAD.** Si `freecadcmd` está disponible, ejecutar también
   `VDO_TEST_DIR=tests VDO_TEST_OUT=/tmp/tf.txt freecadcmd tools/run_tests.py` y registrar el
   resultado. Si no está disponible, anotar en el progreso "pendiente de verificación en FreeCAD".
   No declarar nada como verificado en FreeCAD sin haberlo ejecutado.
7. **Criterio de parada.** Si una fase rompe la línea base y no se arregla en el mismo intento,
   revertir esa fase (`git reset --hard` de la rama de la fase, nunca sobre `main` ni sobre
   ramas previas) y registrar el motivo en el progreso. Pasar a la siguiente fase solo si no
   depende de la rota.
8. **Registro.** Tras cada fase, añadir una entrada en `docs/PROGRESO_REFACTOR.md` (plantilla en §5).
9. **Alcance.** Solo lo que dice la fase. No añadir funcionalidad, no renombrar fuera de lo indicado,
   no reformatear archivos que la fase no toca.
10. **Antes de borrar:** comprobar importadores con grep (`grep -rn "nombre" freecad tests tools`)
    y comprobar que no se referencia por cadena en `package.xml`, `InitGui.py` ni en JSON.

---

## 1. Principios

- **Una sola definición por regla o dato.** Si algo se define dos veces, se elimina una.
- **Core agnóstico:** `freecad/vdo/core/` no importa Qt, `FreeCADGui` ni `ui/`.
- **Qt solo en una capa:** únicamente `freecad/vdo/qt_compat.py` importa PySide.
- **Declarativo antes que imperativo** cuando el contenido es una especificación (formularios, campos).
- **Errores visibles:** nada de `except: pass`.

---

## 2. Decisiones cerradas

| ID | Tema | Decisión |
|---|---|---|
| D-01 | Ramas | Ver §0.1. Base: `refactor/estabilizar-migracion` (commit `836b31e`). |
| D-02 | Idioma de código | Identificadores de dominio en español (como hoy). Nombres de API de FreeCAD/Qt en inglés (`accept`, `setStyleSheet`). Docstrings y mensajes al usuario en español. Sin mezclar en un mismo identificador. |
| D-03 | Manifiesto (datos) | **Un único módulo** `core/vdo_manifest.py`. Se absorbe `core/vdo_loader.py` (métodos `get_material`, `get_hardware`, `get_process`, `validar_compatibilidad`, `calcular_costo_material`, `listar_materiales`, `listar_herrajes`, `get_loader`) como funciones de ese módulo; se conservan los nombres que usan los llamadores y se borra `vdo_loader.py`. |
| D-04 | Carga del manifiesto | Se mantiene la carga **fresca** (sin caché de módulo), principio original del proyecto. Si la UI lo necesita, la caché se hace en la capa llamadora, no en el loader. |
| D-05 | Validación JSON Schema | **Se elimina.** El esquema `core/schemas/vdo_manifest_schema.json` no existe y la validación nunca corre. `jsonschema` sale del código. Si se quiere validar, será una función Python explícita en `vdo_manifest.py` (fase futura, fuera de este plan). |
| D-06 | Duplicado de carga JSON | `core/vdo_defaults.py::_cargar_json_fresco` se reemplaza por la función de `vdo_manifest.py`. |
| D-07 | Panel COCO | **Único panel: `ui/vdo_coco_unified_task.py`** (está cableado en `vdo_view_providers.py` y `vdo_drag_handles.py`). |
| D-08 | Variantes COCO muertas | Se **borran** `ui/vdo_coco_task.py` y `ui/vdo_coco_spaces_task.py` (sin importadores). Hay que ajustar `tests/test_gui_wiring.py` (test `test_extirpacion_combos_planos_en_coco_task` referencia el módulo por nombre): reescribir el test para que apunte a `vdo_coco_unified_task.py` o eliminarlo si ya no aplica, y justificarlo en el progreso. |
| D-09 | Widgets COCO compartidos | `ui/vdo_coco_divisions_task.py` **no es un panel**: contiene `PanelHeaderWidget` (usado por `vdo_zocalo_task.py`) y `DivisionesEditor` (usado por `vdo_coco_unified_task.py`). Se renombra con `git mv` a `ui/vdo_widgets_coco.py` y se actualizan los imports. El contenido no se reescribe en esta fase. |
| D-10 | Tema de color | Módulo único `ui/vdo_theme.py` con tokens (fondo, fondo2, texto, texto_suave, borde, acento, error…). Acento unificado en **`#007acc`** (38 usos frente a 26 de `#0098ff`). Único cambio visual autorizado. |
| D-11 | Qt | Solo `qt_compat.py` importa PySide. Los 7 módulos con import directo y los tests que lo hacen se migran a `from freecad.vdo.qt_compat import …`. Se añade un test que falla si aparece `PySide` fuera de `qt_compat.py`. |
| D-12 | Base de paneles | `ui/vdo_task_base.py` es la **única** base de Task Panels. Las implementaciones idénticas de `reject`, `accept`, `helpRequested`, `getStandardButtons` y `clicked` migran a ella. Los 5 paneles vivos (`cajon`, `unified`, `panel`, `puerta`, `zocalo`) la usan. |
| D-13 | Reglas de dominio | `necesita_expulsor_magnetico`, `necesita_cantos_45` y constantes `APERTURA_*` viven **en `core/vdo_facade_contract.py`** (ya es el contrato). `vdo_cajon_despiece.py` y `vdo_puerta_despiece.py` importan de ahí; se borran sus copias y el wrapper `necesita_expulsor_magnetico_contrato`. Verificar antes que no haya import circular. Si `necesita_cantos_45` no está ya en el contrato, se mueve allí con la misma regla (comprobar primero las copias existentes). |
| D-14 | Motor de despiece | Cajón y puerta comparten un motor en `core/vdo_despiece_base.py` **solo después** de tener tests de snapshot que fijen la salida actual (F5, paso 1). |
| D-15 | Formularios de paneles | Se generan desde especificación declarativa en `ui/vdo_form_builder.py`, apoyado en `core/vdo_module_specs.py`. Migración **uno por uno**, en este orden: `zocalo` → `panel` → `puerta` → `cajon` → `unified`. Cada panel migrado debe mantener sus campos, valores por defecto, validación y señales. |
| D-16 | Excepciones | Prohibido `except: pass` y `except:` desnudo. `except Exception` solo si se registra con `App.Console.PrintWarning/PrintError` incluyendo contexto, y se re-lanza o se devuelve un valor explícito documentado. Se añade un test que lo verifica sobre `freecad/`. |
| D-17 | `print` | Prohibido `print(` en `freecad/`. Usar `App.Console` (o el logger de `vdo_paths`/un helper único si se crea). `tools/` puede usar `print`. |
| D-18 | `sys.path` | Se elimina de `tests/` (el runner ya fija la ruta). Se mantiene en `Init.py`/`InitGui.py` solo si FreeCAD lo requiere; justificar en comentario. |
| D-19 | `_module_dir()` en Init/InitGui | **No se toca.** FreeCAD ejecuta esos archivos sin `__file__`; la duplicación es un requisito de la plataforma. |
| D-20 | Funciones largas | Objetivo: ninguna función > 150 líneas al cerrar F7 (hoy 21 > 120). Se descompone por responsabilidad sin cambiar salidas. Requiere snapshot previo (ver F7). |
| D-21 | Reengrose | `core/vdo_reengrose_solids.py` (52 líneas) se fusiona en `core/vdo_reengrose.py`. Se borra el archivo y se actualizan imports. |
| D-22 | Documentación | `docs/` se ordena así: se **mueven** (no se borran) a `docs/archivo/` los `BASELINE_*`, `RESULTADOS_*`, `SESION_*`, `PLAN_CONVERSION_*`, `workbench investigation.txt` y `Arquitectura de capas espacios a modulos.txt`. Se mantienen en `docs/`: `PROGRESO_VDO.md`/`.yaml` (fuente de progreso), `DEUDA_TECNICA_VDO.md`, `CONTEXTO_TECNICO_VDO.md`, `REVISION_ARQUITECTURA_CAPAS.md`, `MANIFIESTO_DISENO_INTERFAZ_VDO.md`, `vdo_diccionario_semantico.md`, `VDO_NESTING_README.md`, `MATRIZ_MAPEO.md`. Se crea `docs/ARQUITECTURA.md` (F9) como documento vivo que reemplaza a los anteriores para la arquitectura. |
| D-23 | Inspector / optimizador / lista de corte / herrajes | **Fuera de alcance de F1–F8.** Se revisan en F8 solo para eliminar duplicación evidente. No se fusionan módulos sin evidencia de solapamiento de responsabilidad (registrar la evidencia). |
| D-24 | Caja del mueble | `ui/vdo_box_controller.py` y `ui/vdo_chassis_widget.py` comparten `get_svg_icon` (se resuelve en F3). El resto de su fusión queda **fuera de alcance**. |
| D-25 | Herramientas de auditoría | Se conservan en `tools/auditoria/` y son la fuente de las métricas de cierre de cada fase. |

---

## 3. Línea base (medida antes de la refactorización)

| Métrica | Valor | Cómo medirla |
|---|---|---|
| Archivos Python en `freecad/` | 65 | `find freecad -name "*.py" \| wc -l` |
| Líneas Python (`freecad/`, `tests/`, `tools/`) | 28.681 | `find freecad tests tools -name "*.py" \| xargs cat \| wc -l` |
| Tests (modo puro) | 103 ejecutados, 91 OK, 0 fallos, 11 errores, 3 skip, 8 no ejecutados | `tools/run_tests.py` |
| `except ... pass` | ~69 | grep en `freecad/`, `tests/`, `tools/` |
| `except Exception` (en `freecad/`) | 135 | `grep -rn "except Exception" freecad` |
| `except:` desnudo | 6 | grep |
| `print(` en `freecad/` | 119 | `grep -rn "^\s*print(" freecad` |
| `hasattr(` en `freecad/` | 118 | grep |
| `sys.path` (freecad, tests, tools, Init) | 39 | grep |
| `setStyleSheet` | 91 | grep |
| Archivos con colores hex literales | 17 | `grep -rlE "#[0-9a-fA-F]{6}\b" freecad` |
| Funciones > 120 líneas | 21 | `python3 -I tools/auditoria/ast_scan.py freecad` |
| Grupos de funciones con cuerpo idéntico | 7 | `python3 -I tools/auditoria/clones.py freecad` |
| Módulos sin importadores | 3 (794 líneas) | `vdo_coco_task.py`, `vdo_coco_spaces_task.py`, `vdo_detect_config.py` |
| Archivos que importan PySide fuera de `qt_compat` | 7 módulos `ui/` + tests | `grep -rln PySide freecad` |

Nota de corrección: la auditoría inicial contó 8 paneles de tarea. Son **7 vivos** más un archivo de
widgets (ver D-09). Los datos de esta tabla son los correctos.

---

## 4. Fases

Cada fase incluye: objetivo, pasos, criterio de aceptación y verificación. "Métricas" son los
comandos de §3 que deben mejorar (o no empeorar).

### F1 — Código muerto y documentación

**Objetivo:** eliminar lo que no se usa y ordenar `docs/`.

Pasos:
1. Confirmar por grep que `vdo_coco_task.py`, `vdo_coco_spaces_task.py`, `vdo_detect_config.py` no tienen importadores (incluye `package.xml`, `InitGui.py`, `commands.py`, JSON).
2. `git rm` de esos tres archivos (D-08). Ajustar `tests/test_gui_wiring.py` (D-08).
3. `git mv` de `ui/vdo_coco_divisions_task.py` → `ui/vdo_widgets_coco.py` y actualizar imports en `vdo_coco_unified_task.py` y `vdo_zocalo_task.py` (D-09).
4. Reorganizar `docs/` según D-22: `mkdir docs/archivo` y `git mv`.

Aceptación:
- Métrica: módulos sin importadores = 0 (repetir el script de búsqueda de la auditoría).
- Tests: ≥ 91 OK, 0 fallos. El test de `test_gui_wiring` ajustado y justificado.
- Ningún archivo de `docs/` perdido (`git log --follow` o conteo: el total de archivos en `docs/` + `docs/archivo/` no baja).

### F2 — Fuente única de datos (manifiesto y reglas)

**Objetivo:** un solo cargador de manifiesto y una sola definición de las reglas de apertura.

Pasos:
1. Mover a `core/vdo_manifest.py` los métodos de `vdo_loader.py` (D-03). Mantener nombres de función usados por `ui/vdo_cutting_list_preview.py` y `ui/vdo_export_cutting_list.py`; cambiar esos dos imports para usar el módulo único. Borrar `core/vdo_loader.py`.
2. Quitar `jsonschema` y la búsqueda de esquema (D-05).
3. `core/vdo_defaults.py`: reemplazar `_cargar_json_fresco` por la función de `vdo_manifest.py` (D-06).
4. Reglas de apertura en `core/vdo_facade_contract.py` (D-13): eliminar `necesita_expulsor_magnetico` de `vdo_cajon_despiece.py` y `vdo_puerta_despiece.py`, y el wrapper `necesita_expulsor_magnetico_contrato`; importar desde el contrato. Eliminar `APERTURA_PUSH_OPEN` duplicado.
5. Añadir un test de paridad: para cada tipo de apertura conocido, la regla devuelve el mismo valor que antes (valores fijados a mano en el test).

Aceptación:
- Solo existe un archivo que carga `vdo_manifest.json` (`grep -rn "vdo_manifest.json" freecad` → solo `vdo_manifest.py`).
- `grep -rn "def necesita_expulsor_magnetico" freecad` → exactamente 1.
- Tests ≥ 91 OK + el nuevo de paridad, 0 fallos.
- Los cálculos de costo de corte no cambian (test o comparación manual de un caso).

### F3 — Capa Qt, tema y duplicados de estilo

**Objetivo:** que Qt entre por un solo punto y que el color salga de un solo sitio.

Pasos:
1. Migrar los 7 módulos `ui/` con `from PySide…` a `qt_compat` (D-11). Migrar los tests que lo hacen.
2. Crear `ui/vdo_theme.py` con tokens (D-10). Sustituir los 17 archivos con colores hex por referencias a tokens. El acento pasa a `#007acc`.
3. Unificar `get_svg_icon` (D-24): una sola definición en `ui/vdo_theme.py` o `core/vdo_paths.py` según su naturaleza (decidir y registrar en progreso); eliminar las dos copias.
4. Añadir test: `PySide` aparece solo en `qt_compat.py` (D-11).

Aceptación:
- `grep -rln PySide freecad` → solo `freecad/vdo/qt_compat.py`.
- `grep -rlE "#[0-9a-fA-F]{6}\b" freecad` → solo `ui/vdo_theme.py` (y justificar excepciones si las hay).
- `grep -rn "def get_svg_icon" freecad` → 1.
- Tests ≥ 91 OK, 0 fallos.
- Captura de la interfaz antes y después si hay FreeCAD con GUI disponible; si no, registrar "pendiente de verificación visual".

### F4 — Base de paneles de tarea

**Objetivo:** que los paneles compartan su esqueleto en una sola base.

Pasos:
1. Mover a `VDOTaskBase` (D-12) los métodos idénticos: `reject`, `accept`, `helpRequested`, `getStandardButtons`, `clicked` (los 5 clones de `reject` están en `cajon_task`, `coco_unified_task`, `panel_task`, `puerta_task`, `zocalo_task`).
2. Verificar que los 5 paneles heredan de la base; los que no, migrarlos.
3. Eliminar las copias.

Aceptación:
- `grep -rn "def reject" freecad/vdo/ui` → solo la base (o las excepciones justificadas).
- Clones de `reject`: 0 grupos (`clones.py`).
- Tests ≥ 91 OK, 0 fallos.

### F5 — Motor de despiece cajón/puerta

**Objetivo:** un solo motor de despiece parametrizado.

Pasos:
1. **Primero** tests de snapshot: para un conjunto de configuraciones representativas de cajón y puerta, guardar la salida actual (BOM, dimensiones de piezas) en un fixture en `tests/fixtures/`. Estos tests deben pasar **antes** de cualquier cambio.
2. Crear `core/vdo_despiece_base.py` con la lógica común. Cajón y puerta pasan a ser configuraciones/subclases.
3. Los snapshots no pueden cambiar. Si cambian, la fase se revierte (§0.7).

Aceptación:
- Snapshots idénticos antes y después.
- `diff` entre `vdo_cajon_despiece.py` y `vdo_puerta_despiece.py` reducido de forma medible (registrar cifra antes/después; la línea base es ~900 líneas de diff).
- Tests ≥ línea base, 0 fallos.

### F6 — Formularios declarativos

**Objetivo:** que los campos de los paneles salgan de una especificación.

Pasos:
1. Crear `ui/vdo_form_builder.py`: a partir de una lista de campos (tipo, etiqueta, clave, valor por defecto, rango, unidades, dependencias) construye el formulario.
2. Migrar en este orden (D-15): `vdo_zocalo_task.py` → `vdo_panel_task.py` → `vdo_puerta_task.py` → `vdo_cajon_task.py` → `vdo_coco_unified_task.py`. Cada uno en su commit dentro de la fase.
3. Para cada panel, un test que comprueba que el formulario generado tiene los mismos campos, valores por defecto y rangos que antes (la línea base se captura antes de migrar).

Aceptación:
- Cada panel migrado: mismos campos y valores por defecto (test de paridad).
- `_crear_widget` de los paneles migrados: reducido a una llamada al builder.
- Métrica `_crear_widget` > 120 líneas: 0 en los migrados.
- Tests ≥ línea base, 0 fallos.
- Verificación visual en FreeCAD pendiente si no está disponible; registrar.

### F7 — Complejidad

**Objetivo:** ninguna función > 150 líneas (D-20) y reengrose en un solo módulo (D-21).

Pasos:
1. Fusionar `core/vdo_reengrose_solids.py` en `core/vdo_reengrose.py` (D-21).
2. Para cada función > 150 líneas, capturar la salida con un caso representativo **antes**, descomponer, comparar **después**. Prioridad: `vdo_coco_core.execute` (428), `vdo_cajon_despiece.calcular_despiece` (326), `vdo_chassis_widget._init_ui` (238), `vdo_box_controller._construir_ui` (232), `vdo_coco_divisions_task._actualizar_inspector` (222), `vdo_reengrose.generar_tiras_perimetrales` (220), `vdo_chassis_widget.paintEvent` (210), `vdo_universal_inspector.__init__` (207).
3. Los `_crear_widget` restantes que no se migraron en F6 se descomponen aquí.

Aceptación:
- `ast_scan.py`: funciones > 150 líneas = 0.
- Salidas idénticas en los casos capturados.
- Tests ≥ línea base, 0 fallos.

### F8 — Excepciones, `print`, `sys.path` y duplicación restante

**Objetivo:** errores visibles y eliminación de los duplicados que quedan.

Pasos:
1. Aplicar D-16: eliminar `except: pass`, convertir `except:` desnudo. Donde se captura por diseño (p. ej. `cerrar_dialogo` en `vdo_task_base.py`), registrar con `App.Console`.
2. Aplicar D-17: reemplazar `print(` en `freecad/` por `App.Console`.
3. Aplicar D-18: quitar `sys.path` de `tests/`.
4. Eliminar los grupos de clones que queden (`clones.py`), excepto los que D-23 deja fuera.
5. Añadir tests que verifican D-16 y D-17 (escaneo AST/grep sobre `freecad/`).

Aceptación:
- `grep -rn "except:\s*$" freecad` → 0.
- `except ... pass` → 0 (script de búsqueda).
- `print(` en `freecad/` → 0.
- `sys.path` en `tests/` → 0.
- Grupos de clones → 0 (o justificados en progreso).
- Tests ≥ línea base + nuevos, 0 fallos.

### F9 — Cierre y documentación

**Objetivo:** dejar el estado documentado y medido para la revisión final.

Pasos:
1. Recalcular toda la tabla de §3 y registrar "antes / después" en `docs/PROGRESO_REFACTOR.md`.
2. Crear `docs/ARQUITECTURA.md`: capas (core / ui / commands / qt_compat), reglas (D-02 a D-19), cómo añadir un módulo, cómo correr tests. Marcar como reemplazo de los documentos archivados.
3. Actualizar `docs/DEUDA_TECNICA_VDO.md` marcando lo resuelto y lo que queda fuera (D-23, D-24 resto, D-19).
4. Resumen de la reducción de líneas real (`git diff --stat` de la rama contra `refactor/estabilizar-migracion`).

Aceptación: todas las métricas de §3 medidas de nuevo y registradas; documentación actualizada.

---

## 5. Plantilla de progreso (`docs/PROGRESO_REFACTOR.md`)

Crear este archivo en F1 con la cabecera. Por fase:

```
## Fase Fn — <nombre>
- Rama / commit:
- Estado: completada | revertida | parcial
- Pasos hechos:
- Métricas antes → después (de §3):
- Tests (modo puro): OK / fallos / errores / skip
- Tests (FreeCAD): ejecutados / pendiente de verificación
- Decisiones nuevas tomadas (no previstas en §2) y motivo:
- Desviaciones de este plan y motivo:
- Pendiente para revisión humana:
```

---

## 6. Fuera de alcance

- Nuevas funcionalidades, cambios de fórmulas de cálculo o de costos.
- Herramienta de ERP (`tools/vdo_erp_sync/`): no se toca.
- Reescritura de Init.py/InitGui.py (ver D-19).
- Fusión de inspector, optimizador, lista de corte y herrajes (D-23).
- Push, merge a `main`, reescritura de historial.
- Eliminar `Macro/` del historial de git.

---

## 7. Entrega para revisión humana

Al terminar todas las fases, el agente deja:
- Las ramas `refactor/f1-…` a `refactor/f9-…` con sus commits.
- `docs/PROGRESO_REFACTOR.md` completo.
- La tabla de §3 con valores finales.
- Una lista de lo que requiere verificación visual o en FreeCAD con GUI.

No se hace merge. El revisor humano decide.
