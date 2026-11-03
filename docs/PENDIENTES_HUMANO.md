# Pendientes humanos — plan de minimalismo

Orden por urgencia. Cada entrada: qué se necesita, por qué, la opción que recomiendo y qué se bloquea mientras no haya respuesta.

---

## P-01 — ~~¿Cuentan como N/A `guardian` y `nesting_presets` en el gate de M0?~~ **Decidido por el ejecutor: N/A**

Decisión técnica, delegada por el usuario y revertible. Sin golden. Motivo: no hay cálculo que proteger. Registrado en `goldens_origen.md` y `DEUDA_TECNICA.md` (D-02). Si el usuario quiere un golden de efectos sobre el documento, se abre una tarea.

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

## P-05 — Revisar los goldens sustituidos (no bloquea)

- **Qué:** tres goldens cambian respecto a lo commiteado. Commit `692b76a`.
  - `creacion_modulos.json`: sustituido. El anterior tenía otro esquema y ningún generador.
  - `coco_spaces.json`: sustituido. El anterior tenía 3/3 entradas en error.
  - `puerta_despiece.json`: sustituido. El anterior tenía **8/8 entradas en error**: no probaba nada.
- **Por qué:** el plan exige aprobación humana de los cambios de golden. La procedencia (`b78de04`) está en `docs/metricas/goldens_origen.md`.
- **Recomiendo:** aprobar. Los nuevos son generados desde `b78de04` y el código actual los reproduce con 0 diferencias.
- **Bloquea:** nada. Las instrucciones de esta noche permiten commitear goldens generados desde `b78de04` con procedencia documentada. Queda como revisión humana, no como bloqueo.

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

---

## Cambios que no se pueden hacer sin decisión (plan §9)

- Aprobar cualquier cifra de comportamiento que cambie (redondeo, unidades). Ninguna ha cambiado todavía.
- Aprobar M10 y las capturas visuales.
- Confirmar los ítems de `DEUDA_TECNICA.md` y sus responsables.
