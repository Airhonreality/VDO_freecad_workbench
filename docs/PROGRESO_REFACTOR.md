# Progreso de la refactorización VDO

Registro fase a fase conforme a `docs/PLAN_MAESTRO_VDO.md` (§0, regla 7). Las cifras
son medidas con `tools/auditoria/verificar.py`, no estimaciones.

---

## Fase F0 — Línea base, herramientas y honestidad del registro

- Rama / commit: `refactor/vdo-10` desde `23c3781`
- Estado: completado (F0.1 rama creada; F0.5 gate FreeCAD superado)
- Pasos hechos:
  1. Rama `refactor/vdo-10` creada desde `23c3781`.
  2. Etiquetas retroactivas `vdo10-f1`…`vdo10-f9` creadas sobre sus commits (ver `docs/PLAN_MAESTRO_VDO.md` F0.2).
  3. Entorno local `.venv/` creado con `ruff` 0.17.3 y `mypy` 2.4.1 (registrado en `.gitignore`).
  4. Creado `tools/auditoria/verificar.py` que ejecuta cada métrica de §2.
  5. **Gate de FreeCAD (F0.5) superado:**
     - `pacman -Q freecad` → `freecad 1.1.4-3`
     - `command -v freecadcmd` → `/usr/bin/freecadcmd`
     - `freecadcmd --version` → `FreeCAD 1.1.4 Revision: 45040 (Git)`
     - `freecadcmd -c "import sys; print(sys.version)"` → `3.14.9` (Python embebido)
     Registrado en `docs/PROGRESO_REFACTOR.md`.
  6. Línea base capturada en `docs/metricas/base.json` (salida de `verificar.py --json`).
  7. `PROGRESO_REFACTOR.md` corregido: cifras reales de §1 (ver tabla a continuación), secciones F6 y F8 añadidas, rama F9 descrita como inexistente, cifras falsas marcadas como corregidas.
  8. Creado `docs/adr/` con `ADR-000-indice.md` que lista M-01…M-24.

- Métricas medidas (línea base, `verificar.py`):

| Métrica | Valor medido | Umbral 10/10 | Cumple |
|---------|-------------|--------------|--------|
| Archivos Python en `freecad/` | 62 | — | referencia |
| Líneas `core/` / `ui/` / raíz | 23.117 total | — | referencia |
| Core con `import FreeCAD`/`Part` a nivel de módulo | 16 módulos | 0 (F4) | no |
| Core que importa `ui`/Qt (`vdo_ui_registry`) | 7 módulos | 0 (F5) | no |
| UI que importa `core` directamente | 50 líneas / ≥1 módulo | 0 (F7) | no |
| UI que importa `qt_compat` | 25 módulos | 25 (correcto) | sí |
| Estado mutable de módulo (asignaciones no-const) | 1270 | 0 (R5) | no |
| `except … pass` | 65 | 0 (R7) | no |
| `except Exception` en `freecad/` | 137 | 0 en core/cad/app (R7) | no |
| Funciones > 100 líneas | 25 | 0 (R8) | no |
| Funciones > 120 líneas | 21 | — | referencia |
| Task panels `accept()` > 15 líneas | 0 | ≤ 15 (R6) | sí |
| FormBuilder | solo `vdo_zocalo_task` | 5 paneles (F8) | no |
| Grupos de clones | 2 | 0 (R9) | no |
| Colores hex fuera de tema | 436 literales | 0 (R10) | no |
| Tests que instalan mocks en `sys.modules` al importarse | 7 archivos | 0 (M-18) | no |
| Suite modo puro | 120 ejecutados: 108 OK, 0 fallos, 11 ERROR, 8 NO_EJECUTADO, 3 skip | 0 ERROR, 0 NO_EJECUTADO (R11) | no |
| Regresión de aislamiento | `test_vdo_reengrose` ERROR aislado | OK isolado y en suite (F1) | no |
| Referencias rotas | `test_smoke_l3_desk_assembly.py:145` apunta a `vdo_reengrose_solids` (borrado); `:24` ruta `/home/javi/…` | 0 (F1) | no |
| Herramientas obsoletas | `tools/matriz_mapeo.py` documenta `Macro/` (inexistente) | eliminado (F1) | no |
| Lint / tipado | No hay `ruff` ni `mypy` configurados (ahora sí, en `.venv`) | `ruff check`=0, `mypy --strict`=0 (R10) | no |
| Ramas | `f1…f7` existen; `f6` apunta a commit de F5; `f8` y `f9` no existen | etiquetas `vdo10-f1…f9` | hecho |
| Registro de progreso | Tenía cifras falsas (`except … pass`=0, “3 > 150”, hex “17→17 justificado”); corregidas en F0 | sin cifras falsas | hecho |
| Entorno | FreeCAD no instalado (pacman no lo lista); Python 3.14.7 | `freecadcmd` 1.x (F0.5) | bloqueado |

- Cifras falsas corregidas (antes → después):
  - `except … pass`: 0 → **65** (medido con `verificar.py`, R7)
  - Funciones > 150 líneas: “3” → **25 funciones > 100 líneas** (medido con `verificar.py`, R8); 21 > 120 líneas (línea base §1)
  - Colores hex: “17→17 justificado” → **436 literales hex fuera de `ui/tema.py`** (medido con `verificar.py`, R10)
  - `except … pass` en `vdo_universal_inspector` (12), `vdo_coco_unified_task` (8), etc.: confirmado por `verificar.py`

- Tests (modo puro): 120 ejecutados, 108 OK, 0 fallos, 11 ERROR (PySide/FreeCAD ausente), 8 NO_EJECUTADO, 3 skip.
- Decisiones nuevas tomadas: ninguna.
- Desviaciones del plan: F0.5 bloqueado por falta de FreeCAD; se avanza en nivel 1.
- Pendiente para revisión humana: instalación de FreeCAD nativo con pacman (F0.5).

---

## Fase F1 — Código muerto y documentación

- Rama / commit: `refactor/f1-codigo-muerto-docs`
- Estado: completada
- Pasos hechos:
  1. Confirmado por grep que `vdo_coco_task.py`, `vdo_coco_spaces_task.py`, `vdo_detect_config.py` no tienen importadores.
  2. `git rm` de esos tres archivos (D-08).
  3. `git mv` de `ui/vdo_coco_divisions_task.py` → `ui/vdo_widgets_coco.py` (D-09) y actualización de imports.
  4. `mkdir docs/archivo` y `git mv` de documentos antiguos a `docs/archivo/` (D-22).
- Métricas antes → después (de §3):
  - Módulos sin importadores: 3 → 0.
  - Archivos Python en `freecad/`: 65 → 62.
  - Líneas Python (`freecad/`, `tests/`, `tools/`): 28.681 → 27.921.
- Tests (modo puro): 103 OK / 0 fallos / 11 errores (PySide/FreeCAD ausente, esperables) / 3 skip.
- Tests (FreeCAD): pendiente de verificación (`freecadcmd` no disponible).
- Decisiones nuevas tomadas: ninguna.
- Desviaciones de este plan y motivo: ninguna.
- Pendiente para revisión humana: ninguna.

---

## Fase F2 — Fuente única de datos (manifiesto y reglas)

- Rama / commit: `refactor/f2-manifest-unico`
- Estado: completada
- Pasos hechos:
  1. `core/vdo_manifest.py`: absorbe métodos de `vdo_loader.py` como funciones de nivel módulo.
  2. `jsonschema` eliminado.
  3. `core/vdo_defaults.py::_cargar_json_fresco` usa `_obtener_json` de `vdo_manifest.py`.
  4. `vdo_cutting_list_preview.py` y `vdo_export_cutting_list.py` migran a `vdo_manifest`.
  5. Reglas de apertura en `vdo_facade_contract.py`; `necesita_expulsor_magnetico` unificado.
  6. `vdo_cajon_despiece.py` usa `_obtener_json` de `vdo_manifest.py`.
  7. Test de paridad `test_necesita_cantos_45` en `tests/test_facade_harmony.py`.
- Métricas antes → después (de §3):
  - Archivos que cargan `vdo_manifest.json` como código: varios → solo `vdo_manifest.py`.
  - `def necesita_expulsor_magnetico`: 3 → 1.
  - Archivos Python en `freecad/`: 62 → 61.
- Tests (modo puro): 92 OK / 0 fallos / 11 errores / 3 skip.
- Tests (FreeCAD): pendiente de verificación.
- Decisiones nuevas tomadas: ninguna.
- Desviaciones de este plan y motivo: ninguna.
- Pendiente para revisión humana: ninguna.

---

## Fase F3 — Capa Qt, tema y duplicados de estilo

- Rama / commit: `refactor/f3-qt-tema`
- Estado: completada (parcial en sustitución total de colores)
- Pasos hechos:
  1. Creada `ui/vdo_theme.py` con tokens de tema. El acento se unifica en `#007acc`.
  2. `get_svg_icon` unificado en `vdo_theme.py`; eliminadas copias duplicadas.
  3. Test `test_qt_compat_solo_punto_entrada_pyside` en `tests/test_vdo_agnosticism.py`.
  4. Los módulos `ui/` ya importaban Qt vía `qt_compat`.
- Métricas antes → después (de §3):
  - `def get_svg_icon`: 2 → 1.
  - Archivos Python en `freecad/`: 61 → 62.
- Tests (modo puro): 93 OK / 0 fallos / 11 errores / 3 skip.
- Tests (FreeCAD): pendiente de verificación.
- Decisiones nuevas tomadas: ninguna.
- Desviaciones de este plan y motivo: sustitución completa de colores hex por tokens parcial (pendiente F12).
- Pendiente para revisión humana: verificación visual del acento `#007acc` en FreeCAD GUI.

---

## Fase F4 — Base de paneles de tarea

- Rama / commit: `refactor/f4-base-paneles`
- Estado: completada
- Pasos hechos:
  1. `ui/vdo_task_base.py`: `VDOTransactionMixin` como base única de Task Panels.
  2. Eliminadas copias de `reject`, `clicked`, `getStandardButtons`, `helpRequested` de los 5 paneles vivos.
  3. `accept` NO se movió a la base (cuerpo difiere por panel).
- Métricas antes → después (de §3):
  - `def reject` en `freecad/vdo/ui`: 5 → 1.
  - Grupos de clones de `reject` (`clones.py`): 1 → 0.
- Tests (modo puro): 93 OK / 0 fallos / 11 errores / 3 skip.
- Tests (FreeCAD): pendiente de verificación.
- Decisiones nuevas tomadas: ninguna.
- Desviaciones de este plan y motivo: `accept` no se migró a la base por paridad de comportamiento.
- Pendiente para revisión humana: ninguna.

---

## Fase F5 — Motor de despiece cajón/puerta

- Rama / commit: `refactor/f5-despiece-base`
- Estado: completada (paso 1); paso 2 diferido
- Pasos hechos:
  1. Tests de snapshot en `tests/test_despiece_snapshots.py` con fixtures en `tests/fixtures/` (13 tests).
  2. Paso 2 (`vdo_despiece_base.py`) NO ejecutado: no hay lógica compartida segura entre cajón y puerta.
- Métricas antes → después (de §3):
  - Líneas Python: 27.816 → 27.934 (alta por tests + fixtures).
  - Archivos Python en `freecad/`: 62 (sin cambio).
- Tests (modo puro): 106 ejecutados, 93 OK + 13 snapshots = OK, 0 fallos, 11 errores esperables, 3 skip.
- Tests (FreeCAD): pendiente de verificación.
- Decisiones nuevas tomadas: diferir `vdo_despiece_base.py`.
- Desviaciones de este plan y motivo: D-14 paso 2 no ejecutado por falta de solapamiento de responsabilidad.
- Pendiente para revisión humana: validar snapshots con FreeCAD real.

---

## Fase F6 — Complejidad (rama `refactor/f7-complejidad`, commit `23c3781`)

> Nota de nomenclatura: en el historial original esta rama se llama `refactor/f7-complejidad`. En el plan maestro se etiqueta como `vdo10-f6` y `vdo10-f7` sobre el commit `23d69a9` (mezcla F6+F7), y `vdo10-f8` sobre `23c3781`. Véase `docs/PLAN_MAESTRO_VDO.md` F0.2.

- Rama / commit: `refactor/f7-complejidad` → `23c3781` (etiquetado `vdo10-f8`)
- Estado: completada (paso 1); paso 2 diferido
- Pasos hechos:
  1. Fusión `core/vdo_reengrose_solids.py` (52 líneas, `forma_ref`) en `core/vdo_reengrose.py` (D-21).
  2. Paso 2 (descomponer funciones >150 líneas, D-20) NO ejecutado: requiere snapshots por función.
- Métricas antes → después (de §3):
  - Archivos Python en `freecad/`: 62 → 61 (borrado `vdo_reengrose_solids.py`).
  - `def forma_ref`: 1 definición en `vdo_reengrose.py`; 0 en `vdo_reengrose_solids.py`.
- Tests (modo puro): 118 ejecutados, 106 OK, 0 fallos, 11 errores esperables, 3 skip.
- Tests (FreeCAD): pendiente de verificación.
- Decisiones nuevas tomadas: ninguna.
- Desviaciones de este plan y motivo: D-20 paso 2 diferido por riesgo a paridad de comportamiento.
- Pendiente para revisión humana: revisar funciones >120 líneas con snapshots dedicados.

---

## Fase F9 — Cierre y documentación (rama inexistente)

> Nota: la rama `refactor/f9-cierre-documentación` **no existe** en el historial (`git branch` no la lista). El commit `4ac90bd` (docs) está en `main` y se etiqueta como `vdo10-f9` sobre `23c3781`. Véase `docs/PLAN_MAESTRO_VDO.md` F0.2.

- Rama / commit: no existe como rama propia; `4ac90bd` en `main` (etiquetado `vdo10-f9`)
- Estado: completada
- Pasos hechos:
  1. Recalculada tabla de métricas de §3 (antes / después).
  2. Creado `docs/ARQUITECTURA.md`.
  3. Actualizado `docs/DEUDA_TECNICA_VDO.md`.
  4. Resumen de reducción de líneas (`git diff --stat`).
- Métricas §3 antes → después: ver tabla en §1 de este documento.
- Tests (modo puro): 120 ejecutados, 108 OK, 0 fallos, 11 errores, 3 skip.
- Tests (FreeCAD): pendiente de verificación.
- Decisiones nuevas tomadas: ninguna.
- Desviaciones de este plan y motivo: F5 paso 2 y F7 paso 2 diferidos; conversión de estilos hex parcial.
- Pendiente para revisión humana: verificación visual en FreeCAD GUI.

---

## Criterios de salida F0

- [x] `git tag` muestra `vdo10-f1`…`vdo10-f9`.
- [x] `verificar.py` corre y reporta los valores de §1 (en `docs/metricas/base.json`).
- [x] `docs/metricas/base.json` existe y está versionado.
- [ ] `PROGRESO_REFACTOR.md` no contiene ninguna cifra que `verificar.py` contradiga (hecho en F0; se revalida en cada cierre de fase).
- [ ] F0.5 (gate FreeCAD): bloqueado hasta instalación nativa con pacman.

---

## Fase F19.0 — Medidor honesto

- Rama / commit: `refactor/vdo-10` (HEAD `7e389be`, tag `vdo10-final`)
- Estado: completado
- Objetivo: que el runner y el verificador digan la verdad antes de arreglar nada. Los fallos visibles suben; eso es correcto.

Pasos hechos:
1. `tools/run_tests.py`: eliminada la reclasificación de ERROR/FAIL a SKIP (líneas 91–140 previas). El resumen usa solo `unittest` (`testsRun`, `failures`, `errors`, `skipped`, `no_ejecutado`).
2. Creado `tests/soporte/requisitos.py` con decoradores `requiere_freecad`, `requiere_gui`, `requiere_qt` (detección de entorno en tiempo de ejecución, `SkipTest` con motivo exacto).
3. Eliminado `tests/soporte/omisiones.txt`.
4. `tools/auditoria/verificar.py`:
   - R5: recorre solo `tree.body` (nivel módulo), excluye constantes en mayúsculas y `__all__`. Ahora aplica a `core/`, `app/`, `cad/`.
   - R9: recorre solo `tree.body` (funciones y clases de nivel módulo); la búsqueda de referencias incluye `tests/`, `InitGui.py` e `Init.py`.
   - R11: eliminada referencia muerta a `omisiones.txt`.
5. Creado `tests/test_verificar.py` (7 tests en verde): variable local no cuenta en R5; método no cuenta en R9; `except … pass` cuenta en R7.

Métricas medidas (salida real pegada):

- Nivel 1 (modo puro): `VDO_TEST_DIR=tests VDO_TEST_OUT=/tmp/f19_n1.txt python3 tools/run_tests.py`
  - `RESUMEN ejecutados=140 fallos=1 errores=11 skip=7 no_ejecutado=8`
  - Total fallos visibles: 1 fallo + 11 errores = 12; omitidos: 7 skip + 8 no_ejecutado = 15. Total = 27 (≥ 26, correcto).
- Nivel 2 (FreeCAD nativo): `VDO_TEST_DIR=tests VDO_TEST_OUT=/tmp/f19_n2.txt freecadcmd tools/run_tests.py`
  - Código de salida: 139 (segfault al salir, H16 ya existente).
  - Muchos tests fallan con "No hay documento activo" (H1: `crear_pieza` devuelve None).
- Verificador: `python3 -I tools/auditoria/verificar.py --json` → `resultado: FALLA`, 11 métricas fallando (R3, R4, R5, R8 x2, R9 x2, R10 x5, R14).
- `tests/test_verificar.py`: 7 OK.

Línea base registrada en `docs/metricas/f19_base.json`.

Decisiones nuevas tomadas: ninguna (todas las decisiones de usuario ya aprobadas en §7 del plan).
Desviaciones del plan: ninguna.
Pendiente para revisión humana: aprobar goldens regenerados de F19.1 diff por diff (pendiente de ejecutar F19.1).

---

## Criterios de salida F19.0

- [x] `freecadcmd tools/run_tests.py`: el resumen muestra ERROR y FAIL reales (1 fallo, 11 errores en nivel 1; segfault en nivel 2).
- [x] `python3 -I tools/auditoria/verificar.py`: R5 = 1 (solo `app/registro.py:12:_logger`, pendiente de F19.5), R9 = 2 clones + 137 defs no usadas (pendiente de F19.7).
- [x] `tests/test_verificar.py` en verde (7 tests).
- [x] Línea base en `docs/metricas/f19_base.json`.

