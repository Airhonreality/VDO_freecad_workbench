# Pendientes humanos — plan de minimalismo

Orden por urgencia. Cada entrada: qué se necesita, por qué, la opción que recomiendo y qué se bloquea mientras no haya respuesta.

---

## P-01 — ~~¿Cuentan como N/A `guardian` y `nesting_presets` en el gate de M0?~~ **Revisado: `guardian` tiene golden; `nesting_presets` pasa a P-10**

- `guardian`: **ya no es N/A.** La decisión anterior se basó en una premisa falsa: el módulo tiene 3 funciones que reciben un documento y lo modifican. Golden de 9 entradas desde `b78de04`, verificado OK contra el código actual (ver `goldens_origen.md`, sección "Guardián").
- `nesting_presets`: **no es N/A todavía.** Tiene 9 métodos estáticos, pero no carga en `b78de04` (`NameError` al importar). Ver P-10.

El texto original sigue abajo, para historial.

(Texto original, para historial:)

- **Qué:** el gate de M0 pide un golden por cada uno de los 19 módulos de dominio.
  - `guardian` (`core/vdo_guardian.py`): sus funciones (`asegurar_hoja_global`, `asegurar_params_local`, `asegurar_documento`, `vdo_guard`) solo crean y ajustan parámetros en el documento. No calculan nada.
  - `nesting_presets` (`core/vdo_nesting_presets.py`): no tiene funciones públicas, solo datos.
- **Por qué:** un golden de estos sería `{}` o un volcado de efectos sobre el documento. No probaría cálculo alguno.
- **Recomiendo:** aceptar N/A con motivo escrito. Si quieres que `guardian` tenga golden, debe ser un volcado de los parámetros creados, y tendría que hacerlo a mano en M0.
- **Bloquea:** el cierre formal de M0 (gate de 19 goldens).

## P-02 — ~~¿Se amplía el serializador para `module_props.rotacion_z`?~~ **Resuelto por el ejecutor**

Implementado: `_serializar` representa `App.Rotation` por eje y ángulo. Golden de 3 entradas, desde `b78de04`, verificado OK bajo FreeCAD. Ver `goldens_origen.md`, sección de reubicación.

(Texto original, para historial:)

- **Qué:** `rotacion_z(grados)` devuelve `App.Rotation`. `golden.py::_serializar` solo ve el nombre del tipo (`"Rotation"`), así que no protege nada.
- **Opciones:**
  1. (recomendada) Serializar `App.Rotation` por `Axis` y `Angle` en `golden.py`. Son ~5 líneas y un golden de 3 entradas.
  2. Aceptar N/A y dejar la función sin golden.
- **Bloquea:** el cierre de M0 y la prueba de `module_props` (un módulo de 0 funciones cubiertas hoy).

## P-03 — ¿Qué pasa con los 4 flujos de creación que no tienen módulo propio?

**Decidido por el ejecutor:** cubiertos por `creacion_modulos.json`, un golden por flujo. Revertible.


- **Qué:** `panel_core`, `cajon_core`, `puerta_core` y `coco_core` solo tienen funciones de creación (`crear_pieza`, `make_cajon`, `make_puerta`, `make_coco`). Están cubiertos por `creacion_modulos.json`, que tiene un golden por flujo.
- **Recomiendo:** dar por cubiertos los 4 con `creacion_modulos.json`, y anotarlo así en el gate.
- **Bloquea:** nada práctico, pero el gate pide "19 goldens" literales.

## P-04 — Cambios de tests de otra sesión sin commitear

- **Qué:** `tests/test_gui_wiring.py` y `tests/test_single_dock_convergence.py` tienen `os._exit(...)` cambiado a `sys.exit(...)` en los bloques `__main__`. Vienen de otra sesión. Yo no los he tocado ni verificado.
- **Riesgo:** en ejecución directa (no por el runner) `sys.exit` con widgets vivos podría volver a segfaultear. No lo he medido.
- **Recomiendo:** revisar y ejecutar cada archivo directamente. Si cae, dejar `os._exit` ahí y documentarlo. O bien reemplazar el bloque por `liberar_widgets()` de `tests/soporte/qt.py`.
- **Bloquea:** nada del plan. Están fuera de la rama. No los commiteo.

## P-05 — Aprobar los goldens sustituidos (no bloquea)

Tres goldens cambian respecto a lo commiteado en `692b76a^`. Cada cambio es una salida esperada distinta, así que va aquí. Detalle en `goldens_origen.md`, sección "Revisión de goldens sustituidos".

- **`creacion_modulos.json`** — antes: 4 flujos, 1 entrada cada uno, esquema plano (props + volumen), sin `make_puerta`, sin generador en el repo. Ahora: 5 flujos × 3 entradas, con `caja`, `label`, `n_solidos`, `props`, `volumen`. **Volúmenes iguales** en los 4 flujos que ya existían (4320000, 28639296, 3866400, 7417634.708). **Cambia el esquema.** `make_cajon` pasa de 7417634.707993 a 7417634.708: redondeo a 3 decimales, no cambio de valor.
- **`coco_spaces.json`** — antes: 3/3 entradas en **error** (faltaban 5 argumentos). Ahora: 3/3 entradas con **salida**. Cambia una salida esperada de error a valor.
- **`puerta_despiece.json`** — antes: 8/8 entradas en **error**. Ahora: 9 entradas con salida. Igual que el anterior: de error a valor.

- **Por qué necesita aprobación:** el golden anterior no probaba nada en dos casos, y el nuevo cambia lo que se espera. El cambio de error a valor es el único que altera un resultado esperado.
- **Recomiendo:** aprobar. Los nuevos vienen de `b78de04` y el código actual los reproduce con 0 diferencias (verificado en `goldens_origen.md`).
- **Bloquea:** nada. Pero los goldens nuevos siguen sin aprobación humana formal hasta que tú lo confirmes.

## P-06 — ¿Dónde vive `rotacion_z`?

- **Qué:** hay dos copias actuales (`core/vdo_helpers.py` y `cad/propiedades.py`) con la misma lógica. Ver `INVENTARIO_HECHOS.md`, H-60 a H-62.
- **Por qué no lo decido yo:** `core/` no puede importar `App` (MN-03), pero hay 12 ficheros que la usan, y varios son de `core/`. Poner la única copia en `cad/` obliga a que `core` deje de usarla. Eso cambia cómo se calculan rotaciones en `core`.
- **Recomiendo:** `cad/propiedades.py` como única ubicación, y que `core` reciba la rotación ya construida desde quien llama, o trabaje con grados. Hay que revisar los 12 usos antes de tocar.
- **Bloquea:** el destino único de H-60 a H-62 (M1 y M2). El resto de M2 no depende de esto.

## P-07 — ¿`ESQUINAS` y `TIPOS_ENCUENTRO` son el mismo concepto?

- **Qué:** `core/vdo_reengrose.py` define `ESQUINAS` y `ui/vdo_box_controller.py` define `TIPOS_ENCUENTRO`. Tienen el mismo contenido con nombres distintos (`minimalismo.py duplicados`).
- **Por qué no lo decido yo:** unificar sin saber si significan lo mismo puede cambiar el comportamiento de la UI sin que ningún golden lo detecte. Los goldens cubren `core`, no la UI.
- **Recomiendo:** confirmar el significado. Si es el mismo, un solo nombre en `core/vdo_reengrose.py`. Si no, son dos conceptos y se documentan así.
- **Bloquea:** H-04 en M2.

## P-08 — ¿Cómo se rompe el ciclo core ↔ cad?

- **Qué:** medido con AST (`docs/INVENTARIO_HECHOS.md`, sección "Ciclo core ↔ cad (P-08)"). Hay **4 imports de `core` a `cad`**: `forma_ref` en `vdo_coco_core`, `vdo_coco_spaces` y `vdo_panel_core`, y `add_common_props` en `vdo_module_props`. El test `test_core_no_importa_app_ui_cad` ya falla con esa lista exacta.
- **Ciclo real:** solo uno cruza core y cad: `core/vdo_module_props` → `cad/propiedades` → (import diferido) `cad/colocacion` → `core/vdo_module_props`. Los 3 `forma_ref` son violación de capa, no ciclo.
- **Opciones:**
  1. (recomendada) `core` recibe la forma ya construida desde quien llama (`cad` o `app`), y `add_common_props` se llama desde `cad` en vez de desde `core/vdo_module_props`. Hay que medir antes cuántas funciones de `core` usan `forma_ref` (no lo he medido todavía; el inventario solo cuenta imports).
  2. Mover `geometria.forma_ref` a `core` si no usa `App`. Hay que comprobarlo antes; si usa `App`, no es posible.
- **Bloquea:** cualquier cambio en `core/vdo_module_props.py` y en los 3 módulos que importan `forma_ref`. Sin esta decisión no toco esos ficheros, según el encargo.

## P-09 — Sin definir

El encargo de esta sesión cita P-09 como pendiente. Ningún documento del repo ni commit de la rama lo define. **Hace falta que lo definas, o que lo retires del encargo.** No inventé su contenido.

## P-10 — ¿Qué golden tiene `nesting_presets`?

- **Qué:** `nesting_presets` tiene 9 métodos estáticos (`get_preset`, `save_preset`, `delete_preset`, `get_all_presets`, etc.) que leen y escriben las preferencias de FreeCAD. Pero en `b78de04` **el módulo no carga**: al importarlo, `initialize_defaults()` llama a `FreeCAD.ParamGet` sin tener `FreeCAD` en el ámbito (`NameError`, medido con `freecadcmd`). No hay comportamiento de origen que capturar.
- **Opciones:**
  1. (recomendada) Golden desde `b78de04` con un **shim** en el driver que define `FreeCAD` antes de importar el módulo. El golden registra el comportamiento previsto por el código, **no el de origen**, y queda marcado así en `goldens_origen.md`. Se registra aparte el fallo de carga de `b78de04` como hallazgo.
  2. Aceptar N/A con motivo escrito, como hasta ahora, y dejar el módulo sin golden.
  3. Generar el golden desde el código actual (HEAD). **No lo hago**: el plan lo prohíbe sin aprobación humana, porque hacerlo pasar contra el código actual no prueba nada.
- **Procedimiento para (1):** habría que escribir un adaptador que fije la preferencia `Presets` antes de cada llamada, y que se niegue a correr fuera de un HOME temporal, para no tocar las preferencias del usuario. Ese adaptador se escribió durante esta sesión y se retiró antes de commitear, porque no había golden que generar. Hay que reescribirlo si eliges (1).
- **Bloquea:** el gate de M0 (19 goldens). Sin esta decisión M0 queda **parcial** con 18 de 19 cubiertos.

---

## Cambios que no se pueden hacer sin decisión (plan §9)

- Aprobar cualquier cifra de comportamiento que cambie (redondeo, unidades). Ninguna ha cambiado todavía.
- Aprobar M10 y las capturas visuales.
- Confirmar los ítems de `DEUDA_TECNICA.md` y sus responsables.
