# Inventario de hechos del dominio — M1

**Fase:** M1 (plan de minimalismo §6). **Base:** código a `4e29c04`.
**Método:** `tools/auditoria/minimalismo.py duplicados|literales|fachadas` + `grep -rnw` por nombre.
Las cifras de "usos" son ocurrencias de nombre en `freecad/`, `tests/` y `tools/`. Las de "archivos" son ficheros distintos.

Cada hecho duplicado tiene **un destino único**. Donde el plan lo decide (MN-xx), se cita. Donde no, la decisión es del ejecutor, marcada como **[decisión]** y revertible.

---

## A. Tablas constantes idénticas (`minimalismo.py duplicados`: 9 grupos)

| ID | Hecho | Dónde se define hoy | Archivos que lo usan | Destino único | Nota |
|---|---|---|---|---|---|
| H-01 | Anclajes: `ANCLAJES`, `ANCLAJE_LABELS` | `core/vdo_module_props.py`, `cad/propiedades.py` (idénticos) | 7 (`ANCLAJES` 14 usos, `ANCLAJE_LABELS` 15) | `datos/anclajes.json`, cargado por `core/vdo_module_props.py`. `cad/` lo importa de `core/` (MN-03). | Plan §1 lo cita como par. Ver H-01b. |
| H-01b | `ANCLAJE_DEFAULT`, `ANCLAJE_IDS` | `core/vdo_module_props.py`, `cad/propiedades.py` | 7 | Igual que H-01. | Coinciden por AST, no están en el conteo de tablas. |
| H-02 | Cantos válidos: `CANTOS_VALIDOS` | `core/vdo_finish.py`, `core/vdo_panel_core.py`, `core/vdo_reengrose.py` | 4 (9 usos) | `core/vdo_finish.py` (es el módulo de cantos). Los otros dos importan. | **[decisión]** |
| H-03 | Bordes, grupo A: `BORDES` (y `CANTOS` de facade, mismo AST) | `core/vdo_finish.py`, `core/vdo_reengrose.py`, `ui/vdo_widgets_coco.py`; `CANTOS` en `core/vdo_facade_contract.py` | `BORDES`: 4 archivos (29 usos) | `core/vdo_finish.py`. La UI importa. | **[decisión]** Grupo medido por `duplicados`: `[CANTOS(facade), BORDES(finish), BORDES(reengrose), BORDES(widgets_coco)]`. |
| H-03b | Bordes, grupo B: `BORDES_2D` (reengrose) y `BORDES` de `ui/vdo_box_controller.py` | `core/vdo_reengrose.py`, `ui/vdo_box_controller.py` | `BORDES_2D`: 4 archivos (26 usos) | `core/vdo_reengrose.py`. La UI importa. | **Resuelto en `bb58afc`.** El contenido es idéntico en las dos copias: `("frente", "fondo", "izquierda", "derecha")`. La versión anterior de esta fila decía "contenido distinto", y era falso. |
| H-04 | Esquinas y encuentros: `ESQUINAS`, `ESQUINAS_2D`, `TIPOS_ENCUENTRO` | `core/vdo_reengrose.py` (`ESQUINAS`, `ESQUINAS_2D`), `ui/vdo_box_controller.py` (`ESQUINAS`, `TIPOS_ENCUENTRO`) | `ESQUINAS` 2, `ESQUINAS_2D` 3, `TIPOS_ENCUENTRO` 2 | `core/vdo_reengrose.py`. | **[decisión]** `ESQUINAS` (reengrose) y `TIPOS_ENCUENTRO` (UI) tienen el mismo contenido con nombres distintos. Antes de unificar hay que confirmar que el significado es el mismo. Ver P-07. |
| H-05 | Modos de choque: `MODOS_CHOQUE_NUCLEO`, `CHOQUES_NUCLEO` | `core/vdo_reengrose.py` (ambos) | 2 | `core/vdo_reengrose.py`, un solo nombre. | Mismo fichero, dos nombres. **[decisión]** |
| H-06 | Dimensiones: `_DIM`, `_DIM_SOL` | `core/vdo_reengrose.py`, `cad/geometria.py` | 2 | `core/` y `cad/` no pueden compartir lo que no es dato (MN-03). Destino: `datos/dimensiones.json`, cargado por ambos. | **[decisión]** |

**Falsos positivos descartados** (mismo AST entre escalares, eliminados por la regla de contenedores de `31785b2`): `COL_TIPO`/`PAGE_CHASIS`, `COL_VALOR`/`PAGE_VANO`, `VERSION`/`NUM_PISTONES`. No son hechos del dominio.

---

## B. Sistemas de apertura (MN-06)

| ID | Definición | Fichero | Qué define | Destino |
|---|---|---|---|---|
| H-10a | `APERTURA_GOLA`, `APERTURA_45_GRADOS`, `APERTURA_PUSH_OPEN`, `SISTEMAS_APERTURA_VALIDOS`, `necesita_*` | `core/vdo_facade_contract.py` | Constantes oficiales y validación | `core/aperturas.py` |
| H-10b | `APERTURA_TIRADOR`, `APERTURA_GOLA`, `necesita_descuento_gola`, `necesita_bisel_45` | `core/vdo_cajon_despiece.py` (clase) | Constantes y reglas de cajón | `core/aperturas.py` |
| H-10c | `APERTURA_LEGADO_A_CONTRATO`, `APERTURA_DESCUENTO_ALTO`, `_normalizar_apertura` | `core/vdo_puerta_despiece.py` | Mapa legado y descuento de gola | `core/aperturas.py` |
| H-10d | `APERTURA_LABELS`, `APERTURA_VALUES` | `ui/vdo_puerta_task.py` | Etiquetas en pantalla | `core/aperturas.py` (etiqueta en la tabla). La UI la lee. |
| H-10e | Uso de `necesita_*` y etiquetas | `ui/vdo_cajon_task.py` | Consulta | Pasa a consultar `core/aperturas.py`. |

Una sola tabla con: `sistema`, `etiqueta`, `cantos_especiales`, `descuento_gola`, `bisel_45`, `expulsor`, `valor_legado`. **Se unifica la tabla de reglas, no los motores de cálculo** (MN-06). Mapeo de nombres en `datos/aperturas.json`.

---

## C. Catálogos y tablas de datos

| ID | Hecho | Dónde está hoy | Destino | Nota |
|---|---|---|---|---|
| H-20 | Herrajes (bisagras, correderas) | `core/vdo_hardware_catalog.json` **y** `_FALLBACK_BISAGRA` (48 líneas), `_FALLBACK_CORREDIZO` (34) en `core/vdo_hardware_hub.py` | `core/vdo_hardware_catalog.json`, único (MN-05) | Los `_FALLBACK_*` se eliminan. Si el JSON falta, error explícito. |
| H-21 | Ruta del catálogo `_CATALOGO_PATH` | `core/vdo_hardware_hub.py:17` y `ui/vdo_hardware_manager.py:16` (idénticas) | `core/vdo_hardware_hub.py` exporta la ruta; la UI la importa. | **[decisión]** |
| H-22 | Especificación de módulos `MODULE_SPECS` (162 líneas de código) | `core/vdo_module_specs.py` | `datos/modulos.json` (MN-04) | 2 ficheros la usan. |
| H-23 | Iconos `LUCIDE_ICONS` | `ui/vdo_chassis_widget.py` (72 líneas) y `ui/vdo_box_controller.py` (19 líneas) | `ui/tema.py`, único (MN-07) | No comparado todavía el contenido de las dos copias. Hacerlo antes de migrar. |
| H-24 | Caché de iconos `_ICON_CACHE`, logger `_LOG` | `ui/vdo_box_controller.py`, `ui/vdo_chassis_widget.py` | `ui/tema.py` (icono), módulo de logging único (`ui/`). | **[decisión]** |

---

## D. Valores de dominio repetidos (`minimalismo.py literales`: 53 usos)

Valores vigilados en `freecad/vdo/datos/vigilados.json` (MN-04 aplica: un solo sitio).

| ID | Valor | Usos (AST) | Archivos | Destino |
|---|---|---|---|---|
| H-30 | `"melamina_standar"` | 23 | 14 | Constante `MATERIAL_DEFECTO` en `datos/valores.json`, leída por un único módulo. |
| H-31 | `"blum_tandem"` | 14 | 10 | Constante en `datos/valores.json` (marca de corredera). |
| H-32 | `"oculta"` | 8 | 14 | Constante en `datos/valores.json` (tipo de corredera). |
| H-33 | `"tirador"` | 8 | 8 | Constante en `datos/valores.json` (sistema de apertura, ver H-10). |

Los 53 usos están en `minimalismo.py literales`. El detalle por línea está en `docs/metricas/minimalismo_base.json`.

---

## E. Estilos y colores (MN-07)

| ID | Hecho | Dónde está hoy | Destino |
|---|---|---|---|
| H-40 | Literales hex fuera de tema: **417** | `ui/vdo_chassis_widget.py` 139, `ui/vdo_box_controller.py` 88, `ui/vdo_universal_inspector.py` 54, `ui/vdo_hardware_manager.py` 42, `ui/vdo_reengrose_ui.py` 32, `ui/vdo_cajon_task.py` 16, `ui/vdo_widgets_coco.py` 13, otros | `ui/tema.py`, único (MN-07). `ui/tema.py` tiene 19 hex hoy, que son tokens. |
| H-41 | Tokens duplicados con nombre distinto: `FONDO` (tema) / `COLOR_FONDO` (puerta_task), `TEXTO` / `COLOR_TEXTO`, `BORDE_ACTIVO` / `COLOR_ACENTO` | `ui/tema.py`, `ui/vdo_puerta_task.py` | `ui/tema.py`, un solo nombre por token. |
| H-42 | `setStyleSheet` 90, `QLabel(` 171, `addWidget` 401 (plan §1) | varios `ui/` | Patrón, no hecho. Se trata en M6. |

---

## F. Funciones duplicadas (`minimalismo.py duplicados`: 3 grupos de cuerpo)

| ID | Función | Dónde | Destino |
|---|---|---|---|
| H-50 | `_set_combo_data` | `ui/vdo_box_controller.py`, `ui/vdo_panel_task.py`, `ui/vdo_reengrose_ui.py`, `ui/vdo_widgets_coco.py` | `ui/formulario.py` (M6) como función única. |
| H-51 | `_on_cancel` | `ui/vdo_cajon_task.py`, `ui/vdo_coco_unified_task.py`, `ui/vdo_panel_task.py`, `ui/vdo_puerta_task.py`, `ui/vdo_zocalo_task.py` | Clase base de tarea (`ui/vdo_task_base.py`, ya existe). |
| H-52 | `get_panel_class` | `ui/vdo_drag_handles.py`, `ui/vdo_view_providers.py` | Un solo sitio. **[decisión]** |

---

## G. `rotacion_z` (un hecho, tres copias)

| ID | Dónde | Estado |
|---|---|---|
| H-60 | `core/vdo_module_props.py` (`b78de04`) | Eliminado. Ver `DEUDA_TECNICA.md` D-09. |
| H-61 | `core/vdo_helpers.py:22` | Copia 1 (usa `_get_app()`). |
| H-62 | `cad/propiedades.py:74` | Copia 2 (usa `App`). |

Hay que elegir un solo sitio. `core/` no puede importar `App` (MN-03), así que `cad/` es el destino natural. Pero hay 12 ficheros que la usan, y varios son `core/`. **Pendiente de decisión: P-06.**

---

## H. Fachadas y reexportaciones

| Hecho | Medida | Destino |
|---|---|---|
| Módulos fachada (solo reexportan) | `minimalismo.py fachadas`: **0** | — |
| Bloques `__all__` | 12 ficheros: `app/casos_uso/__init__.py`, `app/dto.py`, `core/errores.py`, `core/vdo_facade_contract.py`, `core/vdo_hardware_hub.py`, `core/vdo_puerta_core.py`, `core/vdo_puerta_despiece.py`, `qt_compat.py`, `ui/tema.py`, `ui/vdo_form_builder.py`, `ui/vdo_inspector_dock.py`, `ui/vdo_universal_inspector.py` | Se eliminan fuera de `__init__.py` de paquete (M7). |

---

## I. Capa `app/` (MN-01)

| Fichero | Líneas | Destino (MN-01) |
|---|---|---|
| `app/casos_uso/crear_panel.py`, `colocar_modulo.py`, `editar_modulo.py`, etc. | ver `minimalismo.py resumen`: `app` 941 líneas, 21 archivos | Lógica de decisión → `core/`. Escritura → `cad/`. Solo coordinación → `commands.py`. Se hace en M5. |

---

## Ciclo core ↔ cad (P-08)

Medido con AST sobre `freecad/vdo/` (un `ast.parse` por fichero; no con grep). Cuenta imports de nivel superior y dentro de funciones.

**Imports de `core` hacia `cad` (violan MN-03): 4**

| Fichero | Línea | Import |
|---|---|---|
| `core/vdo_coco_core.py` | 9 | `from freecad.vdo.cad.geometria import forma_ref` |
| `core/vdo_coco_spaces.py` | 13 | `from freecad.vdo.cad.geometria import forma_ref` |
| `core/vdo_module_props.py` | 28 | `from freecad.vdo.cad.propiedades import add_common_props` |
| `core/vdo_panel_core.py` | 20 | `from freecad.vdo.cad.geometria import forma_ref` |

El test `tests/test_arquitectura.py::CapasTests::test_core_no_importa_app_ui_cad` ya falla con esta lista exacta (nivel 1 y nivel 2). No se añade un test nuevo, para no duplicar el fallo.

**Imports de `cad` hacia `core`: 5**

| Fichero | Línea | Import | ¿Dentro de un ciclo? |
|---|---|---|---|
| `cad/colocacion.py` | 17 | `from freecad.vdo.core.vdo_module_props import ANCLAJE_DEFAULT` | sí |
| `cad/colocacion.py` | 52 | `from freecad.vdo.core.vdo_helpers import _get_app` | no (dentro de función) |
| `cad/propiedades.py` | 16 | `from freecad.vdo.core import vdo_frames` | no |
| `cad/vdo_guardian.py` | 14 | `from freecad.vdo.core import vdo_defaults` | no |
| `cad/vdo_guardian.py` | 15 | `from freecad.vdo.core import vdo_manifest` | no |

**Ciclos de importación reales** (componentes fuertemente conexos, Tarjan): 4 componentes. Solo uno cruza core y cad, y es `{cad/colocacion, cad/propiedades, core/vdo_module_props}`:

- `core/vdo_module_props` → `cad/propiedades` (línea 28, nivel superior).
- `cad/propiedades` → `cad/colocacion` (línea 72, **diferida**, dentro de una función).
- `cad/colocacion` → `core/vdo_module_props` (línea 17, nivel superior) y → `cad/propiedades` (línea 16, nivel superior).

Los otros 3 componentes están solo en `ui/` (`vdo_inspector_dock`↔`vdo_universal_inspector`; `vdo_coco_unified_task`↔`vdo_drag_handles`↔`vdo_view_providers`; `vdo_cutting_list_preview`↔`vdo_export_cutting_list`). No pertenecen al ciclo core↔cad.

**Lo que esto implica:**

- Los 3 `forma_ref` no forman ciclo: `geometria` no importa de `core`. Son violaciones de capa, no ciclos.
- El ciclo real es `module_props ↔ colocacion`. El import diferido de `propiedades` no lo rompe a nivel de módulo; para romperlo hay que mover `ANCLAJE_DEFAULT` o `rotacion_z`.
- `rotacion_z` (P-06) y `add_common_props` (P-08) están en el mismo nudo.

**Pendiente:** P-08 (decisión humana). Bloquea cambios en `core/vdo_module_props.py` y en los 3 módulos que importan `forma_ref`.

## Decisiones pendientes que bloquean destinos

| Pendiente | Hechos afectados | Qué hay que decidir |
|---|---|---|
| **P-06** | H-60 a H-62 | Ubicación única de `rotacion_z`: `cad/` (natural, pero hay usos desde `core/`) o `core/` sin `App` (imposible). |
| **P-07** | H-04 | `ESQUINAS` (reengrose) y `TIPOS_ENCUENTRO` (UI) tienen el mismo contenido. ¿Son el mismo concepto? |
| **P-08** | ciclo core ↔ cad | Ver sección "Ciclo core ↔ cad (P-08)" arriba. Bloquea cualquier cambio en `core/vdo_module_props.py` y en los módulos que importan `forma_ref`. |

Ver `docs/PENDIENTES_HUMANO.md`.

---

## Resumen

Las cifras de este documento salen de `minimalismo.py` y de `grep` citados arriba. No hay conteos de resumen estimados.

**Lo que queda abierto:** las decisiones marcadas **[decisión]** son del ejecutor y se aplican en M2 con golden. P-06 (ubicación de `rotacion_z`) y P-07 (`ESQUINAS` frente a `TIPOS_ENCUENTRO`) son del usuario.
