# Progreso — plan de minimalismo VDO

**Rama de trabajo:** `minimalismo/noche-20261102` (desde `c1fa9d2`, punta de `refactor/vdo-10`).
**Plan rector:** `docs/PLAN_MINIMALISMO_VDO.md`. Los planes anteriores están sustituidos.
**Cada cifra de este registro sale de un comando citado. Ninguna es estimación.**

---

## Estado (actualizado 2026-11-03)

| Fase | Estado | Motivo |
|---|---|---|
| Premisas y rama | ✅ | Ver "Comprobaciones iniciales" |
| Segfault al salir (pre-M0) | ✅ | `c1fa9d2` (en `refactor/vdo-10`) |
| **M0** — Congelar y medir | ✅ **cerrada según el criterio del encargo**: 18 goldens válidos + 1 N/A justificado | 18 goldens: 14 de módulo + 4 flujos de creación en `creacion_modulos.json`. `nesting_presets`: N/A con motivo (P-10, `DECISIONES_DELEGADAS.md`), deuda antes de M5. Nivel 2: 1 fallo documentado (`guardian` con locale, ver "Defecto de locale" en `goldens_origen.md`). No se reclasifica. |
| **M1** — Inventario de hechos | ⚠️ **parcial** | Inventario en `docs/INVENTARIO_HECHOS.md`. El gate pide "cada hecho duplicado con destino único decidido". Faltan: H-60 a H-62 (**P-06**), H-04 (**P-07**), y decisiones marcadas [decisión] sin tomar: H-21, H-24, H-52. |
| **M2** — Un hecho, un lugar: datos | ⚠️ **parcial, no cerrada** | Tablas idénticas 9 → 0. `LUCIDE_ICONS` en una tabla. Ruta del catálogo única (corrige un defecto). Quedan: literales de dominio (53) y `MODULE_SPECS` (H-22, sin golden desde `b78de04`). Ver "M2". |
| M3 a M11 | ⏸ no iniciadas | M2 no cierra en esta sesión (ver "M2"). M3 no se inicia. |

### M0: gate

| Criterio | Resultado | Evidencia |
|---|---|---|
| `minimalismo_base.json` existe | ✅ | `fc224dd` |
| 18 goldens válidos existen | ✅ 18 de 18 | 14 ficheros de módulo + 4 flujos de creación. Todos verifican contra el código actual (ver "Medición"). |
| N/A justificado | ✅ | `nesting_presets` (P-10). Motivo y deuda en `goldens_origen.md`. |
| Nivel 2 sin SIGSEGV | ✅ | 0 segfault en todas las ejecuciones. |
| Fallos de comportamiento documentados con causa | ✅ | `guardian` en nivel 2 (locale, `goldens_origen.md`). Los 3 de `test_arquitectura` (D-05). |

**M3 no se inicia:** el plan (§6) exige que M2 cierre antes. M2 sigue parcial.

---

## Comprobaciones iniciales

```
$ git ls-files --error-unmatch docs/PLAN_MINIMALISMO_VDO.md
docs/PLAN_MINIMALISMO_VDO.md          # commiteado en e10cd12 (rama refactor/vdo-10)
$ git show HEAD:docs/PLAN_MAESTRO_VDO.md | head -1      # antes de c59587b: sin aviso
# Plan maestro VDO — de 5,5 a 10/10
$ git show c59587b --stat --format=%s
docs(minimalismo): marcar planes anteriores como sustituidos   (2 ficheros, 4 líneas)
$ readlink ~/.local/share/FreeCAD/Mod/VDO
/home/airhon/Proyectos/VDO_freecad_workbench             # sin cambios (comprobado al cierre)
```

Correcciones a premisas del prompt:
- `cad/colocacion.py`, `ui/vdo_interfaz.py` y `tests/test_creacion_colocacion.py` **ya estaban commiteados** (`abf59b1`, `b2583a6`). No había pendientes de esos.
- El aviso "SUSTITUIDO" de los dos planes viejos no estaba commiteado. Commiteado en `c59587b`.

Estado de otra sesión (**no es mío**):
- Al inicio había dos procesos `claude` con cwd en este repo (PID 36672 y 143086). Siguen vivos al cierre; el encargo indicó seguir.
- `tests/test_gui_wiring.py` y `tests/test_single_dock_convergence.py` siguen **modificados sin commitear** (`os._exit` → `sys.exit`). No los he tocado ni commiteado (P-04). `test_single_dock_convergence.py` tiene 10 incidencias de ruff frente a 9 en HEAD.

---

## Commits de la sesión

| Hash | Fase | Qué hace |
|---|---|---|
| `c59587b` | premisas | Aviso de sustitución en `PLAN_MAESTRO_VDO.md` y `PLAN_CORRECCIONES_F19.md` |
| `5fe5eea` | M0 | `minimalismo.py`: literales por AST y ramas por cadena if/elif real |
| `31785b2` | M0 | `minimalismo.py duplicados`: solo contenedores de 2+ elementos |
| `fc224dd` | M0 | `docs/metricas/minimalismo_base.json` medido |
| `762d768` | M0 | Goldens: herramienta, entradas de 19 módulos, fixtures de layout |
| `692b76a` | M0 | 13 goldens desde `b78de04` + `docs/metricas/goldens_origen.md` |
| `4e29c04` | M0 | `module_props` con golden (serialización de `App.Rotation`, reubicación de `rotacion_z`) |
| `66e0765` | M0 | Cierre de M0 con decisiones P-01 y P-03 (**revisado: M0 no está cerrada, ver arriba**) |
| `8b85ce3` | M2 | Herrajes solo desde el JSON; sin `_FALLBACK_*` (MN-05). Golden `hardware_hub` 0 diferencias. |
| `699e944` | M2 | Anclajes en `datos/anclajes.json`; `cad` deja de duplicar la tabla. Duplicado de carga queda en D-10. |
| `f278a99` | docs | Inventario de hechos (M1) y estado de M2 (de la noche anterior) |
| `a892231` | M0 | Golden de `guardian` desde `b78de04` (9 entradas). Corrige "guardian no tiene función de cálculo" |
| `391dfce` | M0 | Alcance de ruff y mypy (D-04) en `pyproject.toml` y plan §2. Migra la config de ruff a `[tool.ruff.lint]` |
| `882b1fc` | M1 | Inventario medido core↔cad (P-08). Pendientes P-05 (detallado), P-08, P-09, P-10 |
| `200c79c` | M0 | Revisión P-05 de los 3 goldens sustituidos (antes, por qué estaba mal, ahora) |
| `1b5a1b7` | M2 | `CANTOS_VALIDOS` y `BORDES` en una sola definición (H-02, H-03) |
| `bb58afc` | M2 | `CANTOS` de fachada eliminado (sin usos), `CHOQUES_NUCLEO` eliminado (sin usos), `BORDES` de la UI → `BORDES_2D` (H-03, H-03b, H-05) |
| `cbfb55f` | M2 | `DIMENSION_POR_EJE` en `core/vdo_helpers` para `_DIM` y `_DIM_SOL` (H-06) |
| `cc43fdf` | registro | Estado y cifras medidas al cierre de la primera pasada |
| `47045b0` | M2 / P-08 | Quita el re-export de `add_common_props` desde `core/vdo_module_props`; llamadores importan de `cad/propiedades`. Añade `tools/auditoria/ciclos.py`. |
| `843ce9e` | M0 | `tests/test_goldens.py` en el runner; `frames` sin entrada en error; `hardware_hub` +3 y `reengrose` +6 entradas (mínimo 3 por función) |
| `00fdf7f` | M2 / D-12 | `aplicar_rotacion` pasa a `cad/colocacion.py`. Se rompe el ciclo `cad.colocacion` ↔ `cad.propiedades`. Ciclos dentro de `cad`: 0. |
| `169135b` | M0 / D-11 | El guardián escribe números como `=N/D`, que no dependen de LC_NUMERIC. Prueba nueva `tests/test_guardian_locale.py`. **Cambia el contenido de B5 en `guardian.json`; el golden queda pendiente de aprobación humana.** |
| `9040cca` | M2 / P-07 | `TIPOS_ENCUENTRO` y `ESQUINAS` del box controller referencian las tablas de `core/vdo_reengrose`. Tablas idénticas 2 → 0. |
| `04a83e5` | M2 / H-23 | `LUCIDE_ICONS` en una sola tabla en `ui/tema.py` (19 claves). Cambia el icono `inglete_45` del box controller; pendiente de verificación visual. |
| `7566f34` | M2 / H-21 | Una sola ruta del catálogo: `core/vdo_hardware_hub.CATALOGO_PATH`. **Corrige un defecto:** el gestor leía y guardaba en `ui/vdo_hardware_catalog.json`, que no existe. |

Previos en la rama (ya en `refactor/vdo-10`): `e10cd12` (plan rector), `c1fa9d2` (segfault).

---

## Medición (salidas literales)

### Nivel 1 — `python3 -I tools/run_tests.py` (al cierre, tras `cbfb55f`)

```
RESUMEN ejecutados=262 fallos=3 errores=0 skip=107 no_ejecutado=0
FALLO test_arquitectura.CapasTests.test_core_no_importa_app_ui_cad
FALLO test_arquitectura.CapasTests.test_ui_no_escritura_freecad
FALLO test_arquitectura.CapasTests.test_ui_no_importa_core_cad_app_api
```

### Nivel 2 — `freecadcmd tools/run_tests.py`

Cinco ejecuciones sobre `692b76a` (antes de M2):
```
RUN 1..5 EXIT=1 SIGSEGV_LINEAS=0
RESUMEN ejecutados=260 fallos=3 errores=0 skip=26 no_ejecutado=0   (×5)
```

Tres ejecuciones tras cada commit de M2 (`1b5a1b7`, `bb58afc`, `cbfb55f`):
```
RESUMEN ejecutados=260 fallos=3 errores=0 skip=26 no_ejecutado=0   (×3, segfault=0)
```

Código de salida 1 en todas, por los mismos 3 FALLO de `test_arquitectura.py`. No es crash.

### `minimalismo.py resumen` (al cierre)

```
=== RESUMEN por capa ===
capa | archivos | lineas | funciones | api_publica
--------------------------------------------------
core | 26 | 8669 | 308 | 249
ui | 33 | 13505 | 513 | 301
cad | 5 | 367 | 17 | 13
app | 21 | 941 | 42 | 50
TOTAL | 85 | 23482 | 880 | -
```

Base (`fc224dd`): `core` 8780 líneas, `ui` 13507, `cad` 380, `app` 941, total 23608.

### Otros subcomandos (al cierre)

| Subcomando | Base (`fc224dd`) | Ahora | Nota |
|---|---|---|---|
| `duplicados` tablas idénticas | 9 | **2** | Quedan `ESQUINAS` (P-07) y `ESQUINAS_2D`↔`ESQUINAS` de UI (mismo bloque H-04, P-07). |
| `duplicados` cuerpos idénticos | 3 | 3 | Sin cambio. Fuera de M2 (H-50, H-51, H-52 son de M6). |
| `literales` usos de dominio | 53 | **53** | Sin cambio. Ver "M2 pendiente". |
| `ramas` funciones con cadena if/elif ≥ 4 | 12 | 12 | Sin cambio. |
| `tamano` archivos > 400 líneas | 17 | 17 | Sin cambio. |
| `tamano` funciones > 60 líneas | 68 | 68 | Sin cambio. |
| `excepciones` que tragan errores | 90 | **89** | Corregido: el registro decía 90. |

### `verificar.py` (referencia, no es gate de fase)

Salida resumida de `python3 -I tools/auditoria/verificar.py` (sin cambios de reglas):

```
[FALLA] R1_capas: valor=17
[FALLA] R3_dominio_como_datos: valor=32
[FALLA] R8_funciones_le100: valor=25
[FALLA] R8_ruff_c901_le12: valor=28
[FALLA] R9_defs_no_usadas: valor=2
[FALLA] R10_ruff_check_cero: valor=291 (freecad/+tests/+tools/; ver D-04)
[FALLA] R10_mypy_strict_cero: valor=1081
[FALLA] R10_cero_hex_fuera_tema: valor=417
[OK]    R11_golden_masters: valor=15
```

**Corrección:** el registro decía `R10_ruff_check_cero = 288`. Esa cifra no se reproduce: hoy `verificar.py` da 291 con el mismo alcance. La diferencia de 1 incidencia en `test_single_dock_convergence.py` viene de los cambios sin commitear de P-04. Ver `DEUDA_TECNICA.md` D-04.

---

## Medición de la segunda pasada (tras `843ce9e`)

Comandos, salidas literales:

```
$ VDO_TEST_DIR=tests VDO_TEST_OUT=... python3 -I tools/run_tests.py          # nivel 1
RESUMEN ejecutados=280 fallos=3 errores=0 skip=111 no_ejecutado=0
  FALLO test_arquitectura.CapasTests.test_core_no_importa_app_ui_cad
  FALLO test_arquitectura.CapasTests.test_ui_no_escritura_freecad
  FALLO test_arquitectura.CapasTests.test_ui_no_importa_core_cad_app_api
  SKIP x4 test_goldens (coco_spaces, guardian, zocalo_core: importan FreeCAD a nivel de módulo;
         module_props: necesita FreeCAD al ejecutarse) — motivo explícito en cada skip

$ VDO_TEST_DIR=tests VDO_TEST_OUT=... freecadcmd tools/run_tests.py          # nivel 2
RESUMEN ejecutados=278 fallos=4 errores=0 skip=26 no_ejecutado=0   (segfault=0)
  FALLO test_arquitectura (×3, los de siempre)
  FALLO test_goldens.GoldensVerificacionTests.test_guardian   (locale, ver goldens_origen.md)

$ python3 -I tools/auditoria/ciclos.py
CICLOS: 4 componentes  (uno dentro de cad: cad.colocacion, cad.propiedades; tres en ui/)
ARISTAS core->cad: 8

$ .venv/bin/ruff check . --no-cache --statistics                            # comando único de ruff
Found 303 errors.
  freecad/vdo 152 · tools/auditoria 51 · tests/test_smoke_l3_desk_assembly.py 24 ·
  tests/test_workbench_convergence.py 11 · tests/test_single_dock_convergence.py 10 (no mío, P-04) ·
  tests/test_cajon_core.py 9 · tests/test_coco_reengrose_avanzado.py 7 · tools/run_tests.py 5

$ python3 -I tools/auditoria/minimalismo.py resumen
TOTAL | 85 | 23484 | 880 | -        (core 8671 líneas, ui 13505, cad 367, app 941)
$ python3 -I tools/auditoria/minimalismo.py duplicados   -> tablas constantes idénticas: 2
$ python3 -I tools/auditoria/minimalismo.py literales    -> literales vigilados fuera de datos/: 53
$ python3 -I tools/auditoria/minimalismo.py excepciones  -> except que tragan errores: 89
$ python3 -I tools/auditoria/minimalismo.py tamano       -> archivos > 400 líneas: 17
$ python3 -I tools/auditoria/minimalismo.py ramas        -> funciones con 4+ ramas if/elif: 12
```

Goldens: 15 ficheros, 140 entradas, 0 errores (script sobre `tests/golden/*.json`).

Goldens de dominio contra el código actual (`freecadcmd`, `GOLD_MODS=...`): 14 de 14 OK. Creación: `VERIFICAR diferencias= 0`.

Cifras de ruff en el tiempo: el registro decía 288; al cierre de la primera pasada `ruff check .` daba 299; al cierre de esta pasada da 303. Medido por fichero: `tests/test_goldens.py` y `tools/auditoria/ciclos.py` dan 0 incidencias. El resto del aumento no lo he separado por commit, así que no atribuyo causa.

---

## Medición de la tercera pasada (tras `7566f34`)

Comandos, salidas literales (sin editar). Sesión de D-11, D-12 y M2 parcial.

```
$ readlink ~/.local/share/FreeCAD/Mod/VDO
/home/airhon/Proyectos/VDO_freecad_workbench
$ git rev-parse --short HEAD
7566f34

$ VDO_TEST_DIR=tests VDO_TEST_OUT=... python3 -I tools/run_tests.py          # nivel 1
RESUMEN ejecutados=284 fallos=3 errores=0 skip=113 no_ejecutado=0
  FALLO test_arquitectura.CapasTests.test_core_no_importa_app_ui_cad
  FALLO test_arquitectura.CapasTests.test_ui_no_escritura_freecad
  FALLO test_arquitectura.CapasTests.test_ui_no_importa_core_cad_app_api

$ VDO_TEST_DIR=tests VDO_TEST_OUT=... freecadcmd tools/run_tests.py          # nivel 2, 3 ejecuciones
RUN 1 EXIT=1 SIGSEGV_LINEAS=0 -> RESUMEN ejecutados=282 fallos=4 errores=0 skip=26 no_ejecutado=0
RUN 2 EXIT=1 SIGSEGV_LINEAS=0 -> RESUMEN ejecutados=282 fallos=4 errores=0 skip=26 no_ejecutado=0
RUN 3 EXIT=1 SIGSEGV_LINEAS=0 -> RESUMEN ejecutados=282 fallos=4 errores=0 skip=26 no_ejecutado=0
  FALLO test_arquitectura (×3, los de siempre)
  FALLO test_goldens.GoldensVerificacionTests.test_guardian  (golden pendiente, ver D-11)
  (test_guardian_locale: OK en ambas ejecuciones con LC_NUMERIC=es_CO.UTF-8 y LC_NUMERIC=C)

$ python3 -I tools/auditoria/ciclos.py
CICLOS: 3 componentes  (todos en ui/; ninguno en core ni en cad)
ARISTAS core->cad: 8

$ python3 -I tools/auditoria/minimalismo.py resumen
=== RESUMEN por capa ===
capa | archivos | lineas | funciones | api_publica
--------------------------------------------------
core | 26 | 8671 | 308 | 249
ui | 33 | 13472 | 513 | 301
cad | 5 | 387 | 18 | 13
app | 21 | 941 | 42 | 50
TOTAL | 85 | 23471 | 881 | -
$ minimalismo.py duplicados -> tablas constantes idénticas (AST): 0 ; funciones con cuerpo idéntico: 3
$ minimalismo.py literales   -> literales vigilados fuera de datos/: 53
$ minimalismo.py ramas      -> funciones con 4+ ramas if/elif: 12
$ minimalismo.py tamano     -> archivos > 400 líneas: 17 ; funciones > 60 líneas: 68
$ minimalismo.py excepciones-> except que tragan errores: 89
$ minimalismo.py fachadas   -> 0

$ .venv/bin/ruff check . --no-cache --statistics
Found 300 errors.
[*] 23 fixable with `--fix` (10 unsafe fixes available with `--fix --unsafe-fixes`).
```

Cifras de ruff: 303 en la pasada anterior, 300 ahora. El desglose por carpeta no se ha vuelto a medir en esta pasada.

**Nota de una ejecución descartada:** una ejecución de nivel 2 con `VDO_TEST_OUT` apuntando a un directorio terminó con código 139 (SIGSEGV al salir), tras un `IsADirectoryError` en el runner. Con la ruta correcta, 3 de 3 ejecuciones dan código 1 y 0 SIGSEGV. No se ha investigado más allá de esa observación.

### D-11 — salidas de locale (sonda con `freecadcmd`, locale forzado con `locale.setlocale`)

```
# Antes del cambio (escritura str(valor)), LC_NUMERIC forzado es_CO.UTF-8:
A1 entrada='0.4'  lectura=0
A2 entrada='=0.4' lectura=0
A5 entrada='7417634.708' lectura=7417634
# Antes del cambio, LC_NUMERIC forzado C:
A1 entrada='0.4'  lectura=0.4
A5 entrada='7417634.708' lectura=7417634.708

# Después del cambio (=N/D), LC_NUMERIC forzado es_CO.UTF-8 y C:
A1 txt==2/5 leido=0.4 IGUAL ; A2 txt==1854408677/250 leido=7417634.708 IGUAL ; ... (9 casos)
TODAS_IGUALES   (con es_CO.UTF-8)
TODAS_IGUALES   (con C)
```

Nota: `locale.setlocale(LC_NUMERIC)` sin argumentos devuelve `C` en el arranque aunque el entorno pida `es_CO`. Por eso la sonda fuerza el locale con `setlocale(LC_NUMERIC, ...)` explícito.

**Golden `guardian.json`:** diferencia medida con `golden.py` (sin regenerar): en las 6 entradas, solo la celda `Params_Melamina!B5` (`canto_fino`): esperado `{'contenido': '0.4'}`, obtenido `{'contenido': '=2 / 5'}`. El alias y el valor leído no cambian. Requiere aprobación humana.

---

## Alcance de ruff y mypy (D-04)

Ver `docs/PLAN_MINIMALISMO_VDO.md` §2, decisión D-04.

- **Ruff:** `ruff check .` desde la raíz, sin excluir carpetas. **299** incidencias: `freecad/` 147, `tests/` 86, `tools/` 58, `Init.py` + `InitGui.py` 8. Versión 0.17.3 (`.venv`).
- **Mypy:** paquete de `pyproject.toml` (`core`, `app`, `cad`). **1081** errores: `core` 1008, `app` 45, `cad` 28. Versión 2.4.1 (`.venv`).

---

## M0 — goldens

Procedencia completa en `docs/metricas/goldens_origen.md`.

| Fichero | Entradas | Errores |
|---|---|---|
| cajon_despiece, coco_spaces, facade_contract (23), finish, frames (18, 1 en error), guardian (9), hardware_hub, layout, module_props, optimizer_core, puerta_despiece, reengrose (18), spaces, zocalo_core, creacion_modulos (15) | **131** entradas en **15** ficheros | **1** (`frames.interpretar_lados`, JSON inválido, comportamiento de origen) |

Verificación contra el código actual (medida al cierre, `freecadcmd` con `GOLD_MODS`):
- Los 14 goldens de dominio (`facade_contract`, `frames`, `finish`, `reengrose`, `cajon_despiece`, `puerta_despiece`, `coco_spaces`, `hardware_hub`, `module_props`, `guardian`, `zocalo_core`, `layout`, `optimizer_core`, `spaces`): `OK golden` en los 14, 0 diferencias.
- `golden_creacion.py`: `VERIFICAR diferencias= 0`.

Goldens sustituidos (P-05, pendientes de aprobación humana): `creacion_modulos`, `coco_spaces`, `puerta_despiece`. Detalle en `goldens_origen.md`. Dos pasan de error a valor (cambio de salida esperada).

---

## M2 — estado

**Hecho:**
- Herrajes solo desde el JSON; sin `_FALLBACK_*` (`8b85ce3`, H-20).
- Anclajes en `datos/anclajes.json` (`699e944`, H-01). El duplicado de carga en `cad` queda en D-10.
- `CANTOS_VALIDOS` en un solo sitio, `core/vdo_finish` (`1b5a1b7`, H-02).
- `BORDES` en un solo sitio, `core/vdo_finish`; la UI lo consume desde ahí (`1b5a1b7`, H-03 grupo A).
- `CANTOS` de la fachada eliminado: sin usos en el repo (`bb58afc`).
- `CHOQUES_NUCLEO` eliminado: sin usos; queda `MODOS_CHOQUE_NUCLEO` (`bb58afc`, H-05).
- `BORDES_2D` (reengrose) como único sitio para la UI de caja (`bb58afc`, H-03b).
- `DIMENSION_POR_EJE` en `core/vdo_helpers` (`cbfb55f`, H-06).

**Pendiente, con causa:**
- `ESQUINAS` (H-04): **hecho** (`9040cca`, P-07).
- `rotacion_z` (H-60 a H-62): **bloqueado por P-06**.
- Ciclo dentro de `cad`: **resuelto** (`00fdf7f`, D-12). Quedan 3 ciclos dentro de `ui/` (fuera de D-12) y 8 aristas core→cad (H-01b, D-10, `forma_ref`), que se eliminan en M5.
- `MODULE_SPECS` (H-22, 162 líneas): para pasarlo a `datos/modulos.json` hace falta un golden de la tabla antes del cambio. Hoy no hay ninguno. No lo he hecho.
- `LUCIDE_ICONS` (H-23): **hecho** (`04a83e5`). Las dos tablas no eran copias: compartían solo `inglete_45`, con SVG distinto. Decisión registrada en `DECISIONES_DELEGADAS.md`.
- `CATALOGO_PATH` (H-21): **hecho** (`7566f34`). Corrige un defecto: la UI usaba una ruta inexistente.
- Caché de iconos y logger (H-24): **decididos, no unificados** (no son hechos de dominio; ver `DECISIONES_DELEGADAS.md`).
- **Literales (53):** `oculta` y `tirador` ya tienen constantes de dominio (`CORREDERA_OCULTA` en `core/vdo_cajon_despiece.py:22`, `APERTURA_TIRADOR` en `core/vdo_facade_contract.py:14`). Lo correcto es reemplazar por esas constantes, no crear un JSON nuevo. `melamina_standar` (23 usos) y `blum_tandem` (14) necesitan una constante nueva. Es una sustitución por ocurrencia, con su propio golden. No la he hecho en esta pasada.

---

## M3 a M11

No iniciadas. M2 está abierta (literales, `MODULE_SPECS`, `LUCIDE_ICONS`, `_CATALOGO_PATH`).

---

## Abierto

Estado de cada decisión de `DECISIONES_DELEGADAS.md` (fuente vigente; `PENDIENTES_HUMANO.md` lo escribe otra sesión y no se ha tocado):

- **P-04**: no se tocan ni commitean los 2 tests de otra sesión. Pendiente del usuario. Nota: `tests/test_single_dock_convergence.py` usa `sys` sin importarlo (ruff F821, línea 218): su `__main__` falla con NameError. Es un defecto de ese cambio sin commitear.
- **P-05**: aprobados por delegación. Revertir: `git revert 200c79c`.
- **P-06**: decidido (única definición de `rotacion_z` en `cad/propiedades.py`), **no aplicado**: el borrado de la copia de `core/vdo_helpers` es de M5. Fuera de la lista de esta pasada.
- **P-07**: **aplicado** (`9040cca`). `minimalismo.py duplicados`: tablas idénticas 2 → 0.
- **P-08**: **aplicado** (`47045b0`). Core↔cad ya no cierra ciclo. Aristas core→cad: 4 → 8 (ver "Medición"; se eliminan en M5).
- **D-12** (decidida por el asistente): **aplicada** (`00fdf7f`). `aplicar_rotacion` vive en `cad/colocacion.py`. Ciclo dentro de `cad`: resuelto.
- **D-11** (aprobada por el usuario): **código aplicado** (`169135b`). Golden `guardian.json` pendiente de aprobación humana (ver `goldens_origen.md`). Documentos ya guardados con `0` **no se corrigen por código** (ver `DECISIONES_DELEGADAS.md`, pendientes humanos).
- **P-09**: retirado (no hay definición). Lo registra el documento de decisiones.
- **P-10**: N/A con motivo y deuda antes de M5 (`goldens_origen.md`).
- Los planes anteriores siguen sin archivar (MN-13, M11).
