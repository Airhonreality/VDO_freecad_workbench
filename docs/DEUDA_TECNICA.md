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
| A2 | Otras metas de §1 no cumplidas | Tablas idénticas: 1 grupo (meta 0). Funciones con 4 o más ramas: 3 (meta 0). Bloques `__all__`: 11 archivos (meta 0; aumentaron). `QLabel(`: 123 (de 171). `addWidget`: 286 (de 401). `setStyleSheet` fuera de `ui/tema.py`: 0 (medido en M11; la cifra de 2 del grep de M10 eran una línea de docstring y la única llamada, ambas en `tema.py`). Capa `ui`: 14.374 líneas (de 13.507; meta: reducir a presentación). | usuario decide si se aceptan con justificación o se abre fase. Ejecutor, si se abre. | 2026-11-13 (propuesta) |
| A3 | Método de conteo del plan | El plan §1 cita 88 archivos y 23.920 líneas; la herramienta mide 85 y 23.608 sobre la base. Hay que fijar un solo método (D-03). | usuario | 2026-11-13 (propuesta) |
| A4 | Línea base de `app/` | El plan cita 518 líneas; `minimalismo_base.json` mide 21 archivos y 941 líneas. `app/` ya está eliminado; la diferencia queda sin explicar en el registro. | usuario (solo informativo) | 2026-11-13 (propuesta) |

---

## B. Defectos preexistentes para la fase de depuración

Fecha propuesta para toda la sección: 2026-11-20. Responsable: ejecutor, salvo lo indicado.

| ID | Defecto | Estado de la comprobación | Acción propuesta |
|---|---|---|---|
| B1 | **`TipoMontaje` del accept del cajón.** El combo muestra `Parche`, `Semiparche`, `Embebida` (`freecad/vdo/datos/formularios.py`, línea 243). El accept escribe `currentText()` (`ui/cajon_task.py`, línea 283). La enumeración del cajón usa `parche`, `semiparche`, `embebida` (`core/facade_contract.py`). Al cargar, `findText(obj.TipoMontaje)` (`ui/cajon_task.py`, línea 173) no encuentra el valor porque la búsqueda distingue mayúsculas. | Verificado por lectura del código. No reproducido en ejecución. La puerta usa valores con mayúscula en su enumeración (`cad/puerta.py`, línea 196), así que el problema es del cajón. | Usar el valor del enumerado en el accept y en la carga. |
| B2 | **Accept que escribe propiedades antes de un error** (puerta, cajón, coco y paneles). | Reportado en el encargo de M11. No reproducido en esta fase. | Validar antes de escribir, o revertir al fallar. Caso de referencia: `ui/coco_unified_task.py`, `_fallar_accept` (D-75). |
| B3 | **Zócalo: volumen 0.0 en el escenario normal**, sin explicación. | **Resuelto como artefacto de prueba (D-89).** Evidencia: con 600 × 580 × 100 mm el volumen es 3866400.0 mm³ (4 sólidos, caja 600 × 510 × 100) tras `make_zocalo` + `recompute`, y sigue igual tras `ZocaloTaskPanel.accept()` con y sin transacción automática. Leer `Shape.Volume` antes del recálculo lanza `RuntimeError`, no devuelve 0.0. Script y salidas en `/tmp/f3_eq/` (fuera del repo). | Ninguna en código. La prueba que reportaba 0.0 no está en el repo; si existe fuera, debe recalcular antes de leer el volumen. |
| B4 | **`nesting_presets` sin golden.** `core/nesting_presets.py` no carga en `b78de04` (`NameError` al importar, `FreeCAD.ParamGet`). No existe `tests/golden/nesting_presets.json`. | Registrado como P-10. Su plazo, "antes de M5", ya pasó y la deuda sigue abierta. | Arreglar la carga y generar un golden nuevo. Ejecutor propone; el usuario aprueba el golden (regla 2 del plan). |
| B5 | **SIGSEGV intermitente al cerrar un smoke test de nivel 2.** | **No reproducido en 20 ejecuciones limpias (D-90); causa no diagnosticada.** La causa medida (excepción que sale de `main()` sin `liberar_widgets()`) se corrigió en `0521803`. Tras el fix, 20 ejecuciones seguidas de nivel 2 salieron con código 0 y ninguna dio 139 ni 134. **El mecanismo exacto del abort no está diagnosticado:** no se reproduce, así que no hay log de caída que lo localice. Ruido sin relación: `AttributeError: module 'FreeCADGui' has no attribute 'Control'` en `ui/view_providers.py`, que se captura. | Si reaparece 139 o 134, reabrir con los logs de esa ejecución. |
| B6 | **Código muerto en COCO.** `_crear_tab_espacios` y `_crear_grupo_hijos` (`ui/coco_unified_pestanas.py`). | **Resuelto (D-91).** Verificado por búsqueda en todo el repo: sin llamadas desde el panel. Borrados en el commit de F5 de la UI. | — |
| B7 | **Duplicados que siguen abiertos.** (a) `rotacion_z` en `core/helpers.py` (línea 28) y en `cad/propiedades.py` (línea 61), D-09. (b) Cargador de `ANCLAJES` en `core/module_props.py` y en `cad/propiedades.py` (D-10): ambos cargan `datos/anclajes.json`. (c) Tabla `DIMENSION_POR_EJE` / `_CLAVE_DIMENSION` en `core/helpers.py` y `core/reengrose_geometria.py`. | Verificado por búsqueda. El registro (P-06) decidió una sola definición de `rotacion_z`; no se aplicó. | Unificar cada par en un solo sitio (P1). |
| B8 | **Catálogos JSON fuera de `datos/` y con prefijo.** `core/vdo_hardware_catalog.json` y `core/vdo_manifest.json` están en `core/`, no en `datos/` (MN-04), y conservan `vdo_` (MN-09 renombró solo los `.py`). | Verificado por `find`. | Decidir si se mueven (usuario) y mover (ejecutor), con los `CATALOGO_PATH` y las pruebas de ruta. |

---

## C. Calidad mecánica

| ID | Ítem | Medida | Responsable | Fecha |
|---|---|---|---|---|
| C1 | **Códigos `noqa` pendientes de revisión humana.** | `grep` de `noqa` en `freecad/`, `tests/` y `tools/`: 169 líneas, que contienen **168 códigos**: E402 **108**, RUF001 **47**, C901 **13**. El encargo decía 166 (E402 106). La cifra medida es la que vale. | usuario (revisar cada uno) | 2026-11-13 (propuesta) |
| C2 | Funciones con complejidad alta marcadas como C901 (13 a 20) | Motivo registrado en D-81: dividirlas cambia el flujo sin goldens por rama. | usuario decide; ejecutor propone | 2026-11-20 (propuesta) |
| C3 | `ruff` fuera de `freecad/vdo/` | 0 en `freecad/vdo/`. 8 en `ruff check .` (raíz). D-81 registra 9 errores en `tools/auditoria/verificar.py`, congelado y vetado. | usuario decide si se levanta el veto | 2026-11-13 (propuesta) |
| C4 | `mypy` fuera de `core/` y `cad/` | `pyproject.toml`: `packages = ["freecad.vdo.core", "freecad.vdo.cad"]`, strict. Resultado a cero en `core/` y `cad/` (D-83). `ui/`, `tools/` y `tests/` no entran. | usuario decide si se amplía el alcance | 2026-11-13 (propuesta) |
| C5 | Excepción tragada en `ui/` | 1 (`minimalismo.py excepciones`): `ui/coco_unified_task.py`. El error se registra en `_fallar_accept` (D-79). | usuario confirma que se acepta | 2026-11-13 (propuesta) |

---

## D. Estilo y presentación (MN-07)

| ID | Ítem | Medida | Responsable | Fecha |
|---|---|---|---|---|
| D1 | **Colores hex fuera de `ui/tema.py`** en SVG, HTML y `QColor` de `ui/`. D-76 los dejó fuera de alcance. | El plan §2 (MN-07) cita 417 literales hex. La cifra de F12 en el historial es 436. **Ninguna se re-midió en M11.** | ejecutor | 2026-11-20 (propuesta) |
| D2 | Cuatro hojas de estilo locales fuera de `tema.py` | `ESTILO_WIDGET` (`ui/box_hoja_estilos.py`), `_ESTILO_CHASSIS` (`ui/chassis_estilos.py`), hoja `estilo` en `ui/hardware_manager.py` y en `ui/reengrose_ui_construccion.py`. Aceptadas en D-76 por ser hojas de ventana completa. | usuario confirma que se aceptan | 2026-11-13 (propuesta) |

---

## E. Logging y errores de `core/`

| ID | Ítem | Estado | Responsable | Fecha |
|---|---|---|---|---|
| E1 | `core/` registra con `logging` de la biblioteca estándar, sin handler configurado (D-79: `_LOG = logging.getLogger(__name__)`). | Por lectura: los avisos de nivel WARNING o superior salen por **stderr**, con el handler de último recurso de Python, y **no** por la consola de FreeCAD (`App.Console`). Comportamiento estándar de `logging`; no reproducido dentro de FreeCAD. | ejecutor (configurar un handler que llegue a `App.Console`, o documentar el comportamiento); usuario decide | 2026-11-20 (propuesta) |

---

## F. Ciclos en `ui/` (no cubiertos por el plan)

Medidos con `python3 -I tools/auditoria/ciclos.py`: 3 componentes. Romper cualquiera requiere mover lógica entre módulos de UI, no solo datos.

| ID | Componente | Módulos | Responsable | Fecha |
|---|---|---|---|---|
| U-01 | A | `ui/cutting_list_preview.py` ↔ `ui/export_cutting_list.py`. Las aristas usan funciones (`generar_csv_opencutlist`, `extraer_piezas_del_documento`, `main`). | ejecutor | 2026-11-20 (propuesta) |
| U-02 | B | `ui/inspector_dock.py` ↔ `ui/universal_inspector.py`. Las `PAGE_*` son constantes; la clase `VDOUniversalInspectorWidget` sigue en el camino. | ejecutor | 2026-11-20 (propuesta) |
| U-03 | C | `ui/coco_unified_task.py`, `ui/drag_handles.py`, `ui/view_providers.py` (7 aristas, 6 diferidas y 1 a nivel de módulo: `drag_handles.py` importa `VDOViewProviderBase`). Son clases. | ejecutor | 2026-11-20 (propuesta) |

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
| J2 | Verificar que los tests de otra sesión (P-04) están resueltos | PROGRESO, "Abierto" | El registro de M10 lo daba como pendiente del usuario. El estado de git al inicio de M11 estaba limpio, pero no se ha comprobado si los cambios quedaron commiteados o descartados. | usuario | 2026-11-13 (propuesta) |

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
