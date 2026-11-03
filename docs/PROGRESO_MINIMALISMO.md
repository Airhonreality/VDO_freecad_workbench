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
| **M0** — Congelar y medir | ⚠️ **parcial: 18 de 19** | 19 módulos de dominio: 18 con golden (14 de módulo + 4 flujos de creación en `creacion_modulos.json`). Falta `nesting_presets`: en `b78de04` no carga dentro de FreeCAD. Decisión humana: **P-10**. |
| **M1** — Inventario de hechos | ⚠️ **parcial** | Inventario en `docs/INVENTARIO_HECHOS.md`. El gate pide "cada hecho duplicado con destino único decidido". Faltan: H-60 a H-62 (**P-06**), H-04 (**P-07**), y decisiones marcadas [decisión] sin tomar: H-21, H-24, H-52. |
| **M2** — Un hecho, un lugar: datos | ⚠️ **parcial** | Ver "M2" más abajo. Tablas idénticas 9 → 2. Literales: 53 sin cambio. |
| M3 a M11 | ⏸ no iniciadas | M2 sigue abierta. |

### M0: gate

| Criterio | Resultado | Evidencia |
|---|---|---|
| `minimalismo_base.json` existe | ✅ | `fc224dd` |
| 19 goldens de dominio existen | ⚠️ 18 de 19 | `nesting_presets` pendiente (P-10) |
| Nivel 2 sin SIGSEGV en 5 de 5 | ✅ | Ver "Medición" |
| Diferencias documentadas | ✅ | `goldens_origen.md`, secciones "Guardián" y "Revisión de goldens sustituidos (P-05)" |

**Bloqueo de M0:** P-10 (`nesting_presets`). Sin decisión, M0 queda parcial.

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
- `ESQUINAS` (H-04): **bloqueado por P-07**.
- `rotacion_z` (H-60 a H-62): **bloqueado por P-06**.
- Ciclo core↔cad (H-01b, D-10, `forma_ref`): **bloqueado por P-08**.
- `MODULE_SPECS` (H-22, 162 líneas): para pasarlo a `datos/modulos.json` hace falta un golden de la tabla antes del cambio. Hoy no hay ninguno. No lo he hecho.
- `LUCIDE_ICONS` (H-23): el inventario dice "comparar el contenido de las dos copias antes de migrar". No lo he comparado.
- `_CATALOGO_PATH` (H-21) y caché/logger (H-24): marcados [decisión] en el inventario, sin decidir.
- **Literales (53):** `oculta` y `tirador` ya tienen constantes de dominio (`CORREDERA_OCULTA` en `core/vdo_cajon_despiece.py:22`, `APERTURA_TIRADOR` en `core/vdo_facade_contract.py:14`). Lo correcto es reemplazar por esas constantes, no crear un JSON nuevo. `melamina_standar` (23 usos) y `blum_tandem` (14) necesitan una constante nueva. Es una sustitución por ocurrencia, con su propio golden. No la he hecho en esta pasada.

---

## M3 a M11

No iniciadas. M2 está abierta (literales, `MODULE_SPECS`, `LUCIDE_ICONS`, `_CATALOGO_PATH`).

---

## Abierto

- **P-10**: decidir el golden de `nesting_presets` (bloquea M0).
- **P-06**: ubicación de `rotacion_z` (bloquea M1 y parte de M2).
- **P-07**: `ESQUINAS` frente a `TIPOS_ENCUENTRO` (bloquea M1 y parte de M2).
- **P-08**: ciclo core↔cad (bloquea M2 en `core/vdo_module_props.py` y en los módulos con `forma_ref`).
- **P-09**: sin definir en el repo ni en el encargo. Hay que definirlo o retirarlo.
- **P-05**: aprobar los 3 goldens sustituidos.
- **P-04**: cambios de tests de otra sesión sin commitear.
- Los planes anteriores siguen sin archivar (MN-13, M11).
