# Deuda técnica VDO

**Estado a 2026-11-06 (cierre de M11).** Este es el único registro de deuda. Sustituye a `docs/DEUDA_TECNICA_VDO.md`, que se archivó en `docs/archivo/` tras fusionar lo que seguía abierto.

**Cómo leer las tablas**
- **Responsable:** *usuario* = decisión o revisión humana; *ejecutor* = trabajo del asistente.
- **Fecha:** *propuesta*. Las fechas son propuestas del ejecutor y el usuario debe confirmarlas. Ninguna está aprobada.
- **Cifras:** de `docs/metricas/minimalismo_final.json` y `docs/metricas/minimalismo_base.json`, o del registro (`docs/DECISIONES_DELEGADAS.md`, `docs/PROGRESO_MINIMALISMO.md`). Si una cifra viene del encargo y no se encontró en esos archivos, se dice.

---

## A. Metas del plan no cumplidas

| ID | Ítem | Medida | Responsable | Fecha |
|---|---|---|---|---|
| A1 | **Reducción de líneas ≥ 30 % no cumplida.** | 23.608 líneas (base, `minimalismo_base.json`) → 25.171 (final, `minimalismo_final.json`): **+6,6 %**. Frente a las 23.920 del plan §1, el cálculo da +5,2 %. Se acepta o se abre una fase de reducción. | usuario | 2026-11-13 (propuesta) |
| A2 | Otras metas de §1 no cumplidas | Tablas idénticas: 1 grupo (meta 0). Funciones con 4 o más ramas: 3 (meta 0). Bloques `__all__`: 11 archivos (meta 0; aumentaron). `QLabel(`: **109** líneas (medido 2026-11-06 con `grep -rc`; 123 en M11; de 171). `addWidget`: **239** líneas (medido 2026-11-06; 286 en M11; de 401). Suma medida 2026-11-06: **348**. `setStyleSheet` fuera de `ui/tema.py`: 0 (medido en M11; la cifra de 2 del grep de M10 eran una línea de docstring y la única llamada, ambas en `tema.py`). Capa `ui`: 14.374 líneas (de 13.507; meta: reducir a presentación) en M11. Re-medido 2026-11-06 con `wc -l` sobre `freecad/vdo/ui/*.py` (incl. subcarpetas): 13.461. La diferencia con 14.374 no está explicada. | usuario decide si se aceptan con justificación o se abre fase. Ejecutor, si se abre. | 2026-11-13 (propuesta) |
| A3 | Método de conteo del plan | El plan §1 cita 88 archivos y 23.920 líneas; la herramienta mide 85 y 23.608 sobre la base. Hay que fijar un solo método (D-03). | usuario | 2026-11-13 (propuesta) |
| A4 | Línea base de `app/` | El plan cita 518 líneas; `minimalismo_base.json` mide 21 archivos y 941 líneas. `app/` ya está eliminado; la diferencia queda sin explicar en el registro. | usuario (solo informativo) | 2026-11-13 (propuesta) |

---

## B. Defectos preexistentes para la fase de depuración

Revisado con mediciones el 2026-11-06; las entradas marcadas RESUELTO tienen el commit o D-xx que lo prueba.

Fecha propuesta para toda la sección: 2026-11-20. Responsable: ejecutor, salvo lo indicado.

| ID | Defecto | Estado de la comprobación | Acción propuesta |
|---|---|---|---|
| B1 | **`TipoMontaje` del accept del cajón.** El combo muestra `Parche`, `Semiparche`, `Embebida`. El accept escribía `currentText()` y la carga usaba `findText`, que distingue mayúsculas. | **RESUELTO (D-87, commit `a77cafe`).** Medido 2026-11-06: `freecad/vdo/datos/formularios.py` línea 24 define `MONTAJES_FACHADA` con los valores de `core/facade_contract.py` (`parche`, `semiparche`, `embebida`). `freecad/vdo/ui/cajon_task.py` carga con `findData(obj.TipoMontaje)` (línea 164) y escribe con `currentData()` (línea 268). Prueba: `tests/test_cajon_montaje_defecto.py`, 2 tests OK en la ejecución de 2026-11-06. | Ninguna. |
| B2 | **Accept que escribe propiedades antes de un error** (puerta, cajón, coco y paneles). | **RESUELTO (D-88).** Mecanismo único `freecad/vdo/cad/transaccion.py`; commits `f2cbd44` (cajón), `ac7a686` (coco) y `f543f3c` (registro). Prueba: `tests/test_accept_atomico.py`, 5 tests OK (zócalo, panel, puerta, cajón, coco) en la ejecución de 2026-11-06 con `VDO_TEST_DIR=tests freecadcmd tools/run_tests.py` (`fallos=0`). Límite de D-88: las validaciones posteriores a la escritura se cubren restaurando, no reordenando. | — |
| B3 | **Zócalo: volumen 0.0 en el escenario normal**, sin explicación. | **Resuelto como artefacto de prueba (D-89).** Evidencia: con 600 × 580 × 100 mm el volumen es 3866400.0 mm³ (4 sólidos, caja 600 × 510 × 100) tras `make_zocalo` + `recompute`, y sigue igual tras `ZocaloTaskPanel.accept()` con y sin transacción automática. Leer `Shape.Volume` antes del recálculo lanza `RuntimeError`, no devuelve 0.0. Script y salidas en `/tmp/f3_eq/` (fuera del repo). | Ninguna en código. La prueba que reportaba 0.0 no está en el repo; si existe fuera, debe recalcular antes de leer el volumen. |
| B4 | **`nesting_presets` sin golden.** `core/nesting_presets.py` no carga en `b78de04` (`NameError` al importar, `FreeCAD.ParamGet`). No existe `tests/golden/nesting_presets.json`. | **RESUELTO (D-99, commit `a7b2e79`).** Import de FreeCAD opcional: sin FreeCAD el módulo carga y lee `DEFAULT_PRESETS`. Golden nuevo `tests/golden/nesting_presets.json` (`get_preset`), no de origen, aprobado por delegación del usuario en D-99. Prueba de regresión `tests/test_nesting_presets.py` (commit `d22594f`). | Cerrado. |
| B5 | **SIGSEGV intermitente al cerrar un smoke test de nivel 2.** | **No reproducido en 20 ejecuciones limpias (D-90, códigos 0); confirmado el 2026-11-06:** una ejecución más de la suite en modo FreeCAD (`freecadcmd tools/run_tests.py`) salió con código 0 y `fallos=0`. La causa medida (excepción que sale de `main()` sin `liberar_widgets()`) se corrigió en `0521803`. **El mecanismo exacto del abort no está diagnosticado:** no se reproduce, así que no hay log de caída que lo localice. Ruido sin relación: `AttributeError: module 'FreeCADGui' has no attribute 'Control'` en `ui/view_providers.py`, que se captura. | Si reaparece 139 o 134, reabrir con los logs de esa ejecución. Revisado en D-104 (2026-11-06): la lista de imports del paquete (ui y cad, incluidos los módulos tocados por U-03) no cae en 3 ejecuciones antes del cambio ni en 3 después; sigue sin reproducirse. |
| B6 | **Código muerto en COCO.** `_crear_tab_espacios` y `_crear_grupo_hijos` (`ui/coco_unified_pestanas.py`). | **Resuelto (D-91).** Verificado por búsqueda en todo el repo: sin llamadas desde el panel. Borrados en el commit de F5 de la UI. | — |
| B7 | **Duplicados que siguen abiertos.** (a) `rotacion_z` en `core/helpers.py` (línea 28) y en `cad/propiedades.py` (línea 61), D-09. (b) Cargador de `ANCLAJES` en `core/module_props.py` y en `cad/propiedades.py` (D-10): ambos cargan `datos/anclajes.json`. (c) Tabla `DIMENSION_POR_EJE` / `_CLAVE_DIMENSION` en `core/helpers.py` y `core/reengrose_geometria.py`. | Medido 2026-11-06 por `grep`: **(a) RESUELTO (D-97, commit e12b6f3):** una sola `def rotacion_z`, en `cad/propiedades.py`; la copia de `core/helpers.py` se eliminó. **(b) RESUELTO (D-97, commit a8e2228):** `ANCLAJES` se carga una sola vez, en `core/module_props.py` (`cargar_anclajes()`); `cad/propiedades.py` importa de ahí. **(c) RESUELTO (D-92, F6):** `DIMENSION_POR_EJE` se define solo en `core/helpers.py:13`, `reengrose_geometria.py` la importa, y `_CLAVE_DIMENSION` ya no existe. | (a) y (b): RESUELTO en D-97. (c): ninguna. |
| B8 | **Catálogos JSON fuera de `datos/` y con prefijo.** `core/vdo_hardware_catalog.json` y `core/vdo_manifest.json` estaban en `core/` y con `vdo_` (MN-04, MN-09). | **RESUELTO (D-98, commit `18ae981`).** Movidos con `git mv` a `datos/hardware_catalog.json` y `datos/manifest.json`, contenido idéntico byte a byte. Carga igual que antes: catálogo 4 familias y 11 SKU; manifest 12 claves raíz y 268 recursivas. Nivel 1 y nivel 2 con `fallos=0`. Pendiente fuera de alcance: `tools/erp_sync` escribe `tools/erp_sync/vdo_hardware_catalog.json`, que ningún código lee. | 

---

## C. Calidad mecánica

| ID | Ítem | Medida | Responsable | Fecha |
|---|---|---|---|---|
| C1 | **Códigos `noqa` pendientes de revisión humana.** | **RESUELTO (D-105).** Medido con `grep -rn noqa freecad tests tools --include='*.py' \| wc -l`: antes **167** líneas (RUF001 40, E402 111, C901 13, F401 2, sin código 1; la cifra de 164 que había aquí estaba desactualizada). Después **0** líneas. RUF001: constantes en `core/simbolos.py` y `ui/tema.py`. E402: guardas de la UI movidas bajo los imports; helpers de `tests/soporte/` (`entorno`, `con_mock`, `qt_offscreen`). Commits `fac6d99`, `1a1b218`, `3ad60d0`. Pendiente de verificación visual (M10): el orden de la guarda de `FreeCADGui` en `ui/` (ver D-105). | — | 2026-11-06 |
| C2 | Funciones con complejidad alta marcadas como C901 (13 a 20) | **RESUELTO (D-105, commit `1a1b218`).** Las 13 funciones se dividieron en auxiliares por extracción literal. Medido: C901 antes **13**, después **0**. Verificación: comparación AST de sentencias por función y nivel 1 y 2 sin fallos. Riesgo residual: las ramas nuevas sin golden propio. | — | 2026-11-06 |
| C3 | `ruff` fuera de `freecad/vdo/` | 0 en `freecad/vdo/`. 8 en `ruff check .` (raíz). D-81 registra 9 errores en `tools/auditoria/verificar.py`, congelado y vetado. | usuario decide si se levanta el veto | 2026-11-13 (propuesta) |
| C4 | `mypy` fuera de `core/` y `cad/` | `pyproject.toml`: `packages = ["freecad.vdo.core", "freecad.vdo.cad"]`, strict. Resultado a cero en `core/` y `cad/` (D-83). `ui/`, `tools/` y `tests/` no entran. | usuario decide si se amplía el alcance | 2026-11-13 (propuesta) |
| C5 | Excepción tragada en `ui/` | 1 (`minimalismo.py excepciones`): `ui/coco_unified_task.py`. El error se registra en `_fallar_accept` (D-79). | usuario confirma que se acepta | 2026-11-13 (propuesta) |

---

## D. Estilo y presentación (MN-07)

| ID | Ítem | Medida | Responsable | Fecha |
|---|---|---|---|---|
| D1 | **Colores hex fuera de `ui/tema.py`** en SVG, HTML y `QColor` de `ui/`. D-76 los dejó fuera de alcance. | Re-medido 2026-11-06 en `freecad/vdo/ui` y `freecad/vdo/cad`, fuera de `ui/tema.py`: `#[0-9a-fA-F]{6}`: **0**; `rgb(`: **0**; `QColor(` con literal numérico: **0** (las 88 llamadas `QColor(` usan constantes `tema.*`). **0 en código; quedan 32 ocurrencias hex en 11 archivos de `docs/`.** Cifras anteriores: 417 (plan §2) y 436 (F12). D-94 movió los 249 literales de color a `ui/tema.py`. | ejecutor (docs: decisión del usuario) | 2026-11-20 (propuesta) |
| D2 | Cuatro hojas de estilo locales fuera de `tema.py` | `ESTILO_WIDGET` (`ui/box_hoja_estilos.py`), `_ESTILO_CHASSIS` (`ui/chassis_estilos.py`), hoja `estilo` en `ui/hardware_manager.py` y en `ui/reengrose_ui_construccion.py`. Aceptadas en D-76 por ser hojas de ventana completa. | usuario confirma que se aceptan | 2026-11-13 (propuesta) |

---

## E. Logging y errores de `core/`

| ID | Ítem | Estado | Responsable | Fecha |
|---|---|---|---|---|
| E1 | `core/` registra con `logging` de la biblioteca estándar, sin handler configurado (D-79: `_LOG = logging.getLogger(__name__)`). | **RESUELTO (D-101, commit `d589286`).** Handler único sobre el logger `freecad.vdo`, instalado desde `freecad/vdo/__init__.py` (no desde `Init.py`: importar el paquete fija `QT_QPA_PLATFORM`, y en la fase de consola eso iría antes de la QApplication de la GUI). Código: `freecad/vdo/registro.py`. Medido 2026-11-06 con `freecadcmd`: un `warning` de `freecad.vdo.core.hardware_hub` sale por `App.Console.PrintWarning`; DEBUG no sale. Prueba: `tests/test_logging_consola.py` (falló antes del fix, pasa después; nivel 1 y 2 `fallos=0`). | Ninguna. | 2026-11-06 |

---

## F. Ciclos en `ui/` (no cubiertos por el plan)

Medidos con `python3 -I tools/auditoria/ciclos.py`: 3 componentes al inicio de la ola D-102; ahora 1 (U-03). Romper cualquiera requiere mover lógica entre módulos de UI, no solo datos.

| ID | Componente | Módulos | Responsable | Fecha |
|---|---|---|---|---|
| U-01 | A | RESUELTO en `c9f8075` (D-102): `generar_csv_opencutlist` y `extraer_piezas_del_documento` pasan a `cad/lista_corte.py`. | ejecutor | 2026-11-20 (propuesta) |
| U-02 | B | RESUELTO en `8909e31` (D-91, F5): la importación inversa desde `universal_inspector.py` ya no existe. D-102 lo verificó. | ejecutor | 2026-11-20 (propuesta) |
| U-03 | C | RESUELTO en `1e488df` (D-103): `VDOViewProviderBase`, `_gui`, `enfocar_inspector_universal`, `ViewProviderCajon` y `ViewProviderPuerta` pasan a `ui/view_provider_base.py`. `ciclos.py` da 0 componentes en `ui/`. | ejecutor | 2026-11-20 (propuesta) |

Fecha objetivo original "M5": ya pasó y los ciclos siguen.

---

## G. Documentos de usuario

| ID | Ítem | Medida | Responsable | Fecha |
|---|---|---|---|---|
| G1 | **Documentos guardados con `canto_fino = 0`** por el locale de coma decimal (D-15, antes U-04). | En este equipo: 0 documentos `.FCStd` en el repo (M10). Búsqueda previa en este equipo: 23 `.FCStd`, 7 con hoja de cálculo, ninguno con el alias `canto_fino`. **Falta revisar la otra máquina.** Los documentos ya guardados no se corrigen por código. | usuario | 2026-11-13 (propuesta) |

---

## H. Build y entrega

| ID | Ítem | Estado | Responsable | Fecha |
|---|---|---|---|---|
| H1 | **`dist/VDO-1.1.0.zip` sobrescrito** el día de la verificación M10. | `dist/` no contiene hoy ningún zip. El build de M10 (172 ficheros, según PROGRESO) quedó en `/tmp/ola79_build/VDO-1.1.0.zip`, fuera del repo. Ese directorio temporal puede desaparecer. | usuario decide si se regenera en `dist/`; ejecutor lo regenera con `tools/build_zip.py` | 2026-11-13 (propuesta) |

---

## I. Verificación visual pendiente

| ID | Ítem | Estado | Responsable | Fecha |
|---|---|---|---|---|
| I1 | **Verificación visual en FreeCAD GUI** de los paneles cambiados en M6 y M7 (zócalo, panel, puerta, cajón y coco; D-70 a D-75), del panel de coco en M7 (D-40) y del icono de M4. Incluye las capturas comparadas contra M0 del paso 3 de M10. | Pendiente. Nivel 3 de la verificación. Sin sesión gráfica revisada por una persona, la fase no se da por cerrada en este punto. | usuario | 2026-11-13 (propuesta) |

---

## J. Diferidos del historial

| ID | Ítem | Origen | Estado | Responsable | Fecha |
|---|---|---|---|---|---|
| J1 | Motor de despiece compartido cajón/puerta | F5 del historial | Diferido. M3 unificó la tabla de aperturas, no los motores (MN-06). | usuario decide si se abre | 2026-11-20 (propuesta) |
| J2 | Verificar que los tests de otra sesión (P-04) están resueltos | **RESUELTO (2026-11-06).** `git status --short` vacío, y `git diff --stat HEAD -- tests/test_gui_wiring.py tests/test_single_dock_convergence.py` vacío. Ambos archivos usan `sys.exit` (`test_gui_wiring.py:159`, `test_single_dock_convergence.py:218`) desde el commit `ef4ecd0` (D-80). | — | — |

---

## K. Cerrados (sin acción; se conservan para trazabilidad)

| Ítem | Cierre |
|---|---|
| D-01 (golden de `rotacion_z`) | Resuelto (P-02). |
| D-02 (golden de `guardian`) | `guardian` resuelto (golden de 9 entradas). `nesting_presets` sigue abierto como B4. |
| D-05 (3 FALLO en `test_arquitectura.py`) | Resuelto. Nivel 1 de M11: las 5 pruebas de `test_arquitectura.CapasTests` y las 2 de `test_capas_arquitectura` pasan (`docs/PROGRESO_MINIMALISMO.md`, M11). |
| D-06 (`os._exit` en tests de otra sesión) | Ya no aparece en el código: hay `sys.exit` en `tests/test_gui_wiring.py` y `tests/test_single_dock_convergence.py`. |
| D-07 (golden de `frames` con una entrada en error) | Se conserva como caso de error a propósito. |
| D-11 (locale numérico del guardián) | Resuelto (D-13 y D-14). Ver G1 para los documentos ya guardados. |
| D-12 (ciclo dentro de `cad`) | Resuelto (`00fdf7f`). |
| D-13 (aristas `core->cad`, 8 en su momento) | `ARISTAS core->cad: 0` en el estado actual (`tools/auditoria/ciclos.py`). |
| F13 (renombrado `vdo_*`) | Resuelto en M8 (D-77) para los `.py`. Queda B8. |
| F7 y F10 (funciones largas de la UI) | `minimalismo.py tamano`: 0 funciones de más de 60 líneas, 0 de más de 100 (M10). |
| F14 (anotaciones de tipo) | Parcial: `mypy` a cero en `core/` y `cad/` (C4). |
| `sys` sin importar en `tests/test_single_dock_convergence.py` | Hay `import sys` en el estado actual. |
| D4 (`nesting_presets` escribe preferencias al importarse) | D4 resuelto (D-100, commit `8619878`). Importar el módulo ya no escribe; la inicialización es explícita al abrir el workflow de Nesting. |
| U-01 (ciclo `cutting_list_preview` ↔ `export_cutting_list`) | Resuelto en `c9f8075` (D-102): funciones compartidas en `cad/lista_corte.py`. |
| U-02 (ciclo `inspector_dock` ↔ `universal_inspector`) | Resuelto en `8909e31` (D-91); verificado en D-102. |
| U-03 (ciclo `coco_unified_task` ↔ `drag_handles` ↔ `view_providers`) | Resuelto en `1e488df` (D-103): base de ViewProviders en `ui/view_provider_base.py`. |
