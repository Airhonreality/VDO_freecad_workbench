# Decisiones delegadas (plan de minimalismo)

**Quién decide:** el asistente, por delegación explícita del usuario en la conversación ("podrías tomar las decisiones que faltan"). Cada decisión es **revertible**: si el usuario no la acepta, se cambia antes del commit que la aplica.

**Fecha:** 2026-11-03. **Rama:** `minimalismo/noche-20261102`.

Este archivo sustituye la espera en `docs/PENDIENTES_HUMANO.md` para las entradas P-04 a P-10. Ese archivo no se toca aquí porque otra sesión lo escribe.

---

## Resumen

| ID | Tema | Decisión | Desbloquea | Reversible |
|---|---|---|---|---|
| P-04 | Cambios de tests de otra sesión | **No se tocan ni se commitean.** No son de este plan. | nada | sí |
| P-05 | Goldens sustituidos | **Aprobados**, por delegación. Vienen de `b78de04`. | cierre de M0 | sí |
| P-06 | Ubicación de `rotacion_z` | **Única definición en `cad/propiedades.py`.** La copia de `core/vdo_helpers` se elimina en M5. | H-60 a H-62 | sí |
| P-07 | `ESQUINAS` y `TIPOS_ENCUENTRO` | **Se unifican solo los duplicados exactos.** El `TIPOS_ENCUENTRO` del chasis no se toca. | H-04 | sí |
| P-08 | Ciclo core ↔ cad | **Se rompe el ciclo ya**, quitando el re-export de `core/vdo_module_props`. Los imports restantes de core a cad se eliminan en M5. | desbloquea M2 | sí |
| P-09 | Sin definir | **Retirado del alcance.** No hay definición en el repo ni en el encargo. | nada | — |
| P-10 | Golden de `nesting_presets` | **N/A con motivo** y deuda con responsable. No se genera golden contra código actual. | cierre formal de M0 | sí |

---

## P-04 — Cambios de tests de otra sesión

**Hecho:** `tests/test_gui_wiring.py` y `tests/test_single_dock_convergence.py` tienen `os._exit(...)` cambiado a `sys.exit(...)` en su bloque `__main__`. No son parte del plan y no los verificamos.

**Decisión:** no se commitean, no se revierten, no se editan. Quedan fuera de todo commit de este plan.

**Por qué:** revertirlos destruiría trabajo ajeno. Commitearlos mezclaría cambios sin verificar. Dejarlos sin tocar es la única opción que no decide por otra sesión.

**Efecto en las pruebas:** ninguno en el runner, porque el cambio solo afecta a la ejecución directa del archivo, no a `run_tests.py`.

**Pendiente del usuario (no bloquea):** confirmar si esos cambios se descartan o se conservan.

---

## P-05 — Goldens sustituidos

**Decisión:** aprobados. Los tres (`creacion_modulos`, `coco_spaces`, `puerta_despiece`) vienen de `b78de04` y el código actual los reproduce con 0 diferencias.

**Qué cambia:**
- `creacion_modulos.json`: de 4 flujos con esquema plano a 5 flujos con esquema nuevo. Los volúmenes de los 4 flujos antiguos son iguales. `make_cajon` pasa de `7417634.707993` a `7417634.708`: es redondeo, no cambio de valor.
- `coco_spaces.json` y `puerta_despiece.json`: de entradas en error a entradas con salida. Son los únicos cambios de resultado esperado.

**Riesgo asumido:** los goldens antiguos no probaban nada en esos casos, así que la aprobación no supone pérdida de cobertura.

**Revertir:** `git revert` del commit `200c79c`.

---

## P-06 — Ubicación de `rotacion_z`

**Hechos medidos:**
- Dos definiciones: `core/vdo_helpers.py:26` y `cad/propiedades.py:61`.
- Llamadores de `core`: `vdo_coco_core.py:618`, `vdo_zocalo_core.py:401`, `vdo_panel_core.py:337`. Los tres escriben `obj.Placement` dentro de `execute`.
- Llamadores de `cad`: `cad/colocacion.py:73` y `cad/propiedades.py:76`.

**Decisión:** la única definición vive en `cad/propiedades.py`, porque devuelve `App.Rotation`, y eso es escritura de plataforma.

**Lo que no se hace ahora:** no se elimina la copia de `core/vdo_helpers` en M2. Sus tres llamadores escriben objetos dentro de `execute`, y esa escritura se traslada a `cad/` en M5. Quitar la copia antes dejaría `core` sin función y rompería el comportamiento.

**Deuda registrada:** la copia de `core/vdo_helpers` queda con responsable `ejecutor` y se elimina en M5, con golden de `module_props.rotacion_z` ya existente.

---

## P-07 — `ESQUINAS` y `TIPOS_ENCUENTRO`

**Hechos medidos:**

| Símbolo | Dónde | Valores | Igual a |
|---|---|---|---|
| `ESQUINAS` | `core/vdo_reengrose.py:53` | `vertical_domina`, `horizontal_domina`, `inglete_45`, `marco_interior` | `TIPOS_ENCUENTRO` de `ui/vdo_box_controller.py:63`: **idéntico** |
| `ESQUINAS_2D` | `core/vdo_reengrose.py:52` | `frente_izquierda`, `frente_derecha`, `fondo_izquierda`, `fondo_derecha` | `ESQUINAS` de `ui/vdo_box_controller.py:84`: **idéntico** |
| `TIPOS_ENCUENTRO` | `ui/vdo_chassis_widget.py:115` | `tapa_domina`, `lateral_domina`, `inglete_45` | **distinto**: solo comparte `inglete_45` |

**Decisión:**
1. Los dos duplicados exactos de `ui/vdo_box_controller.py` se sustituyen por importación de las tablas de `core/vdo_reengrose.py`. Es un dato puro, así que MN-03 lo permite. No hay cambio de valor.
2. El `TIPOS_ENCUENTRO` del chasis **no se unifica**. Sus valores son distintos (`tapa_domina` y `lateral_domina` no existen en el dominio de reengrose). Puede ser el mismo concepto con otros nombres, pero renombrar un valor de dominio cambia lo que se muestra y lo que se guarda, y ningún golden cubre la UI.

**Pendiente de verificación (no bloquea):** comprobar si el valor del chasis se persiste en propiedades de documentos. Si se persiste, cualquier renombrado requiere migración.

---

## P-08 — Ciclo core ↔ cad

**Hechos medidos con AST:**
- `core/vdo_module_props.py:28` importa `add_common_props` de `cad/propiedades`. Es un re-export con `noqa`.
- `cad/propiedades.py:72` importa `ancla_local` de `cad/colocacion` de forma diferida.
- `cad/colocacion.py:17` importa `ANCLAJE_DEFAULT` de `core/vdo_module_props`.
- Ciclo: `core/vdo_module_props` → `cad/propiedades` → (diferido) `cad/colocacion` → `core/vdo_module_props`.

Corrección al registro anterior: el ciclo sí existe, y pasa por la importación diferida de `ancla_local`. Los tres `forma_ref` de `core` no forman ciclo; son violaciones de capa.

**Decisión en dos pasos:**

*Paso ahora (M2):* se elimina el re-export de `core/vdo_module_props.py:28`. Los llamadores de `core` que usan `add_common_props` lo importan directamente de `cad/propiedades`. Con eso, `core/vdo_module_props` ya no importa `cad` y el ciclo desaparece. **Verificación obligatoria:** un script que compruebe que el grafo de imports del paquete no tiene ciclos, y que `test_core_no_importa_app_ui_cad` sigue fallando solo por los imports restantes de core a cad, no por ciclo.

*Después (M5):* los 4 `forma_ref` en `core` y las llamadas a `add_common_props` dentro de `execute` se sustituyen por planes de datos en `core` y aplicación en `cad`. Eso elimina todos los imports de core a cad.

**Por qué no se hace un shim ni se añade excepción en el test:** la excepción esconde la violación. Según F19-D1 y el encargo, el test se queda en rojo hasta M5.

**Lo que no se decide:** `forma_ref` no se mueve a `core`, porque usa `App` y `Part`.

---

## P-09 — Retirado

No hay definición de P-09 ni en el repo ni en el encargo. No se inventa contenido. Si el usuario tenía algo en mente, debe decirlo; hasta entonces no bloquea nada.

---

## P-10 — Golden de `nesting_presets`

**Hechos medidos:** `core/vdo_nesting_presets.py` no carga en `b78de04`. `initialize_defaults()` usa `FreeCAD.ParamGet` sin tener `FreeCAD` en el ámbito, y falla con `NameError`. No hay comportamiento de origen que capturar.

**Decisión:** N/A con motivo, documentado en `docs/metricas/goldens_origen.md`. No se genera golden desde código actual, porque el plan lo prohíbe sin aprobación y porque no probaría nada de origen.

**Deuda registrada:** `nesting_presets` queda sin golden. Responsable: `ejecutor`. Plazo: antes de M5, porque toca escritura de preferencias. Hay que arreglar la carga en el código actual, decidir su comportamiento correcto y generar un golden de ese comportamiento, marcado como "nuevo, no de origen".

**Efecto en el gate de M0:** 18 goldens más 1 N/A justificado, en lugar de 19 literales.

---

## Efecto sobre el plan

- M0 queda cerrada con 18 goldens y 1 N/A justificado, una vez que el registro lo refleje.
- M2 puede continuar en: literales de dominio, `MODULE_SPECS`, `LUCIDE_ICONS` y `CATALOGO_PATH`. Lo que depende de P-06 (la copia de `core/vdo_helpers`) se hace en M5.
- M5 queda como fase con más trabajo, porque absorbe el resto del ciclo, las escrituras de `core` y la copia de `rotacion_z`.
- El test de arquitectura sigue en rojo hasta M5. Es lo esperado.

---

## Sesión del 2026-11-03 (continuación): D-11, D-12, H-21, H-23, H-24

### D-11 — Locale (aprobada por el usuario)

**Hecho medido:** con `LC_NUMERIC=es_CO.UTF-8`, FreeCAD 1.1.4 lee `"0.4"` y también `"=0.4"` como `0`, y trunca `"7417634.708"` a `7417634`. La forma de expresión decimal no sirve.

**Decisión:** `cad/vdo_guardian.py` escribe cada número como fracción entera `=N/D`, con `Fraction(repr(valor))`. Los enteros se escriben sin `=`. Medido: `=N/D` da el mismo valor en `es_CO.UTF-8` y en `C`, incluidos negativos, `1e-05` y `7417634.708`. Es la única escritura numérica con `str()` en hojas o propiedades de `cad/` y `core/` (grep: solo `vdo_guardian.py`). Los demás `str(` son de texto.

**Efecto visible:** el contenido de la celda cambia de `0.4` a `=2 / 5`. El valor no cambia. El golden `guardian.json` no se regenera: requiere aprobación humana (ver pendientes).

**Revertir:** `git revert 169135b`.

### D-12 — Ciclo dentro de cad (decidida por el asistente)

**Decisión:** `aplicar_rotacion` se mueve de `cad/propiedades.py` a `cad/colocacion.py`. Los cuatro importadores de `ui/` y la lista de `tests/test_smoke_l3_desk_assembly.py` apuntan al nuevo sitio. `ciclos.py` confirma que el ciclo `cad.colocacion ↔ cad.propiedades` desaparece.

**No cubierto:** quedan 3 ciclos dentro de `ui/`. No son parte de D-12. Se registran en el registro de progreso.

**Revertir:** `git revert 00fdf7f`.

### H-21 — Ruta del catálogo de herrajes (corrige un defecto)

**Hecho medido:** `ui/vdo_hardware_manager.py` calculaba `ui/vdo_hardware_catalog.json`, que no existe. El catálogo está en `core/`. El gestor mostraba un error y trabajaba con catálogo vacío al abrir, y al guardar creaba un fichero que el hub nunca lee.

**Decisión:** una sola ruta, `core/vdo_hardware_hub.CATALOGO_PATH`. La UI la importa. Es un cambio de comportamiento, y está declarado en el commit `7566f34`.

**Revertir:** `git revert 7566f34` (el gestor vuelve a leer y escribir en la ruta inexistente).

### H-23 — LUCIDE_ICONS (decidida por el asistente)

**Hecho medido:** las dos tablas no eran copias. Solo compartían `inglete_45`, con SVG distinto: color `#007acc` con trazo de línea frente a `#00d4ff` con trazo de contorno, y tamaño 18 frente a 22.

**Decisión:** una tabla de 19 claves en `ui/tema.py`. Para `inglete_45` se conserva la versión del chasis, que es la definición más completa. El icono del box controller cambia de aspecto. Es presentación y reversible.

**Pendiente:** verificación visual en nivel 3 del icono `inglete_45` del box controller.

**Revertir:** `git revert 04a83e5`.

### H-24 — Caché de iconos y logger (decidida por el asistente)

**Decisión:** no se unifican. La caché de runtime y el `getLogger(__name__)` de cada módulo no son hechos de dominio. Unificarlos no quita ninguna duplicación de información.

### P-07 — aplicado

Commit `9040cca`. Las tablas idénticas pasan de 2 a 0.

---

## Pendientes para el humano (sesión del 2026-11-03)

Este bloque va aquí y no en `docs/PENDIENTES_HUMANO.md`. Ese archivo lo escribe otra sesión, y no se ha tocado.

1. **Aprobar la regeneración de `tests/golden/guardian.json`** (celda B5, `canto_fino`, de `"0.4"` a `"=2 / 5"`, 6 entradas). Mientras no se apruebe, `test_goldens.test_guardian` queda en rojo con causa documentada.
2. **Documentos ya guardados con `0` por el locale de coma decimal.** El código corregido no cambia lo que hay guardado. Revisar a mano el valor de `canto_fino` (y otros parámetros del guardián) en los documentos afectados, o restablecerlo.
3. **Verificación visual (nivel 3)** del icono `inglete_45` del box controller, que cambia de aspecto (H-23).
4. **P-04** (sin cambios): `tests/test_gui_wiring.py` y `tests/test_single_dock_convergence.py` siguen modificados sin commitear. No son de este plan.
5. **Literales de dominio (53) y `MODULE_SPECS` (H-22):** siguen abiertos. Para `MODULE_SPECS` hace falta un golden desde `b78de04`, con procedencia en `goldens_origen.md`. Ese golden no existe todavía.


---

## Decisiones del asistente (sesión del 2026-11-03, tercera): D-13 a D-18

**Criterio.** El usuario indicó que no quiere aprobar cada decisión y que el asistente tome las decisiones con sentido común, sin poner en riesgo el proceso. Cada decisión de esta sección es del asistente, es revertible con `git revert` del commit indicado, y se registra con su razón. Se detiene y consulta solo ante acciones destructivas o irreversibles, o ante conflicto con otra sesión.

### D-13 — Forma de escribir números en la hoja (cierra D-11 y el pendiente 1)

**Decisión:** se mantiene `=N/D`. Dos cambios:
1. Antes de la fracción, el valor se redondea a 10 decimales: `Fraction(repr(round(valor, 10)))`. Así el denominador queda por debajo de 10^10, muy por debajo de 2^53, y la lectura de FreeCAD es exacta. El cambio máximo es menor que 5·10^-11 mm. Para medidas de carpintería no tiene efecto.
2. Si el numerador o el denominador superan 2^53, la función lanza `ParametroInvalido` (de `core/errores.py`). No se escribe un valor incorrecto en silencio.

**Por qué no otra forma:** las medidas de `es_CO` muestran que `"0.4"` y `"=0.4"` se leen como 0 y que `"7417634.708"` se trunca. No hay otra escritura de texto que sea independiente del locale.

**Efecto visible que se acepta:** la celda muestra `=2 / 5` en vez de `0.4`. El valor es el mismo. Es feo, pero es correcto y reversible.

**Prueba obligatoria:** lectura de vuelta en `LC_NUMERIC=es_CO.UTF-8` y en `C` para todos los valores que escribe el guardián, leídos del manifiesto con un comando, no a mano. Y una prueba que confirme que un valor con denominador mayor que 2^53 lanza el error.

**Revertir:** `git revert` del commit que aplique D-13.

### D-14 — Golden `guardian.json` (cierra el pendiente 1)

**Decisión:** se regenera. Razón: la lectura de vuelta da el mismo valor en ambos locales, así que el cambio es solo de representación de la celda. El golden guarda lo que se escribe, y eso es lo que cambia.

**Condición:** el diff de la regeneración debe tocar solo la celda B5 (y las demás celdas de `canto_fino` si las hay). Si toca otra cosa, se revierte la regeneración y se registra.

**Revertir:** `git revert` del commit de la regeneración.

### D-15 — Documentos guardados con `0` (cierra el pendiente 2)

**Decisión:** no se corrigen. El código no puede arreglar documentos ya guardados y no hay forma segura de adivinar qué valor debía tener cada parámetro. Se registra la lista de documentos afectados si existe alguno localizable, y el usuario los revisa a mano. Es la única decisión de esta sección que deja trabajo para una persona, y no se puede resolver de otra manera sin riesgo.

**Deuda:** `docs/DEUDA_TECNICA.md`, responsable `usuario`.

### D-16 — Literales de dominio (cierra la parte de literales de M2)

**Decisión:** un módulo de datos `freecad/vdo/datos/valores.py` con una constante por valor: `MELAMINA_ESTANDAR`, `BLUM_TANDEM`, `OCULTA`, `TIRADOR`. El código de `core/` y `ui/` usa las constantes. Los JSON de `datos/` conservan los literales, porque ahí son datos. Los tests pueden seguir con literales cuando comprueban un valor concreto del manifiesto, porque así se detecta un cambio de dato. Ningún otro archivo del paquete debe contener esos literales.

**Revertir:** `git revert` de cada commit de literales.

### D-17 — `MODULE_SPECS` (cierra H-22)

**Decisión:** antes de mover nada se genera el golden desde `b78de04`, serializando el diccionario `MODULE_SPECS` tal como existe en ese commit. Si el golden de origen coincide con el actual, el diccionario se mueve a `freecad/vdo/datos/modulos.json` y `core/vdo_module_specs.py` conserva solo las funciones (`get_spec`, `resolver_panel`, `_resolver`). Si el origen no coincide, se registra la diferencia y no se mueve.

**Por qué es sensato:** el diccionario no tiene funciones ni lambdas (solo strings, números, booleanos y tuplas de strings). Es un dato puro, y MN-04 dice que los datos van en `datos/`.

**Revertir:** `git revert` del commit del movimiento.

### D-18 — Estado de módulo de solo lectura (cierra H-24 y el criterio R5)

**Decisión:** la regla MN-08 prohíbe **estado mutable** de módulo. No prohíbe datos de solo lectura cargados una vez. Por tanto:
- `VDO_MANIFEST`, `_MANIFEST` y `_CATALOGO` se convierten en constantes de solo lectura (`types.MappingProxyType` sobre dict, o tuplas) con nombre en mayúsculas. Su contenido no cambia en tiempo de ejecución.
- `LOGGER` en `app/registro.py` queda como está: es configuración de logging, no dominio.
- Los caché de iconos de runtime no se tocan.

Si `verificar.py` o `minimalismo.py` cuentan estas constantes como estado mutable, la regla de conteo se corrige para distinguir solo lectura, y la corrección va en el mismo commit con su motivo.

**Revertir:** `git revert` del commit.

### Ciclos dentro de `ui/` (no cubierto por el plan)

**Decisión:** el agente lista los tres componentes con sus imports exactos. Si un ciclo se rompe moviendo una constante o un dato a `ui/tema.py` o a `datos/`, se hace y se registra. Si requiere mover lógica entre módulos de UI, se deja documentado en `DEUDA_TECNICA.md` con responsable `ejecutor` y no se toca en esta sesión.

### Regla de consulta

Solo se consulta al usuario ante: borrar datos de usuario, cambiar archivos fuera de este repo, o conflicto con otra sesión activa. Lo demás se decide, se registra y se avisa en el informe final.
