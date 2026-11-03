# Progreso — plan de minimalismo VDO

**Rama de trabajo:** `minimalismo/noche-20261102` (desde `c1fa9d2`, punta de `refactor/vdo-10`).
**Plan rector:** `docs/PLAN_MINIMALISMO_VDO.md`. Los planes anteriores están sustituidos.
**Cada cifra de este registro sale de un comando citado. Ninguna es estimación.**

---

## Estado

| Fase | Estado | Motivo |
|---|---|---|
| Premisas y rama | ✅ | Ver "Comprobaciones iniciales" |
| Segfault al salir (pre-M0) | ✅ | `c1fa9d2` (en `refactor/vdo-10`) |
| **M0** — Congelar y medir | ⚠️ **parcial** | Goldens: 14 ficheros que cubren 17 de 19 módulos. Quedan 2 sin función de cálculo (P-01) y la aprobación de goldens (P-05). |
| M1 a M11 | ⏸ no iniciadas | El plan exige cerrar M0 antes de empezar M1. |

**Bloqueo:** el gate de M0 pide "los 19 goldens existen". Hoy hay 14 ficheros:
- 13 de dominio (incluye `module_props`, con golden desde `b78de04` y reubicación documentada).
- `creacion_modulos.json` cubre además `panel_core`, `cajon_core`, `puerta_core` y `coco_core`.
- Quedan `guardian` y `nesting_presets`, que no tienen función de cálculo. Cerrar el gate exige decidir si cuentan como N/A (P-01).

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
/home/airhon/Proyectos/VDO_freecad_workbench             # sin cambios
```

Correcciones a premisas del prompt:
- `cad/colocacion.py`, `ui/vdo_interfaz.py` y `tests/test_creacion_colocacion.py` **ya estaban commiteados** (`abf59b1`, `b2583a6`). No había pendientes de esos.
- El aviso "SUSTITUIDO" de los dos planes viejos no estaba commiteado. Commiteado en `c59587b`.

Cambios de otra sesión que **no** son míos (ver `PENDIENTES_HUMANO.md`, P-04):
- `tests/test_gui_wiring.py` y `tests/test_single_dock_convergence.py`: `os._exit` → `sys.exit` en bloques `__main__`. **Sin commitear.** No verificados.

---

## Commits de la noche

| Hash | Fase | Qué hace |
|---|---|---|
| `c59587b` | premisas | Aviso de sustitución en `PLAN_MAESTRO_VDO.md` y `PLAN_CORRECCIONES_F19.md` |
| `5fe5eea` | M0 | `minimalismo.py`: literales por AST y ramas por cadena if/elif real |
| `31785b2` | M0 | `minimalismo.py duplicados`: solo contenedores de 2+ elementos |
| `fc224dd` | M0 | `docs/metricas/minimalismo_base.json` medido |
| `762d768` | M0 | Goldens: herramienta, entradas de 19 módulos, fixtures de layout |
| `692b76a` | M0 | 13 goldens desde `b78de04` + `docs/metricas/goldens_origen.md` |
| `4e29c04` | M0 | `module_props` con golden (serialización de `App.Rotation`, reubicación de `rotacion_z`) |

Previos en la rama (ya en `refactor/vdo-10`): `e10cd12` (plan rector), `c1fa9d2` (segfault).

---

## M0 — medición

### Línea base (`minimalismo.py`, sobre `fc224dd`)

Salida de `python3 -I tools/auditoria/minimalismo.py resumen` (literal):

```
=== RESUMEN por capa ===
capa | archivos | lineas | funciones | api_publica
--------------------------------------------------
core | 26 | 8780 | 308 | 249
ui | 33 | 13507 | 513 | 301
cad | 5 | 380 | 17 | 13
app | 21 | 941 | 42 | 50
TOTAL | 85 | 23608 | 880 | -
```

Diferencia con el plan (§1): el plan dice 88 archivos y 23.920 líneas (medido en `e4b10d3`).
La herramienta mide 85 y 23.608. Causa: el conteo del plan y el de la herramienta no
cuentan igual. Pendiente de decidir qué método es el de referencia (ver `DEUDA_TECNICA.md`).

Resto de subcomandos, sobre el código actual (`docs/metricas/minimalismo_base.json`):

| Subcomando | Valor | Plan (§1) | Nota |
|---|---|---|---|
| `duplicados` tablas idénticas | **9** | 2 pares | El plan contó a mano; la herramienta mide 9 grupos de contenedores con 2+ elementos. Incluye `ANCLAJES`/`ANCLAJE_LABELS`. |
| `duplicados` cuerpos idénticos | 3 | — | |
| `literales` usos de dominio | **53** | 26 + 14 + 9 + 8 | Cuenta por AST sobre literales de cadena. `melamina_standar` = 23. |
| `ramas` funciones con cadena if/elif ≥ 4 | **12** | 16 | Heurística distinta de la del plan. |
| `fachadas` | 0 | — | |
| `tamano` archivos > 400 líneas | 17 | 10 | Límite de 400 del plan §3; el plan citaba 10 módulos > 600. |
| `tamano` funciones > 60 líneas | 68 | 25 > 100 | Medido con umbral 60 (plan §3). |
| `excepciones` que tragan errores | 90 | — | Ver `minimalismo.py excepciones`. |

**Correcciones de la herramienta antes de medir** (commits `5fe5eea`, `31785b2`):
- `literales` contaba subcadenas en texto (`tirador` en `tirador_x`, comentarios). Ahora cuenta literales de cadena por AST.
- `ramas` sumaba `if` independientes. Ahora cuenta la mayor cadena `if`/`elif` real.
- `duplicados` contaba escalares (`VERSION = 1`) como tablas. Ahora solo contenedores de 2+ elementos. Pasó de 30 a 9.

### Verificación de referencia (`verificar.py`, con `.venv` en PATH)

Salida de `python3 -I tools/auditoria/verificar.py` (resumen; salida completa en `/tmp/vdo_m0/verificar_salida.txt`):

```
[FALLA] R1_capas: valor=17
[FALLA] R3_dominio_como_datos: valor=32
[FALLA] R8_funciones_le100: valor=25
[FALLA] R8_ruff_c901_le12: valor=28
[FALLA] R9_defs_no_usadas: valor=2
[FALLA] R10_ruff_check_cero: valor=288
[FALLA] R10_mypy_strict_cero: valor=1081
[FALLA] R10_cero_hex_fuera_tema: valor=417
[OK]    R11_golden_masters: valor=13
MÉTRICAS FALLADAS (8): ...
```

Contraste con el prompt: R1=17, R3=32, R8>100=25, C901=28, R9=2, mypy=1081, hex=417 coinciden.
**ruff da 288, no 259.** Con `.venv/bin/ruff` 0.17.3 la cifra cambia. Registrado tal cual.

### Nivel 1 y nivel 2

Nivel 2, `freecadcmd tools/run_tests.py`, 5 ejecuciones (tras `692b76a`):

```
RESUMEN ejecutados=260 fallos=3 errores=0 skip=26 no_ejecutado=0   (×5, SIGSEGV=0 en las 5)
```

Código de salida 1 en las 5, por los 3 FALLO de `test_arquitectura.py`. No es crash.

Nivel 1, `python3 -I tools/run_tests.py`:

```
RESUMEN ejecutados=262 fallos=3 errores=0 skip=107 no_ejecutado=0
```

### Goldens

Procedencia completa en `docs/metricas/goldens_origen.md`.

Verificación de los 13 ficheros contra el código actual:

```
$ PYTHONPATH=$PWD python3 tools/auditoria/golden.py --verificar <modulo>   # 12 de dominio: OK, 0 diferencias
$ freecadcmd tools/auditoria/golden_creacion.py                            # VERIFICAR diferencias= 0
```

**Diferencias entre `b78de04` y el código actual:**
- **Firma de creación**: `b78de04` usa `f(configuracion)` con `App.ActiveDocument`. El código actual usa `f(doc, configuracion)`. Es un cambio de interfaz, no de comportamiento: las salidas de los 15 casos son iguales. Causa: refactor posterior a `b78de04`.
- **`crear_panel`**: no existe en `b78de04`. No tiene golden de referencia.
- **Ningún golden de dominio tiene diferencias de comportamiento** con el código actual.

**Cambios de golden respecto a lo commiteado** (requieren revisión humana, P-05):
- `creacion_modulos.json`: sustituido. El anterior tenía otro esquema y ningún generador en el repo.
- `coco_spaces.json`: sustituido. El anterior tenía 3 de 3 entradas en error.
- `puerta_despiece.json`: sustituido. El anterior tenía 8 de 8 entradas en error. **No probaba nada.**

Entradas en error que quedan (comportamiento registrado, no ocultado):
- `frames.json` › `interpretar_lados`: 1 de 18. Entrada JSON inválida en `b78de04` y en el código actual.

### Gate de M0

| Criterio | Resultado | Evidencia |
|---|---|---|
| `minimalismo_base.json` existe | ✅ | `fc224dd` |
| 19 goldens existen | ⚠️ **17 de 19** | 14 ficheros: 13 dominio + creación (5 flujos, cubre 4 módulos). Quedan `guardian` y `nesting_presets` (P-01). |
| Nivel 2 sin SIGSEGV en 5 de 5 | ✅ | 5 de 5, SIGSEGV=0 |
| Diferencias documentadas | ✅ | Interfaz en `goldens_origen.md`; sin diferencias de comportamiento |

---

## Abierto (M0)

- **P-01**: aprobar `guardian` y `nesting_presets` como N/A (sin función de cálculo).
- **P-02**: resuelto. `App.Rotation` se serializa y `module_props` tiene golden.
- **P-03**: aceptar que los 4 flujos de creación se den por cubiertos con `creacion_modulos.json`.
- **P-05**: aprobar los 3 goldens sustituidos (`creacion_modulos`, `coco_spaces`, `puerta_despiece`).
- **P-04**: destino de los cambios de otra sesión en tests (`os._exit` → `sys.exit`).
- Los planes anteriores siguen sin archivar (MN-13, M11).
