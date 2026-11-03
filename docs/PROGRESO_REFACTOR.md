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

## Fase F19.2-ter — Medidor honesto (corrección de F19.2-bis) y primer contacto con F19.4

Commits (rama `refactor/vdo-10`, sin push, sin merge):
- `34e6d51` deuda de tests: 12 `except Exception` del smoke L3 sustituidos por `_ERRORES_ESPERADOS`; guardas de import a `ImportError`.
- `c7ad8fd` `tests/test_arquitectura.py` y `tools/run_tests.py` (ver abajo).
- `7f9f9a2` `tools/auditoria/verificar.py` y `pyproject.toml` (ver abajo).

### Correcciones a cifras y afirmaciones anteriores

| Afirmación anterior | Medido ahora | Origen del error |
|---|---|---|
| F19.2-bis: "nivel 1 y nivel 2 con 0 fallos; verificador R1–R3 OK en arquitectura" | Nivel 2 y nivel 1: 3 FALLO cada uno (`test_arquitectura`) | `test_arquitectura.py` tenía `ROOT` tres niveles arriba (`/home/airhon/Proyectos`): escaneaba 0 archivos y pasaba en vacío. Las 5 pruebas eran falsos verdes. |
| F19.2-bis: `run_tests.py` "exit=0" como gate | `run_tests.py` salía con 0 aunque hubiera fallos | El runner nunca devolvía código de error. Corregido: devuelve 1 si hay FALLO, ERROR o NO_EJECUTADO. |
| F19.8: "ruff check hoy falla con 1 error" | 273 incidencias antes de esta subfase; 260 ahora | `verificar.py` registraba el código de salida de ruff (1) como si fuera el número de incidencias. |
| R8 C901 "valor=1 (incidencias)" | 28 funciones de `freecad/` con complejidad > 12 | Mismo error de medición. Además `--config max-complexity=12` no es válido en ruff: el umbral va en `pyproject.toml`. |
| `_grep_count` y `_grep_files` | — | Devolvían 0 ante cualquier excepción (si falla `rg`, R10 daría verde). Ahora solo rc=1 es "cero coincidencias". |

Nota: `tests/test_arquitectura.py` ahora falla si una capa no existe o no tiene `.py` (ya no puede pasar en vacío).

### Estado medido de F19.4 (lo que el test de arquitectura ya ve)

- `core/` importa `cad/`: 4 módulos (`vdo_coco_core`, `vdo_coco_spaces`, `vdo_module_props`, `vdo_panel_core`). Causa: `forma_ref` (`cad/geometria`) y `add_common_props` (`cad/propiedades`, reexportado en `vdo_module_props` línea 83 con `noqa: F401`).
- `ui/` escribe en FreeCAD: 20 módulos. Test `test_ui_no_escritura_freecad`.
- `ui/` importa `core`/`cad`: 18 módulos. Test `test_ui_no_importa_core_cad_app_api`.
- `core/` escribe en el documento: `make_coco`, `make_panel`, `make_zocalo`, `make_cajon`, `make_puerta` llaman a `addObject`/`recompute` y asignan propiedades. Es la causa raíz de los dos primeros puntos y la razón por la que F19.4 no puede cerrarse por bloques pequeños: hay que separar, función a función, el cálculo puro (que queda en `core/`) de la escritura (que pasa a `cad/`), tal como pide F4.8–F4.13. Tamaño medido: 2.793 líneas en los 7 módulos y 145 líneas de importadores fuera de ellos.
- `app/casos_uso/` tiene los 13 archivos (R4 OK), pero son esqueletos de 12–36 líneas, y la UI no los llama. `crear_coco` llama a `make_coco` de core, así que app→core escribe en el documento.

Decisión tomada (no requiere al usuario): la separación cálculo/escritura se hace por módulo, en commits separados, con nivel 2 en verde tras cada uno. El orden es el de F4: `module_props` (quitar reexport), `coco`, `panel`, `zocalo`, `cajon`, `puerta`.

### Gate medido de esta subfase

```
$ VDO_TEST_DIR=tests VDO_TEST_OUT=/tmp/f19c/n2e.txt freecadcmd tools/run_tests.py; echo exit=$?
exit=1
RESUMEN ejecutados=251 fallos=3 errores=0 skip=26 no_ejecutado=0
FALLO test_arquitectura.CapasTests.test_core_no_importa_app_ui_cad
FALLO test_arquitectura.CapasTests.test_ui_no_escritura_freecad
FALLO test_arquitectura.CapasTests.test_ui_no_importa_core_cad_app_api

$ VDO_TEST_DIR=tests VDO_TEST_OUT=/tmp/f19c/n1e.txt python3 tools/run_tests.py; echo exit=$?
exit=1
RESUMEN ejecutados=253 fallos=3 errores=0 skip=98 no_ejecutado=0
(mismos 3 FALLO)

$ python3 -m unittest tests.test_verificar
Ran 14 tests in 0.001s
OK

$ .venv/bin/ruff check freecad tests tools
Found 260 errors.
[*] 12 fixable with `--fix`.

$ .venv/bin/mypy freecad/vdo/core freecad/vdo/app freecad/vdo/cad
Found 1092 errors in 46 files (checked 51 source files)

$ python3 -I tools/auditoria/verificar.py; echo exit=$?
=== VDO — verificación de métricas §2 ===
[FALLA] R1_capas: valor=18 umbral=0 (violaciones: freecad/vdo/ui/vdo_box_controller.py, freecad/vdo/ui/vdo_cajon_task.py, freecad/vdo/ui/vdo_coco_preview2d.py, freecad/vdo/ui/vdo_coco_unified_task.py, freecad/vdo/ui/vdo_cutting_list_preview.py, freecad/vdo/ui/vdo_export_cutting_list.py, freecad/vdo/ui/vdo_hardware_manager.py, freecad/vdo/ui/vdo_nesting_workflow.py, freecad/vdo/ui/vdo_optimizer_dialog.py, freecad/vdo/ui/vdo_optimizer_view.py, freecad/vdo/ui/vdo_panel_task.py, freecad/vdo/ui/vdo_placement.py, freecad/vdo/ui/vdo_puerta_task.py, freecad/vdo/ui/vdo_reengrose_ui.py, freecad/vdo/ui/vdo_universal_inspector.py, freecad/vdo/ui/vdo_view_providers.py, freecad/vdo/ui/vdo_widgets_coco.py, freecad/vdo/ui/vdo_zocalo_task.py)
[OK] R2_agnosticismo_core: valor=0 umbral=0 (ninguno)
[FALLA] R3_dominio_como_datos: valor=33 umbral=0 (escrituras fuera de cad/: freecad/vdo/app/casos_uso/colocar_modulo.py, freecad/vdo/app/casos_uso/editar_modulo.py, freecad/vdo/app/registro.py, freecad/vdo/app/vdo_creacion.py, freecad/vdo/commands.py, freecad/vdo/core/vdo_cajon_core.py, freecad/vdo/core/vdo_cajon_despiece.py, freecad/vdo/core/vdo_coco_core.py, freecad/vdo/core/vdo_module_props.py, freecad/vdo/core/vdo_panel_core.py, freecad/vdo/core/vdo_puerta_core.py, freecad/vdo/core/vdo_reengrose.py, freecad/vdo/core/vdo_zocalo_core.py, freecad/vdo/ui/vdo_bim_bridge.py, freecad/vdo/ui/vdo_cajon_task.py, freecad/vdo/ui/vdo_coco_unified_task.py, freecad/vdo/ui/vdo_cutting_list_menu.py, freecad/vdo/ui/vdo_cutting_list_preview.py, freecad/vdo/ui/vdo_drag_handles.py, freecad/vdo/ui/vdo_export_cutting_list.py, freecad/vdo/ui/vdo_inspector_dock.py, freecad/vdo/ui/vdo_nesting_workflow.py, freecad/vdo/ui/vdo_optimizer_dialog.py, freecad/vdo/ui/vdo_panel_task.py, freecad/vdo/ui/vdo_placement.py, freecad/vdo/ui/vdo_plano_cero.py, freecad/vdo/ui/vdo_puerta_task.py, freecad/vdo/ui/vdo_selection_bridge.py, freecad/vdo/ui/vdo_task_base.py, freecad/vdo/ui/vdo_universal_inspector.py, freecad/vdo/ui/vdo_view_providers.py, freecad/vdo/ui/vdo_widgets_coco.py, freecad/vdo/ui/vdo_zocalo_task.py)
[OK] R4_orquestacion_app: valor=0 umbral=0 (todos presentes)
[OK] R5_estado_inmutable: valor=0 umbral=0 (ninguna)
[OK] R6_paneles_accept_le15: valor=0 umbral=0 (todos ≤ 15)
[OK] R7_except_pass: valor=0 umbral=0 (0 except … pass)
[OK] R7_except_exception_core_cad_app: valor=0 umbral=0 (0 except Exception en core/cad/app)
[FALLA] R8_funciones_le100: valor=25 umbral=0 (funciones > 100 líneas: [('freecad/vdo/core/vdo_cajon_core.py', 'execute', 152), ('freecad/vdo/core/vdo_cajon_despiece.py', 'calcular_despiece', 323), ('freecad/vdo/core/vdo_coco_core.py', 'execute', 420), ('freecad/vdo/core/vdo_coco_spaces.py', 'generar_divisiones_matriz', 195), ('freecad/vdo/core/vdo_panel_core.py', 'crear_pieza', 101), ('freecad/vdo/core/vdo_puerta_core.py', 'execute', 138), ('freecad/vdo/core/vdo_reengrose.py', 'normalizar_modificador', 102), ('freecad/vdo/core/vdo_reengrose.py', 'generar_tiras_perimetrales', 220), ('freecad/vdo/core/vdo_spaces.py', 'resolver_espacios_eje', 122), ('freecad/vdo/core/vdo_zocalo_core.py', 'calcular_geometria_zocalo', 189), ('freecad/vdo/ui/vdo_box_controller.py', 'paintEvent', 105), ('freecad/vdo/ui/vdo_box_controller.py', '_construir_ui', 232), ('freecad/vdo/ui/vdo_cajon_task.py', '_crear_widget', 209), ('freecad/vdo/ui/vdo_chassis_widget.py', 'paintEvent', 210), ('freecad/vdo/ui/vdo_chassis_widget.py', '_init_ui', 238), ('freecad/vdo/ui/vdo_chassis_widget.py', '_aplicar_estilos', 112), ('freecad/vdo/ui/vdo_coco_unified_task.py', '_crear_widget', 172), ('freecad/vdo/ui/vdo_panel_task.py', '_crear_widget', 126), ('freecad/vdo/ui/vdo_puerta_task.py', '_crear_widget', 169), ('freecad/vdo/ui/vdo_reengrose_ui.py', '_construir', 139), ('freecad/vdo/ui/vdo_universal_inspector.py', '__init__', 207), ('freecad/vdo/ui/vdo_universal_inspector.py', '_actualizar_vista_completa', 110), ('freecad/vdo/ui/vdo_widgets_coco.py', '_crear_widget', 247), ('freecad/vdo/ui/vdo_widgets_coco.py', '_actualizar_inspector', 222), ('freecad/vdo/ui/vdo_zocalo_task.py', '_crear_widget', 123)])
[FALLA] R8_ruff_c901_le12: valor=28 umbral=0 (ruff C901 (max 12): 28 incidencias)
[OK] R9_clones: valor=0 umbral=0 (0 grupos de clones)
[FALLA] R9_defs_no_usadas: valor=2 umbral=0 (2 definiciones no usadas)
[FALLA] R10_ruff_check_cero: valor=260 umbral=0 (ruff check: 260 incidencias)
[FALLA] R10_mypy_strict_cero: valor=1092 umbral=0 (mypy strict: 1092 errores)
[OK] R10_cero_print: valor=0 umbral=0 (0 print() en freecad/)
[FALLA] R10_cero_hex_fuera_tema: valor=417 umbral=0 (417 literales hex fuera de ui/tema.py)
[OK] R11_golden_masters: valor=9 umbral=>=1 (9 golden.json)
[OK] R11_suite_nivel1_estructura: valor=0 umbral=0 (tests/ existe)
[OK] R12_documentacion: valor=0 umbral=0 (ARQUITECTURA=True, ADRs=4, DEUDA=True, GLOSARIO=True)
[OK] R14_freecad_real: valor=1.1.4 umbral=1.x (binario: /usr/bin/freecadcmd, salida: FreeCAD 1.1.4 Revision: 45040 (Git))

MÉTRICAS FALLADAS (8): R1_capas, R3_dominio_como_datos, R8_funciones_le100, R8_ruff_c901_le12, R9_defs_no_usadas, R10_ruff_check_cero, R10_mypy_strict_cero, R10_cero_hex_fuera_tema
exit=1
```

Estado: F19.2-ter cumple su objetivo (medidor honesto). F19 no está cerrada: R1, R3, R8, R9, R10 siguen en FALLA, y la suite de nivel 1 y 2 tiene 3 FALLO reales que son trabajo de F19.4.

Pendiente de decisión humana (sin cambios desde F19.2-bis): `iniciar_colocacion` (`ui/vdo_placement.py`): conectar al workbench o eliminar; `ruta_recursos` (`app/rutas.py`) se decide en F19.5.

## Fase F19.2-ter (sesión 2) — Colocación, segfault y medición

Commits (rama `refactor/vdo-10`, sin push, sin merge, sin etiqueta de cierre):
- `abf59b1` paso 1: colocación restaurada en el flujo de creación y dos defectos de creación.
- `6bab241` paso 2: segfault al salir corregido en el runner (ADR-005 actualizado).
- `b2583a6` paso 3: duplicado de rotación eliminado y tipado de las funciones nuevas.

### Paso 1 — Colocación (regresión de F5)

Qué estaba roto (medido, no supuesto):
- `b78de04` abría el panel y, al aceptar, llamaba a `iniciar_colocacion` a través de `core/vdo_ui_registry`. F5 quitó el registro y `ui/vdo_registro.registrar_piezas` es un no-op desde entonces. Resultado: el módulo se creaba oculto en el origen, sin panel y sin colocación.
- `ui/vdo_placement.py` no se podía importar: pedía `rotacion_z` a `core/vdo_module_props`, y esa función había pasado a `cad/propiedades` en F19.1.
- `panel.puerta` no se podía abrir: `ImportError` de `SISTEMAS_APERTURA` en `vdo_facade_contract` (se había movido a `vdo_puerta_despiece`).
- `make_coco`, `crear_pieza` y `make_zocalo` fallaban con `AttributeError` con rotación distinta de cero (`VDO_MOD.rotacion_z` no existe). Probe: `AttributeError module 'freecad.vdo.core.vdo_module_props' has no attribute 'rotacion_z'`.

Qué cambió:
- `app/vdo_creacion.crear_modulo_interactivo(..., *, abrir_panel=None, colocar=None)`: las dos funciones de interfaz llegan por parámetro. `app/` no importa `ui/`. Sin ellas confirma en el origen.
- `ui/vdo_interfaz.py` (nuevo): `abrir_panel` (mapa `panel.* -> clase TaskPanel`, el mismo de `b78de04`) y `colocar` (`iniciar_colocacion`).
- `commands.py`: inyecta la interfaz solo si hay GUI (`_gui_activa()`).
- `cad/colocacion.py` (nuevo): `leer_rotacion`, `ancla_local`, `preparar_colocacion`, `aplicar_colocacion`. Movidos desde `core/vdo_module_props.py` (que pierde 43 líneas).
- `app/casos_uso/colocar_modulo.py`: `preparar_colocacion` y `colocar_en_punto` como API para la UI.
- `cad/propiedades.ocultar_vista`: oculta la vista. Tolera objetos sin `ViewObject`.

Tests nuevos en `tests/test_creacion_colocacion.py` (nivel 2, 8 tests): flujo aceptar, aceptar dos veces, cancelar, colocación real sin GUI (cancela y devuelve `False`), rotación de coco/panel/zócalo, y resolución de la clase de panel para todas las specs.

Lo que NO está verificado: la colocación con clic en GUI (Snapper o fallback Coin3D). Solo se ejecuta la rama sin GUI. Requiere sesión gráfica y revisión humana (F19.11).

Desviación de la prueba: `HasPendingTransaction` es siempre `False` en `freecadcmd` (medido con `/tmp/f19d/probe_tx.py`), así que el test no afirma sobre él.

### Paso 2 — Segfault al salir

Corrección de F19.2-bis: el registro decía "5 de 5 ejecuciones con código 0". El código era 0, pero el log contenía `Program received signal SIGSEGV` en cada ejecución (la señal sale en el backtrace de shiboken, durante la finalización). El segfault no estaba resuelto.

Localización (medida):
- Cada módulo de test que usa Qt, en su propio proceso: `rc=0`, sin SIGSEGV.
- Todos los módulos en un proceso con un cargador propio que termina normalmente: `rc=0`, sin SIGSEGV.
- El mismo cargador con `sys.exit(0)` o `sys.exit(1)` al final: SIGSEGV.
- Disparador: `tools/run_tests.py` terminaba con `sys.exit(main())`, introducido en `c7ad8fd` (F19.2-ter, paso anterior de esta sesión). El segfault del registro original venía de otra causa (ADR-005), pero la salida con `sys.exit` lo reproducía igual.

Cambio: el runner escribe el informe, vacía stdout/stderr y termina con `os._exit(codigo)`. El código sigue siendo el de los resultados. Nada se excluye.

Resultado de las 5 ejecuciones de nivel 2 con el comando del prompt (`VDO_TEST_DIR=tests VDO_TEST_OUT=/tmp/x.txt freecadcmd tools/run_tests.py; echo $?`):
```
1: RESUMEN ejecutados=260 fallos=3 errores=0 skip=26 no_ejecutado=0
2: RESUMEN ejecutados=260 fallos=3 errores=0 skip=26 no_ejecutado=0
3: RESUMEN ejecutados=260 fallos=3 errores=0 skip=26 no_ejecutado=0
4: RESUMEN ejecutados=260 fallos=3 errores=0 skip=26 no_ejecutado=0
5: RESUMEN ejecutados=260 fallos=3 errores=0 skip=26 no_ejecutado=0
```
Código 1 en las cinco por los 3 FALLO de `test_arquitectura` (F19.4). Sin SIGSEGV en las cinco (`grep -c SIGSEGV` = 0).

### Paso 3 — Duplicado y tipado

- `_rotacion_z` estaba copiado en tres módulos de core. R9_clones pasó a 1. Ahora un solo `rotacion_z` en `core/vdo_helpers`. R9_clones = 0.
- Anotaciones de tipo en las funciones nuevas. Medido: mypy strict en `core/ app/ cad/` pasó de 1108 (tras el paso 1) a 1081. La línea base de la sesión era 1092.
- La docstring de `rotacion_z` decía `App.Rotation`: R3 la contaba como escritura de FreeCAD. Reescrita.

### Medición literal (paso 4)

Nivel 1 (`VDO_TEST_DIR=tests VDO_TEST_OUT=/tmp/x.txt python3 tools/run_tests.py; echo exit=$?`):
```
SKIP setUpClass (test_comandos_workbench.ComandosFreeCADTests) :: requiere FreeCAD real (freecadcmd)
SKIP setUpClass (test_headless_core.HeadlessCoreTests) :: requiere FreeCAD real (freecadcmd)
OK test_arquitectura.CapasTests.test_app_no_importa_ui
OK test_arquitectura.CapasTests.test_cad_no_importa_ui_app
FALLO test_arquitectura.CapasTests.test_core_no_importa_app_ui_cad :: -  'freecad/vdo/core/vdo_panel_core.py'] : core/ importa app/ui/cad: ['freecad/vdo/core/vdo_coco_core.py', 'freecad/vdo/core/vdo_coco_spaces.py', 'freecad/vdo/core/vdo_module_props.py', 'freecad/vdo/core/vdo_panel_core.py']
FALLO test_arquitectura.CapasTests.test_ui_no_escritura_freecad :: Diff is 857 characters long. Set self.maxDiff to None to see it. : ui/ escribe en FreeCAD: ['freecad/vdo/ui/vdo_bim_bridge.py', 'freecad/vdo/ui/vdo_cajon_task.py', 'freecad/vdo/ui/vdo_coco_unified_task.py', 'freecad/vdo/ui/vdo_cutting_list_menu.py', 'freecad/vdo/ui/vdo_cutting_list_preview.py', 'fre
FALLO test_arquitectura.CapasTests.test_ui_no_importa_core_cad_app_api :: Diff is 743 characters long. Set self.maxDiff to None to see it. : ui/ importa core/cad/app.vdo_api: ['freecad/vdo/ui/vdo_box_controller.py', 'freecad/vdo/ui/vdo_cajon_task.py', 'freecad/vdo/ui/vdo_coco_preview2d.py', 'freecad/vdo/ui/vdo_coco_unified_task.py', 'freecad/vdo/ui/vdo_cutting_list_previe
OK test_build_zip.TestBuildZip.test_leer_version
OK test_build_zip.TestBuildZip.test_zip_contiene_solo_archivos_permitidos
OK test_cajon_core.TestBooleanLogicMocked.test_aplicar_corte_devuelve_original_si_falla
OK test_cajon_core.TestBooleanLogicMocked.test_bisel_45_crea_herramienta_triangular
OK test_cajon_core.TestBooleanLogicMocked.test_notch_reduce_volumen
OK test_cajon_core.TestBooleanLogicMocked.test_pin_hole_reduce_volumen
OK test_cajon_core.TestBooleanLogicMocked.test_ranura_piso_reduce_volumen
OK test_cajon_core.TestCoordenadasCalculadas.test_fachada_con_gola
OK test_cajon_core.TestCoordenadasCalculadas.test_piso_en_ranura_telescopica
OK test_cajon_core.TestCoordenadasCalculadas.test_posiciones_laterales
OK test_cajon_core.TestDespieceTipologias.test_listar_marcas_incluye_nuevas
OK test_cajon_core.TestDespieceTipologias.test_metalica_sin_laterales
OK test_cajon_core.TestDespieceTipologias.test_oculta_blum_tandem
OK test_cajon_core.TestDespieceTipologias.test_oculta_generica
OK test_cajon_core.TestDespieceTipologias.test_telescopica
OK test_cajon_core.TestFacadeContractIntegracion.test_cantos_por_sistema_apertura
OK test_cajon_core.TestFacadeContractIntegracion.test_gola_descuenta_35mm_en_alto
OK test_cajon_core.TestFacadeContractIntegracion.test_inglete_45_conserva_altura
OK test_cajon_core.TestFacadeContractIntegracion.test_push_open_conserva_altura
OK test_cajon_core.TestFacadeContractIntegracion.test_tirador_conserva_altura
OK test_cajon_core.TestHardwareHubIntegracion.test_resolve_blum_tandem_desde_manifest
OK test_cajon_core.TestHardwareHubIntegracion.test_resolve_generica
OK test_cajon_core.TestHardwareHubIntegracion.test_resolve_inexistente_lanza_keyerror
OK test_cajon_core.TestHardwareHubIntegracion.test_resolve_sku_directo
OK test_cajon_core.TestHardwareHubIntegracion.test_resolve_telescopica
OK test_capas_arquitectura.CapasTests.test_core_no_importa_interfaz_ni_qt
OK test_capas_arquitectura.CapasTests.test_registro_de_ui_no_esta_en_core
OK test_cli_optimizador.TestOptimizadorCLI.test_parse_board_con_decimales
OK test_cli_optimizador.TestOptimizadorCLI.test_parse_board_invalido
OK test_cli_optimizador.TestOptimizadorCLI.test_parse_board_valido
SKIP test_coco_reengrose.CocoReengroseTests.test_carcasa_base_sin_solapes :: requiere FreeCAD real (import falló o solo hay un mock)
SKIP test_coco_reengrose.CocoReengroseTests.test_carcasa_lateral_sin_solapes :: requiere FreeCAD real (import falló o solo hay un mock)
SKIP test_coco_reengrose.CocoReengroseTests.test_coco_estandar_regresion :: requiere FreeCAD real (import falló o solo hay un mock)
SKIP test_coco_reengrose.CocoReengroseTests.test_export_csv_grupo :: requiere FreeCAD real (import falló o solo hay un mock)
SKIP test_coco_reengrose.CocoReengroseTests.test_mocheo_repisa :: requiere FreeCAD real (import falló o solo hay un mock)
SKIP test_coco_reengrose.CocoReengroseTests.test_pacha_en_despiece :: requiere FreeCAD real (import falló o solo hay un mock)
SKIP test_coco_reengrose.CocoReengroseTests.test_retroceso_repisa :: requiere FreeCAD real (import falló o solo hay un mock)
SKIP test_coco_reengrose.CocoReengroseTests.test_ui_contextual :: requiere FreeCAD real (import falló o solo hay un mock)
SKIP test_coco_reengrose_avanzado.CocoReengroseAvanzadoTests.test_borde_unico_retrocompatible :: requiere FreeCAD real (import falló o solo hay un mock)
SKIP test_coco_reengrose_avanzado.CocoReengroseAvanzadoTests.test_division_reengrose_no_colapsa_repisa :: requiere FreeCAD real (import falló o solo hay un mock)
SKIP test_coco_reengrose_avanzado.CocoReengroseAvanzadoTests.test_esquina_techo_lateral_horizontal_domina :: requiere FreeCAD real (import falló o solo hay un mock)
SKIP test_coco_reengrose_avanzado.CocoReengroseAvanzadoTests.test_esquina_techo_lateral_vertical_domina :: requiere FreeCAD real (import falló o solo hay un mock)
SKIP test_coco_reengrose_avanzado.CocoReengroseAvanzadoTests.test_esquinas_independientes_ui :: requiere FreeCAD real (import falló o solo hay un mock)
SKIP test_coco_reengrose_avanzado.CocoReengroseAvanzadoTests.test_inglete_45_sin_solapes :: requiere FreeCAD real (import falló o solo hay un mock)
SKIP test_coco_reengrose_avanzado.CocoReengroseAvanzadoTests.test_interrumpir_tira_en_division :: requiere FreeCAD real (import falló o solo hay un mock)
SKIP test_coco_reengrose_avanzado.CocoReengroseAvanzadoTests.test_marco_perimetral_4_bordes_inglete :: requiere FreeCAD real (import falló o solo hay un mock)
SKIP test_coco_reengrose_avanzado.CocoReengroseAvanzadoTests.test_repisa_retranqueada_ancla_cara_real :: requiere FreeCAD real (import falló o solo hay un mock)
SKIP test_coco_reengrose_avanzado.CocoReengroseAvanzadoTests.test_sync_esquinas_ui :: requiere FreeCAD real (import falló o solo hay un mock)
SKIP test_coco_reengrose_avanzado.CocoReengroseAvanzadoTests.test_techo_reengrose_division_vertical :: requiere FreeCAD real (import falló o solo hay un mock)
SKIP test_coco_reengrose_avanzado.CocoReengroseAvanzadoTests.test_techo_retroceso_contiene_repisas :: requiere FreeCAD real (import falló o solo hay un mock)
SKIP test_coco_reengrose_avanzado.CocoReengroseAvanzadoTests.test_ui_contextual_modos_nuevos :: requiere FreeCAD real (import falló o solo hay un mock)
SKIP test_coco_reengrose_avanzado.CocoReengroseAvanzadoTests.test_zocalo_u_tres_bordes :: requiere FreeCAD real (import falló o solo hay un mock)
SKIP test_comandos_workbench.ComandosFreeCADTests.test_barras_solo_referencian_comandos_registrados :: requiere FreeCAD real (freecadcmd)
SKIP test_comandos_workbench.ComandosFreeCADTests.test_comandos_registrados :: requiere FreeCAD real (freecadcmd)
SKIP test_comandos_workbench.ComandosFreeCADTests.test_panel_estandar_crea_hoja_y_panel :: requiere FreeCAD real (freecadcmd)
SKIP test_comandos_workbench.ComandosFreeCADTests.test_todos_los_iconos_existen :: requiere FreeCAD real (freecadcmd)
SKIP test_comandos_workbench.ComandosFreeCADTests.test_zocalo_anade_objetos :: requiere FreeCAD real (freecadcmd)
OK test_comandos_workbench.SinExecTests.test_ningun_exec_builtin_en_el_codigo
SKIP test_creacion_colocacion.FlujoCreacionColocacionTests.test_aceptar_abre_panel_y_coloca_el_modulo :: requiere FreeCAD real (import falló o solo hay un mock)
SKIP test_creacion_colocacion.FlujoCreacionColocacionTests.test_aceptar_dos_veces_coloca_una_sola :: requiere FreeCAD real (import falló o solo hay un mock)
SKIP test_creacion_colocacion.FlujoCreacionColocacionTests.test_cancelar_panel_borra_el_modulo :: requiere FreeCAD real (import falló o solo hay un mock)
SKIP test_creacion_colocacion.FlujoCreacionColocacionTests.test_colocacion_real_sin_gui_cancela_y_devuelve_falso :: requiere FreeCAD real (import falló o solo hay un mock)
SKIP test_creacion_colocacion.FlujoCreacionColocacionTests.test_sin_interfaz_confirma_en_origen :: requiere FreeCAD real (import falló o solo hay un mock)
SKIP test_creacion_colocacion.PanelesResuelvenTests.test_todas_las_specs_tienen_clase_de_panel :: requiere FreeCAD real (import falló o solo hay un mock)
SKIP test_creacion_colocacion.RotacionCreacionTests.test_coco_con_rotacion :: requiere FreeCAD real (import falló o solo hay un mock)
SKIP test_creacion_colocacion.RotacionCreacionTests.test_panel_con_rotacion :: requiere FreeCAD real (import falló o solo hay un mock)
SKIP test_creacion_colocacion.RotacionCreacionTests.test_zocalo_con_rotacion :: requiere FreeCAD real (import falló o solo hay un mock)
SKIP test_creacion_modulos.CreacionModulosTests.test_crear_pieza_devuelve_panel_con_shape :: requiere FreeCAD real (import falló o solo hay un mock)
SKIP test_creacion_modulos.CreacionModulosTests.test_crear_pieza_sin_doc_devuelve_none :: requiere FreeCAD real (import falló o solo hay un mock)
SKIP test_creacion_modulos.CreacionModulosTests.test_make_cajon_devuelve_objeto_con_shape :: requiere FreeCAD real (import falló o solo hay un mock)
SKIP test_creacion_modulos.CreacionModulosTests.test_make_coco_devuelve_objeto_con_shape :: requiere FreeCAD real (import falló o solo hay un mock)
SKIP test_creacion_modulos.CreacionModulosTests.test_make_zocalo_devuelve_objeto_con_shape :: requiere FreeCAD real (import falló o solo hay un mock)
OK test_despiece_snapshots.TestDespieceSnapshotsCajon.test_gola
OK test_despiece_snapshots.TestDespieceSnapshotsCajon.test_inglete_45
OK test_despiece_snapshots.TestDespieceSnapshotsCajon.test_metalica
OK test_despiece_snapshots.TestDespieceSnapshotsCajon.test_oculta_blum
OK test_despiece_snapshots.TestDespieceSnapshotsCajon.test_oculta_generica
OK test_despiece_snapshots.TestDespieceSnapshotsCajon.test_push_open
OK test_despiece_snapshots.TestDespieceSnapshotsCajon.test_telescopica
OK test_despiece_snapshots.TestDespieceSnapshotsCajon.test_tirador
OK test_despiece_snapshots.TestDespieceSnapshotsPuerta.test_batiente_embebida
OK test_despiece_snapshots.TestDespieceSnapshotsPuerta.test_batiente_parche
OK test_despiece_snapshots.TestDespieceSnapshotsPuerta.test_batiente_semiparche
OK test_despiece_snapshots.TestDespieceSnapshotsPuerta.test_bisagras_para_puerta_800
OK test_despiece_snapshots.TestDespieceSnapshotsPuerta.test_corrediza_2hojas
OK test_facade_harmony.TestAplicarSistemaApertura.test_gola_con_descuento_personalizado
OK test_facade_harmony.TestAplicarSistemaApertura.test_gola_descuenta_35
OK test_facade_harmony.TestAplicarSistemaApertura.test_inglete_45_conserva_altura
OK test_facade_harmony.TestAplicarSistemaApertura.test_push_open_conserva_altura
OK test_facade_harmony.TestAplicarSistemaApertura.test_sistema_invalido
OK test_facade_harmony.TestAplicarSistemaApertura.test_tirador_conserva_altura
OK test_facade_harmony.TestCalculoFachadaBase.test_embebida
OK test_facade_harmony.TestCalculoFachadaBase.test_holgura_personalizada
OK test_facade_harmony.TestCalculoFachadaBase.test_montaje_invalido
OK test_facade_harmony.TestCalculoFachadaBase.test_parche
OK test_facade_harmony.TestCalculoFachadaBase.test_semiparche
OK test_facade_harmony.TestContratoFachadas.test_constantes_taller
OK test_facade_harmony.TestContratoFachadas.test_enums_validos
OK test_facade_harmony.TestContratoFachadas.test_operaciones_canto
OK test_facade_harmony.TestContratoFachadas.test_sistemas_apertura_validos
OK test_facade_harmony.TestFuncionesAuxiliares.test_cantos_por_sistema_apertura
OK test_facade_harmony.TestFuncionesAuxiliares.test_necesita_bisel_45
OK test_facade_harmony.TestFuncionesAuxiliares.test_necesita_cantos_45
OK test_facade_harmony.TestFuncionesAuxiliares.test_necesita_descuento_gola
OK test_facade_harmony.TestFuncionesAuxiliares.test_necesita_expulsor_magnetico
OK test_facade_harmony.TestImportacionYEnums.test_cajon_consume_contrato
OK test_facade_harmony.TestImportacionYEnums.test_contrato_importable
OK test_facade_harmony.TestImportacionYEnums.test_no_discrepancias_strings
OK test_facade_harmony.TestImportacionYEnums.test_puerta_consume_contrato
OK test_facade_harmony.TestInglete45.test_altura_conservada
OK test_facade_harmony.TestInglete45.test_operacion_canto_bisel_45
OK test_facade_harmony.TestSimetriaGolaPuertaVsCajon.test_altura_igual_con_gola
SKIP test_gui_wiring.TestGuiWiring.test_dock_inspector_en_mainwindow :: requiere FreeCAD con GUI (GuiUp, FreeCADGui y DISPLAY/WAYLAND_DISPLAY)
SKIP test_gui_wiring.TestGuiWiring.test_enfocar_inspector_universal :: requiere FreeCAD con GUI (GuiUp, FreeCADGui y DISPLAY/WAYLAND_DISPLAY)
SKIP test_gui_wiring.TestGuiWiring.test_extirpacion_combos_planos_en_coco_task :: requiere FreeCAD con GUI (GuiUp, FreeCADGui y DISPLAY/WAYLAND_DISPLAY)
SKIP test_gui_wiring.TestGuiWiring.test_viewprovider_coco_redireccion :: requiere FreeCAD con GUI (GuiUp, FreeCADGui y DISPLAY/WAYLAND_DISPLAY)
OK test_hardware_hub.HardwareHubTests.test_calculate_sliding_doors_alacena_al1535
OK test_hardware_hub.HardwareHubTests.test_calculate_sliding_doors_placard_d52
OK test_hardware_hub.HardwareHubTests.test_get_family
OK test_hardware_hub.HardwareHubTests.test_get_family_corredera_oculta
OK test_hardware_hub.HardwareHubTests.test_get_family_corredera_telescopica
OK test_hardware_hub.HardwareHubTests.test_get_hardware_al1535
OK test_hardware_hub.HardwareHubTests.test_get_hardware_ducasse_d52
OK test_hardware_hub.HardwareHubTests.test_get_hardware_sku_no_existente
OK test_hardware_hub.HardwareHubTests.test_no_gui_imports
OK test_hardware_hub.HardwareHubTests.test_resolve_drawer_slide_blum_tandem
OK test_hardware_hub.HardwareHubTests.test_resolve_drawer_slide_sku_directo
OK test_hardware_hub.HardwareHubTests.test_resolve_drawer_slide_sku_inexistente
OK test_hardware_hub.HardwareHubTests.test_resolve_drawer_slide_telescopica
OK test_hardware_hub.HardwareHubTests.test_resolve_hinge_generic_parche
OK test_hardware_hub.HardwareHubTests.test_resolve_hinge_prefer_sku
OK test_hardware_hub.HardwareHubTests.test_resolve_sliding
SKIP test_headless_core.HeadlessCoreTests.test_core_no_carga_gui_ni_pyside :: requiere FreeCAD real (freecadcmd)
SKIP test_headless_core.HeadlessCoreTests.test_freecad_no_tiene_init_en_el_repo :: requiere FreeCAD real (freecadcmd)
SKIP test_headless_core.HeadlessCoreTests.test_namespace_freecad_incluye_paquete_del_repo :: requiere FreeCAD real (freecadcmd)
OK test_layout_reengrose.LayoutReengroseTests.test_ambos_lados
OK test_layout_reengrose.LayoutReengroseTests.test_division_derecha_reduce_vano
OK test_layout_reengrose.LayoutReengroseTests.test_division_izquierda_reduce_vano
OK test_layout_reengrose.LayoutReengroseTests.test_lateral_izquierdo
OK test_layout_reengrose.LayoutReengroseTests.test_repisa_nominal_para_mocheo
OK test_layout_reengrose.LayoutReengroseTests.test_sin_reengrose
SKIP test_puerta_core.CoreImportTests.test_import_core :: requiere FreeCAD real (import falló o solo hay un mock)
SKIP test_puerta_core.CoreImportTests.test_make_puerta_existe :: requiere FreeCAD real (import falló o solo hay un mock)
OK test_puerta_core.DespieceBasculanteTests.test_descripcion_piston
OK test_puerta_core.DespieceBasculanteTests.test_fuerza_piston
OK test_puerta_core.DespieceBasculanteTests.test_masa_puerta
OK test_puerta_core.DespieceBasculanteTests.test_piston_recomendado
OK test_puerta_core.DespieceBatienteTests.test_bisagras_para_puerta
OK test_puerta_core.DespieceBatienteTests.test_cantidad_bisagras
OK test_puerta_core.DespieceBatienteTests.test_cota_cazoleta
OK test_puerta_core.DespieceBatienteTests.test_dimensiones_embebida
OK test_puerta_core.DespieceBatienteTests.test_dimensiones_parche
OK test_puerta_core.DespieceBatienteTests.test_dimensiones_semiparche
OK test_puerta_core.DespieceBatienteTests.test_posiciones_cazoleta_2_bisagras
OK test_puerta_core.DespieceBatienteTests.test_posiciones_cazoleta_3_bisagras
OK test_puerta_core.DespieceBatienteTests.test_posiciones_cazoleta_4_bisagras
OK test_puerta_core.DespieceCorredizaTests.test_corrediza_al1535
OK test_puerta_core.DespieceCorredizaTests.test_corrediza_d52
OK test_puerta_core.SistemasAperturaTests.test_ajuste_altura_gola
OK test_puerta_core.SistemasAperturaTests.test_ajuste_altura_push
OK test_puerta_core.SistemasAperturaTests.test_ajuste_altura_tirador
OK test_puerta_core.SistemasAperturaTests.test_necesita_cantos_45
OK test_puerta_core.SistemasAperturaTests.test_necesita_expulsor
SKIP test_reengrose_l1.ReengroseL1Tests.test_desde_objeto :: requiere FreeCAD real (import falló o solo hay un mock)
SKIP test_reengrose_l1.ReengroseL1Tests.test_independiente :: requiere FreeCAD real (import falló o solo hay un mock)
SKIP test_reengrose_l1.ReengroseL1Tests.test_pacha_parcial :: requiere FreeCAD real (import falló o solo hay un mock)
SKIP test_reengrose_l1.ReengroseL1Tests.test_pacha_total :: requiere FreeCAD real (import falló o solo hay un mock)
SKIP test_reengrose_l1.ReengroseL1Tests.test_panel_viejo_sin_propiedades :: requiere FreeCAD real (import falló o solo hay un mock)
SKIP test_reengrose_l1.ReengroseL1Tests.test_ui_tooltips_y_accept :: requiere FreeCAD real (import falló o solo hay un mock)
SKIP test_selection_bridge.SelectionBridgeTests.test_add_selection_dispara_callback :: requiere FreeCAD con GUI (GuiUp, FreeCADGui y DISPLAY/WAYLAND_DISPLAY)
SKIP test_selection_bridge.SelectionBridgeTests.test_add_selection_todos_los_tipos :: requiere FreeCAD con GUI (GuiUp, FreeCADGui y DISPLAY/WAYLAND_DISPLAY)
SKIP test_selection_bridge.SelectionBridgeTests.test_classify_box_nativo_desconocido :: requiere FreeCAD con GUI (GuiUp, FreeCADGui y DISPLAY/WAYLAND_DISPLAY)
SKIP test_selection_bridge.SelectionBridgeTests.test_classify_cajon :: requiere FreeCAD con GUI (GuiUp, FreeCADGui y DISPLAY/WAYLAND_DISPLAY)
SKIP test_selection_bridge.SelectionBridgeTests.test_classify_coco :: requiere FreeCAD con GUI (GuiUp, FreeCADGui y DISPLAY/WAYLAND_DISPLAY)
SKIP test_selection_bridge.SelectionBridgeTests.test_classify_none :: requiere FreeCAD con GUI (GuiUp, FreeCADGui y DISPLAY/WAYLAND_DISPLAY)
SKIP test_selection_bridge.SelectionBridgeTests.test_classify_panel :: requiere FreeCAD con GUI (GuiUp, FreeCADGui y DISPLAY/WAYLAND_DISPLAY)
SKIP test_selection_bridge.SelectionBridgeTests.test_classify_precision_100 :: requiere FreeCAD con GUI (GuiUp, FreeCADGui y DISPLAY/WAYLAND_DISPLAY)
SKIP test_selection_bridge.SelectionBridgeTests.test_classify_puerta :: requiere FreeCAD con GUI (GuiUp, FreeCADGui y DISPLAY/WAYLAND_DISPLAY)
SKIP test_selection_bridge.SelectionBridgeTests.test_classify_zocalo :: requiere FreeCAD con GUI (GuiUp, FreeCADGui y DISPLAY/WAYLAND_DISPLAY)
SKIP test_selection_bridge.SelectionBridgeTests.test_clear_selection_resetear_estado :: requiere FreeCAD con GUI (GuiUp, FreeCADGui y DISPLAY/WAYLAND_DISPLAY)
SKIP test_selection_bridge.SelectionBridgeTests.test_desregistrar_observer_idempotente :: requiere FreeCAD con GUI (GuiUp, FreeCADGui y DISPLAY/WAYLAND_DISPLAY)
SKIP test_selection_bridge.SelectionBridgeTests.test_repeticion_seleccion_deseleccion_sin_excepciones :: requiere FreeCAD con GUI (GuiUp, FreeCADGui y DISPLAY/WAYLAND_DISPLAY)
SKIP test_single_dock_convergence.TestSingleDockConvergence.test_abrir_panel_objeto_no_abre_dialogo_flotante :: requiere FreeCAD real (import falló o solo hay un mock)
SKIP test_single_dock_convergence.TestSingleDockConvergence.test_anatomia_panel_unico :: requiere FreeCAD real (import falló o solo hay un mock)
SKIP test_single_dock_convergence.TestSingleDockConvergence.test_carga_coco_puebla_micro_header_y_arbol :: requiere FreeCAD real (import falló o solo hay un mock)
SKIP test_single_dock_convergence.TestSingleDockConvergence.test_click_arbol_conmuta_stack :: requiere FreeCAD real (import falló o solo hay un mock)
SKIP test_single_dock_convergence.TestSingleDockConvergence.test_click_preview_2d_sincroniza_arbol_y_stack :: requiere FreeCAD real (import falló o solo hay un mock)
SKIP test_single_dock_convergence.TestSingleDockConvergence.test_edicion_micro_header_actualiza_coco_y_preview :: requiere FreeCAD real (import falló o solo hay un mock)
SKIP test_smoke_l3_desk_assembly.TestSmokeL3DeskAssembly.test_00_api_coverage :: requiere FreeCAD real (import falló o solo hay un mock)
SKIP test_smoke_l3_desk_assembly.TestSmokeL3DeskAssembly.test_01_chain1_subdivision_torre_cajones :: requiere FreeCAD real (import falló o solo hay un mock)
SKIP test_smoke_l3_desk_assembly.TestSmokeL3DeskAssembly.test_02_chain2_sistemas_apertura_fachadas :: requiere FreeCAD real (import falló o solo hay un mock)
SKIP test_smoke_l3_desk_assembly.TestSmokeL3DeskAssembly.test_03_chain3_reengrose_boleo_cubierta :: requiere FreeCAD real (import falló o solo hay un mock)
SKIP test_smoke_l3_desk_assembly.TestSmokeL3DeskAssembly.test_04_chain4_pose_duplicacion_en_l :: requiere FreeCAD real (import falló o solo hay un mock)
SKIP test_smoke_l3_desk_assembly.TestSmokeL3DeskAssembly.test_05_chain5_lista_materiales_despiece :: requiere FreeCAD real (import falló o solo hay un mock)
SKIP test_smoke_l3_desk_assembly.TestSmokeL3DeskAssembly.test_99_report_matriz :: requiere FreeCAD real (import falló o solo hay un mock)
SKIP test_universal_inspector.UniversalInspectorTests.test_cerrar_inspector_no_lanza :: requiere FreeCAD real (import falló o solo hay un mock)
SKIP test_universal_inspector.UniversalInspectorTests.test_desconexion_observer_limpia :: requiere FreeCAD real (import falló o solo hay un mock)
SKIP test_universal_inspector.UniversalInspectorTests.test_instanciacion_sin_errores :: requiere FreeCAD real (import falló o solo hay un mock)
SKIP test_universal_inspector.UniversalInspectorTests.test_pagina_inicial_es_chasis :: requiere FreeCAD real (import falló o solo hay un mock)
SKIP test_universal_inspector.UniversalInspectorTests.test_puente_creado :: requiere FreeCAD real (import falló o solo hay un mock)
SKIP test_universal_inspector.UniversalInspectorTests.test_seleccion_coco_cambia_a_chasis :: requiere FreeCAD real (import falló o solo hay un mock)
SKIP test_universal_inspector.UniversalInspectorTests.test_seleccion_panel_actualiza_header_cantos :: requiere FreeCAD real (import falló o solo hay un mock)
SKIP test_universal_inspector.UniversalInspectorTests.test_seleccion_panel_cambia_a_pieza :: requiere FreeCAD real (import falló o solo hay un mock)
SKIP test_universal_inspector.UniversalInspectorTests.test_seleccion_vacio_regresa_chasis :: requiere FreeCAD real (import falló o solo hay un mock)
OK test_vdo_agnosticism.TestReglasCalidadFreecad.test_no_except_desnudo_en_freecad
OK test_vdo_agnosticism.TestReglasCalidadFreecad.test_no_print_en_freecad
OK test_vdo_agnosticism.VDOAgnosticismTests.test_01_contrato_espacial_del_vano
OK test_vdo_agnosticism.VDOAgnosticismTests.test_02_agnosticidad_dilatacion_muro
OK test_vdo_agnosticism.VDOAgnosticismTests.test_03_agnosticidad_zocalo_con_amarres
OK test_vdo_agnosticism.VDOAgnosticismTests.test_04_simulacion_inserto_universal
OK test_vdo_agnosticism.VDOAgnosticismTests.test_qt_compat_solo_punto_entrada_pyside
OK test_vdo_chassis_widget.TestVDOChassisWidget.test_archetypes
OK test_vdo_chassis_widget.TestVDOChassisWidget.test_corner_cycling
OK test_vdo_chassis_widget.TestVDOChassisWidget.test_default_config
OK test_vdo_chassis_widget.TestVDOChassisWidget.test_estrategia_base_switching
OK test_vdo_chassis_widget.TestVDOChassisWidget.test_face_toggling
OK test_vdo_chassis_widget.TestVDOChassisWidget.test_fondo_selection
OK test_vdo_chassis_widget.TestVDOChassisWidget.test_set_chassis_config
OK test_vdo_reengrose.ReengrosePureTests.test_colision_y_mocheo
OK test_vdo_reengrose.ReengrosePureTests.test_defaults_and_validation
OK test_vdo_reengrose.ReengrosePureTests.test_despiece_pacha
OK test_vdo_reengrose.ReengrosePureTests.test_pacha_total
OK test_vdo_reengrose.ReengrosePureTests.test_paralela_cara_a
OK test_vdo_reengrose.ReengrosePureTests.test_paralela_fondo_y_cara_b
OK test_vdo_reengrose.ReengrosePureTests.test_politica_cantos
OK test_vdo_reengrose.ReengrosePureTests.test_transversal
OK test_vdo_reengrose.ReengrosePureTests.test_vano_neto
SKIP test_vdo_zocalo.ZocaloGeometryTests.test_despiece_longitudes :: requiere FreeCAD real (import falló o solo hay un mock)
SKIP test_vdo_zocalo.ZocaloGeometryTests.test_errores_de_configuracion :: requiere FreeCAD real (import falló o solo hay un mock)
SKIP test_vdo_zocalo.ZocaloGeometryTests.test_geometria_con_trasera :: requiere FreeCAD real (import falló o solo hay un mock)
SKIP test_vdo_zocalo.ZocaloGeometryTests.test_make_zocalo_sin_solapes :: requiere FreeCAD real (import falló o solo hay un mock)
SKIP test_vdo_zocalo.ZocaloGeometryTests.test_sin_trasera_y_amarres :: requiere FreeCAD real (import falló o solo hay un mock)
OK test_verificar.TestR5EstadoInmutable.test_asignacion_anotada_de_modulo_si_cuenta
OK test_verificar.TestR5EstadoInmutable.test_asignacion_de_modulo_si_cuenta
OK test_verificar.TestR5EstadoInmutable.test_constante_mayusculas_y_all_no_cuentan
OK test_verificar.TestR5EstadoInmutable.test_variable_local_no_cuenta
OK test_verificar.TestR7Errores.test_except_con_raise_no_se_cuenta
OK test_verificar.TestR7Errores.test_except_exception_se_cuenta_con_cualquier_cuerpo
OK test_verificar.TestR7Errores.test_except_pass_se_cuenta
OK test_verificar.TestR9DefsNoUsadas.test_funcion_sin_referencias_se_reporta
OK test_verificar.TestR9DefsNoUsadas.test_metodo_no_cuenta_como_def_modulo
OK test_verificar.TestR9DefsNoUsadas.test_privada_sin_referencias_se_reporta
OK test_verificar.TestR9DefsNoUsadas.test_referencia_por_cadena_cuenta
OK test_verificar.TestR9DefsNoUsadas.test_uso_en_el_mismo_archivo_cuenta
OK test_verificar.TestR9DefsNoUsadas.test_uso_por_atributo_cuenta
OK test_verificar.TestR9DefsNoUsadas.test_uso_por_import_from_cuenta
SKIP test_workbench_convergence.TestWorkbenchConvergence.test_interaccion_box_controller_pieza :: requiere FreeCAD con GUI (GuiUp, FreeCADGui y DISPLAY/WAYLAND_DISPLAY)
SKIP test_workbench_convergence.TestWorkbenchConvergence.test_interaccion_chasis_emite_capa1 :: requiere FreeCAD con GUI (GuiUp, FreeCADGui y DISPLAY/WAYLAND_DISPLAY)
SKIP test_workbench_convergence.TestWorkbenchConvergence.test_interaccion_vano_dock :: requiere FreeCAD con GUI (GuiUp, FreeCADGui y DISPLAY/WAYLAND_DISPLAY)
SKIP test_workbench_convergence.TestWorkbenchConvergence.test_lifecycle_context_manager :: requiere FreeCAD con GUI (GuiUp, FreeCADGui y DISPLAY/WAYLAND_DISPLAY)
SKIP test_workbench_convergence.TestWorkbenchConvergence.test_zoom_semantico_chasis :: requiere FreeCAD con GUI (GuiUp, FreeCADGui y DISPLAY/WAYLAND_DISPLAY)
SKIP test_workbench_convergence.TestWorkbenchConvergence.test_zoom_semantico_cierre_cajon :: requiere FreeCAD con GUI (GuiUp, FreeCADGui y DISPLAY/WAYLAND_DISPLAY)
SKIP test_workbench_convergence.TestWorkbenchConvergence.test_zoom_semantico_cierre_puerta :: requiere FreeCAD con GUI (GuiUp, FreeCADGui y DISPLAY/WAYLAND_DISPLAY)
SKIP test_workbench_convergence.TestWorkbenchConvergence.test_zoom_semantico_pieza_l1 :: requiere FreeCAD con GUI (GuiUp, FreeCADGui y DISPLAY/WAYLAND_DISPLAY)
SKIP test_workbench_convergence.TestWorkbenchConvergence.test_zoom_semantico_vano :: requiere FreeCAD con GUI (GuiUp, FreeCADGui y DISPLAY/WAYLAND_DISPLAY)

RESUMEN ejecutados=262 fallos=3 errores=0 skip=107 no_ejecutado=0
exit=1
```

Nivel 2 (`VDO_TEST_DIR=tests VDO_TEST_OUT=/tmp/x.txt freecadcmd tools/run_tests.py; echo exit=$?`):
```
OK test_arquitectura.CapasTests.test_app_no_importa_ui
OK test_arquitectura.CapasTests.test_cad_no_importa_ui_app
FALLO test_arquitectura.CapasTests.test_core_no_importa_app_ui_cad :: -  'freecad/vdo/core/vdo_panel_core.py'] : core/ importa app/ui/cad: ['freecad/vdo/core/vdo_coco_core.py', 'freecad/vdo/core/vdo_coco_spaces.py', 'freecad/vdo/core/vdo_module_props.py', 'freecad/vdo/core/vdo_panel_core.py']
FALLO test_arquitectura.CapasTests.test_ui_no_escritura_freecad :: Diff is 857 characters long. Set self.maxDiff to None to see it. : ui/ escribe en FreeCAD: ['freecad/vdo/ui/vdo_bim_bridge.py', 'freecad/vdo/ui/vdo_cajon_task.py', 'freecad/vdo/ui/vdo_coco_unified_task.py', 'freecad/vdo/ui/vdo_cutting_list_menu.py', 'freecad/vdo/ui/vdo_cutting_list_preview.py', 'fre
FALLO test_arquitectura.CapasTests.test_ui_no_importa_core_cad_app_api :: Diff is 743 characters long. Set self.maxDiff to None to see it. : ui/ importa core/cad/app.vdo_api: ['freecad/vdo/ui/vdo_box_controller.py', 'freecad/vdo/ui/vdo_cajon_task.py', 'freecad/vdo/ui/vdo_coco_preview2d.py', 'freecad/vdo/ui/vdo_coco_unified_task.py', 'freecad/vdo/ui/vdo_cutting_list_previe
OK test_build_zip.TestBuildZip.test_leer_version
OK test_build_zip.TestBuildZip.test_zip_contiene_solo_archivos_permitidos
OK test_cajon_core.TestBooleanLogicMocked.test_aplicar_corte_devuelve_original_si_falla
OK test_cajon_core.TestBooleanLogicMocked.test_bisel_45_crea_herramienta_triangular
OK test_cajon_core.TestBooleanLogicMocked.test_notch_reduce_volumen
OK test_cajon_core.TestBooleanLogicMocked.test_pin_hole_reduce_volumen
OK test_cajon_core.TestBooleanLogicMocked.test_ranura_piso_reduce_volumen
OK test_cajon_core.TestCoordenadasCalculadas.test_fachada_con_gola
OK test_cajon_core.TestCoordenadasCalculadas.test_piso_en_ranura_telescopica
OK test_cajon_core.TestCoordenadasCalculadas.test_posiciones_laterales
OK test_cajon_core.TestDespieceTipologias.test_listar_marcas_incluye_nuevas
OK test_cajon_core.TestDespieceTipologias.test_metalica_sin_laterales
OK test_cajon_core.TestDespieceTipologias.test_oculta_blum_tandem
OK test_cajon_core.TestDespieceTipologias.test_oculta_generica
OK test_cajon_core.TestDespieceTipologias.test_telescopica
OK test_cajon_core.TestFacadeContractIntegracion.test_cantos_por_sistema_apertura
OK test_cajon_core.TestFacadeContractIntegracion.test_gola_descuenta_35mm_en_alto
OK test_cajon_core.TestFacadeContractIntegracion.test_inglete_45_conserva_altura
OK test_cajon_core.TestFacadeContractIntegracion.test_push_open_conserva_altura
OK test_cajon_core.TestFacadeContractIntegracion.test_tirador_conserva_altura
OK test_cajon_core.TestHardwareHubIntegracion.test_resolve_blum_tandem_desde_manifest
OK test_cajon_core.TestHardwareHubIntegracion.test_resolve_generica
OK test_cajon_core.TestHardwareHubIntegracion.test_resolve_inexistente_lanza_keyerror
OK test_cajon_core.TestHardwareHubIntegracion.test_resolve_sku_directo
OK test_cajon_core.TestHardwareHubIntegracion.test_resolve_telescopica
OK test_capas_arquitectura.CapasTests.test_core_no_importa_interfaz_ni_qt
OK test_capas_arquitectura.CapasTests.test_registro_de_ui_no_esta_en_core
OK test_cli_optimizador.TestOptimizadorCLI.test_parse_board_con_decimales
OK test_cli_optimizador.TestOptimizadorCLI.test_parse_board_invalido
OK test_cli_optimizador.TestOptimizadorCLI.test_parse_board_valido
OK test_coco_reengrose.CocoReengroseTests.test_carcasa_base_sin_solapes
OK test_coco_reengrose.CocoReengroseTests.test_carcasa_lateral_sin_solapes
OK test_coco_reengrose.CocoReengroseTests.test_coco_estandar_regresion
OK test_coco_reengrose.CocoReengroseTests.test_export_csv_grupo
OK test_coco_reengrose.CocoReengroseTests.test_mocheo_repisa
OK test_coco_reengrose.CocoReengroseTests.test_pacha_en_despiece
OK test_coco_reengrose.CocoReengroseTests.test_retroceso_repisa
OK test_coco_reengrose.CocoReengroseTests.test_ui_contextual
OK test_coco_reengrose_avanzado.CocoReengroseAvanzadoTests.test_borde_unico_retrocompatible
OK test_coco_reengrose_avanzado.CocoReengroseAvanzadoTests.test_division_reengrose_no_colapsa_repisa
OK test_coco_reengrose_avanzado.CocoReengroseAvanzadoTests.test_esquina_techo_lateral_horizontal_domina
OK test_coco_reengrose_avanzado.CocoReengroseAvanzadoTests.test_esquina_techo_lateral_vertical_domina
OK test_coco_reengrose_avanzado.CocoReengroseAvanzadoTests.test_esquinas_independientes_ui
OK test_coco_reengrose_avanzado.CocoReengroseAvanzadoTests.test_inglete_45_sin_solapes
OK test_coco_reengrose_avanzado.CocoReengroseAvanzadoTests.test_interrumpir_tira_en_division
OK test_coco_reengrose_avanzado.CocoReengroseAvanzadoTests.test_marco_perimetral_4_bordes_inglete
OK test_coco_reengrose_avanzado.CocoReengroseAvanzadoTests.test_repisa_retranqueada_ancla_cara_real
OK test_coco_reengrose_avanzado.CocoReengroseAvanzadoTests.test_sync_esquinas_ui
OK test_coco_reengrose_avanzado.CocoReengroseAvanzadoTests.test_techo_reengrose_division_vertical
OK test_coco_reengrose_avanzado.CocoReengroseAvanzadoTests.test_techo_retroceso_contiene_repisas
OK test_coco_reengrose_avanzado.CocoReengroseAvanzadoTests.test_ui_contextual_modos_nuevos
OK test_coco_reengrose_avanzado.CocoReengroseAvanzadoTests.test_zocalo_u_tres_bordes
OK test_comandos_workbench.ComandosFreeCADTests.test_barras_solo_referencian_comandos_registrados
OK test_comandos_workbench.ComandosFreeCADTests.test_comandos_registrados
OK test_comandos_workbench.ComandosFreeCADTests.test_panel_estandar_crea_hoja_y_panel
OK test_comandos_workbench.ComandosFreeCADTests.test_todos_los_iconos_existen
OK test_comandos_workbench.ComandosFreeCADTests.test_zocalo_anade_objetos
OK test_comandos_workbench.SinExecTests.test_ningun_exec_builtin_en_el_codigo
OK test_creacion_colocacion.FlujoCreacionColocacionTests.test_aceptar_abre_panel_y_coloca_el_modulo
OK test_creacion_colocacion.FlujoCreacionColocacionTests.test_aceptar_dos_veces_coloca_una_sola
OK test_creacion_colocacion.FlujoCreacionColocacionTests.test_cancelar_panel_borra_el_modulo
OK test_creacion_colocacion.FlujoCreacionColocacionTests.test_colocacion_real_sin_gui_cancela_y_devuelve_falso
OK test_creacion_colocacion.FlujoCreacionColocacionTests.test_sin_interfaz_confirma_en_origen
OK test_creacion_colocacion.PanelesResuelvenTests.test_todas_las_specs_tienen_clase_de_panel
OK test_creacion_colocacion.RotacionCreacionTests.test_coco_con_rotacion
OK test_creacion_colocacion.RotacionCreacionTests.test_panel_con_rotacion
OK test_creacion_colocacion.RotacionCreacionTests.test_zocalo_con_rotacion
OK test_creacion_modulos.CreacionModulosTests.test_crear_pieza_devuelve_panel_con_shape
OK test_creacion_modulos.CreacionModulosTests.test_crear_pieza_sin_doc_devuelve_none
OK test_creacion_modulos.CreacionModulosTests.test_make_cajon_devuelve_objeto_con_shape
OK test_creacion_modulos.CreacionModulosTests.test_make_coco_devuelve_objeto_con_shape
OK test_creacion_modulos.CreacionModulosTests.test_make_zocalo_devuelve_objeto_con_shape
OK test_despiece_snapshots.TestDespieceSnapshotsCajon.test_gola
OK test_despiece_snapshots.TestDespieceSnapshotsCajon.test_inglete_45
OK test_despiece_snapshots.TestDespieceSnapshotsCajon.test_metalica
OK test_despiece_snapshots.TestDespieceSnapshotsCajon.test_oculta_blum
OK test_despiece_snapshots.TestDespieceSnapshotsCajon.test_oculta_generica
OK test_despiece_snapshots.TestDespieceSnapshotsCajon.test_push_open
OK test_despiece_snapshots.TestDespieceSnapshotsCajon.test_telescopica
OK test_despiece_snapshots.TestDespieceSnapshotsCajon.test_tirador
OK test_despiece_snapshots.TestDespieceSnapshotsPuerta.test_batiente_embebida
OK test_despiece_snapshots.TestDespieceSnapshotsPuerta.test_batiente_parche
OK test_despiece_snapshots.TestDespieceSnapshotsPuerta.test_batiente_semiparche
OK test_despiece_snapshots.TestDespieceSnapshotsPuerta.test_bisagras_para_puerta_800
OK test_despiece_snapshots.TestDespieceSnapshotsPuerta.test_corrediza_2hojas
OK test_facade_harmony.TestAplicarSistemaApertura.test_gola_con_descuento_personalizado
OK test_facade_harmony.TestAplicarSistemaApertura.test_gola_descuenta_35
OK test_facade_harmony.TestAplicarSistemaApertura.test_inglete_45_conserva_altura
OK test_facade_harmony.TestAplicarSistemaApertura.test_push_open_conserva_altura
OK test_facade_harmony.TestAplicarSistemaApertura.test_sistema_invalido
OK test_facade_harmony.TestAplicarSistemaApertura.test_tirador_conserva_altura
OK test_facade_harmony.TestCalculoFachadaBase.test_embebida
OK test_facade_harmony.TestCalculoFachadaBase.test_holgura_personalizada
OK test_facade_harmony.TestCalculoFachadaBase.test_montaje_invalido
OK test_facade_harmony.TestCalculoFachadaBase.test_parche
OK test_facade_harmony.TestCalculoFachadaBase.test_semiparche
OK test_facade_harmony.TestContratoFachadas.test_constantes_taller
OK test_facade_harmony.TestContratoFachadas.test_enums_validos
OK test_facade_harmony.TestContratoFachadas.test_operaciones_canto
OK test_facade_harmony.TestContratoFachadas.test_sistemas_apertura_validos
OK test_facade_harmony.TestFuncionesAuxiliares.test_cantos_por_sistema_apertura
OK test_facade_harmony.TestFuncionesAuxiliares.test_necesita_bisel_45
OK test_facade_harmony.TestFuncionesAuxiliares.test_necesita_cantos_45
OK test_facade_harmony.TestFuncionesAuxiliares.test_necesita_descuento_gola
OK test_facade_harmony.TestFuncionesAuxiliares.test_necesita_expulsor_magnetico
OK test_facade_harmony.TestImportacionYEnums.test_cajon_consume_contrato
OK test_facade_harmony.TestImportacionYEnums.test_contrato_importable
OK test_facade_harmony.TestImportacionYEnums.test_no_discrepancias_strings
OK test_facade_harmony.TestImportacionYEnums.test_puerta_consume_contrato
OK test_facade_harmony.TestInglete45.test_altura_conservada
OK test_facade_harmony.TestInglete45.test_operacion_canto_bisel_45
OK test_facade_harmony.TestSimetriaGolaPuertaVsCajon.test_altura_igual_con_gola
SKIP test_gui_wiring.TestGuiWiring.test_dock_inspector_en_mainwindow :: requiere FreeCAD con GUI (GuiUp, FreeCADGui y DISPLAY/WAYLAND_DISPLAY)
SKIP test_gui_wiring.TestGuiWiring.test_enfocar_inspector_universal :: requiere FreeCAD con GUI (GuiUp, FreeCADGui y DISPLAY/WAYLAND_DISPLAY)
SKIP test_gui_wiring.TestGuiWiring.test_extirpacion_combos_planos_en_coco_task :: requiere FreeCAD con GUI (GuiUp, FreeCADGui y DISPLAY/WAYLAND_DISPLAY)
SKIP test_gui_wiring.TestGuiWiring.test_viewprovider_coco_redireccion :: requiere FreeCAD con GUI (GuiUp, FreeCADGui y DISPLAY/WAYLAND_DISPLAY)
OK test_hardware_hub.HardwareHubTests.test_calculate_sliding_doors_alacena_al1535
OK test_hardware_hub.HardwareHubTests.test_calculate_sliding_doors_placard_d52
OK test_hardware_hub.HardwareHubTests.test_get_family
OK test_hardware_hub.HardwareHubTests.test_get_family_corredera_oculta
OK test_hardware_hub.HardwareHubTests.test_get_family_corredera_telescopica
OK test_hardware_hub.HardwareHubTests.test_get_hardware_al1535
OK test_hardware_hub.HardwareHubTests.test_get_hardware_ducasse_d52
OK test_hardware_hub.HardwareHubTests.test_get_hardware_sku_no_existente
OK test_hardware_hub.HardwareHubTests.test_no_gui_imports
OK test_hardware_hub.HardwareHubTests.test_resolve_drawer_slide_blum_tandem
OK test_hardware_hub.HardwareHubTests.test_resolve_drawer_slide_sku_directo
OK test_hardware_hub.HardwareHubTests.test_resolve_drawer_slide_sku_inexistente
OK test_hardware_hub.HardwareHubTests.test_resolve_drawer_slide_telescopica
OK test_hardware_hub.HardwareHubTests.test_resolve_hinge_generic_parche
OK test_hardware_hub.HardwareHubTests.test_resolve_hinge_prefer_sku
OK test_hardware_hub.HardwareHubTests.test_resolve_sliding
OK test_headless_core.HeadlessCoreTests.test_core_no_carga_gui_ni_pyside
OK test_headless_core.HeadlessCoreTests.test_freecad_no_tiene_init_en_el_repo
OK test_headless_core.HeadlessCoreTests.test_namespace_freecad_incluye_paquete_del_repo
OK test_layout_reengrose.LayoutReengroseTests.test_ambos_lados
OK test_layout_reengrose.LayoutReengroseTests.test_division_derecha_reduce_vano
OK test_layout_reengrose.LayoutReengroseTests.test_division_izquierda_reduce_vano
OK test_layout_reengrose.LayoutReengroseTests.test_lateral_izquierdo
OK test_layout_reengrose.LayoutReengroseTests.test_repisa_nominal_para_mocheo
OK test_layout_reengrose.LayoutReengroseTests.test_sin_reengrose
OK test_puerta_core.CoreImportTests.test_import_core
OK test_puerta_core.CoreImportTests.test_make_puerta_existe
OK test_puerta_core.DespieceBasculanteTests.test_descripcion_piston
OK test_puerta_core.DespieceBasculanteTests.test_fuerza_piston
OK test_puerta_core.DespieceBasculanteTests.test_masa_puerta
OK test_puerta_core.DespieceBasculanteTests.test_piston_recomendado
OK test_puerta_core.DespieceBatienteTests.test_bisagras_para_puerta
OK test_puerta_core.DespieceBatienteTests.test_cantidad_bisagras
OK test_puerta_core.DespieceBatienteTests.test_cota_cazoleta
OK test_puerta_core.DespieceBatienteTests.test_dimensiones_embebida
OK test_puerta_core.DespieceBatienteTests.test_dimensiones_parche
OK test_puerta_core.DespieceBatienteTests.test_dimensiones_semiparche
OK test_puerta_core.DespieceBatienteTests.test_posiciones_cazoleta_2_bisagras
OK test_puerta_core.DespieceBatienteTests.test_posiciones_cazoleta_3_bisagras
OK test_puerta_core.DespieceBatienteTests.test_posiciones_cazoleta_4_bisagras
OK test_puerta_core.DespieceCorredizaTests.test_corrediza_al1535
OK test_puerta_core.DespieceCorredizaTests.test_corrediza_d52
OK test_puerta_core.SistemasAperturaTests.test_ajuste_altura_gola
OK test_puerta_core.SistemasAperturaTests.test_ajuste_altura_push
OK test_puerta_core.SistemasAperturaTests.test_ajuste_altura_tirador
OK test_puerta_core.SistemasAperturaTests.test_necesita_cantos_45
OK test_puerta_core.SistemasAperturaTests.test_necesita_expulsor
OK test_reengrose_l1.ReengroseL1Tests.test_desde_objeto
OK test_reengrose_l1.ReengroseL1Tests.test_independiente
OK test_reengrose_l1.ReengroseL1Tests.test_pacha_parcial
OK test_reengrose_l1.ReengroseL1Tests.test_pacha_total
OK test_reengrose_l1.ReengroseL1Tests.test_panel_viejo_sin_propiedades
OK test_reengrose_l1.ReengroseL1Tests.test_ui_tooltips_y_accept
SKIP test_selection_bridge.SelectionBridgeTests.test_add_selection_dispara_callback :: requiere FreeCAD con GUI (GuiUp, FreeCADGui y DISPLAY/WAYLAND_DISPLAY)
SKIP test_selection_bridge.SelectionBridgeTests.test_add_selection_todos_los_tipos :: requiere FreeCAD con GUI (GuiUp, FreeCADGui y DISPLAY/WAYLAND_DISPLAY)
SKIP test_selection_bridge.SelectionBridgeTests.test_classify_box_nativo_desconocido :: requiere FreeCAD con GUI (GuiUp, FreeCADGui y DISPLAY/WAYLAND_DISPLAY)
SKIP test_selection_bridge.SelectionBridgeTests.test_classify_cajon :: requiere FreeCAD con GUI (GuiUp, FreeCADGui y DISPLAY/WAYLAND_DISPLAY)
SKIP test_selection_bridge.SelectionBridgeTests.test_classify_coco :: requiere FreeCAD con GUI (GuiUp, FreeCADGui y DISPLAY/WAYLAND_DISPLAY)
SKIP test_selection_bridge.SelectionBridgeTests.test_classify_none :: requiere FreeCAD con GUI (GuiUp, FreeCADGui y DISPLAY/WAYLAND_DISPLAY)
SKIP test_selection_bridge.SelectionBridgeTests.test_classify_panel :: requiere FreeCAD con GUI (GuiUp, FreeCADGui y DISPLAY/WAYLAND_DISPLAY)
SKIP test_selection_bridge.SelectionBridgeTests.test_classify_precision_100 :: requiere FreeCAD con GUI (GuiUp, FreeCADGui y DISPLAY/WAYLAND_DISPLAY)
SKIP test_selection_bridge.SelectionBridgeTests.test_classify_puerta :: requiere FreeCAD con GUI (GuiUp, FreeCADGui y DISPLAY/WAYLAND_DISPLAY)
SKIP test_selection_bridge.SelectionBridgeTests.test_classify_zocalo :: requiere FreeCAD con GUI (GuiUp, FreeCADGui y DISPLAY/WAYLAND_DISPLAY)
SKIP test_selection_bridge.SelectionBridgeTests.test_clear_selection_resetear_estado :: requiere FreeCAD con GUI (GuiUp, FreeCADGui y DISPLAY/WAYLAND_DISPLAY)
SKIP test_selection_bridge.SelectionBridgeTests.test_desregistrar_observer_idempotente :: requiere FreeCAD con GUI (GuiUp, FreeCADGui y DISPLAY/WAYLAND_DISPLAY)
SKIP test_selection_bridge.SelectionBridgeTests.test_repeticion_seleccion_deseleccion_sin_excepciones :: requiere FreeCAD con GUI (GuiUp, FreeCADGui y DISPLAY/WAYLAND_DISPLAY)
OK test_single_dock_convergence.TestSingleDockConvergence.test_abrir_panel_objeto_no_abre_dialogo_flotante
OK test_single_dock_convergence.TestSingleDockConvergence.test_anatomia_panel_unico
OK test_single_dock_convergence.TestSingleDockConvergence.test_carga_coco_puebla_micro_header_y_arbol
OK test_single_dock_convergence.TestSingleDockConvergence.test_click_arbol_conmuta_stack
OK test_single_dock_convergence.TestSingleDockConvergence.test_click_preview_2d_sincroniza_arbol_y_stack
OK test_single_dock_convergence.TestSingleDockConvergence.test_edicion_micro_header_actualiza_coco_y_preview
OK test_smoke_l3_desk_assembly.TestSmokeL3DeskAssembly.test_00_api_coverage
OK test_smoke_l3_desk_assembly.TestSmokeL3DeskAssembly.test_01_chain1_subdivision_torre_cajones
OK test_smoke_l3_desk_assembly.TestSmokeL3DeskAssembly.test_02_chain2_sistemas_apertura_fachadas
OK test_smoke_l3_desk_assembly.TestSmokeL3DeskAssembly.test_03_chain3_reengrose_boleo_cubierta
OK test_smoke_l3_desk_assembly.TestSmokeL3DeskAssembly.test_04_chain4_pose_duplicacion_en_l
OK test_smoke_l3_desk_assembly.TestSmokeL3DeskAssembly.test_05_chain5_lista_materiales_despiece
OK test_smoke_l3_desk_assembly.TestSmokeL3DeskAssembly.test_99_report_matriz
OK test_universal_inspector.UniversalInspectorTests.test_cerrar_inspector_no_lanza
OK test_universal_inspector.UniversalInspectorTests.test_desconexion_observer_limpia
OK test_universal_inspector.UniversalInspectorTests.test_instanciacion_sin_errores
OK test_universal_inspector.UniversalInspectorTests.test_pagina_inicial_es_chasis
OK test_universal_inspector.UniversalInspectorTests.test_puente_creado
OK test_universal_inspector.UniversalInspectorTests.test_seleccion_coco_cambia_a_chasis
OK test_universal_inspector.UniversalInspectorTests.test_seleccion_panel_actualiza_header_cantos
OK test_universal_inspector.UniversalInspectorTests.test_seleccion_panel_cambia_a_pieza
OK test_universal_inspector.UniversalInspectorTests.test_seleccion_vacio_regresa_chasis
OK test_vdo_agnosticism.TestReglasCalidadFreecad.test_no_except_desnudo_en_freecad
OK test_vdo_agnosticism.TestReglasCalidadFreecad.test_no_print_en_freecad
OK test_vdo_agnosticism.VDOAgnosticismTests.test_01_contrato_espacial_del_vano
OK test_vdo_agnosticism.VDOAgnosticismTests.test_02_agnosticidad_dilatacion_muro
OK test_vdo_agnosticism.VDOAgnosticismTests.test_03_agnosticidad_zocalo_con_amarres
OK test_vdo_agnosticism.VDOAgnosticismTests.test_04_simulacion_inserto_universal
OK test_vdo_agnosticism.VDOAgnosticismTests.test_qt_compat_solo_punto_entrada_pyside
OK test_vdo_chassis_widget.TestVDOChassisWidget.test_archetypes
OK test_vdo_chassis_widget.TestVDOChassisWidget.test_corner_cycling
OK test_vdo_chassis_widget.TestVDOChassisWidget.test_default_config
OK test_vdo_chassis_widget.TestVDOChassisWidget.test_estrategia_base_switching
OK test_vdo_chassis_widget.TestVDOChassisWidget.test_face_toggling
OK test_vdo_chassis_widget.TestVDOChassisWidget.test_fondo_selection
OK test_vdo_chassis_widget.TestVDOChassisWidget.test_set_chassis_config
OK test_vdo_reengrose.ReengrosePureTests.test_colision_y_mocheo
OK test_vdo_reengrose.ReengrosePureTests.test_defaults_and_validation
OK test_vdo_reengrose.ReengrosePureTests.test_despiece_pacha
OK test_vdo_reengrose.ReengrosePureTests.test_pacha_total
OK test_vdo_reengrose.ReengrosePureTests.test_paralela_cara_a
OK test_vdo_reengrose.ReengrosePureTests.test_paralela_fondo_y_cara_b
OK test_vdo_reengrose.ReengrosePureTests.test_politica_cantos
OK test_vdo_reengrose.ReengrosePureTests.test_transversal
OK test_vdo_reengrose.ReengrosePureTests.test_vano_neto
OK test_vdo_zocalo.ZocaloGeometryTests.test_despiece_longitudes
OK test_vdo_zocalo.ZocaloGeometryTests.test_errores_de_configuracion
OK test_vdo_zocalo.ZocaloGeometryTests.test_geometria_con_trasera
OK test_vdo_zocalo.ZocaloGeometryTests.test_make_zocalo_sin_solapes
OK test_vdo_zocalo.ZocaloGeometryTests.test_sin_trasera_y_amarres
OK test_verificar.TestR5EstadoInmutable.test_asignacion_anotada_de_modulo_si_cuenta
OK test_verificar.TestR5EstadoInmutable.test_asignacion_de_modulo_si_cuenta
OK test_verificar.TestR5EstadoInmutable.test_constante_mayusculas_y_all_no_cuentan
OK test_verificar.TestR5EstadoInmutable.test_variable_local_no_cuenta
OK test_verificar.TestR7Errores.test_except_con_raise_no_se_cuenta
OK test_verificar.TestR7Errores.test_except_exception_se_cuenta_con_cualquier_cuerpo
OK test_verificar.TestR7Errores.test_except_pass_se_cuenta
OK test_verificar.TestR9DefsNoUsadas.test_funcion_sin_referencias_se_reporta
OK test_verificar.TestR9DefsNoUsadas.test_metodo_no_cuenta_como_def_modulo
OK test_verificar.TestR9DefsNoUsadas.test_privada_sin_referencias_se_reporta
OK test_verificar.TestR9DefsNoUsadas.test_referencia_por_cadena_cuenta
OK test_verificar.TestR9DefsNoUsadas.test_uso_en_el_mismo_archivo_cuenta
OK test_verificar.TestR9DefsNoUsadas.test_uso_por_atributo_cuenta
OK test_verificar.TestR9DefsNoUsadas.test_uso_por_import_from_cuenta
SKIP test_workbench_convergence.TestWorkbenchConvergence.test_interaccion_box_controller_pieza :: requiere FreeCAD con GUI (GuiUp, FreeCADGui y DISPLAY/WAYLAND_DISPLAY)
SKIP test_workbench_convergence.TestWorkbenchConvergence.test_interaccion_chasis_emite_capa1 :: requiere FreeCAD con GUI (GuiUp, FreeCADGui y DISPLAY/WAYLAND_DISPLAY)
SKIP test_workbench_convergence.TestWorkbenchConvergence.test_interaccion_vano_dock :: requiere FreeCAD con GUI (GuiUp, FreeCADGui y DISPLAY/WAYLAND_DISPLAY)
SKIP test_workbench_convergence.TestWorkbenchConvergence.test_lifecycle_context_manager :: requiere FreeCAD con GUI (GuiUp, FreeCADGui y DISPLAY/WAYLAND_DISPLAY)
SKIP test_workbench_convergence.TestWorkbenchConvergence.test_zoom_semantico_chasis :: requiere FreeCAD con GUI (GuiUp, FreeCADGui y DISPLAY/WAYLAND_DISPLAY)
SKIP test_workbench_convergence.TestWorkbenchConvergence.test_zoom_semantico_cierre_cajon :: requiere FreeCAD con GUI (GuiUp, FreeCADGui y DISPLAY/WAYLAND_DISPLAY)
SKIP test_workbench_convergence.TestWorkbenchConvergence.test_zoom_semantico_cierre_puerta :: requiere FreeCAD con GUI (GuiUp, FreeCADGui y DISPLAY/WAYLAND_DISPLAY)
SKIP test_workbench_convergence.TestWorkbenchConvergence.test_zoom_semantico_pieza_l1 :: requiere FreeCAD con GUI (GuiUp, FreeCADGui y DISPLAY/WAYLAND_DISPLAY)
SKIP test_workbench_convergence.TestWorkbenchConvergence.test_zoom_semantico_vano :: requiere FreeCAD con GUI (GuiUp, FreeCADGui y DISPLAY/WAYLAND_DISPLAY)

RESUMEN ejecutados=260 fallos=3 errores=0 skip=26 no_ejecutado=0
exit=1 (SIGSEGV en el log: 0)
```

Verificador (`python3 -I tools/auditoria/verificar.py; echo exit=$?`):
```
=== VDO — verificación de métricas §2 ===
[FALLA] R1_capas: valor=17 umbral=0 (violaciones: freecad/vdo/ui/vdo_box_controller.py, freecad/vdo/ui/vdo_cajon_task.py, freecad/vdo/ui/vdo_coco_preview2d.py, freecad/vdo/ui/vdo_coco_unified_task.py, freecad/vdo/ui/vdo_cutting_list_preview.py, freecad/vdo/ui/vdo_export_cutting_list.py, freecad/vdo/ui/vdo_hardware_manager.py, freecad/vdo/ui/vdo_nesting_workflow.py, freecad/vdo/ui/vdo_optimizer_dialog.py, freecad/vdo/ui/vdo_optimizer_view.py, freecad/vdo/ui/vdo_panel_task.py, freecad/vdo/ui/vdo_puerta_task.py, freecad/vdo/ui/vdo_reengrose_ui.py, freecad/vdo/ui/vdo_universal_inspector.py, freecad/vdo/ui/vdo_view_providers.py, freecad/vdo/ui/vdo_widgets_coco.py, freecad/vdo/ui/vdo_zocalo_task.py)
[OK] R2_agnosticismo_core: valor=0 umbral=0 (ninguno)
[FALLA] R3_dominio_como_datos: valor=32 umbral=0 (escrituras fuera de cad/: freecad/vdo/app/casos_uso/colocar_modulo.py, freecad/vdo/app/casos_uso/editar_modulo.py, freecad/vdo/app/registro.py, freecad/vdo/app/vdo_creacion.py, freecad/vdo/commands.py, freecad/vdo/core/vdo_cajon_core.py, freecad/vdo/core/vdo_cajon_despiece.py, freecad/vdo/core/vdo_coco_core.py, freecad/vdo/core/vdo_panel_core.py, freecad/vdo/core/vdo_puerta_core.py, freecad/vdo/core/vdo_reengrose.py, freecad/vdo/core/vdo_zocalo_core.py, freecad/vdo/ui/vdo_bim_bridge.py, freecad/vdo/ui/vdo_cajon_task.py, freecad/vdo/ui/vdo_coco_unified_task.py, freecad/vdo/ui/vdo_cutting_list_menu.py, freecad/vdo/ui/vdo_cutting_list_preview.py, freecad/vdo/ui/vdo_drag_handles.py, freecad/vdo/ui/vdo_export_cutting_list.py, freecad/vdo/ui/vdo_inspector_dock.py, freecad/vdo/ui/vdo_nesting_workflow.py, freecad/vdo/ui/vdo_optimizer_dialog.py, freecad/vdo/ui/vdo_panel_task.py, freecad/vdo/ui/vdo_placement.py, freecad/vdo/ui/vdo_plano_cero.py, freecad/vdo/ui/vdo_puerta_task.py, freecad/vdo/ui/vdo_selection_bridge.py, freecad/vdo/ui/vdo_task_base.py, freecad/vdo/ui/vdo_universal_inspector.py, freecad/vdo/ui/vdo_view_providers.py, freecad/vdo/ui/vdo_widgets_coco.py, freecad/vdo/ui/vdo_zocalo_task.py)
[OK] R4_orquestacion_app: valor=0 umbral=0 (todos presentes)
[OK] R5_estado_inmutable: valor=0 umbral=0 (ninguna)
[OK] R6_paneles_accept_le15: valor=0 umbral=0 (todos ≤ 15)
[OK] R7_except_pass: valor=0 umbral=0 (0 except … pass)
[OK] R7_except_exception_core_cad_app: valor=0 umbral=0 (0 except Exception en core/cad/app)
[FALLA] R8_funciones_le100: valor=25 umbral=0 (funciones > 100 líneas: [('freecad/vdo/core/vdo_cajon_core.py', 'execute', 152), ('freecad/vdo/core/vdo_cajon_despiece.py', 'calcular_despiece', 323), ('freecad/vdo/core/vdo_coco_core.py', 'execute', 420), ('freecad/vdo/core/vdo_coco_spaces.py', 'generar_divisiones_matriz', 195), ('freecad/vdo/core/vdo_panel_core.py', 'crear_pieza', 101), ('freecad/vdo/core/vdo_puerta_core.py', 'execute', 138), ('freecad/vdo/core/vdo_reengrose.py', 'normalizar_modificador', 102), ('freecad/vdo/core/vdo_reengrose.py', 'generar_tiras_perimetrales', 220), ('freecad/vdo/core/vdo_spaces.py', 'resolver_espacios_eje', 122), ('freecad/vdo/core/vdo_zocalo_core.py', 'calcular_geometria_zocalo', 189), ('freecad/vdo/ui/vdo_box_controller.py', 'paintEvent', 105), ('freecad/vdo/ui/vdo_box_controller.py', '_construir_ui', 232), ('freecad/vdo/ui/vdo_cajon_task.py', '_crear_widget', 209), ('freecad/vdo/ui/vdo_chassis_widget.py', 'paintEvent', 210), ('freecad/vdo/ui/vdo_chassis_widget.py', '_init_ui', 238), ('freecad/vdo/ui/vdo_chassis_widget.py', '_aplicar_estilos', 112), ('freecad/vdo/ui/vdo_coco_unified_task.py', '_crear_widget', 172), ('freecad/vdo/ui/vdo_panel_task.py', '_crear_widget', 126), ('freecad/vdo/ui/vdo_puerta_task.py', '_crear_widget', 169), ('freecad/vdo/ui/vdo_reengrose_ui.py', '_construir', 139), ('freecad/vdo/ui/vdo_universal_inspector.py', '__init__', 207), ('freecad/vdo/ui/vdo_universal_inspector.py', '_actualizar_vista_completa', 110), ('freecad/vdo/ui/vdo_widgets_coco.py', '_crear_widget', 247), ('freecad/vdo/ui/vdo_widgets_coco.py', '_actualizar_inspector', 222), ('freecad/vdo/ui/vdo_zocalo_task.py', '_crear_widget', 123)])
[FALLA] R8_ruff_c901_le12: valor=28 umbral=0 (ruff C901 (max 12): 28 incidencias)
[OK] R9_clones: valor=0 umbral=0 (0 grupos de clones)
[FALLA] R9_defs_no_usadas: valor=2 umbral=0 (2 definiciones no usadas)
[FALLA] R10_ruff_check_cero: valor=259 umbral=0 (ruff check: 259 incidencias)
[FALLA] R10_mypy_strict_cero: valor=1081 umbral=0 (mypy strict: 1081 errores)
[OK] R10_cero_print: valor=0 umbral=0 (0 print() en freecad/)
[FALLA] R10_cero_hex_fuera_tema: valor=417 umbral=0 (417 literales hex fuera de ui/tema.py)
[OK] R11_golden_masters: valor=9 umbral=>=1 (9 golden.json)
[OK] R11_suite_nivel1_estructura: valor=0 umbral=0 (tests/ existe)
[OK] R12_documentacion: valor=0 umbral=0 (ARQUITECTURA=True, ADRs=4, DEUDA=True, GLOSARIO=True)
[OK] R14_freecad_real: valor=1.1.4 umbral=1.x (binario: /usr/bin/freecadcmd, salida: FreeCAD 1.1.4 Revision: 45040 (Git))

MÉTRICAS FALLADAS (8): R1_capas, R3_dominio_como_datos, R8_funciones_le100, R8_ruff_c901_le12, R9_defs_no_usadas, R10_ruff_check_cero, R10_mypy_strict_cero, R10_cero_hex_fuera_tema
```

Otras cifras medidas en esta subfase:
- `.venv/bin/ruff check freecad tests tools` → 259 incidencias (`Found 259 errors` en el resumen de ruff).
- `python3 -m unittest tests.test_verificar` → `OK` (14 tests).
- `readlink ~/.local/share/FreeCAD/Mod/VDO` → `/home/airhon/Proyectos/VDO_freecad_workbench` (sin cambios).
- `git rev-parse --short vdo10-final` → `7e389be` (no movido).

### Correcciones de cifras de la entrada anterior (F19.2-ter sesión 1)

| Entrada anterior | Corrección |
|---|---|
| "Gate de F19.2-ter" no mencionaba el segfault | El segfault seguía (SIGSEGV en log en 5 de 5). Ver paso 2. |
| R10 mypy "1092" como cifra estable | Medido en esta sesión: 1108 tras el paso 1 y 1081 tras el paso 3. |

### Qué queda abierto (con causa)

1. **F19.4 sin cerrar.** `test_arquitectura` falla en 3 pruebas. Causas medidas: `core/` importa `cad/` (4 módulos), `ui/` escribe en FreeCAD (20 módulos) e `ui/` importa `core/` o `cad/` (17 módulos tras el paso 1). Las escrituras de `make_*` siguen en `core/`.
2. **Conflicto de plan (decisión humana).** Existe `docs/PLAN_MINIMALISMO_VDO.md` (sin commitear) que declara sustituidos `PLAN_MAESTRO_VDO.md` y `PLAN_CORRECCIONES_F19.md`, y MN-01 elimina `app/`. Este prompt exige F19.4 con `app/casos_uso/`. No se ha ejecutado ninguno de los dos planes en exclusiva; el trabajo de esta sesión es compatible con ambos solo en la colocación.
3. **Colocación con clic sin verificar en GUI** (F19.11, humano).
4. **Goldens nuevos (F19.10)**: no se han generado ni commiteado.
5. **Defectos fuera de alcance observados:** `vdo_cajon_despiece.py:34` F401 (preexistente). `commands.py` y `crear_modulo_interactivo` con C901 > 12 (F19.6).
6. **Tests que se omiten en nivel 1 por entorno**: 107 SKIP (antes 98), los 9 nuevos son `requiere_freecad` en modo puro. Motivo impreso.
