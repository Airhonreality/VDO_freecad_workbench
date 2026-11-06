Sustituido por docs/PLAN_MINIMALISMO_VDO.md

> **SUSTITUIDO** por `docs/PLAN_MINIMALISMO_VDO.md`. No ejecutar este documento.

# Plan de correcciones F19

**Estado:** vinculante. Se ejecuta sobre `refactor/vdo-10` (HEAD `7e389be`, tag `vdo10-final`).
**Origen:** auditoría del estado `vdo10-final`, que dio **2/10** y **FALLA** en el propio verificador (11 de 20 métricas). No se acepta el tag `vdo10-final` como cierre.
**Objetivo:** que una auditoría independiente dé 10/10 según la rúbrica R1–R14 de `docs/PLAN_MAESTRO_VDO.md` §2, sin deuda sin dueño y sin fallos ocultos.

---

## 0. Reglas (obligatorias, más estrictas que el plan maestro)

1. **Primero la verdad, luego el código.** F19.0 corrige el medidor (runner y verificador) antes de tocar funcionalidad. Mientras el medidor oculte fallos, ningún arreglo se puede dar por bueno.
2. **Prohibido reclasificar fallos como SKIP.** Un test se omite solo si su entorno falta, y esa comprobación se hace en tiempo de ejecución (`requiere_freecad`, `requiere_gui`, `requiere_qt`), nunca por lista. `tests/soporte/omisiones.txt` se elimina.
3. **Prohibido ajustar un test para que pase** sin demostrar que el test estaba mal. Si el comportamiento cambia, es una regresión hasta que se pruebe lo contrario, con evidencia en el registro.
4. **Golden masters:** se regeneran solo con aprobación humana del diff (`golden.py --regenerar` pide confirmación explícita). El agente no regenera para hacer pasar un test.
5. **Un commit por subfase**, en `refactor/vdo-10`. Mensaje en español, terminado en `Co-Authored-By: Claude Haiku 5.5 <noreply@anthropic.com>`. Sin push. Sin merge a `main`.
6. **Criterio de parada:** si una subfase rompe un criterio ya cumplido, se revierte esa subfase (sin tocar commits anteriores) y se registra el motivo.
7. **Entorno:** FreeCAD 1.1.4 nativo (`/usr/bin/freecadcmd`). El paquete se enlaza desde `~/.local/share/FreeCAD/Mod/VDO` → repo. **No cambiar ese enlace** salvo que la subfase lo indique explícitamente, y en ese caso restaurarlo al terminar (verificar con `readlink`).
8. **Registro:** cada subfase deja entrada en `docs/PROGRESO_REFACTOR.md` con cifras de los comandos de §5, pegadas como salida real.

---

## 1. Hallazgos que F19 debe cerrar (con evidencia)

| ID | Hallazgo | Evidencia reproducida |
|---|---|---|
| H1 | `crear_pieza` devuelve `None` con documento activo: no se crea ningún módulo | `/tmp/vdo_audit/repro/repro_panel.py`: previo `<Part::Feature>`, actual `None` |
| H2 | Copia mutilada de `vdo_guardian` en `core/`; cuatro módulos la llaman sin documento | `core/vdo_panel_core.py:265`, `vdo_coco_core.py:588`, `vdo_zocalo_core.py:369`, `vdo_cajon_core.py:443` |
| H3 | `forma_ref` perdió el `try/except` con fallback a caja | comparación `vdo_reengrose.py` (previo) vs `cad/geometria.py` (actual) |
| H4 | 21 ERROR + 5 FAIL en nivel 2 reportados como 7 | log de `freecadcmd tools/run_tests.py`; `run_tests.py` líneas 91–140 |
| H5 | 19 errores de nivel 1 reclasificados como "requiere entorno" | `grep "requiere entorno"` en la salida de nivel 1 |
| H6 | Motivos falsos en `omisiones.txt` (p. ej. "requiere PySide" para un fallo de geometría) | `test_coco_reengrose`: `NoneType … Shape` |
| H7 | Regla R5 cuenta variables locales (1261) en vez de estado de módulo (9 reales) | `verificar.py` `_m5_estado_inmutable` usa `ast.walk` |
| H8 | Regla R9 cuenta métodos como no usados (322) en vez de funciones de módulo (17 candidatos) | `verificar.py` `_contar_defs_no_usadas` |
| H9 | `app/vdo_api.py` reexporta todo core; 18 módulos de UI pasan por él | `app/vdo_api.py` (210 líneas, sin lógica) |
| H10 | 9 módulos de UI escriben en objetos FreeCAD o llaman a `recompute` | grep de `.Ancho =`, `addObject`, `recompute()` en `ui/` |
| H11 | Solo 1 caso de uso en `app/` de 13 exigidos | `app/casos_uso/` |
| H12 | 9 estados de módulo mutables | `vdo_bim_bridge.py:21-22` (`_estado`, `_conexiones`), `vdo_cutting_list_preview.py:25`, `vdo_export_cutting_list.py:21`, `vdo_nesting_workflow.py:11`, `ui/vdo_qt.py:9`, `vdo_chassis_widget.py:103`, `vdo_box_controller.py:53`, `app/registro.py:12` |
| H13 | 24 funciones > 100 líneas; `ruff` C901 con 1 incidencia | `verificar.py` R8 |
| H14 | 2 grupos de clones: `_cargar_reengroses`/`_leer_reengroses`, `_on_n_changed`×2 | `verificar.py` R9 |
| H15 | 17 definiciones de nivel módulo sin referencias (revisar, no asumir muertas) | script de revisión de F19.0 |
| H16 | Segfault al salir de FreeCAD en nivel 2 (`exit 139` ya en el estado previo) | `PySide6/QtWidgets` en `destroyQCoreApplication` |
| H17 | Smoke L3 con `FAIL=4`, gap de API y `NoneType Shape` | `test_smoke_l3_desk_assembly` |
| H18 | `test_bisel_45` falla: `makePolygon() takes no keyword arguments` | log nivel 2 |
| H19 | ruff: 280 errores (el resumen decía 405) | `ruff check freecad` |
| H20 | mypy strict: 1121 errores en 35 archivos | `mypy freecad/vdo/core freecad/vdo/app freecad/vdo/cad` |
| H21 | 417 literales hex fuera de `ui/tema.py` (DEUDA dice 436) | `verificar.py` R10 |
| H22 | 3 ADR de 24 exigidos | `docs/adr/` |
| H23 | `DEUDA_TECNICA.md` sin dueño ni fecha; no recoge H1–H22 | lectura |
| H24 | `PROGRESO_REFACTOR.md` con títulos de fase incorrectos, faltan F7/F8/F18 | lectura |
| H25 | `final.json` dice FALLA; el resumen dice "11/14 cumplen" | `docs/metricas/final.json` |
| H26 | Goldens de 8 módulos de 19 exigidos | `tests/golden/` |

---

## 2. Decisiones cerradas (F19)

| ID | Decisión |
|---|---|
| F19-D1 | Un fallo nunca se oculta. El runner reporta ERROR y FAIL tal cual del log de unittest. |
| F19-D2 | Omisiones solo por detección de entorno en runtime (decoradores `requiere_*`). Se elimina `omisiones.txt`. |
| F19-D3 | Una sola copia de `vdo_guardian`: `cad/vdo_guardian.py`. `core/vdo_guardian.py` se elimina. La creación de documentos la hace `app/`. |
| F19-D4 | `vdo_api.py` se elimina. La UI habla con casos de uso de `app/` y con DTOs de `app/`. No reexporta core. |
| F19-D5 | Un caso de uso por operación de usuario (13 en total, lista en F19.4). |
| F19-D6 | Escritura en objetos FreeCAD solo en `cad/`. La UI pide a `app/`. |
| F19-D7 | Estado de módulo mutable: prohibido. Se convierte en atributo de objeto, en contexto inyectado, o en constante inmutable. |
| F19-D8 | `mypy --strict` en `core/`, `app/`, `cad/` (0 errores). En `ui/`: `mypy --check-untyped-defs` (0 errores). Los imports de FreeCAD/PySide se marcan con `ignore_missing_imports` solo para esos paquetes. |
| F19-D9 | `ruff check` = 0 con la configuración de `pyproject.toml`. Cada `noqa` lleva motivo en la misma línea. |
| F19-D10 | Tema: 0 literales hex fuera de `ui/tema.py`. Los SVG embebidos pasan a `Resources/icons/`. |
| F19-D11 | Umbral de función: 100 líneas. Sin excepciones. |
| F19-D12 | El verificador tiene sus propios tests (`tests/test_verificar.py`). Si una regla está mal, el test lo detecta. |
| F19-D13 | DEUDA_TECNICA: cada ítem lleva **responsable** (rol: "usuario" para decisiones, "ejecutor" para trabajo pendiente) y **fecha límite**. Si no hay ítems, el documento lo dice. |
| F19-D14 | El tag `vdo10-final` no se mueve. El cierre se marca con `vdo10-f19` solo cuando F19.13 pasa. |

---

## 3. Fases

### F19.0 — Medidor honesto

**Objetivo:** que el runner y el verificador digan la verdad antes de arreglar nada. Después de esta fase, los fallos aparecerán (no es una regresión, es visibilidad).

Pasos:
1. `tools/run_tests.py`: eliminar la reclasificación de ERROR/FAIL a SKIP (líneas 91–140). El resumen usa solo `unittest` (`testsRun`, `failures`, `errors`, `skipped`).
2. Crear `tests/soporte/requisitos.py` con decoradores:
   - `requiere_freecad` → comprueba `import FreeCAD` real (no mock) en tiempo de ejecución.
   - `requiere_gui` → comprueba `FreeCADGui` y `DISPLAY`/`WAYLAND_DISPLAY`.
   - `requiere_qt` → comprueba `PySide6` importable.
   Cada decorador hace `SkipTest` con el motivo exacto detectado.
3. Eliminar `tests/soporte/omisiones.txt`. Aplicar los decoradores a los tests que hoy dependen de la lista (los 16 archivos de la lista).
4. `tools/auditoria/verificar.py`:
   - R5: recorrer solo `tree.body` (nivel módulo), excluir constantes en mayúsculas y `__all__`.
   - R9: recorrer solo `tree.body` (funciones y clases de nivel módulo); la búsqueda de referencias incluye tests, InitGui e Init.
   - Ambas reglas se documentan con su definición exacta en `docs/metricas/README.md`.
5. Crear `tests/test_verificar.py`: fixtures pequeñas con código a propósito incorrecto (una variable local no debe contar en R5; un método no debe contar en R9; un `except … pass` debe contar en R7).
6. Revisar a mano los 17 candidatos de R9. Cada uno: **usado** (y entonces la regla debe reconocerlo), o **muerto** (se borra en F19.7). Registrar la decisión por candidato.
7. Registrar la línea base de F19 en `docs/metricas/f19_base.json`.

Salida:
- `freecadcmd tools/run_tests.py`: el resumen muestra ERROR y FAIL reales. Se anota el número en el registro (se espera ≥ 26).
- `python3 -I tools/auditoria/verificar.py`: R5 = 9 y R9 = 17 (o los valores exactos tras la revisión manual, anotados).
- `tests/test_verificar.py` en verde.

Riesgo: bajo técnicamente, alto de percepción: el número de fallos sube. Es correcto.

---

### F19.1 — Restaurar la creación de módulos (H1, H2, H3)

**Objetivo:** que `crear_pieza`, `make_coco`, `crear_zocalo` y `make_cajon` vuelvan a crear objetos.

Pasos:
1. Eliminar `freecad/vdo/core/vdo_guardian.py` (F19-D3). Antes, verificar con grep que nada del core lo necesita después de los cambios de este paso.
2. En `core/vdo_panel_core.py`, `vdo_coco_core.py`, `vdo_zocalo_core.py`, `vdo_cajon_core.py`: la función recibe el documento como parámetro (`doc`) y no lo busca. El caso de uso de `app/` lo pasa. Los llamadores actuales (`app/vdo_creacion.py:46`, `commands.py:68`) se revisan para que pasen el documento.
3. Restaurar `forma_ref` con el mismo comportamiento que el original: fallback a caja cuando falla el extrusionado. Comparar con `git show b78de04:freecad/vdo/core/vdo_reengrose.py` línea a línea y dejar una nota de equivalencia en el commit.
4. Añadir test de nivel 2 `tests/test_creacion_modulos.py` (decorador `requiere_freecad`):
   - `crear_pieza` con documento devuelve objeto con `Shape` válido.
   - `make_coco`, `crear_zocalo`, `make_cajon` idem.
   - Cada test crea y cierra su documento.
5. Golden de creación: `tests/golden/creacion_<modulo>.json` con las propiedades (no el objeto) del módulo creado. Generado **desde el código previo** (`b78de04`) con enlace temporal al worktree, y aprobado por el usuario antes de commit.

Salida:
- `repro_panel.py` devuelve `<Part::Feature>`.
- `test_creacion_modulos.py` en verde en nivel 2.
- Los goldens de creación coinciden con el código previo.
- `grep -rn "vdo_guard()" freecad` = 0 llamadas sin documento.

Riesgo: alto. Es el corazón del workbench. Requiere aprobación del golden antes de avanzar.

---

### F19.2 — Nivel 2 en verde (H4, H5, H6, H17, H18)

**Objetivo:** que todos los tests de nivel 2 pasen con la causa corregida, no con un ajuste del test.

Subfases por causa, cada una con commit propio:

- **F19.2a — Reengrose.** `test_reengrose_l1`, `test_coco_reengrose`, `test_coco_reengrose_avanzado`, `test_layout_reengrose`. Causa: H1 y H3. Tras F19.1, reejecutar y clasificar lo que quede. Cualquier fallo restante se documenta con traceback y se corrige en el código.
- **F19.2b — Comandos.** `test_comandos_workbench` (5 fallos "La factory no devolvió un objeto"). Causa: H1. Verificar que cada comando devuelve y ejecuta.
- **F19.2c — Cajón bisel.** `test_cajon_core.test_bisel_45_crea_herramienta_triangular` (H18). Causa: llamada a `Part.makePolygon` con argumentos nombrados. Corregir la llamada al API real de FreeCAD. Si `makePolygon` no acepta esos nombres, cambiar a la forma posicional que sí acepta, y comprobar contra la documentación de FreeCAD 1.1 con `freecadcmd -c "import Part; help(Part.makePolygon)"`.
- **F19.2d — Smoke L3.** `test_smoke_l3_desk_assembly` (H17). Causa: depende de F19.1 y de los gaps de API. Tras F19.1, reejecutar. Los gaps se resuelven por API real, no por lista blanca.
- **F19.2e — Resto.** Cualquier fallo de nivel 2 que siga tras F19.2a–d: cada uno con causa escrita.

Salida:
- `freecadcmd tools/run_tests.py` con **0 ERROR, 0 FAIL**. Las omisiones son solo por entorno detectado (p. ej. GUI sin display), con el motivo impreso.
- Cada subfase con su commit y su entrada en el registro.

Riesgo: medio. Puede aparecer más de una causa por test; se documenta cada una.

---

### F19.3 — Segfault al salir (H16)

**Objetivo:** que el proceso de nivel 2 termine con código 0.

Causa previa conocida: `QCoreApplication` creada en tests headless que PySide destruye al finalizar el intérprete.

Pasos:
1. Reproducir: `freecadcmd tools/run_tests.py; echo $?` debe dar 139 en el estado previo también (ya medido).
2. Localizar qué test crea `QtWidgets.QApplication`. Mover esa creación a un fixture que la deja viva hasta fin de proceso, o eliminar la creación si el test no necesita widgets (`requiere_gui` lo decide).
3. Si el segfault persiste, aislar cada módulo de test en su propio proceso en el runner (`subprocess` por archivo). Documentar la decisión en ADR-005.
4. Repetir 5 veces: `for i in 1 2 3 4 5; do freecadcmd tools/run_tests.py >/dev/null 2>&1; echo $?; done` → todas 0.

Salida: código de salida 0 en 5 de 5 ejecuciones.

Riesgo: medio. Depende de la causa exacta.

---

### F19.4 — Frontera real UI → app (H9, H10, H11)

**Objetivo:** que la UI no conozca core ni escriba en FreeCAD.

Pasos:
1. Lista de los 13 casos de uso (F19-D5):
   `crear_hoja`, `crear_panel`, `crear_zocalo`, `crear_cajon`, `crear_puerta`, `crear_coco`, `editar_modulo`, `colocar_modulo`, `exportar_lista_corte`, `optimizar_corte`, `nesting`, `consultar_herrajes`, `recargar_catalogo`.
2. Cada caso de uso vive en `app/casos_uso/<nombre>.py`, recibe un DTO de entrada (`dataclass` frozen en `app/dto.py`) y un `Documento` (puerto), y devuelve un DTO de salida.
3. Eliminar `app/vdo_api.py`. Cada módulo de UI que lo importaba pasa a importar del caso de uso o del DTO.
4. Las 9 escrituras en FreeCAD dentro de `ui/` se mueven a `cad/` o a los casos de uso. La UI recibe datos listos para mostrar.
5. Test de arquitectura `tests/test_arquitectura.py` (AST):
   - `ui/` no importa `freecad.vdo.core`, `freecad.vdo.cad` ni `freecad.vdo.app.vdo_api`.
   - `ui/` no contiene asignaciones a atributos de objetos FreeCAD ni llamadas a `addObject`/`recompute`.
   - `core/` no importa `app`, `ui` ni `cad`.
   - `app/` no importa `ui`.
   - `cad/` no importa `ui` ni `app`.

Salida:
- `verificar.py`: R1 = 0 (sin `vdo_api`), R3 = 0, R4 = 0 (13 casos de uso).
- `test_arquitectura.py` en verde.
- Ningún caso de uso importa PySide.

Riesgo: alto. Es la mayor parte del trabajo de UI. Se hace por bloques (coco, paneles, inspector, corte, herrajes, comandos) con un commit cada uno y el nivel 2 en verde tras cada bloque.

---

### F19.5 — Estado de módulo (H12)

**Objetivo:** R5 = 0.

Tratamiento por caso:
- `vdo_bim_bridge._estado`, `_conexiones`: pasan a un objeto `EstadoBim` creado por `registrar_integracion_bim()` y guardado en el contexto de `app/composicion.py`. Ninguna función lo usa por nombre de módulo.
- `_macro_dir` (×2) y `_vdo_macro_dir`: se reemplazan por `app/rutas.py` → `ruta_recursos()` sin estado.
- `ui/vdo_qt._QDoubleSpinBox`: alias de clase, se convierte en constante en mayúsculas (`QDOUBLESPINBOX_BASE`) o se importa directamente.
- `get_svg_icon` (×2): alias de función, se elimina el alias y se usa la función de `ui/tema.py`.
- `app/registro._logger`: se renombra a `LOGGER` (constante) y se acepta.

Salida: `verificar.py` R5 = 0.

---

### F19.6 — Complejidad (H13)

**Objetivo:** R8 = 0 (ninguna función > 100 líneas; C901 ≤ 12).

Orden: primero las de core (ya tienen golden), luego las de UI (verificación en nivel 3 con capturas).

| Función | Líneas | Estrategia |
|---|---|---|
| `cajon_despiece.calcular_despiece` | 326 | Por etapas: caja, frente, herrajes, expulsor. Golden previo obligatorio. |
| `cajon_core.execute` | 152 | Plan puro + aplicación en `cad/`. |
| `puerta_core.execute` | 157 | Idem. |
| `chassis_widget._init_ui`, `paintEvent` | 238, 210 | Por bloques visuales y por capas de pintura. |
| `box_controller._construir_ui` | 232 | Por secciones. |
| `universal_inspector.__init__` | 207 | Constructores de sección. |
| `widgets_coco._crear_widget`, `_actualizar_inspector` | 247, 222 | Por bloque. |
| `reengrose.generar_tiras_perimetrales` | 220 | Por lado. Golden de reengrose obligatorio. |
| ... (resto de la lista de `verificar.py`) | | Mismo método. |

Reglas:
- Ninguna división sin golden o snapshot previo que pase en la versión dividida.
- La división de `generar_tiras_perimetrales` previa falló por variables inmutables entre ámbitos anidados. Las funciones auxiliares devuelven valores nuevos, no reasignan variables del llamador.

Salida: `verificar.py` R8 = 0; `ruff --select C901` = 0.

Riesgo: medio-alto en UI. Verificar con nivel 3.

---

### F19.7 — Duplicación y muerte (H14, H15)

Pasos:
1. Clones: `_cargar_reengroses` y `_leer_reengroses` → una función en `core/reengrose.py`. `_on_n_changed` ×2 → una función y un bucle o un parámetro.
2. Candidatos de F19.0 marcados como muertos: se borran. Los marcados como usados: la regla R9 se corrige para reconocerlos, y se documenta.
3. Eliminar cualquier `TODO`/`FIXME` que quede (verificar con grep).

Salida: `clones.py` = 0; R9 = 0.

---

### F19.8 — Lint y tipos (H19, H20)

Pasos:
1. `ruff check --fix` para lo automático. Lo que no es automático se corrige a mano. Sin `# noqa` sin motivo.
2. `mypy --strict` en `core/`, `app/`, `cad/` (F19-D8). Anotar firmas públicas primero, luego internas.
3. `mypy --check-untyped-defs` en `ui/`.
4. Los imports de FreeCAD y PySide tienen `# type: ignore[import-not-found]` **solo** si no hay stubs; si hay stubs, se usan.

Salida: `ruff check freecad` = 0; mypy = 0 en los dos alcances.

Riesgo: medio. Puede descubrir errores reales de tipo; se corrigen en código.

---

### F19.9 — Tema y estilos (H21)

Pasos:
1. Mapear cada uno de los 417 literales a un token de `ui/tema.py`. Si no encaja en ningún token, se crea token nuevo con nombre semántico.
2. SVG embebidos → `Resources/icons/*.svg`, cargados por `ruta_recursos()`.
3. El acento sigue siendo `#007acc` (ya decidido en M-12). Cualquier otro cambio visual se registra y se revisa en nivel 3.

Salida: `verificar.py` R10 hex = 0.

---

### F19.10 — Golden masters completos (H26)

Pasos:
1. Lista de los 19 módulos de dominio (generada con `tools/auditoria/golden.py --listar`). Los 11 que faltan se cubren con golden de nivel 1 o 2 según dependan de FreeCAD.
2. Cada golden con al menos 3 entradas, incluidas las del snapshot de despiece y las de creación de F19.1.
3. `golden.py --verificar` en nivel 1 y, para los de FreeCAD, `freecadcmd tools/auditoria/golden.py --verificar`.

Salida: 19 goldens, 100 % iguales.

---

### F19.11 — Nivel 3 (GUI) (R14)

**Objetivo:** que los paneles y comandos funcionen en la GUI real.

Pasos:
1. Gate: comprobar `echo $DISPLAY $WAYLAND_DISPLAY` y `freecad --version`. Si hay sesión gráfica, se ejecuta. Si no, la fase queda **bloqueada** y se declara así; no se da por cumplida.
2. Script de humo `tests/nivel3/humo_gui.py` (ejecutado con `freecad` GUI en modo script, o con `freecadcmd` y `Gui` disponible): para cada comando de `commands.py`, activarlo, abrir el panel, pulsar Aceptar y Cancelar, comprobar que no hay excepción no registrada.
3. Capturas antes/después (ver F19.9): la diferencia permitida es solo el acento. Cualquier otra diferencia es un defecto.
4. Recarga de catálogo probada.
5. Instalación limpia: `tools/build_zip.py` → zip → instalar en un HOME temporal → cargar el workbench.

Salida: registro de la ejecución (fecha, versión de FreeCAD, comandos, resultados, capturas en `docs/metricas/capturas/` si el usuario acepta versionarlas).

Riesgo: alto por dependencia de sesión gráfica.

---

### F19.12 — Documentación honesta (H22–H25)

Pasos:
1. `docs/adr/`: ADR-001…ADR-024, uno por decisión M-01…M-24, más ADR-025…ADR-030 para F19-D1…F19-D14 agrupadas. Cada uno: contexto, decisión, consecuencias, referencia a commit.
2. `docs/DEUDA_TECNICA.md`: reescrito. Cada ítem con responsable (F19-D13) y fecha. Ítems actuales a incluir mientras existan. Si al cierre no queda ninguno, el documento lo dice.
3. `docs/PROGRESO_REFACTOR.md`: reescrito con una sección por fase real (F0…F19), con cifras pegadas de los comandos. Sin títulos incorrectos. Sin cifras que `verificar.py` contradiga.
4. `docs/ARQUITECTURA.md`: describe las capas reales y las reglas de `test_arquitectura.py`. Lista de módulos actualizada.
5. `docs/metricas/final.json` regenerado al final de F19 (no antes).
6. `CHANGELOG.md`: entrada 2.0.0 (M-23) — pendiente de aprobación del usuario; mientras tanto, entrada en "Sin publicar".

Salida: `verificar.py` y `PROGRESO_REFACTOR.md` coinciden; `test_docs.py` en verde.

---

### F19.13 — Auditoría de cierre (gate final)

**Objetivo:** que el cierre lo mida alguien que no escribió el código.

Pasos:
1. `python3 -I tools/auditoria/verificar.py` → exit 0, todas las métricas OK (incluida R14 si F19.11 se ejecutó).
2. `freecadcmd tools/run_tests.py` → 0 ERROR, 0 FAIL, código de salida 0.
3. `python3 tools/run_tests.py` (nivel 1) → 0 ERROR, 0 FAIL, SKIP solo por entorno detectado.
4. Recalcular a mano, con los scripts de `/tmp` de la auditoría (no reutilizar las reglas corregidas): reclasificaciones = 0, `vdo_api` = 0, estado de módulo = 0, funciones > 100 = 0.
5. Revisión por checklist R1–R14 con evidencia por criterio.
6. Etiqueta `vdo10-f19` sobre el commit de cierre. **No mover `vdo10-final`.**

Salida: informe de cierre en `docs/PROGRESO_REFACTOR.md` con cada criterio marcado. Si alguno no cumple, F19 no se cierra y se dice cuál.

---

## 4. Orden y dependencias

```
F19.0 (medidor) → F19.1 (creación) → F19.2 (nivel 2 verde) → F19.3 (segfault)
                                         ↓
F19.4 (frontera) → F19.5 (estado) → F19.6 (complejidad) → F19.7 (duplicación)
                                         ↓
F19.8 (lint/tipos) → F19.9 (tema) → F19.10 (goldens) → F19.11 (GUI)
                                         ↓
                          F19.12 (documentación) → F19.13 (cierre)
```

F19.0 a F19.3 son obligatorias antes de cualquier otra fase. F19.4 puede empezar en paralelo con F19.5 solo si tocan archivos distintos.

---

## 5. Comandos de medición (referencia)

```bash
# Nivel 1 (modo puro) — sin reclasificación
VDO_TEST_DIR=tests VDO_TEST_OUT=/tmp/f19_n1.txt python3 tools/run_tests.py

# Nivel 2 (FreeCAD nativo)
VDO_TEST_DIR=tests VDO_TEST_OUT=/tmp/f19_n2.txt freecadcmd tools/run_tests.py; echo "exit=$?"

# Métricas y umbrales
python3 -I tools/auditoria/verificar.py; echo "exit=$?"

# Lint y tipos
.venv/bin/ruff check freecad tests tools
.venv/bin/mypy freecad/vdo/core freecad/vdo/app freecad/vdo/cad
.venv/bin/mypy --check-untyped-defs freecad/vdo/ui

# Clones y muerte
python3 -I tools/auditoria/clones.py freecad
python3 -I tools/auditoria/ast_scan.py freecad

# Guard y creación (repro)
freecadcmd /tmp/vdo_audit/repro/repro_panel.py
```

Nota: los scripts de `/tmp` no sobreviven a reinicios. Los que son necesarios para F19 se copian a `tools/auditoria/` en F19.0 (`repro_panel.py`, `handlers.py`, `real_metrics.py`).

---

## 6. Riesgos

| Riesgo | Probabilidad | Mitigación |
|---|---|---|
| Corregir H1 cambia salidas numéricas | Media | Golden de creación desde el código previo (F19.1 paso 5). |
| Aparecen más fallos al corregir el medidor (F19.0) | Alta | Esperado. Son visibilidad, no regresión nueva. |
| La frontera UI→app (F19.4) es muy grande | Alta | Bloques con commit y nivel 2 en verde tras cada uno. |
| Sin sesión gráfica no hay nivel 3 | Media | Gate explícito en F19.11; se declara bloqueada, no se da por cumplida. |
| El agente vuelve a reclasificar fallos | Media | F19-D1 y `test_verificar.py` lo impiden técnicamente. |
| Los decoradores `requiere_*` ocultan tests que sí deberían correr | Baja | Cada decorador imprime el motivo y el nivel; el resumen los cuenta aparte. |

---

## 7. Decisiones del usuario (ya resueltas)

| Decisión | Estado | Detalle |
|---|---|---|
| Goldens regenerados de F19.1 | **APROBADO** | Proceso diff por diff, aprobación humana antes de cada commit. Ningún golden se regenera para hacer pasar un test. |
| Versión `2.0.0` + CHANGELOG | **APROBADO** | Entrada en "Sin publicar"; se publica tras F19.13. Tag `vdo10-final` no se mueve; cierre `vdo10-f19`. |
| Capturas de F19.11 | **NO versionar** | Registro local en `docs/metricas/capturas/` (añadir a `.gitignore`). F19.11 bloqueada si no hay sesión gráfica. |
| Responsable de cada ítem de DEUDA | **CONFIRMADO** | Usuario = decisiones de alcance/arquitectura. Ejecutor = trabajo de código. Matriz en F19-D13. |
| Cambio en `~/.local/share/FreeCAD/Mod/` | **NO autorizado** | El enlace de desarrollo se mantiene tal cual salvo que una subfase lo indique explícitamente. |

Todo lo demás lo decide este plan.
