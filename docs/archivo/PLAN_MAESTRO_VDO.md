Sustituido por docs/PLAN_MINIMALISMO_VDO.md

> **SUSTITUIDO** por `docs/PLAN_MINIMALISMO_VDO.md`. No ejecutar este documento.

# Plan maestro VDO — de 5,5 a 10/10

**Estado:** vinculante. Sustituye a `docs/PLAN_REFACTOR_VDO.md` (F1–F9) y al plan de costuras (P0–P9 de la conversación). Lo que ya está hecho en esos planes se incorpora aquí como punto de partida, no se repite como trabajo.

**Objetivo:** que una auditoría independiente de arquitectura y calidad, hecha sobre el código final, dé **10/10** según la rúbrica de §2. No quedan trabajos a medias ni deuda técnica sin decisión registrada. Si algo no se puede cerrar, el plan dice cómo se mide y quién lo cierra.

**Qué ejecuta este plan:** un agente, fase por fase, en el orden de §4. Cada fase tiene criterios de salida ejecutables. Una fase no empieza hasta que la anterior cumple todos sus criterios.

---

## 0. Reglas de ejecución (todas obligatorias)

1. **Rama única de integración:** `refactor/vdo-10`, creada desde la punta actual de `refactor/f7-complejidad` (`23c3781`). No se reescribe historia. Las ramas `refactor/f1…f7` se conservan como referencia.
2. **Un commit por fase como mínimo.** Mensaje en español, formato `tipo(ámbito): resumen`. Termina con `Co-Authored-By: Claude Haiku 5.5 <noreply@anthropic.com>`. **No push. No merge a `main`.**
3. **Etiquetas de fase:** al cerrar cada fase, `git tag vdo10-fN`. Las etiquetas retroactivas de F1–F7 se crean sobre sus commits (ver F0.2).
4. **Paridad numérica:** ninguna fase cambia cifras de piezas, BOM, costos, cortes ni geometría. La única excepción autorizada es el color de acento de F12 (decisión M-12), y se verifica visualmente contra la línea base de F0.
5. **Golden masters primero:** ninguna función de dominio se modifica sin que antes exista un golden test que fije su salida (F2 lo construye para todos los módulos).
6. **Pruebas en tres niveles** (§5). Un criterio “verde” solo cuenta si se ejecutó en el nivel que lo exige.
7. **Registro obligatorio:** `docs/PROGRESO_REFACTOR.md` se actualiza al cerrar cada fase con cifras medidas (salida de `tools/auditoria/verificar.py`), no con estimaciones. Las cifras de `PROGRESO_REFACTOR.md` que contradicen el código se corrigen en F0.
8. **Criterio de parada:** si una fase rompe un golden test o un criterio y no se arregla en el mismo intento, se revierte esa fase con `git reset` **solo en la rama de la fase**, nunca en `refactor/vdo-10` ya etiquetada. Se registra el motivo.
9. **Sin alcance nuevo:** no se añaden funciones de producto, fórmulas nuevas ni cambios de UX que no estén aquí.
10. **Cero excepciones de proceso:** si una decisión de §3 parece errónea, se documenta como `ADR` en `docs/adr/` con la evidencia, y se aplica la decisión tal como está hasta que un humano la cambie.

---

## 1. Punto de partida (medido, no estimado)

Línea base en `refactor/f7-complejidad` (`23c3781`). Estos números son el punto de salida de F0; se reconfirman con `tools/auditoria/`.

| Área | Estado actual | Fuente de la medición |
|---|---|---|
| Archivos Python en `freecad/` | 62 | `find freecad -name "*.py" \| wc -l` |
| Líneas `freecad/vdo/core` / `ui` / raíz | 9.258 / 13.479 / 380 | `wc -l` |
| Core con `import FreeCAD`/`Part` a nivel de módulo | **13 módulos** | grep `^import FreeCAD\|^import Part\|^from FreeCAD` en `core/` |
| Core que importa `ui`/Qt (directo o vía registro) | 7 módulos usan `vdo_ui_registry` (`adjuntar_vista`/`obtener`) | grep |
| UI que importa `core` directamente | **20 módulos** (p. ej. `vdo_coco_unified_task` 9 imports, `vdo_widgets_coco` 8) | grep |
| UI que importa `qt_compat` | 25 módulos (correcto) | grep |
| Estado de módulo mutable / caché de carga | 4 cargas a nivel de módulo: `vdo_manifest.VDO_MANIFEST`, `vdo_defaults._MANIFEST`, `vdo_cajon_despiece._MANIFEST`, `vdo_hardware_hub._CATALOGO`; más `vdo_ui_registry._cache` | grep |
| `except … pass` | **65** (55 con `except Exception`). Concentrados en `vdo_universal_inspector` (12), `vdo_coco_unified_task` (8), `vdo_placement` (7), `vdo_creation_flow` (6), `vdo_cajon_despiece` (5), `vdo_hardware_hub` (5), `vdo_selection_bridge` (4), `vdo_view_providers` (3), `vdo_widgets_coco` (3), y 1–2 en 12 módulos más | AST: `tools/auditoria/handlers.py` |
| `except Exception` total en `freecad/` | 135 | grep |
| Funciones > 150 líneas | **16** (la mayor: `vdo_coco_core.execute`, 428) | `tools/auditoria/ast_scan.py` |
| Funciones > 120 líneas | 21 | idem |
| Task panels: `accept()` | 41–101 líneas por panel; lógica de dominio y escritura en `obj` dentro de `accept` | lectura de código |
| FormBuilder | Usado solo por `vdo_zocalo_task` | grep |
| Grupos de clones | 2 (`_cargar_reengroses`/`_leer_reengroses`; `_on_n_changed` ×2) | `tools/auditoria/clones.py` |
| Colores hex fuera de tema | 368 líneas en 16 archivos; `vdo_theme` usado por 2 | grep |
| Tests que instalan mocks en `sys.modules` al importarse | **7 archivos** (`test_cajon_core`, `test_despiece_snapshots`, `test_facade_harmony`, `test_headless_core`, `test_puerta_core`, `test_selection_bridge`, `test_universal_inspector`) | grep |
| Suite modo puro | 120 ejecutados: 108 OK, 0 fallos, **11 ERROR**, **8 NO_EJECUTADO**, 3 skip (el runner escribe 1 línea SKIP para 3 skips) | `tools/run_tests.py` |
| Regresión de aislamiento | `test_vdo_reengrose` (9 OK en base) → **ERROR aislado** en `f7` | ejecución aislada |
| Referencias rotas | `tests/test_smoke_l3_desk_assembly.py:145` apunta a `vdo_reengrose_solids` (borrado); `:24` contiene `/home/javi/…` | grep |
| Herramientas obsoletas | `tools/matriz_mapeo.py` documenta `Macro/` (ya no existe) | lectura |
| Lint / tipado | No hay `ruff` ni `mypy` configurados | — |
| Ramas | Solo existen `f1…f7`. `f6` apunta a un commit de F5; el código de F6 está dentro de `23d69a9` (mensaje de F7). `f8` y `f9` no existen | `git branch`, `git log` |
| Registro de progreso | Contiene cifras falsas (`except … pass` = 0; “3 > 150”; hex “17→17 justificado”); faltan secciones F6 y F8 | comparación con código |
| Entorno | FreeCAD se instala de forma nativa con pacman (la instalación seguía en curso al cerrar este plan; `pacman -Q freecad` aún no lo lista). Sin Flatpak. Python del sistema 3.14; Node disponible | `pacman -Q freecad`, `command -v freecadcmd` |

---

## 2. Rúbrica 10/10 (criterios medibles)

Cada criterio tiene un umbral y un comando. Un 10 exige **todos** los umbrales. La auditoría final (F18) recalcula cada uno.

| # | Dimensión | Umbral para 10 | Comprobación |
|---|---|---|---|
| R1 | **Capas** | Cuatro capas con dependencias únicas (§3, M-04). Ningún import que las viole. | `tests/test_arquitectura.py` (AST) en verde |
| R2 | **Agnosticismo del dominio** | `core/` importa solo biblioteca estándar y `core/`. Cualquier módulo de `core/` se importa con `python3 -I` sin FreeCAD, sin Qt, sin `sys.modules` falsos. | test que importa cada módulo en subproceso limpio |
| R3 | **Dominio como datos** | Cada módulo de dominio devuelve estructuras (`dataclass`) inmutables. La escritura en el documento FreeCAD ocurre solo en `cad/`. | `grep` de escrituras (`.Ancho =`, `addObject`, `recompute`) fuera de `cad/` = 0 |
| R4 | **Orquestación** | Existe `app/` con un caso de uso por operación de usuario. Los paneles y comandos solo llaman a `app/`. | `tests/test_arquitectura.py` |
| R5 | **Inyección y estado** | Cero estado mutable de módulo (excepto constantes inmutables). Catálogos y manifiesto entran por parámetro desde la composición. | AST: asignaciones de módulo que no sean constantes = 0 |
| R6 | **Paneles** | `accept()` ≤ 15 líneas en los 5 paneles; formularios 100 % declarativos vía `FormBuilder`. | medición AST + `grep` |
| R7 | **Errores** | Cero `except … pass`. Cero `except Exception` en `core/`, `cad/`, `app/`. En `ui/` y `commands` solo en entradas de usuario, con log y mensaje. Jerarquía tipada en `core/errores.py`. | `tools/auditoria/handlers.py` = 0 y `grep` |
| R8 | **Complejidad** | Ninguna función > 100 líneas. `ruff` C901 con `max-complexity = 12` sin incidencias. | `ruff check` + `ast_scan` |
| R9 | **Duplicación y muerte** | 0 grupos de clones. 0 definiciones no usadas (script `tools/auditoria/defs_no_usadas.py`). | `clones.py` y script = 0 |
| R10 | **Consistencia** | `ruff check` = 0. `mypy --strict` = 0 errores en `core/`, `app/`, `cad/`. Cero `print` en paquete. Cero `sys.path` fuera de `Init.py`/`InitGui.py`. Cero colores hex fuera de `ui/theme.py`. Cero rutas de usuario en el repo. | comandos de §6 |
| R11 | **Pruebas** | Golden masters para todos los módulos de dominio. Suite de nivel 1 (pura) con 0 ERROR y 0 NO_EJECUTADO; skips solo con motivo explícito en lista blanca. Nivel 2 (FreeCAD) y nivel 3 (GUI) ejecutados y en verde. | `tools/run_tests.py` en los 3 niveles |
| R12 | **Documentación** | `docs/ARQUITECTURA.md` describe el código real (verificado por test de enlaces y de nombres). ADRs para cada decisión de §3. `docs/DEUDA_TECNICA.md` sin ítems abiertos, o con ítems que tienen dueño y fecha. Ningún documento contradice una cifra medida. | revisión de F16 con `verificar.py` |
| R13 | **Entrega** | Empaquetado reproducible: el zip contiene solo runtime, verificado por test. Historia con etiquetas por fase. Árbol limpio. | `tools/build_zip.py` + test |
| R14 | **Verificación real** | Pruebas en FreeCAD 1.x real (`freecadcmd` y GUI). Capturas antes/después con diferencias solo en lo autorizado. | registro en F17 |

**Umbrales exactos del script de verificación** (`tools/auditoria/verificar.py`, creado en F0): todos los del cuadro. El script devuelve código ≠ 0 si cualquiera falla.

---

## 3. Decisiones cerradas (M-01 a M-24)

Las decisiones anteriores D-01…D-25 quedan sustituidas donde se indique. Lo que no se indique, sigue vigente.

| ID | Tema | Decisión | Sustituye |
|---|---|---|---|
| M-01 | Alcance | Todo el repositorio: `freecad/vdo/`, `tests/`, `tools/`, `docs/`, `Init.py`, `InitGui.py`, `package.xml`, `README.md`, `LICENSE`. `tools/vdo_erp_sync/` se **extrae** a `tools/erp_sync/` con README propio, se excluye del zip, y se verifica con `tsc --noEmit` (R10). | — |
| M-02 | Ramas e historia | Integración en `refactor/vdo-10` desde `23c3781`. Sin reescritura. La mezcla de F6 en `23d69a9` se documenta en `PROGRESO_REFACTOR.md` y se etiqueta. | Plan F1–F9 (ramas) |
| M-03 | Idioma | Nombres de dominio en español (`zocalo`, `cajon`, `puerta`, `despiece`, `tablero`). Nombres de API externa en inglés (`accept`, `setStyleSheet`, `Part.makeBox`). Mensajes al usuario y docstrings en español. Glosario en `docs/GLOSARIO.md` (parte de `vdo_diccionario_semantico.md`). | D-02 (se mantiene y se formaliza) |
| M-04 | **Capas** | Cuatro capas + entrada: **`core/`** (dominio puro, stdlib); **`cad/`** (adaptador FreeCAD: único lugar con `App`, `Part`, `FreeCAD`, `FreeCADGui`); **`app/`** (casos de uso, composición, puertos); **`ui/`** (Qt; solo habla con `app/` y `qt_compat`); **entrada**: `commands.py`, `Init.py`, `InitGui.py`. Dependencias permitidas: `ui → app → cad → core`, `app → core`, `cad → core`. Ninguna otra. | D-04 (agnosticismo) y §1 del plan anterior |
| M-05 | Dependencias de FreeCAD | Permitidas **solo** en `cad/` y en entrada. Prohibidas en `core/`, `app/` y `ui/` (en `ui/` solo lo que `app/` expone). | §1 del plan anterior (que permitía FreeCAD en core) |
| M-06 | Puertos | Un único puerto: `app/puertos.py` define `Documento` (crear/leer/escribir objetos, transacción, recompute). `cad/` lo implementa. Tests usan una implementación en memoria (`tests/soporte/documento_falso.py`). No hay otros puertos. | — |
| M-07 | Registro de vistas | `core/vdo_ui_registry.py` se **elimina**. Core no sabe de vistas. `app/` recibe las fábricas de UI en la composición (`commands.py`). Las llamadas `adjuntar_vista`/`obtener` desaparecen de core. | D24 (registro en core) |
| M-08 | Estado global y caché | Prohibido estado mutable de módulo. El manifiesto y el catálogo se cargan **una vez por sesión** en `app/composicion.py` (`contexto()`), se pasan como parámetro y son inmutables (`MappingProxyType`/dataclass `frozen`). Recarga solo por comando explícito “Recargar catálogo”. | **D-04 (carga fresca) — sustituida**. Motivo: la carga fresca en cada acceso no se cumplía en el código y no aporta valor frente a recarga explícita. |
| M-09 | Validación de manifiesto | Validación Python explícita en `core/manifiesto.py` (claves obligatorias, tipos, rangos). Sin jsonschema. Errores tipados (`CatalogoError`). | D-05 (se mantiene la eliminación de jsonschema, se añade validación propia) |
| M-10 | Formularios | Todos los paneles usan `ui/formulario.py` (`FormBuilder`). La especificación de campos (etiqueta, tipo, rango, valor por defecto, unidades, dependencias) es **dato puro** en `app/formularios.py`, sin Qt. | D-15 (se completa) |
| M-11 | Task panels | `accept()` ≤ 15 líneas: leer valores del formulario → construir `Parametros` → llamar al caso de uso de `app/` → cerrar. Transacciones dentro del caso de uso (vía `Documento`). Base común en `ui/panel_base.py`. | D-12 (base) — ampliada |
| M-12 | Colores y estilos | Un único módulo de tema `ui/tema.py`. Colores solo ahí. Acento unificado `#007acc`. SVG embebidos en código se mueven a `Resources/icons/*.svg`. Única excepción visual: el cambio de acento, verificado en F17 contra F0. | D-10 (se completa) |
| M-13 | Errores | `core/errores.py`: `VDOError` → `ParametroInvalido`, `ReglaDeDominio`, `CatalogoError`, `GeometriaError`. `cad/` traduce excepciones de FreeCAD a estas. Prohibido `except Exception` en `core`, `cad`, `app`. | D-16 (se endurece) |
| M-14 | Logging | Un único canal: `app/registro.py` envuelve `App.Console` (y un `logging` de respaldo sin FreeCAD para pruebas). Prohibido `print` en paquete. | D-17 |
| M-15 | Límite de función | Máximo 100 líneas por función en todo el paquete. `ruff` C901 con complejidad máxima 12. | D-20 (se endurece de 150 a 100) |
| M-16 | Tabla de aperturas | Una única tabla de sistemas de apertura (`core/aperturas.py`) con reglas (expulsor, cantos 45°, gola, bisel). Cajón y puerta la consultan. Sus motores de cálculo siguen separados, porque su lógica no se solapa. | D-13 y D-14 (paso 2 se convierte en tabla compartida, no en motor compartido) |
| M-17 | Geometría | Core calcula con números y tuplas inmutables (`Rect`, `Caja`). `cad/` convierte a `App.Vector`/`Part.Shape`. | — |
| M-18 | Tests | Prohibido instalar mocks en `sys.modules` al importar. Los tests de nivel 1 usan `Documento` en memoria y no requieren FreeCAD. Nivel 2 y 3 se ejecutan con `freecadcmd` y GUI. | — |
| M-19 | Golden masters | Para cada módulo de dominio: entradas representativas (incluidas las de snapshots actuales) y salidas en `tests/golden/*.json`. Se regeneran solo con comando explícito y revisión humana del diff. | D-14 paso 1 (generalizado) |
| M-20 | Nombres de módulo | Se elimina el prefijo `vdo_` dentro del paquete `freecad.vdo` (redundante). Ejemplo: `core/vdo_zocalo_core.py` → `core/zocalo.py`. Se hace con script que reescribe imports y pruebas. Se fusionan módulos de < 80 líneas con un único importador. | — |
| M-21 | Entrada y `_module_dir` | `Init.py` e `InitGui.py` mantienen su copia de `_module_dir` (requisito de FreeCAD sin `__file__`). Son los únicos sitios con `sys.path`. | D-19 (se mantiene) |
| M-22 | Herramientas | `tools/matriz_mapeo.py` se **elimina** (documenta un árbol que ya no existe). `tools/build_zip.py` y `tools/vdo_optimizador_cli.py` se conservan con prueba. `tools/auditoria/` se conserva y se amplía. | — |
| M-23 | Versión | Versión mayor `2.0.0` en `package.xml` al cierre (cambio de API interna y de estructura). Se documenta en `CHANGELOG.md`. | — |
| M-24 | Documentación | `docs/` final: `ARQUITECTURA.md`, `DEUDA_TECNICA.md`, `PROGRESO_REFACTOR.md`, `GLOSARIO.md`, `adr/ADR-*.md`, `PLAN_MAESTRO_VDO.md`. Todo lo demás se mueve a `docs/archivo/` (ya existe). | D-22 (se amplía) |

---

## 4. Fases en orden

Orden por dependencias. Cada fase lista: **objetivo**, **pasos**, **salida** (criterios ejecutables) y **riesgo**.

### F0 — Línea base, herramientas y honestidad del registro

**Objetivo:** partir de números verdaderos, con herramientas de verificación y la rama de integración creada.

Pasos:
1. Crear `refactor/vdo-10` desde `23c3781`.
2. Etiquetar (las etiquetas describen el historial; no reescriben nada). Orden real del historial, de más antiguo a más reciente: `83023ca` (F1), `99ae898` (F2), `f033f93` (F3), `e652ce1` (F4), `2e048f1` (F5, snapshots), `c7b0a65` (F5, docs), `23d69a9` (F6 **y** F7 juntos: el commit contiene `vdo_form_builder.py`, la migración de `vdo_zocalo_task.py` y la fusión de `vdo_reengrose_solids`), `4ac90bd` (F9, docs), `23c3781` (F8, código). Etiquetas: `vdo10-f1` → `83023ca`; `vdo10-f2` → `99ae898`; `vdo10-f3` → `f033f93`; `vdo10-f4` → `e652ce1`; `vdo10-f5` → `c7b0a65`; `vdo10-f6` y `vdo10-f7` → `23d69a9` (con nota de mezcla en `PROGRESO_REFACTOR.md`); `vdo10-f9` → `4ac90bd`; `vdo10-f8` → `23c3781`. Nota: F9 (docs) queda antes que F8 (código) en el historial; se registra así para no reordenar.
3. Crear entorno local `.venv/` (añadir a `.gitignore`) con `ruff` y `mypy`. Registrar versiones en `docs/PROGRESO_REFACTOR.md`.
4. Crear `tools/auditoria/verificar.py`: ejecuta cada métrica de §2 y devuelve código ≠ 0 si no se cumple. Incluye los scripts existentes y los nuevos de F9 y F13 (`handlers.py`, `defs_no_usadas.py`).
5. **Gate de FreeCAD (nativo, pacman):** el usuario lo instala él mismo. Comprobar, en este orden: (a) `pacman -Q freecad` devuelve una versión **1.x**; (b) `command -v freecadcmd` (en Arch el binario de consola puede llamarse `freecadcmd` o `freecad-cli`; registrar cuál existe); (c) `freecadcmd --version` responde. Registrar en `PROGRESO_REFACTOR.md`: versión exacta, ruta del binario y versión del Python embebido (`freecadcmd -c "import sys;print(sys.version)"`). **Si el paquete aún no aparece, F0 se detiene aquí y se pregunta al usuario; no se asume que está instalado.** Sin FreeCAD, F3–F17 solo cierran el nivel 1 y F17 queda bloqueada. El nivel 1 sí puede avanzar mientras tanto.
6. Capturar línea base en `docs/metricas/base.json` (salida de `verificar.py --json`).
7. Corregir `PROGRESO_REFACTOR.md`: cifras reales de §1, secciones F6 y F8 añadidas (con lo que hay), la rama de F9 descrita como inexistente, y las cifras falsas marcadas como corregidas.
8. Crear `docs/adr/` con `ADR-000-indice.md` que liste M-01…M-24 y cuál sustituye a qué.

Salida:
- `git tag` muestra `vdo10-f1…f9`.
- `verificar.py` corre y reporta los valores de §1 (con los mismos números o explicando la diferencia).
- `docs/metricas/base.json` existe y está versionado.
- `PROGRESO_REFACTOR.md` no contiene ninguna cifra que `verificar.py` contradiga.

Riesgo: bajo. Instalar FreeCAD requiere permiso del usuario (paso 5).

---

### F1 — Higiene de repositorio y de pruebas

**Objetivo:** que la suite diga la verdad: sin errores por entorno en modo puro, sin efectos secundarios entre tests, sin referencias rotas.

Pasos:
1. **Quitar mocks globales.** Crear `tests/soporte/freecad_falso.py` con un contexto `instalado()` que coloca `FreeCAD`/`Part` falsos en `sys.modules` y los **restaura** al salir. Los 7 archivos de §1 dejan de instalar mocks al importarse; usan el contexto en `setUp`/`tearDown` o un decorador. Con esto `test_vdo_reengrose` pasa aislado.
2. **Referencia rota:** `tests/test_smoke_l3_desk_assembly.py` — eliminar la entrada de `vdo_reengrose_solids` (F7 ya la fusionó en `vdo_reengrose`, se verifica que `forma_ref` existe ahí) y sustituir `/home/javi/…` por una ruta relativa al repositorio o un `FREECAD_MACRO_DIR` por entorno; si no hay entorno, el test se salta con motivo.
3. **Errores por entorno → skips con motivo.** Cada test que requiere PySide o FreeCAD real se marca con `@requiere_qt` / `@requiere_freecad` que hace `SkipTest("requiere …")`. Modo puro: **0 ERROR**. Los skips tienen lista blanca en `tests/soporte/omisiones.txt` (nombre, motivo, nivel).
4. **NO_EJECUTADO → 0:** los 8 de `test_comandos_workbench` y `test_headless_core` pasan a ejecutarse (los que requieren FreeCAD se marcan como nivel 2 y se omiten con motivo) o se eliminan si son redundantes, con justificación en el registro.
5. **Runner:** corregir `tools/run_tests.py` para que escriba una línea `SKIP` por cada omitido (hoy escribe 1 para 3).
6. **Obsoletos:** eliminar `tools/matriz_mapeo.py` (M-22). Revisar `tools/build_zip.py` y `tools/vdo_optimizador_cli.py` que sigan funcionando.
7. **ERP (M-01):** mover `tools/vdo_erp_sync/` a `tools/erp_sync/`. Reemplazar cualquier URL de ejemplo por variable de entorno `VDO_ERP_URL` **sin valor por defecto**; falla con mensaje claro si falta. Añadir `README.md` del componente. Verificar `npm run typecheck` (`tsc --noEmit`).
8. Revisar `.gitignore`: añadir `.venv/`, `*.log`, y confirmar que `dist/` y `__pycache__/` no están versionados.

Salida:
- Modo puro: **0 ERROR, 0 NO_EJECUTADO**, skips = lista de `omisiones.txt`.
- Test de reengrose pasa **aislado** y en suite completa.
- `grep -rn "/home/" tests tools freecad` = 0 (excepto documentación archivada).
- `tools/erp_sync` typecheck en verde.

Riesgo: bajo-medio. Los tests dependen del orden de carga hoy; el paso 1 lo elimina. Verificar cada archivo aislado y en suite.

---

### F2 — Golden masters de todo el dominio

**Objetivo:** fijar la salida actual de **todos** los módulos de dominio antes de tocarlos (M-19).

Pasos:
1. Inventariar funciones públicas de dominio en `core/` (lista generada por script y guardada en `docs/metricas/funciones_dominio.txt`).
2. Para cada módulo de dominio, crear `tests/golden/<modulo>.py` con entradas representativas (incluye configuraciones de los snapshots existentes) y `tests/golden/<modulo>.json` con las salidas **actuales**. Los datos de cajón y puerta ya existen en `tests/fixtures/` y se reutilizan.
3. Cubrir al menos: `zocalo`, `panel`, `coco` (`execute` y `generar_divisiones_matriz`), `cajon`, `puerta`, `reengrose` (`generar_tiras_perimetrales`, `calcular_geometria_reengrose`), `layout`, `spaces`, `hardware_hub` (consultas), `optimizer_core`, `nesting_presets`, `module_props`, `frames`, `finish`.
4. Generación de golden: comando explícito `python3 tools/auditoria/golden.py --regenerar <modulo>`. Requiere que el humano revise el diff; el agente no regenera a ciegas.
5. Los golden de geometría que dependen de OCC se ejecutan en nivel 2. Los de cálculo puro, en nivel 1.

Salida:
- Un golden por módulo de dominio listado. `golden.py --verificar` = 100 % iguales.
- Cada golden tiene al menos 3 entradas.

Riesgo: medio. Si la salida actual depende de estado (orden de diccionarios, fechas), se normaliza en el golden y se documenta.

---

### F3 — Puerto CAD y primera costura: `reengrose`

**Objetivo:** crear `cad/` y dejar `vdo_reengrose.py` puro, como pide el criterio de R2.

Pasos:
1. Crear `freecad/vdo/cad/__init__.py` y `freecad/vdo/cad/geometria.py`.
2. Mover a `cad/geometria.py` `forma_ref` y cualquier uso de `App`/`Part` de `reengrose`. Devolver a `core/` solo números (tuplas, `Caja`).
3. `reengrose` no importa FreeCAD ni `Part` en ningún punto (ni a nivel de módulo ni dentro de funciones).
4. Actualizar importadores (`coco_core`, `coco_spaces`, `panel_core`, `layout`, `zocalo_core`) para que la parte FreeCAD venga de `cad/`.
5. Verificar golden de `reengrose` y de sus consumidores.

Salida:
- `python3 -I -c "import freecad.vdo.core.reengrose"` (tras renombrar en F13; antes, `vdo_reengrose`) funciona sin FreeCAD.
- `vdo_layout` también importa sin FreeCAD (hoy falla; F7 lo rompió).
- Golden de reengrose y layout = 100 %.

Riesgo: medio. `layout` depende de `reengrose`; se verifican ambos juntos.

---

### F4 — Dominio puro por módulo (la costura principal)

**Objetivo:** cada módulo de `core/` que hoy importa FreeCAD pasa a ser puro. Su salida es un `dataclass` (plan); `cad/` aplica el plan al documento.

Orden (hojas primero, para que cada paso tenga dependencias ya puras):

| Paso | Módulo actual | Qué cambia | Dependencias ya puras |
|---|---|---|---|
| F4.1 | `module_props.py` | Propiedades como datos; escritura en `cad/propiedades.py` | — |
| F4.2 | `guardian.py` | Validaciones devuelven errores tipados | — |
| F4.3 | `nesting_presets.py` | Sin App; datos puros | — |
| F4.4 | `view_base.py` | Eliminar: la vista es responsabilidad de `ui/` (M-07) | — |
| F4.5 | `frames.py`, `finish.py` | Puros (ya no importan FreeCAD si F3 los tocó) | — |
| F4.6 | `cajon_despiece.py` | Plan de despiece puro; apertura consultada en `aperturas.py` (M-16) | `aperturas` nuevo |
| F4.7 | `puerta_despiece.py` | Plan puro; apertura en `aperturas.py` | `aperturas` |
| F4.8 | `zocalo_core.py` | `calcular_geometria_zocalo` → `Plan`; `execute` sin `App`; escritura en `cad/zocalo.py` | F3 |
| F4.9 | `panel_core.py` | Idem | F3, F4.5 |
| F4.10 | `cajon_core.py` | Plan de cajón; `CajonFeature` queda en `cad/` | F4.6 |
| F4.11 | `puerta_core.py` | Plan de puerta; `execute` en `cad/` | F4.7 |
| F4.12 | `coco_spaces.py` | `generar_divisiones_matriz` (195 líneas) → plan puro | F3 |
| F4.13 | `coco_core.py` | `execute` (428 líneas) → plan + subfunciones ≤ 100 líneas | F4.8–F4.12 |
| F4.14 | `creation_flow.py` | Orquestación pasa a `app/` (M-04); core no crea documentos | F4.8–F4.13 |
| F4.15 | `vdo_defaults.py`, `vdo_hardware_hub.py` | Sin estado de módulo (M-08); catálogo inyectado | F6 (se completa allí) |

Para cada paso:
1. Verificar golden del módulo (F2) = 100 %.
2. Introducir el `dataclass` de salida (inmutable).
3. Mover la escritura al documento a `cad/`.
4. Verificar golden = 100 % (salida de dominio idéntica; la forma del objeto cambia solo si el golden se normalizó en F2).
5. Verificar que el módulo importa en `python3 -I`.

Salida:
- Ningún módulo de `core/` contiene `import FreeCAD`, `import Part`, `App.`, `Part.` ni `FreeCAD.` (grep = 0).
- Golden global = 100 %.
- Escrituras a objetos FreeCAD fuera de `cad/` = 0 (grep de `\.Ancho =` etc., con lista de patrones en `verificar.py`).

Riesgo: **alto**. Es la fase con más cambios. Mitigación: un módulo por commit; golden antes y después; si un golden cambia, se revierte el commit.

---

### F5 — Desacoplar core de UI

**Objetivo:** core no conoce vistas (M-07).

Pasos:
1. Eliminar `core/vdo_ui_registry.py` y todas las llamadas `adjuntar_vista`/`obtener` de core (`cajon_core`, `coco_core`, `panel_core`, `puerta_core`, `zocalo_core`, `creation_flow`, `module_specs`, `view_base`).
2. Las vistas se adjuntan desde `app/` tras crear el plan: `app/vistas.py` recibe las fábricas en la composición (`commands.py`).
3. `creation_flow` deja de importar UI: su lógica pasa a `app/creacion.py`.
4. `module_specs` (datos de módulo) se queda en core solo si no toca UI; si mezcla, se divide.

Salida:
- `grep -rn "vdo.ui\|PySide\|qt_compat\|vdo_ui_registry\|adjuntar_vista" freecad/vdo/core` = 0.
- Golden = 100 %.

Riesgo: medio.

---

### F6 — Capa `app/` y composición

**Objetivo:** un caso de uso por operación de usuario; composición única; sin caché global (M-08).

Pasos:
1. Crear `app/__init__.py`, `app/puertos.py` (`Documento`, M-06), `app/composicion.py` (`contexto()` con manifiesto y catálogo inmutables), `app/registro.py` (logging, M-14), `app/casos_uso/` con un módulo por operación:
   - `crear_hoja`, `crear_panel`, `crear_zocalo`, `crear_cajon`, `crear_puerta`, `crear_coco`, `editar_modulo`, `colocar_modulo`, `exportar_lista_corte`, `optimizar_corte`, `nesting`, `consultar_herrajes`, `recargar_catalogo`.
2. Cada caso de uso recibe `Parametros` (dataclass) y `Documento` (puerto) y devuelve resultado. Transacciones dentro del caso de uso.
3. Eliminar `_MANIFEST`, `VDO_MANIFEST`, `_CATALOGO` y `_cargar_json_fresco` (alias). El contexto se construye una vez y se pasa.
4. `commands.py` construye el contexto y las fábricas, y delega en `app/`.

Salida:
- `grep` de estado de módulo mutable en el paquete = 0 (script de R5).
- Cada comando de `commands.py` llama a un único caso de uso.
- Tests de casos de uso en nivel 1 con `Documento` en memoria.

Riesgo: medio-alto. Cambia el punto de entrada de todos los comandos. Verificar cada comando manualmente en F17.

---

### F7 — UI solo habla con `app/`

**Objetivo:** cumplir la dependencia `ui → app` (M-04) en los 20 módulos que hoy importan `core`.

Pasos:
1. Para cada módulo de `ui/` que importa `core` (lista de §1), sustituir por el caso de uso o la estructura expuesta por `app/`. Si `app/` no expone lo necesario, se añade allí (no se importa core desde UI).
2. Estructuras de datos que UI necesita (p. ej. resúmenes de lista de corte) se devuelven como `dataclass` desde `app/`.
3. Añadir `tests/test_arquitectura.py`: AST que falla si `ui/` importa `core` o `cad`.

Salida:
- `grep -rln "freecad.vdo.core" freecad/vdo/ui` = 0.
- `test_arquitectura.py` en verde.

Riesgo: medio. Muchos archivos; un commit por bloque (coco, paneles, inspector, corte, herrajes).

---

### F8 — Paneles delgados y formularios declarativos

**Objetivo:** R6. Los 5 paneles con `accept()` ≤ 15 líneas y formulario por `FormBuilder`.

Orden: `zocalo` → `panel` → `puerta` → `cajon` → `coco_unified`.

Para cada panel:
1. Capturar, antes de migrar, la lista de campos, valores por defecto, rangos y dependencias (script que lee el panel actual en nivel 3, o se especifica a mano desde el código). Guardar en `tests/golden/formularios/<panel>.json`.
2. Escribir la especificación en `app/formularios.py` como datos.
3. Reemplazar `_crear_widget` por una llamada a `FormBuilder`.
4. Reemplazar `accept()` por: leer → `Parametros` → caso de uso → cerrar (M-11).
5. Mover la lógica de `_on_*` que sea de dominio a `app/`. Lo que sea solo presentación queda en el panel.
6. Test de paridad: la especificación generada coincide con el golden de formulario.

`coco_unified` (1.199 líneas, 9 imports de core, `accept` de 101 líneas): dividir en subpaneles declarativos (`DivisionesEditor` y `PanelHeaderWidget` ya están en `ui/widgets_coco.py`) antes de migrarlo; cada subpanel con su especificación.

Salida:
- `accept()` ≤ 15 líneas en los 5 (medición AST).
- `_crear_widget` de los 5 paneles ≤ 20 líneas cada uno (solo llama al builder).
- Tests de paridad de formularios en verde (nivel 1).
- Verificación visual en F17.

Riesgo: alto para `coco_unified`. Es el panel más grande; se migra al final de la fase.

---

### F9 — Errores y excepciones

**Objetivo:** R7.

Pasos:
1. Crear `core/errores.py` (M-13).
2. Clasificar los 65 `except … pass` por sitio (tabla en `docs/PROGRESO_REFACTOR.md`):
   - si el error es esperado (p. ej. `KeyError` al buscar una opción opcional): reemplazar por consulta explícita (`dict.get`, comprobación previa) y eliminar el `try`;
   - si es un fallo real: propagar como error tipado o registrar con `app/registro.py` y devolver un resultado explícito;
   - prohibido dejar `pass`.
3. Los 135 `except Exception` de `freecad/`:
   - en `core/`, `cad/`, `app/`: 0. Se sustituyen por excepciones tipadas o se eliminan.
   - en `ui/` y `commands.py`: solo en el borde (manejador de comando o diálogo), con registro y mensaje al usuario.
4. `handlers.py` y un test (`test_arquitectura.py`) verifican que no vuelve a aparecer ninguno.

Salida:
- `handlers.py` (solo-pass) = 0.
- `except Exception` en `core/`, `cad/`, `app/` = 0.
- En `ui/` y `commands.py`, cada `except Exception` tiene una línea de registro (verificado por script).

Riesgo: medio. Los `except` mal clasificados pueden ocultar errores reales; por eso el paso 2 exige una tabla con decisión por sitio.

---

### F10 — Complejidad

**Objetivo:** R8. Ninguna función > 100 líneas; `ruff` C901 ≤ 12.

Pasos (las 16 de §1 primero; luego las de 100–150 líneas que aparezcan):
1. `coco_core.execute` (428) — ya dividida en F4.13; verificar ≤ 100.
2. `cajon_despiece.calcular_despiece` (326) — dividir por etapas (caja, frente, herrajes, expulsor).
3. `widgets_coco._crear_widget` (247), `_actualizar_inspector` (222) — ya en `ui/widgets_coco.py`; dividir por bloque visual o por datos.
4. `chassis_widget._init_ui` (238), `paintEvent` (210) — dividir pintura por capa (fondo, piezas, cotas).
5. `box_controller._construir_ui` (232) — por sección.
6. `reengrose.generar_tiras_perimetrales` (220) — por lado.
7. `universal_inspector.__init__` (207) — extraer constructores de secciones.
8. `coco_spaces.generar_divisiones_matriz` (195) — ya en F4.12; verificar.
9. `zocalo_core.calcular_geometria_zocalo` (189) — ya en F4.8; verificar.
10. `coco_unified._crear_widget` (172), `puerta_task._crear_widget` (169), `cajon_task._crear_widget` (209) — por F8.
11. `puerta_core.execute` (157), `cajon_core.execute` (152) — por F4.10–F4.11; verificar.

Cada división: golden o snapshot de la salida antes y después (F2). En UI, verificación visual en F17.

Salida:
- `ast_scan` con umbral 100: 0 funciones.
- `ruff check --select C901 --config max-complexity=12`: 0.

Riesgo: medio. Muchas funciones de UI sin golden: para ellas, la prueba de regresión es nivel 3.

---

### F11 — Duplicación y código muerto

**Objetivo:** R9.

Pasos:
1. Clones actuales: `_cargar_reengroses`/`_leer_reengroses` → una sola función en `core/reengrose.py`; `_on_n_changed` ×2 → una.
2. Ejecutar `tools/auditoria/defs_no_usadas.py` (creado en F0) y eliminar lo que no se usa (verificar importadores y referencias por cadena en `package.xml`, `InitGui.py` y JSON).
3. Normalizar reglas repetidas que queden tras F4: `_normalizar_apertura` y cualquier constante duplicada → `core/aperturas.py`.
4. Fusionar módulos pequeños con un único importador (M-20), en el paso de nombres (F13).

Salida:
- `clones.py` = 0. `defs_no_usadas.py` = 0.
- Golden = 100 %.

Riesgo: bajo.

---

### F12 — Tema, estilos y SVG

**Objetivo:** R10 (colores) y M-12.

Pasos:
1. Crear `ui/tema.py` con todos los tokens (fondo, fondo2, texto, texto_suave, borde, acento `#007acc`, error, aviso, éxito).
2. Sustituir los 368 literales en 16 archivos por tokens. Mapear cada color a un token; los que no encajan, se añade token nuevo (no se deja literal).
3. Mover los SVG embebidos en código (`ui/vdo_theme` y `ui/vdo_*`) a `Resources/icons/`. Cargar por ruta.
4. Capturas de referencia de F0 (si FreeCAD está disponible en F0) para comparar en F17.

Salida:
- `grep -rnE "#[0-9a-fA-F]{6}" freecad` fuera de `ui/tema.py` = 0.
- Ningún SVG embebido en `.py` (grep de `<svg` = 0 fuera de `Resources/`).

Riesgo: bajo en lógica, medio visual. El único cambio visual autorizado es el acento (M-12); se verifica en F17.

---

### F13 — Nombres y estructura

**Objetivo:** minimalismo de módulos (M-20).

Pasos:
1. Script `tools/auditoria/renombrar.py` que aplica `vdo_<x>.py` → `<x>.py` dentro de `freecad/vdo/` y reescribe imports en paquete y tests. Ejecutar en un commit único y verificar golden y suite (niveles 1 y 2).
2. Fusionar módulos de < 80 líneas con un único importador (lista generada por el script; decisión registrada por módulo en `PROGRESO_REFACTOR.md`).
3. Renombrar tests para que el nombre describa el comportamiento (`test_<area>_<comportamiento>`), y eliminar tests duplicados de un mismo comportamiento.
4. `Init.py`, `InitGui.py`, `package.xml` no se renombran (requisito de FreeCAD).

Salida:
- Ningún archivo `vdo_*.py` dentro de `freecad/vdo/` salvo los que M-21 exige (ninguno).
- Golden = 100 %, suite nivel 1 en verde.
- Número de módulos de `freecad/vdo/` anotado en `ARQUITECTURA.md` con su lista.

Riesgo: medio. Churn grande. Se hace en un único commit para que `git blame` sea recuperable (`git log --follow`).

---

### F14 — Tipado, lint y estilo

**Objetivo:** R10.

Pasos:
1. `pyproject.toml` (en raíz) con configuración de `ruff` (reglas: `E,F,W,B,UP,C901,SIM,I,RUF`) y `mypy` (`strict = true` para `core/`, `app/`, `cad/`; `ignore_missing_imports` solo para `FreeCAD`, `Part`, `PySide*`).
2. Resolver todo lo que reporten `ruff` y `mypy`. No se usan `# noqa` ni `# type: ignore` sin motivo escrito en la línea.
3. Tipado completo de firmas públicas en `core/`, `app/`, `cad/`.
4. `ruff format` solo en archivos tocados por las fases anteriores (no reformatear todo de golpe).

Salida:
- `ruff check .` = 0. `mypy` = 0 errores en `core/`, `app/`, `cad/`.
- Cada `noqa` / `type: ignore` tiene motivo.

Riesgo: bajo-medio (los tipos pueden exponer errores reales; se corrigen en código, no se silencian).

---

### F15 — Herramientas auxiliares

**Objetivo:** que nada quede a medias fuera del paquete.

Pasos:
1. `tools/erp_sync/`: `tsc --noEmit` = 0; variable `VDO_ERP_URL` sin default; README; sin secretos (grep).
2. `tools/vdo_optimizador_cli.py`: test de humo en `tests/test_cli_optimizador.py` (nivel 1).
3. `tools/build_zip.py`: test que construye el zip en directorio temporal y verifica que contiene solo `package.xml`, `Init.py`, `InitGui.py`, `freecad/`, `Resources/`, `LICENSE`, `README.md`.
4. `tools/auditoria/`: README con cómo ejecutar `verificar.py`.

Salida: los cuatro tests/comandos verdes.

Riesgo: bajo.

---

### F16 — Documentación final y ADRs

**Objetivo:** R12.

Pasos:
1. `docs/ARQUITECTURA.md` reescrito desde cero: capas (M-04), dependencias permitidas, puertos (M-06), flujo de un comando (ejemplo: crear zócalo), cómo añadir un módulo, cómo correr cada nivel de prueba, lista de módulos (F13).
2. `docs/adr/ADR-001` … uno por decisión M-01…M-24 con contexto, decisión, consecuencias y referencia al commit/etiqueta.
3. `docs/DEUDA_TECNICA.md`: solo ítems con dueño y fecha; si no hay ninguno abierto, el documento lo dice explícitamente.
4. `docs/GLOSARIO.md` (desde `vdo_diccionario_semantico.md`); los términos de código coinciden con el glosario (test de nombres en `tests/test_docs.py`: cada `[[enlace]]` y cada término de `GLOSARIO` aparece en código o se marca como término de usuario).
5. `docs/PROGRESO_REFACTOR.md`: entrada final por fase con cifras de `verificar.py`.
6. `CHANGELOG.md` con `2.0.0`.
7. Eliminar duplicados de `docs/` (ya archivados en F1–F9; se verifica).

Salida:
- `test_docs.py` en verde.
- `verificar.py` y `PROGRESO_REFACTOR.md` dan las mismas cifras.

Riesgo: bajo.

---

### F17 — Verificación real en FreeCAD

**Objetivo:** R14. Esta fase no se puede cerrar sin FreeCAD 1.x.

Pasos:
1. **Nivel 2 (FreeCAD sin GUI):** `freecadcmd tools/run_tests.py` con `VDO_TEST_DIR=tests`. Todo verde; las omisiones son solo las de `omisiones.txt`.
2. **Golden de geometría en FreeCAD:** `golden.py --verificar --freecad`.
3. **Nivel 3 (GUI):** con FreeCAD GUI, script de humo que, para cada comando de `commands.py`: lo activa, abre el panel, lo acepta y lo cancela. Registra errores en log. Debe completar sin excepción no registrada.
4. **Capturas:** para cada panel y para el inspector, captura antes (de F0, si existe) y después. Diferencias solo en el acento `#007acc` (M-12). Cualquier otra diferencia es un defecto.
5. **Recargar catálogo:** comando explícito probado.
6. **Instalación limpia:** instalar el zip de `build_zip.py` en un perfil temporal de FreeCAD (HOME temporal, para no tocar `~/.local/share/FreeCAD/Mod/` del usuario) y verificar que el workbench carga. Antes de tocar nada, comprobar si el usuario tiene `VDO` enlazado en su `Mod/`, y no modificarlo.

Salida:
- Registro de F17 en `PROGRESO_REFACTOR.md` con fecha, versión de FreeCAD, comandos y resultados.
- Capturas en `docs/metricas/capturas/` (si el usuario acepta versionarlas; si no, en un directorio fuera del repo y se referencia el hash).

Riesgo: alto por dependencia externa. Si no hay display, el nivel 3 se queda pendiente y **la auditoría final no puede dar 10 en R14**; se declara explícitamente.

---

### F18 — Auditoría final

**Objetivo:** que la auditoría calcule la rúbrica sobre el código final.

Pasos:
1. `tools/auditoria/verificar.py --json docs/metricas/final.json`.
2. Revisión manual por el checklist de §2 (R1–R14). Cada criterio marcado con evidencia.
3. Lista de cosas que la auditoría humana pueda objetar, con respuesta escrita en `docs/ARQUITECTURA.md` o en un ADR.
4. Tabla final antes/después en `PROGRESO_REFACTOR.md`.
5. Etiqueta `vdo10-final`.

Salida:
- 14 de 14 dimensiones con evidencia. Si alguna no llega a 10, el plan lo dice con su causa; no se redondea.

---

## 5. Pruebas en tres niveles

| Nivel | Qué prueba | Requiere | Dónde corre |
|---|---|---|---|
| **1 — pura** | `core/`, `app/` con `Documento` en memoria; golden de cálculo; arquitectura; docs; herramientas | Python 3 | cualquier máquina (`tools/run_tests.py`) |
| **2 — FreeCAD** | `cad/`, golden de geometría, integración de documentos | `freecadcmd` | con FreeCAD instalado |
| **3 — GUI** | paneles, comandos, inspector, capturas | FreeCAD GUI con display | con FreeCAD GUI |

Reglas:
- Un criterio de §4 que exige nivel 2 o 3 no se da por cumplido con solo nivel 1.
- Los skips están en `tests/soporte/omisiones.txt` con nivel y motivo. Un skip fuera de la lista = fallo.
- La suite de nivel 1 no instala mocks en `sys.modules` (M-18).

---

## 6. Comandos de verificación (referencia)

Nota: `freecadcmd` es el binario nativo instalado con pacman (F0.5). Si el paquete expone otro nombre, se usa ese y se registra en `PROGRESO_REFACTOR.md`. Las pruebas de nivel 2 usan el Python embebido de FreeCAD, distinto de `python3`; los golden de nivel 1 se verifican con `python3 -I` y los de nivel 2 con `freecadcmd`.

```bash
# Suite nivel 1
VDO_TEST_DIR=tests VDO_TEST_OUT=/tmp/t1.txt python3 tools/run_tests.py

# Suite nivel 2
VDO_TEST_DIR=tests VDO_TEST_OUT=/tmp/t2.txt freecadcmd tools/run_tests.py

# Métricas y umbrales (código ≠ 0 si falla)
python3 -I tools/auditoria/verificar.py

# Lint y tipos
.venv/bin/ruff check .
.venv/bin/mypy freecad/vdo/core freecad/vdo/app freecad/vdo/cad

# Golden
python3 -I tools/auditoria/golden.py --verificar

# Herramienta ERP
cd tools/erp_sync && npm run typecheck
```

---

## 7. Riesgos principales y mitigación

| Riesgo | Probabilidad | Mitigación |
|---|---|---|
| Cambio de salida numérica al mover cálculo a `Plan` (F4) | Media | Golden de F2 antes de cada paso; un módulo por commit. |
| Churn de nombres (F13) rompe imports | Media | Script de renombrado + suite nivel 1 y 2 en el mismo commit. |
| `coco_unified` (1.199 líneas) se atasca (F8) | Alta | Dividir en subpaneles antes de migrar; migrar al final. |
| Sin FreeCAD disponible, F17 queda bloqueada | Media (instalación nativa en curso) | Gate explícito en F0.5; el nivel 1 avanza sin FreeCAD. |
| Simplificación excesiva rompe UX | Media | Capturas de F17; único cambio visual autorizado es el acento. |
| Exceptions mal clasificadas ocultan fallos (F9) | Media | Tabla con decisión por sitio; prohibido `pass`. |

---

## 8. Qué no está en este plan (y por qué)

- **Nuevas funciones de producto:** fuera de alcance (regla 9 de §0).
- **Motor de despiece único para cajón y puerta:** no se hace. La lógica de apertura se unifica (M-16); los motores siguen separados porque no comparten cálculo. Esto es una decisión de diseño, no una deuda.
- **Publicación en el catálogo oficial de FreeCAD:** fuera de alcance.
- **Reescritura de la historia de git:** no se hace (M-02).

---

## 9. Qué queda para el humano

- ~~Autorizar la instalación de FreeCAD~~ — hecho por el usuario (instalación nativa con pacman). Falta confirmar que termina y que la versión es 1.x (F0.5).
- Decidir si las capturas de F17 se versionan (F17.4).
- Revisar el diff de cada golden regenerado (F2.4).
- Aprobar el cambio de versión a `2.0.0` (M-23).
- Aprobar el cambio de acento (M-12).

Todo lo demás lo decide el plan.
