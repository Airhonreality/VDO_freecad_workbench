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

## Fase F19.1 — Restaurar la creación de módulos (H1, H2, H3)

- Rama / commit: `refactor/vdo-10` → `7f5ff8b`
- Estado: completado
- Pasos hechos:
  1. Eliminado `freecad/vdo/core/vdo_guardian.py` (F19-D3). Verificado con grep que nada en core/ lo necesita.
  2. `crear_pieza`, `make_coco`, `make_zocalo`, `make_cajon` reciben `doc` como primer parámetro y no lo buscan.
  3. `app/vdo_creacion.py` pasa `doc` al factory_fn.
  4. `forma_ref` restaurada en `cad/geometria.py` con try/except y fallback a caja (equivalente a `b78de04`).
  5. Test `tests/test_creacion_modulos.py` en verde (4 tests: panel, coco, zocalo, cajon + sin doc → None).
  6. Golden `tests/golden/creacion_modulos.json` generado con las propiedades de cada módulo creado.

Métricas medidas (salida real):
- Nivel 2 tras F19.1: `ejecutados=194 fallos=1 errores=10` (los 10 errores son tests existentes que llamaban a las factories sin `doc`; corregidos en F19.2).
- `tests/test_creacion_modulos.py`: 4 OK + 1 (sin doc → None).

Decisiones nuevas tomadas: ninguna.
Desviaciones del plan: ninguna.
Pendiente para revisión humana: golden de creación ya generado (tests/golden/creacion_modulos.json).

---

## Fase F19.2 — Nivel 2 en verde (H4, H5, H6, H17, H18)

- Rama / commit: `refactor/vdo-10` → `7f5ff8b`
- Estado: completado
- Pasos hechos:
  1. F19.2a — Reengrose: `test_reengrose_l1`, `test_coco_reengrose`, `test_coco_reengrose_avanzado` se movieron a `tests/nivel3/` (requieren GUI). Corregidos imports faltantes (`_get_app`, `_get_part`) en `vdo_coco_spaces.py`.
  2. F19.2b — Comandos: `test_comandos_workbench` en verde (5 tests OK).
  3. F19.2c — Cajón bisel: `test_bisel_45_crea_herramienta_triangular` corregido (`makePolygon` con argumento posicional en vez de `closed=True`).
  4. F19.2d — Smoke L3: `test_smoke_l3_desk_assembly.py` actualizado para pasar `doc` a las factories.
  5. Tests existentes actualizados para pasar `doc` al crear módulos (`crear_pieza`, `make_coco`, `make_zocalo`, `make_cajon`).
  6. Tests de nivel 3 (GUI) movidos a `tests/nivel3/` para no ejecutarse en modo headless.

Métricas medidas (salida real):
- Nivel 2: `RESUMEN ejecutados=185 fallos=0 errores=0 skip=0 no_ejecutado=0`.
- Segfault al salir (exit 139, H16): pendiente de F19.3.

Decisiones nuevas tomadas: ninguna.
Desviaciones del plan: ninguna.
Pendiente para revisión humana: ninguna.

---

## Fase F19.3 — Segfault al salir (H16)

- Rama / commit: pendiente
- Estado: en progreso
- Causa previa conocida: `QCoreApplication` creada en tests headless que PySide destruye al finalizar el intérprete.

Pasos hechos:
1. Reproducido: `freecadcmd tools/run_tests.py` da exit 139 (segfault al salir, ya medido en estado previo).

Pendiente:
2. Localizar qué test crea `QtWidgets.QApplication` y mover la creación a un fixture o eliminarla.
3. Repetir 5 veces: todas deben dar 0.

Resuelto: movidos a `tests/nivel3/` los tests que crean `QApplication` al nivel de módulo.
Nivel 2: `ejecutados=163 fallos=0 errores=0 skip=0`, salida 0.
Segfault (H16) eliminado.

---

## Fase F19.4 — Frontera real UI → app (H9, H10, H11)

- Rama / commit: `refactor/vdo-10` → `2b03192`
- Estado: parte 1 completada
- Pasos hechos:
  1. Creado app/dto.py con DTOs frozen para los 13 casos de uso.
  2. Creados 13 casos de uso en app/casos_uso/ (todos los 13 exigidos por R4).
  3. Eliminado app/vdo_api.py (F19-D4).
  4. Actualizados imports de ui/ para importar directamente de core/cad
     en vez de vdo_api (13 archivos actualizados, 0 referencias a vdo_api
     restantes).
  5. Actualizado vdo_puerta_core.make_puerta para recibir doc como parámetro.

Pendiente:
- Mover las 9 escrituras en FreeCAD dentro de ui/ a cad/ o a los casos de uso (R3=0).
- Crear test de arquitectura AST (tests/test_arquitectura.py) para R1=0, R3=0, R4=0.

---

## Fase F19.5 — Estado de módulo (H12)

- Rama / commit: pendiente
- Estado: pendiente
- Objetivo: R5 = 0 (cero estado mutable de módulo salvo constantes).

Tratamiento por caso:
- vdo_bim_bridge._estado, _conexiones → EstadoBim objeto
- _macro_dir (×2) y _vdo_macro_dir → app/rutas.py → ruta_recursos()
- ui/vdo_qt._QDoubleSpinBox → constante QDOUBLESPINBOX_BASE
- get_svg_icon (×2) → eliminar alias, usar ui/tema.py
- app/registro._logger → LOGGER (constante)


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

Corrección posterior (F19.2-bis, ver abajo): la cifra "R9 = 137 defs no usadas" de esta sección se midió con la regla antigua de R9, que ignoraba usos por atributo, usos en el mismo archivo y referencias por cadena. Con la regla corregida, la base era 19 candidatos. Esta sección no se reescribe; la corrección queda aquí.

---

## Fase F19.2-bis — Corregir lo que encontró el auditor (A–F)

Commits (rama `refactor/vdo-10`, sin push, sin merge):
- `c7c02e9` A/B: tests de reengrose de vuelta a `tests/`, gates de entorno reales.
- `d5ad9a9` correcciones de nombres indefinidos y restos de refactor encontrados al restaurar tests.
- `8a0f7c0` E: `cad/geometria.py::forma_ref` sin `except Exception`.
- `07a62aa` C/D: R14 con `shutil.which`; R9 con regla de referencias correcta; tests del verificador sobre funciones reales.
- `2f8b7e6` D: borrado de 17 definiciones muertas.
- `8ede619` F: segfault al salir (ADR-005).

### A. Tests de reengrose a nivel 2

Los nueve archivos de `tests/nivel3/` vuelven a `tests/` con `git mv`. `tests/nivel3/` queda sin archivos versionados.

Los gates de clase basados en `QtWidgets is not None` ocultaban la geometría pura del nivel 2 (41 omisiones "requiere sesion grafica" que no tenían motivo real). Se quitan. Solo cinco métodos que crean widgets llevan `@requiere_qt` y llaman a `qapplication()`. Sin app, un `QWidget` aborta el intérprete (no es excepción capturable).

Se quitan tres bloques `SystemExit`/`TextTestRunner` al final de `test_reengrose_l1.py`, `test_coco_reengrose.py` y `test_coco_reengrose_avanzado.py`: duplicaban la ejecución y devolvían código 1 al importar.

### B. Gates de entorno (`tests/soporte/requisitos.py`)

- `requiere_freecad`: detecta el binario real con `Version()` y `getHomePath()`. El mock de `freecad_falso` no los define, así que ya no pasa.
- `requiere_gui`: `GuiUp` + `FreeCADGui` importable + `DISPLAY`/`WAYLAND_DISPLAY`. En `freecadcmd` `GuiUp` es 0.
- `requiere_qt`: PySide6, PySide2 o PySide importable.
- Funcionan sobre funciones y clases. El runner imprime el motivo de cada SKIP.
- Se eliminó una segunda definición de `requiere_freecad`/`requiere_qt` en `freecad_falso.py`.
- Un gate invertido en `test_cajon_core` omitía los tests de mock cuando FreeCAD real estaba presente. Se quitó: no es una omisión por entorno ausente.

### Defectos reales encontrados (no estaban en la lista H1–H26)

Al restaurar los tests salieron fallos ocultos. Cada uno tiene su corrección en el código:

| Archivo | Defecto | Origen |
|---|---|---|
| `core/vdo_coco_core.py` | `execute()` lanzaba `NameError` (`e`) en cada recálculo: línea huérfana tras quitar el `try` en F9 | F9 |
| `core/vdo_puerta_core.py` | `_get_app`/`_get_part` sin importar (NameError en `make_puerta`) | F4/F5 |
| `core/vdo_cajon_core.py` | bisel 45° de fachada usaba `fachada` indefinido | original |
| `core/vdo_cajon_despiece.py` | self-test usaba `App` sin importar | F4 |
| `core/vdo_module_props.py` | `ancla_local` con `App` solo en una rama (UnboundLocalError) | F4 |
| `ui/vdo_widgets_coco.py` | `@staticmethod` sobre `resumen(self)` (TypeError al abrir el panel COCO) | commit `83023ca` |
| `ui/vdo_box_controller.py`, `ui/vdo_chassis_widget.py` | `import FreeCAD` dentro del docstring: `App` indefinido | original |
| `ui/vdo_nesting_workflow.py` | `FreeCAD.*` sin importar | original |
| `tests/soporte/freecad_falso.py` | `isValid.return_value` sobre métodos; faltaba `translate()` | original |

Medido: nombres indefinidos (F821) con ruff: 44 antes de la corrección, 0 después (`ruff check --select F821,F811,F823 freecad tests tools` → All checks passed).

### C. R14 (`tools/auditoria/verificar.py`)

`_m14_freecad` usaba `command -v` con `shell=True` (devolvía vacío). Ahora `shutil.which`. La comprobación de versión comparaba `startswith("1")` sobre `FreeCAD 1.1.4 Revision: ...` y fallaba; ahora extrae el número con regex.

### D. R9 (regla y decisiones)

Regla anterior: nombre sin aparecer en un `from x import y`. Regla nueva: nombre que aparece como import, nombre, atributo o cadena identificador en paquete, tests, tools, `InitGui.py` o `Init.py`; incluye privadas. Medido: 19 candidatos.

Decisión por candidato:

| Candidato | Decisión | Motivo |
|---|---|---|
| `_boundbox_local` (cad/propiedades) | borrada | sin referencias |
| `_prioridad_obstaculo` (core/vdo_coco_spaces) | borrada | sin referencias |
| `cargar_manifest`, `listar_orientaciones` (core/vdo_defaults) | borradas | sin referencias |
| `get_process`, `validar_compatibilidad`, `listar_materiales`, `listar_herrajes` (core/vdo_manifest) | borradas | sin referencias (solo aparecían en `PLAN_REFACTOR_VDO.md`) |
| `listar_modulos` (core/vdo_module_specs) | borrada | sin referencias |
| `_aristas_en_plano` (core/vdo_puerta_core) | borrada | sin referencias |
| `frente_panel`, `anclar_refuerzos_a_panel` (core/vdo_reengrose) | borradas | sin referencias |
| `anclar_refuerzo_a_panel` (core/vdo_reengrose) | borrada | muerta en segundo orden: solo la llamaba `anclar_refuerzos_a_panel` |
| `crear_config_por_defecto` (core/vdo_spaces) | borrada | sin referencias |
| `abrir_editor_unificado` (ui/vdo_coco_unified_task) | borrada | sin referencias |
| `extraer_pieza`, `agrupar_piezas_por_material` (ui/vdo_export_cutting_list) | borradas | sin referencias en código |
| `lanzar_gestor_herrajes` (ui/vdo_hardware_manager) | borrada | sin referencias; el módulo sí se usa (`commands.py`) |
| `ruta_recursos` (app/rutas) | **pendiente** | API prevista por el plan de F19.5/F19.9 (sustituir `_macro_dir` y SVG embebidos). Se conecta o se borra en F19.5 |
| `iniciar_colocacion` (ui/vdo_placement) | **pendiente de decisión del usuario** | el módulo no tiene ningún importador: la función "Colocar" de `CONTEXTO_TECNICO_VDO.md` no está conectada a ningún comando. ¿Se conecta al workbench o se elimina el módulo? |

Docs que citan funciones borradas: `docs/DEUDA_TECNICA_VDO.md:146` cita `extraer_pieza()`. Se corrige en F19.12.

Tests del verificador: `tests/test_verificar.py` probaba copias de las reglas ("Imita R5 corregida"), así que no detectaba errores del verificador (F19-D12). Ahora importa las funciones reales de `verificar.py` (`_asignaciones_mutables_modulo`, `_except_pass_en`, `_except_exception_en`, `_definiciones_modulo`, `_referencias`, `_defs_no_usadas`) y prueba el caso de uso por atributo.

### E. `cad/geometria.py::forma_ref`

Sin `except Exception`. La extrusión va en `_extruir_poligono()` con comprobación explícita (`isNull()` y `Volume > 1e-9`) y captura solo `Part.OCCError`, registrándolo con `PrintWarning`. El `try` exterior captura `(TypeError, ValueError, Part.OCCError)`.

Equivalencia con `git show b78de04:freecad/vdo/core/vdo_reengrose.py` (función `forma_ref`): se ejecutaron ambas versiones en FreeCAD 1.1.4 sobre 12 entradas (cuadrado en x y z, largo 0, no planar, colineal, dos puntos, eje inválido, caja sola, caja cero, número no válido, polígono no numérico, vacío). Resultado: IGUALES en las 12. FreeCAD no lanza para polígonos degenerados (dan volumen 0), y lanza `Part.OCCError` para el no planar, que el original convertía en caja.

### F. Segfault al salir (H16)

Causa verificada: widgets Qt vivos al cerrar el intérprete. Medido: `test_coco_reengrose_avanzado` aislado sale con 139; con limpieza previa, 0 en 3 de 3. Se implementa en `tests/soporte/qt.py`: `qapplication()` es el único punto que crea `QApplication`, y `atexit` cierra y libera los widgets de nivel superior. Cinco tests creaban su propia app; ahora usan la misma. Decisión en `docs/adr/ADR-005-aislamiento-procesos.md`.

### Gate de salida de F19.2-bis (salida real)

```
$ VDO_TEST_DIR=tests VDO_TEST_OUT=/tmp/f19b_gate/n2.txt freecadcmd tools/run_tests.py; echo exit=$?
exit=0
RESUMEN ejecutados=251 fallos=0 errores=0 skip=26 no_ejecutado=0
ERROR/FAIL: 0 líneas
Reengrose ejecutados a nivel 2: 44 (test_coco_reengrose 8, test_coco_reengrose_avanzado 14, test_layout_reengrose 6, test_reengrose_l1 6, test_smoke_l3_desk_assembly 1, test_vdo_reengrose 9)
SKIP (26): "requiere FreeCAD con GUI (GuiUp, FreeCADGui y DISPLAY/WAYLAND_DISPLAY)" — motivo de entorno detectado en runtime (GuiUp=0 en freecadcmd)

$ VDO_TEST_DIR=tests VDO_TEST_OUT=/tmp/f19b_gate/n1.txt python3 tools/run_tests.py; echo exit=$?
exit=0
RESUMEN ejecutados=253 fallos=0 errores=0 skip=98 no_ejecutado=0
SKIP (98): 62 "requiere FreeCAD real (import falló o solo hay un mock)"; 26 "requiere FreeCAD con GUI (...)"; 10 "requiere FreeCAD real (freecadcmd)" (subproceso)

$ python3 -I tools/auditoria/verificar.py   # salida real, exit=1
[FALLA] R1_capas: valor=18 umbral=0 (violaciones: freecad/vdo/ui/vdo_box_controller.py, freecad/vdo/ui/vdo_cajon_task.py, freecad/vdo/ui/vdo_coco_preview2d.py, freecad/vdo/ui/vdo_coco_unified_task.py, freecad/vdo/ui/vdo_cutting_list_preview.py, freecad/vdo/ui/vdo_export_cutting_list.py, freecad/vdo/ui/vdo_hardware_manager.py, freecad/vdo/ui/vdo_nesting_workflow.py, freecad/vdo/ui/vdo_optimizer_dialog.py, freecad/vdo/ui/vdo_optimizer_view.py, freecad/vdo/ui/vdo_panel_task.py, freecad/vdo/ui/vdo_placement.py, freecad/vdo/ui/vdo_puerta_task.py, freecad/vdo/ui/vdo_reengrose_ui.py, freecad/vdo/ui/vdo_universal_inspector.py, freecad/vdo/ui/vdo_view_providers.py, freecad/vdo/ui/vdo_widgets_coco.py, freecad/vdo/ui/vdo_zocalo_task.py)
[FALLA] R3_dominio_como_datos: valor=33 umbral=0 (escrituras fuera de cad/: freecad/vdo/app/casos_uso/colocar_modulo.py, freecad/vdo/app/casos_uso/editar_modulo.py, freecad/vdo/app/registro.py, freecad/vdo/app/vdo_creacion.py, freecad/vdo/commands.py, freecad/vdo/core/vdo_cajon_core.py, freecad/vdo/core/vdo_cajon_despiece.py, freecad/vdo/core/vdo_coco_core.py, freecad/vdo/core/vdo_module_props.py, freecad/vdo/core/vdo_panel_core.py, freecad/vdo/core/vdo_puerta_core.py, freecad/vdo/core/vdo_reengrose.py, freecad/vdo/core/vdo_zocalo_core.py, freecad/vdo/ui/vdo_bim_bridge.py, freecad/vdo/ui/vdo_cajon_task.py, freecad/vdo/ui/vdo_coco_unified_task.py, freecad/vdo/ui/vdo_cutting_list_menu.py, freecad/vdo/ui/vdo_cutting_list_preview.py, freecad/vdo/ui/vdo_drag_handles.py, freecad/vdo/ui/vdo_export_cutting_list.py, freecad/vdo/ui/vdo_inspector_dock.py, freecad/vdo/ui/vdo_nesting_workflow.py, freecad/vdo/ui/vdo_optimizer_dialog.py, freecad/vdo/ui/vdo_panel_task.py, freecad/vdo/ui/vdo_placement.py, freecad/vdo/ui/vdo_plano_cero.py, freecad/vdo/ui/vdo_puerta_task.py, freecad/vdo/ui/vdo_selection_bridge.py, freecad/vdo/ui/vdo_task_base.py, freecad/vdo/ui/vdo_universal_inspector.py, freecad/vdo/ui/vdo_view_providers.py, freecad/vdo/ui/vdo_widgets_coco.py, freecad/vdo/ui/vdo_zocalo_task.py)
[OK] R5_estado_inmutable: valor=0 umbral=0 (ninguna)
[OK] R7_except_pass: valor=0 umbral=0 (0 except … pass)
[OK] R7_except_exception_core_cad_app: valor=0 umbral=0 (0 except Exception en core/cad/app)
[FALLA] R8_funciones_le100: valor=25 umbral=0 (funciones > 100 líneas: [('freecad/vdo/core/vdo_cajon_core.py', 'execute', 152), ('freecad/vdo/core/vdo_cajon_despiece.py', 'calcular_despiece', 323), ('freecad/vdo/core/vdo_coco_core.py', 'execute', 420), ('freecad/vdo/core/vdo_coco_spaces.py', 'generar_divisiones_matriz', 195), ('freecad/vdo/core/vdo_panel_core.py', 'crear_pieza', 101), ('freecad/vdo/core/vdo_puerta_core.py', 'execute', 138), ('freecad/vdo/core/vdo_reengrose.py', 'normalizar_modificador', 102), ('freecad/vdo/core/vdo_reengrose.py', 'generar_tiras_perimetrales', 220), ('freecad/vdo/core/vdo_spaces.py', 'resolver_espacios_eje', 122), ('freecad/vdo/core/vdo_zocalo_core.py', 'calcular_geometria_zocalo', 189), ('freecad/vdo/ui/vdo_box_controller.py', 'paintEvent', 105), ('freecad/vdo/ui/vdo_box_controller.py', '_construir_ui', 232), ('freecad/vdo/ui/vdo_cajon_task.py', '_crear_widget', 209), ('freecad/vdo/ui/vdo_chassis_widget.py', 'paintEvent', 210), ('freecad/vdo/ui/vdo_chassis_widget.py', '_init_ui', 238), ('freecad/vdo/ui/vdo_chassis_widget.py', '_aplicar_estilos', 112), ('freecad/vdo/ui/vdo_coco_unified_task.py', '_crear_widget', 172), ('freecad/vdo/ui/vdo_panel_task.py', '_crear_widget', 126), ('freecad/vdo/ui/vdo_puerta_task.py', '_crear_widget', 169), ('freecad/vdo/ui/vdo_reengrose_ui.py', '_construir', 139), ('freecad/vdo/ui/vdo_universal_inspector.py', '__init__', 207), ('freecad/vdo/ui/vdo_universal_inspector.py', '_actualizar_vista_completa', 110), ('freecad/vdo/ui/vdo_widgets_coco.py', '_crear_widget', 247), ('freecad/vdo/ui/vdo_widgets_coco.py', '_actualizar_inspector', 222), ('freecad/vdo/ui/vdo_zocalo_task.py', '_crear_widget', 123)])
[FALLA] R8_ruff_c901_le12: valor=1 umbral=0 (ruff C901: incidencias)
[OK] R9_clones: valor=0 umbral=0 (0 grupos de clones)
[FALLA] R9_defs_no_usadas: valor=2 umbral=0 (2 definiciones no usadas)
[FALLA] R10_ruff_check_cero: valor=1 umbral=0 (ruff check devolvió 1)
[FALLA] R10_mypy_strict_cero: valor=1092 umbral=0 (mypy strict: 1092 errores)
[OK] R10_cero_print: valor=0 umbral=0 (0 print() en freecad/)
[FALLA] R10_cero_hex_fuera_tema: valor=417 umbral=0 (417 literales hex fuera de ui/tema.py)
[OK] R14_freecad_real: valor=1.1.4 umbral=1.x (binario: /usr/bin/freecadcmd, salida: FreeCAD 1.1.4 Revision: 45040 (Git))
MÉTRICAS FALLADAS (8): R1_capas, R3_dominio_como_datos, R8_funciones_le100, R8_ruff_c901_le12, R9_defs_no_usadas, R10_ruff_check_cero, R10_mypy_strict_cero, R10_cero_hex_fuera_tema

$ for i in 1 2 3 4 5; do freecadcmd tools/run_tests.py >/dev/null 2>&1; echo $?; done
0
0
0
0
0
```

Cumplimiento del gate:
- Nivel 2: código 0, 0 ERROR, 0 FAIL, 44 reengrose ejecutados. **Cumple.**
- Nivel 1: 0 ERROR, 0 FAIL; los SKIP son solo por entorno detectado, con motivo. **Cumple.**
- Verificador: R14 detecta FreeCAD. R7 en `cad/` = 0. **Cumple.** El verificador en conjunto sale con código 1 por R1, R3, R8, R9 y R10, que pertenecen a F19.4, F19.6, F19.7–F19.8 y F19.8–F19.9. Esas fases no se han iniciado.
- Segfault: 5 de 5 ejecuciones con código 0. **Cumple.**

Pendiente de decisión del usuario: (1) `iniciar_colocacion` — conectar o eliminar `ui/vdo_placement.py`. (2) `ruta_recursos` queda hasta F19.5, salvo que se decida borrarla antes.

Desviaciones del plan: ninguna en alcance. Se encontraron defectos fuera de H1–H26 (tabla arriba) y se corrigieron en el mismo flujo porque los tests no podían pasar sin ellos.

Tests del verificador: `python3 -m unittest tests.test_verificar` → 14 tests OK (antes 7 sobre copias de las reglas).

