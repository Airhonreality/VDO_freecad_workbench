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

---

## Registro de ejecución de D-13 a D-18 (sesión del 2026-11-03, cuarta)

**Por qué aquí y no en PROGRESO_MINIMALISMO.md:** al inicio de la sesión había tres procesos `claude` con cwd en este repo (PIDs 36672, 143086 y 264170). El encargo pide confirmar que no hay conflicto antes de escribir en `PROGRESO_MINIMALISMO.md` o `PENDIENTES_HUMANO.md`. No se pudo confirmar. **Pendiente: volcar este registro en PROGRESO cuando se confirme que no hay conflicto.**

### 1. Segfault con código 139 (prioridad máxima)

- **Causa medida:** con `VDO_TEST_OUT` apuntando a un directorio, o a una ruta cuyo padre no existe, la escritura del resumen en `tools/run_tests.py` lanzaba `IsADirectoryError` / `FileNotFoundError` al final. La excepción salía de `main()` sin llamar a `liberar_widgets()`, y freecadcmd terminaba con abort (134) o SIGSEGV (139).
- **Medido antes del fix, 5 ejecuciones por variante:** directorio existente: 134, 139, 134, 1, 134. Padre inexistente: 139, 139, 134, 139, 134. Ruta válida (control): 1 en las 5.
- **Corrección** (`0521803`): validación temprana de `VDO_TEST_OUT` con código 2 y mensaje en stderr; `liberar_widgets()` en `finally`.
- **Medido después:** directorio: 2, 2, 2, 2, 2. Padre inexistente: 2, 2, 2, 2, 2. Control: 1 en las 5.
- **Prueba:** `tests/test_runner_salida.py`, lanza el runner en un subproceso `python3`.
- **No diagnosticado:** el mecanismo exacto del abort/SIGSEGV durante el cierre de freecadcmd. Lo que sí está medido es que el disparador es la excepción que escapa de `main()`, y que evitarla elimina el crash en todas las ejecuciones medidas.
- **Ruido no relacionado:** en todas las ejecuciones aparece `AttributeError: module 'FreeCADGui' has no attribute 'Control'` desde `ui/vdo_view_providers.py:244`. Se captura en el código y no provoca el crash. Queda fuera de este registro.

### 2. D-13: escritura numérica en `cad/vdo_guardian.py` (`1984d9e`)

- `_celda_numerica` usa `Fraction(repr(round(valor, 10)))`. Si numerador o denominador superan 2^53, lanza `ParametroInvalido` de `core/errores.py`.
- **Premisa no cumplida tal cual:** tras redondear a 10 decimales, el denominador nunca supera 10^10, muy por debajo de 2^53. La rama de error se dispara por el **numerador**. La guarda del denominador se mantiene. La prueba usa `_celda_numerica(1e16)`.
- **Lista de valores** obtenida con comando sobre el manifiesto (`parametros_globales` y `parametros_locales`): 10 valores, todos numéricos (`/tmp/vdo_seg2/valores_guardian.txt`). La prueba de nivel 2 los lee del manifiesto.
- **Lectura de vuelta, FreeCAD real, LC_NUMERIC del entorno = locale probado:**
  ```
  LOCALE=es_CO.UTF-8 RESULTADO=TODOS_IGUALES n=10
  LOCALE=C RESULTADO=TODOS_IGUALES n=10
  ```
  Valor a valor: `canto_fino` manifiesto 0.4 → celda `'=2 / 5'` → leído 0.4 (IGUAL). `fondo_umbral_delgado` manifiesto 8.0 → celda `'8'` → leído 8 (IGUAL). Las 10 filas son IGUAL en ambos locales.

### 3. D-14: regeneración de `guardian.json` (`d7e5737`)

- Regenerado con `golden.py`, función `regenerar("guardian")`, desde el código de D-13.
- **Diff comparado campo a campo: 6 cambios, todos en `Params_Melamina!B5` (`canto_fino`):**
  ```
  -                "contenido": "0.4",
  +                "contenido": "=2 / 5",
  ```
  (6 entradas: `asegurar_hoja_global[0..2]` y `vdo_guard[0..2]`). Ningún otro campo cambia.
- `verificar(guardian)` = True. `test_goldens.test_guardian` pasa.

### 4. D-15: documentos guardados con `0` (deuda U-04)

- Búsqueda de solo lectura en este equipo: **23 `.FCStd`**, **7 con hoja de cálculo**, **0 con el alias `canto_fino`**. Ningún documento local afectado.
- La otra máquina no se ha revisado. Está registrado en `docs/DEUDA_TECNICA.md` (U-04, responsable usuario).

### 5. D-16: literales de dominio (`datos/valores.py`)

- Se crea `freecad/vdo/datos/valores.py` (`MELAMINA_ESTANDAR`, `BLUM_TANDEM`, `OCULTA`, `TIRADOR`) y `freecad/vdo/datos/__init__.py`.
- **Un commit por grupo:** `9504456` melamina_standar (23), `556d5f8` blum_tandem (14), `570302f` oculta (8), `e66f014` tirador (8). Total: 53.
- **Alcance:** también se sustituyeron los literales de `app/` (`dto.py`, `casos_uso/consultar_herrajes.py`). El encargo exige 0 fuera de `datos/` y tests, y `app/` estaba dentro de esa medición.
- `CORREDERA_OCULTA` y `APERTURA_TIRADOR` pasan a ser alias de `OCULTA` y `TIRADOR`, como pide el encargo.
- **Medido** con `minimalismo.py literales`: 0 fuera de `datos/`.
- **Golden igual:** nivel 2, `test_goldens` OK en los 14 módulos tras cada grupo.

### 6. D-17: `MODULE_SPECS` (`cfb9794`, `6ec9471`, `6c1c485`)

- **Golden desde `b78de04`:** `git show b78de04:...` + `ast.literal_eval`. 7 módulos, orden de claves original. Se guarda en `tests/golden/module_specs.json`. Procedencia en `goldens_origen.md`.
- **Condición comprobada antes de mover:** el valor de `MODULE_SPECS` en HEAD (con constantes resueltas) es igual al de `b78de04`. `IGUALES (valor, nombres resueltos): True`.
- **Movido** a `freecad/vdo/datos/modulos.json`. `core/vdo_module_specs.py` pasa de 196 a 41 líneas y conserva las funciones.
- **Error mío registrado:** `cfb9794` se commiteó con una prueba que comparaba tuplas con listas. Fallaba en el nivel 1. Se corrigió en `6ec9471` normalizando ambos lados por JSON. El golden no cambió. El fallo se detectó tras el commit, no antes.
- **Diferencia de representación:** las tuplas de `factory` son listas en JSON. `_resolver` las desempaqueta igual.

### 7. D-18: estado de solo lectura (`89a1677`)

- `VDO_MANIFEST` (`core/vdo_manifest.py`) y `_MANIFEST` (`core/vdo_cajon_despiece.py`) son `MappingProxyType`. Asignar lanza `TypeError`. Prueba: `tests/test_estado_solo_lectura.py`.
- **Límite:** la inmutabilidad es superficial, como decide D-18. Los sub-dicts siguen siendo dicts. Ningún código los muta (verificado con grep).
- **`_CATALOGO`: no existe en el código.** No se aplica. No hay ninguna variable con ese nombre (buscado en `freecad/`, `tools/` y `tests/`). La premisa no se cumple.
- **Regla R5 de `verificar.py`: no se cambia.** `"_MANIFEST".isupper()` es `True` en Python, así que R5 nunca lo contó. Ejecutada sobre todo `freecad/vdo/`: **0 hallazgos**.

### 8. Ciclos dentro de `ui/` (punto 7 del encargo)

- Tres componentes. Ninguno se rompe moviendo constantes o datos. Las aristas son funciones o clases, y las constantes `PAGE_*` no rompen el ciclo porque el dock también necesita la clase.
- Requieren mover lógica entre módulos de UI, así que quedan en `docs/DEUDA_TECNICA.md` como **U-01, U-02 y U-03** (responsable ejecutor, fecha M5).

### 9. M2 y M3

- **M2 cierra** según el gate del encargo: literales fuera de `datos/` = 0; `MODULE_SPECS` en `datos/` con golden igual; tablas idénticas = 0.
- **Reserva:** el plan (§6, M2) también pide reducir las líneas de `core/vdo_hardware_hub.py`. No se cumple: 301 → 303 líneas (+2 por el import de `CATALOGO_PATH` y el de `valores`). Se declara aquí; no cambia el gate del encargo.
- **M3 empieza y se cierra** (`e88ce23`, `602f686`). Tabla única en `core/aperturas.py`:
  - Verificado: `LEGADO_A_CONTRATO` (11 claves), `DESCUENTO_ALTO` y el orden del selector son iguales a HEAD.
  - **Único cambio de salida:** el orden de `SISTEMAS_APERTURA_VALIDOS` (solo aparece en el texto del error de validación).
  - Goldens `cajon_despiece`, `puerta_despiece` y `facade_contract`: OK, sin cambio. Snapshots de despiece: **13/13 OK**.
  - Gate "una sola definición de cada sistema": verificado con grep. Ninguna definición de `APERTURA_*`, `necesita_*`, `APERTURA_LABELS`, `APERTURA_LEGADO`, `APERTURA_DESCUENTO`, `_normalizar` ni `SISTEMAS_APERTURA =` queda fuera de `core/aperturas.py`. `minimalismo.py` no tiene subcomando para reglas de apertura, así que el gate usa grep.
  - Los motores de cajón y puerta no se unifican (MN-06).
  - El `except ImportError` del cajón desaparece: ya no se traga ningún error de import.

### Medición final (salidas literales resumidas)

```
$ VDO_TEST_DIR=tests VDO_TEST_OUT=... python3 -I tools/run_tests.py       # nivel 1
RESUMEN ejecutados=291 fallos=3 errores=0 skip=114 no_ejecutado=0
  FALLO test_arquitectura (3, los de siempre)

$ VDO_TEST_DIR=tests VDO_TEST_OUT=... freecadcmd tools/run_tests.py       # nivel 2, 3 ejecuciones
RUN 1 EXIT=1 SIGSEGV=0 RESUMEN ejecutados=289 fallos=3 errores=0 skip=26 no_ejecutado=0
RUN 2 EXIT=1 SIGSEGV=0 RESUMEN ejecutados=289 fallos=3 errores=0 skip=26 no_ejecutado=0
RUN 3 EXIT=1 SIGSEGV=0 RESUMEN ejecutados=289 fallos=3 errores=0 skip=26 no_ejecutado=0

$ python3 -I tools/auditoria/ciclos.py
CICLOS: 3 componentes (todos en ui/)

$ .venv/bin/ruff check . --no-cache --statistics
Found 294 errors.

$ python3 -I tools/auditoria/minimalismo.py resumen
capa | archivos | lineas | funciones | api_publica
core | 27 | 8506 | 304 | 245
ui   | 33 | 13472 | 513 | 301
cad  |  5 |  398 |  18 |  13
app  | 21 |  944 |  42 |  50
TOTAL | 86 | 23320 | 877 | -

$ minimalismo.py duplicados -> tablas constantes idénticas: 0 ; funciones con cuerpo idéntico: 3
$ minimalismo.py literales  -> literales vigilados fuera de datos/: 0
$ minimalismo.py ramas      -> funciones con 4+ ramas if/elif: 12
$ minimalismo.py tamano     -> archivos > 400 líneas: 17 ; funciones > 60 líneas: 68
$ minimalismo.py excepciones-> except que tragan errores: 89
$ minimalismo.py fachadas   -> 0
```

### Abierto (con causa)

- **M4 a M11:** no iniciadas. El encargo cubre hasta M3.
- **`test_arquitectura`: 3 fallos**, hasta M5 (decisión del encargo).
- **Ciclos en `ui/`:** U-01 a U-03 (requieren mover lógica).
- **Documentos con `0` en la otra máquina:** U-04.
- **Registro en `PROGRESO_MINIMALISMO.md` y `PENDIENTES_HUMANO.md`:** pendiente, por conflicto potencial con otras sesiones activas.
- **Ruff 294:** el desglose por carpeta no se ha vuelto a medir en esta sesión. `F821` en `tests/test_single_dock_convergence.py:218` pertenece a P-04, de la otra sesión.

## D-19 a D-21 (ola 1 a 3 del director)

- **D-19:** el gate de literales cubre el paquete de primer nivel (`commands.py`, `Init.py`, `InitGui.py`). No cubre `tools/` ni `tests/`. Razón: D-16 exige 0 en el paquete; `tools/` y `tests/` usan literales a propósito.
- **D-20:** se elimina el alias de reexportación `APERTURA_DESCUENTO_ALTO` en `vdo_puerta_despiece.py`. Sin usos externos.
- **D-21:** M4.3 `generar_tiras_perimetrales` se reescribe como tabla de lados y reglas. Gates: goldens reengrose y zocalo_core OK; equivalencia exacta 20000/20000 con script fuera del repo. **El gate "ramas baja en 1" NO se cumple:** la función nunca contó en el auditor (su cadena if/elif máxima era de 3 ramas). Se acepta porque el criterio real del plan es comportamiento congelado, no la cifra del auditor. Revertir: `git revert e28e5e0`.

## D-22 (ola 6)

- **D-22:** se eliminan los stubs `app/casos_uso/exportar_lista_corte.py` y `app/casos_uso/recargar_catalogo.py` (sin lógica). La regla R4 de tools/auditoria/verificar.py exige su existencia y pasará a FALLO. Razón: MN-01 elimina app/, y el plan §5 declara que verificar.py es solo referencia; el cierre de fase se decide con minimalismo.py. Revertir: git revert del commit de T2.


## D-23 (ola 8)

- **D-23:** los DTO de app/dto.py (dataclasses inmutables, sin FreeCAD ni cálculo) pasan a core/dto.py. Razón: plan §3, TIPOS de core/cad; MN-03 permite que cad/ e ui/ importen core/. Revertir: git revert de T5.

## D-24 (ola 11)

- **D-24:** vdo_creacion.py y los crear_*.py pasan a freecad/vdo/creacion.py (307 líneas según `wc -l` de los archivos origen, suma medida; bajo el límite de P5). commands.py no crece. Razón: juntos con commands.py (359) superarían 400 líneas. Revertir: git revert de T12b y T12c.

## D-25 (ola 12)

- **D-25:** `test_arquitectura.py::test_app_no_importa_ui` falla cuando `app/` no tiene `.py`, porque el helper exige archivos. MN-01 elimina `app/`, así que la capa ausente debe considerarse cumplida. La regla se mantiene si `app/` existe. Cambio aprobado por el director (no es debilitar la regla). Revertir: `git revert` del commit de T2.

## D-26 (ola 14)

- **D-26:** el usuario confirmó que no hay documentos VDO que conservar. Verificado: el único .FCStd de usuario fuera del repo (Escritorio) no referencia VDO (0 coincidencias). Se mueven las clases Feature y make_* de core/ a cad/, sin puente de compatibilidad. Revertir: git revert de los commits de esta ola.

**Resultado de la ola 14 (D-26):** bloqueado y revertido. Se movieron `vdo_puerta_core`, `vdo_zocalo_core` y `vdo_cajon_core` (`8dd5550`, `3523be7`, `216f1f6`); el nivel 2 dio fallos nuevos (`test_comandos_workbench` x5 por `AttributeError`, `test_creacion_colocacion` x1 por `ModuleNotFoundError`). Causa: las rutas `factory` de `freecad/vdo/datos/modulos.json` apuntan a esos módulos, y `tests/golden/module_specs.json` congela esas rutas (`test_valor_y_orden_de_claves_iguales_al_golden`). Cambiarlas exige tocar `datos/` y un golden, ambos fuera de alcance sin aprobación humana. Revertidos con `git revert` (`5ba4013`, `80f67a5`, `12d2a30`). Nivel 2 tras revertir: `ejecutados=289 fallos=3`.

No movidos, con motivo: `vdo_coco_spaces` (`forma_ref` va dentro de `generar_divisiones_matriz`, que devuelve formas; separar cambia el contrato usado por goldens y tests); `vdo_coco_core` y `vdo_panel_core` (`tests/test_single_dock_convergence.py` importa `CocoFeature` y `PanelFeature` de `core/` a nivel de módulo; ese archivo tiene cambios ajenos y no se toca).

Decisión pendiente para el humano: aprobar el cambio de rutas `factory` en `modulos.json` junto con la regeneración de `module_specs.json`, o mantener los Feature en `core/` y tratar la arista como deuda explícita.

## D-28 (ola 16)

- **D-28:** opción A completa. Rutas `factory` de `freecad/vdo/datos/modulos.json` y golden `tests/golden/module_specs.json` regenerados (el usuario confirmó que no hay documentos VDO). Import de `tests/test_single_dock_convergence.py` reapuntado (2 líneas; resto del archivo intacto). Revertir: `git revert` de esta ola.

## D-29 (ola 17)

- **D-29:** la última arista core→cad (`core.vdo_coco_spaces -> cad.geometria`, por `forma_ref`) se elimina separando plan de formas. En `core/vdo_coco_spaces.py` queda el cálculo puro: `planificar_divisiones_matriz` devuelve el plan (cajas con cortes, tiras, piezas como datos, resumen, resuelto) sin formas OCC. En `cad/coco_espacios.py` viven `_shape_caja`, `_punto_inglete`, `_prisma_inglete`, `_shape_tira` y `generar_divisiones_matriz`, que consume el plan y devuelve las mismas formas, con la misma firma y el mismo orden de operaciones. `resolver_tiras` se queda en core (no construye formas). Reapuntados los imports de `cad/coco.py`, `tests/test_coco_reengrose_avanzado.py`, `tests/test_smoke_l3_desk_assembly.py` (REQUIRED_API) y la ruta de reubicación de `tools/auditoria/golden.py` (`RELOCALIZADAS`) para el golden `coco_spaces`; `tests/golden/` no se toca. Revertir: `git revert` de los commits de esta ola.

**Resultado de la ola 17 (D-29):** bloqueado y revertido. Commit de implementación `0fa1435`, revertido con `898cfcb`. Nivel 2 con el cambio: `ejecutados=289 fallos=2` (solo test_arquitectura; el golden `coco_spaces` OK con FreeCAD real). Nivel 1 con el cambio: `ejecutados=291 fallos=3`, con el golden `test_goldens.GoldensVerificacionTests.test_coco_spaces` fallando: el módulo core deja de depender de FreeCAD, así que el test ya no se salta y se ejecuta con el mock, que no reproduce las formas grabadas con FreeCAD real. Desbloqueo pendiente: que `tests/test_goldens.py` trate los goldens de salida Part.Shape como solo-FreeCAD (decisión humana, fuera de alcance), o regrabar el golden con el mock. Tras revertir, nivel 1: `ejecutados=291 fallos=3 skip=113`.

## D-30 (ola 18)

- **D-30 (decisión del director):** corrección de clasificación, justificada: el test del golden `coco_spaces` necesita formas OCC reales. El skip previo era accidental (dependía del import de `core/vdo_coco_spaces`, que importaba FreeCAD), no un requisito declarado. Se añade una guarda de entorno en tiempo de ejecución en `tests/test_goldens.py` que, si no hay FreeCAD real (`_freecad_real()`, la misma detección de `tests/soporte/requisitos.py`), hace SKIP con el motivo "requiere FreeCAD real (formas OCC)". No cambia el golden ni la comparación. Revertir: `git revert` del commit de D-30 (guarda).

## D-31 (ola 19)

- **D-31 (decisión del director):** `ui/` puede importar `core` y `cad`, como fija MN-03 del plan vinculante (`docs/PLAN_MINIMALISMO_VDO.md` §2). La prueba `test_ui_no_importa_core_cad_app_api` era más estricta que el plan: prohibía `core` y `cad`. Se alinea: los prohibidos pasan a ser solo `freecad.vdo.app.vdo_api` (y `app`, ya eliminado). (a) Cambio de la lista de prohibidos y del mensaje de la prueba; sin cambio en las demás pruebas.
- **(b)** Las escrituras de `ui/` en FreeCAD (`.recompute()`, `addProperty`, `addObject`, asignación de `Placement` y de propiedades) se mueven a funciones con nombre claro en `cad/` (p. ej. `cad/documento.py` con `recalcular(doc)`, y las propiedades en el módulo de `cad/` que corresponda). La UI llama a esas funciones. La lógica no cambia.
- Revertir: `git revert` de los commits de esta ola (registro, alineación de la prueba y escrituras movidas).

## D-32 (ola 20)

- **D-32 (decisión del director):** completar las escrituras residuales de `ui/` en FreeCAD (`test_ui_no_escritura_freecad` fallaba por escrituras reales, no por `App.Vector`). (a) Cada asignación de propiedades (`.Ancho/.Alto/.Espesor`), `.LocalPlacement/.Placement =`, `addProperty`, `addObject` y `recompute` de `ui/` pasa a una función de `cad/` (se reutilizan las existentes de `cad/documento.py` y `cad/propiedades.py` si sirven; si no, se crea una con nombre claro, p. ej. `asignar_dimensiones(obj, ancho, alto, espesor)` o `asignar_placement_local(obj, placement)`). La UI solo llama a esas funciones. Mismo valor y mismo orden de asignación. (b) La prueba se hace fiel a la regla del plan (M5 punto 3): `_tiene_escritura_freecad` detecta también `Espesor`, `LocalPlacement` y `Placement` además de `Ancho|Alto|Largo`. Tras (b), la prueba puede fallar en archivos aún no migrados; esa es la lista de trabajo.
- Archivos de la ola, un commit por archivo: `ui/vdo_zocalo_task.py`, `ui/vdo_puerta_task.py`, `ui/vdo_coco_unified_task.py`, `ui/vdo_universal_inspector.py`.
- Revertir: `git revert` del commit de D-32 (registro), del commit (b) y de cada migración por archivo.

## D-33 (ola 21)

- **D-33 (decisión del director):** `_tiene_escritura_freecad` (`tests/test_arquitectura.py`) es más amplia que la regla del plan. Marca cualquier `App.\w+` o `Part.\w+`, incluidas lecturas (`App.Console.PrintMessage`, `App.ActiveDocument`) que no escriben nada. (a) Se restringe a escrituras: `.addObject(`, `.removeObject(`, `.recompute()`, `.addProperty(` y asignaciones a `Ancho`, `Alto`, `Largo`, `Espesor`, `Placement`, `LocalPlacement`. Se quita la detección genérica de `App.\w+` y `Part.\w+`. Comprobado antes de quitarla: no hay ningún `Part.` en `ui/`; los `App.` restantes son logs o lecturas. (b) `doc.removeObject(hijo.Name)` de `ui/vdo_coco_unified_task.py` (gestión de huérfanos) es escritura y pasa a `cad/documento.py::eliminar_objeto(doc, nombre)`, con el mismo orden y efecto.
- Revertir: `git revert --no-edit` de los commits de esta ola (registro, (a) y (b)).

## D-34 (ola 22)

- **D-34:** M7 parte archivos por concepto; reapuntar imports, sin reexportaciones (P6).

## D-35 (ola 23)

- **D-35:** M7 vdo_layout partido por concepto, sin reexportaciones (P6).

## D-36 (ola 24)

- **D-36:** M7 vdo_cajon_despiece partido por concepto, sin reexportaciones (P6).

## D-39

- **D-39 (decisión del director):** M7 cad/coco. `CocoFeature` se queda en `cad/coco.py` con su nombre y ruta (sin reexportación, P6). Se extrae el cuerpo de `execute` y `_cortar_shape` a módulos por concepto dentro de `cad/`: `coco_cortes.py` (resta de formas y tiras de carcasa frente a divisiones y núcleos), `coco_carcasa.py`, `coco_shell.py`, `coco_divisiones.py` y `coco_propiedades.py`. Cada bloque es una función de módulo que recibe exactamente las variables que lee y devuelve las que escribe, en el mismo orden de operaciones. Meta: `cad/coco.py` < 400 líneas y ninguna función > 60 líneas.
- Revertir: `git revert --no-edit` de los commits de esta extracción.

## D-40 (ola 28)

- **D-40:** M7 ui/vdo_widgets_coco partido por concepto, sin reexportaciones (P6). Verificación visual pendiente (M10).
- Decisión de implementación: `DivisionesEditor` (una sola clase de ~1.600 líneas) se reparte en mixins por concepto, uno por módulo; la clase raíz queda en `ui/coco_construccion_widgets.py`. Los métodos se mueven sin cambios de código. Son cinco módulos nuevos (`coco_construccion`, `coco_inspector`, `coco_arbol`, `coco_edicion`, `coco_reengrose`), todos bajo 400 líneas. `PanelHeaderWidget` va con el inspector, porque `_actualizar_header_pieza` es quien lo actualiza.

## D-41 (ola 29)

- **D-41:** M7 ui/vdo_universal_inspector partido por concepto. Verificación visual pendiente (M10).

## D-42

- **D-42:** el bloque QT_QPA_PLATFORM (copiado en 7 archivos) pasa a freecad/vdo/__init__.py (P1). Motivo: debe ejecutarse antes de cualquier import Qt del paquete.

## D-43

- **D-43:** M7 ui/vdo_coco_unified_task partido por concepto. Verificación visual pendiente (M10).
- Decisión de implementación: la clase `CocoUnifiedTaskPanel` se reparte en mixins por concepto (`coco_unified_construccion`, `coco_unified_pestanas`, `coco_unified_valores`, `coco_unified_celdas`, `coco_unified_espacios`, `coco_unified_aplicar`), sin cambios de código en los métodos. La tabla de espacios (constantes, `EspacioRow`, `SpacesTableWidget`) va a `coco_unified_tabla`. El original queda como clase raíz con `__init__` (menos de 400 líneas), sin reexportaciones (P6); sus consumidores no cambian.

## D-44

- **D-44:** M7 ui/vdo_box_controller partido por concepto. Verificación visual pendiente (M10).
- Decisión de implementación: la clase `VDOBoxControllerWidget` queda como raíz en `ui/vdo_box_controller.py` y hereda de mixins por concepto (`box_construccion`, `box_margen`, `box_esquinas`, `box_estado`, `box_config`), sin cambios de código. Constantes, hoja de estilos y canvas van a `box_constantes`, `box_hoja_estilos` y `box_canvas`. Sin reexportaciones (P6). Los alias de clase (`get_config`, `set_config`, `seleccionar_margen`) se quedan en el mismo mixin que su destino. Ningún consumidor cambia: `coco_reengrose_widgets.py` e `inspector_pagina_pieza.py` solo importan `VDOBoxControllerWidget`.

## D-45

- **D-45:** M7 ui/vdo_chassis_widget partido por concepto. Verificación visual pendiente (M10).
- Decisión de implementación: la clase `VDOChassisControllerWidget` queda como raíz en `ui/vdo_chassis_widget.py` y hereda de mixins por concepto (`chassis_construccion`, `chassis_estilos`, `chassis_eventos`, `chassis_estado`, `chassis_config`), sin cambios de código. Constantes, tablas e iconos van a `chassis_constantes` y el canvas de sección a `chassis_canvas`. Las señales quedan en la raíz, porque son atributos de clase QObject. Los alias de método (`set_chassis_config`, `get_chassis_config`) se quedan en el mixin de su destino (`chassis_config`). Sin reexportaciones (P6).

## D-46

- **D-46:** M7 ui/vdo_reengrose_ui partido por concepto. Verificación visual pendiente (M10).
- Decisión de implementación: la clase `ReengroseBorderEditor` queda como raíz en `ui/vdo_reengrose_ui.py` y hereda de mixins por concepto (`reengrose_ui_construccion`, `reengrose_ui_eventos`, `reengrose_ui_estado`, `reengrose_ui_config`), sin cambios de código. Las constantes van a `reengrose_ui_constantes` y `VDOBoardPreview` a `reengrose_ui_preview`. La señal `changed` y `__init__` quedan en la raíz. Sin reexportaciones (P6). El único consumidor (`vdo_panel_task`) importa `ReengroseBorderEditor` desde la raíz, que no cambia.

## D-47

- **D-47:** M7 core/vdo_optimizer_core partido por concepto, sin reexportaciones (P6).
- Decisión de implementación: la lista de corte (lectura del CSV, expansión a piezas unitarias, cantos y medidas de corte) va a `core/optimizer_lista_corte.py`. El original queda como raíz con presets, kerf/margen, motor MaxRects, `optimize`, `optimize_by_group` y resumen (359 líneas). Sin reexportaciones: `tools/vdo_optimizador_cli.py` y `ui/vdo_optimizer_dialog.py` importan de cada módulo. `tools/auditoria/golden.py` añade `optimizer_core` a `AGREGADOS` para que el golden busque en ambos módulos; `tests/golden/` no cambia.

## D-48

- **D-48:** M7 core/vdo_coco_spaces partido por concepto, sin reexportaciones (P6). Golden de formas OCC verificado solo en nivel 2.
- Decisión de implementación: el modelo de caja y la clave de pieza (`_clave_pieza`, `_modificador`, `_caja_pieza`, `_ejes_pieza`, `_caja_dict`, `_fusionar_caja`, `_modo_obstaculo`, `_corte_expandido`, `_huella_caja`, `_agregar_interrupcion`, `_modo_efectivo`) van a `core/espacios_cajas.py`, sin cambios de código. La raíz `core/vdo_coco_spaces.py` (379 líneas) conserva choques, tiras y `planificar_divisiones_matriz`, e importa solo los nombres que usa. Ningún consumidor externo usa esos nombres, así que no cambia ningún import; `tools/auditoria/golden.py` no necesita cambios porque el golden solo busca `generar_divisiones_matriz`, que sigue en `cad/coco_espacios.py`. Sin ciclos nuevos; `core->cad` sigue en 0. Revertir: `git revert` del commit de esta ola.

## D-49

- **D-49:** M7 cad/cajon partido por concepto. Verificación visual pendiente (M10).
- Decisión de implementación: los helpers geométricos puros (`_box`, `_cilindro`, `_aplicar_corte`, `_corte_notch_lateral`, `_corte_pin_trasero`, `_corte_ranura_piso`, `_aplicar_bisel_45_fachada`) van a `cad/cajon_geometria.py`, sin cambios de código. La raíz `cad/cajon.py` (396 líneas) conserva `CajonFeature` y `make_cajon`, así que la ruta `factory` de `datos/modulos.json` y el golden de `module_specs` no cambian. Sin reexportaciones (P6): `tests/test_cajon_core.py` importa los helpers desde `cad/cajon_geometria`. Sin ciclos nuevos.

## D-50

- **D-50:** M7 ui/vdo_cajon_task partido por concepto. Verificación visual pendiente (M10).
- Decisión de implementación: `PanelHeaderWidget` (cabecera de cotas y cantos) va a `ui/cajon_task_cabecera.py`, sin cambios de código. `CajonTaskPanel._crear_widget` (construcción de la ventana) va a un mixin en `ui/cajon_task_construccion.py`. La raíz `ui/vdo_cajon_task.py` conserva `CajonTaskPanel` con `__init__`, selectores, carga de valores, cabecera y aceptar, y así `vdo_interfaz.py` y `vdo_view_providers.py` no cambian. Sin reexportaciones (P6). Sin ciclos nuevos.

## D-51

- **D-51:** M7 ui/vdo_puerta_task partido por concepto. Verificación visual pendiente (M10).
- Decisión de implementación: las constantes de presentación y opciones (`FAMILIAS`, `SENTIDOS_*`, `COLOR_*`) van a `ui/puerta_task_constantes.py`, sin cambios de código. `PanelHeaderWidget` va a `ui/puerta_task_cabecera.py`. `PuertaTaskPanel._crear_widget` va a un mixin en `ui/puerta_task_construccion.py`. La raíz `ui/vdo_puerta_task.py` conserva `PuertaTaskPanel` con `__init__`, carga de valores, cálculo de visibilidad, cabecera, aceptar y cancelar, y así `vdo_interfaz.py` y `vdo_view_providers.py` no cambian. Las constantes van primero para evitar ciclos: el mixin no puede importar de la raíz. Sin reexportaciones (P6).

## D-52

- **D-52:** M7 ui/vdo_hardware_manager partido por concepto. Verificación visual pendiente (M10).
- Decisión de implementación: las tablas de presentación (`FAMILIAS`, `ETIQUETAS`, `CLAVES_BOOL`) van a `ui/hardware_constantes.py`, sin cambios de código. La función `_resumen_cotas` (texto resumen de cotas para la tabla) va a `ui/hardware_resumen.py`. La raíz `ui/vdo_hardware_manager.py` conserva `VDOHardwareManagerDialog`, y `freecad/vdo/commands.py` no cambia. Sin reexportaciones (P6). La prueba `test_catalogo_herrajes_ruta` sigue leyendo el original sin cambios. Sin ciclos nuevos.

## D-53

- **D-53:** calcular_despiece (323 líneas) se divide en bloques de módulo, sin cambiar valores ni orden (P3/P5). Golden cajon_despiece y 13 snapshots son la prueba.
Ola 42: bloques movidos a core/cajon_calculo_bloques.py para cumplir P5.

## D-54

- **D-54:** funciones de core > 120 líneas divididas en bloques (zocalo, tiras perimetrales, espacios eje). Mismo criterio que D-53.

## D-55

- **D-55:** planificar_divisiones_matriz y CajonFeature.execute divididos en bloques. Mismo criterio que D-53 y D-54.

## D-56

- **D-56:** funciones de cad/ puerta.execute, panel.crear_pieza y panel.add_reengrose_props divididas en bloques. Mismo criterio que D-55.

## D-56 verificación (ola 46)

- **Verificación de D-56 en FreeCAD real:** PuertaFeature.execute anterior (6db54e2) y nuevo (69a4674 y HEAD 6bb3bbf) producen cifras crudas idénticas (volumen, área, sólidos, caras, cilindros de cazoleta, placements y todas las propiedades) para 10 configuraciones: control (Batiente Vertical, Izquierda, Parche), Derecha (Parche y Embebida/45°), Doble (Parche y Semiparche/gola), Corrediza (2 hojas tirador, 2 hojas 45°, 3 hojas Doble) y Basculante Horizontal (gola y tirador). Sin diferencias. Script fuera del repo (/tmp/ola46_eq/extraer_puertas.py).

## D-57

- **D-57:** seis funciones de core de 87-102 líneas divididas en bloques. Mismo criterio que D-54.

## D-58

- **D-58:** ocho funciones restantes de core y cad de mas de 60 lineas divididas en bloques (ver lista en el commit). Mismo criterio que D-57.

## D-59

- **D-59:** funciones de construcción de widgets de ui/ de más de 200 líneas divididas en secciones por extracción literal, verificada con AST. El comportamiento de la GUI se verifica solo con importación y nivel 2; la verificación visual queda para M10.

## D-60

- **D-60:** cinco funciones de ui/ más largas divididas en secciones por extracción literal, verificada con AST (mismo criterio que D-59). Verificación visual pendiente (M10).

## D-61

- **D-61:** cinco funciones de ui/ más largas divididas en secciones por extracción literal, verificada con AST (mismo criterio que D-59 y D-60). Verificación visual pendiente (M10).

## D-62

- **D-62:** cierre de excepciones de D-59/D-61. chassis_estilos: CSS a constante de módulo (texto idéntico, verificado). _actualizar_vista_completa: verificador AST ampliado a asignaciones de retorno. Cinco funciones más de ui/ divididas. Verificación visual pendiente (M10).

## D-63

- **D-63:** cinco funciones más de ui/ divididas por extracción literal, verificada con AST. Verificación visual pendiente (M10), que el usuario hará al final.

## D-64

- **D-64:** cinco funciones más de ui/ divididas por extracción literal, verificada con AST antes de commitear.

## D-65

- **D-65:** cinco funciones de ui/ de 73-75 líneas divididas por extracción literal, verificada con AST antes de commitear.

## D-66

- **D-66:** _pintar_vanos y cuatro funciones de ui/ de 73-75 líneas divididas. coco_arbol_widgets.py partido para respetar P5 (400 líneas).

## D-67

- **D-67:** últimas cinco funciones de ui/ de 62-66 líneas bajo 60 líneas por extracción literal, verificada con AST. Cierra M7 con classify_object resuelto en D-68 (criterio de función, P5).

- **D-68:** classify_object convertido a tabla de despacho (P3), verificado por equivalencia exacta sobre tipos de proxy.

## D-69

- **D-69:** corrección de error preexistente: `fila=` duplicado en chk_trasera hacía imposible construir el panel de zócalo (desde 23d69a9). Intención igual (fila 3). Desviación del encargo: quitar solo el duplicado no bastaba, porque `_campo` coloca los checkbox en `fila_check` (por defecto None) y el panel seguía fallando con `addWidget(QLabel, NoneType, int)`. Por eso `fila=3` se sustituye por `fila_check=3`. Verificado: ZocaloTaskPanel se construye en offscreen. Revertir: git revert del commit.

## D-70

- **D-70:** M6 usa vdo_form_builder.FormBuilder como constructor genérico (no se duplica). El panel de zócalo se migra a especificación.

## D-71

- **D-71:** M6 panel de paneles migrado a especificación. Árbol de widgets idéntico (361 nodos). Visual pendiente (M10, usuario). FormBuilder gana los tipos texto, expresion y vdo_double_spin, y la marca sin_etiqueta (celda sin etiqueta); el zócalo no cambia. Accept en normal y error (reengrose inválido) igual que la versión anterior. Revertir: git revert del commit.

## D-72

- **D-72:** M6 panel de puerta migrado a especificación. Árbol de widgets idéntico (41 nodos de rejilla, 101 QWidget incl. internos Qt; visibilidad por apertura incluida: 3 sistemas x 4 aperturas x 3 montajes = 36 combinaciones). Visual pendiente (M10, usuario). Desviaciones: FormBuilder gana estilo por clave, ajustar_texto, construir_suelto y construir_bloques (compatibles con los paneles anteriores); las listas FAMILIAS y SENTIDOS_* pasan de ui/puerta_task_constantes a datos/formularios.py (ui las reexporta) para que datos no importe de ui. Accept normal y de error idénticos a la versión anterior. Observado y no corregido: en el error, la versión anterior ya deja escritas las propiedades del objeto aunque accept devuelva False (el abort no revierte propiedades en esta prueba). Revertir: git revert del commit.

## D-73

- **D-73:** M6 panel de cajón migrado a especificación. Árbol de widgets idéntico (61 nodos de rejilla, 135 QWidget incl. internos Qt; 72 combinaciones de tipo x apertura x montaje fachada x montaje trasera; el cajón no oculta widgets). Visual pendiente (M10, usuario). Nota: el accept anterior deja propiedades escritas tras un error (preexistente, no corregido). Observado también, preexistente y no corregido: con objeto real el accept falla siempre al escribir TipoMontaje, porque las etiquetas del combo (Parche, Semiparche, Embebida) no pertenecen al enumerado (parche, semiparche, embebida). El accept normal se verificó con un enumerado de prueba y coincide con la versión anterior. La cabecera (PanelHeaderWidget) no se actualiza en el entorno de prueba (aviso en ambas versiones), así que su contenido no queda verificado con valores reales. Desviaciones: cajon_bloques(marcas) en datos/formularios.py (las marcas llegan de listar_marcas); FormBuilder gana las claves editable y texto_especial. Revertir: git revert del commit.

## D-74

- **D-74:** M6 panel de coco migrado a especificación solo en sus campos simples. Migrado: grupo Medidas Generales (alto, ancho, fondo módulo, espesor), rotación (widget creado con FormBuilder.crear; los botones ±90° siguen a mano), anclaje y los 6 combos de exposición (FormBuilder.construir_celda en la rejilla existente). Especificación en datos/formularios.py (COCO_MEDIDAS, COCO_ROTACION, COCO_ANCLAJE, COCO_EXPOSICION). Excepciones, no migradas: botones ±90° (campo más botones en fila propia, sin soporte en el builder), pestaña Estructura (VDOChassisControllerWidget), pestaña Divisiones (DivisionesEditor), pestañas de espacios/celdas/hijos (coco_unified_pestanas, coco_unified_celdas, coco_unified_espacios), resumen y el flujo de accept (chequeo de desbordamiento, insertos, divisiones, transacción). Tamaño del accept: 37 líneas en total, sin cambios de flujo; su parte migrada son 3 llamadas (_asignar_dimensiones, _asignar_anclaje_rotacion, _guardar_exposicion), cuyos cuerpos pasan por form_coco. Comparación con objeto real (make_coco nombre, alto 720, ancho 600, fondo 500, como en test_gui_wiring): árbol de 385 nodos QWidget (incluidos internos Qt), rejilla, valores, rangos, decimales, sufijos, tooltips e ítems idénticos antes y después, 0 diferencias. Accept normal: propiedades del objeto idénticas tras cambiar medidas, anclaje y exposición. Accept de error (fallo forzado al volcar divisiones): retorno False en ambas versiones y propiedades idénticas, incluidas las escritas antes del fallo (preexistente, igual que en D-72 y D-73). Valores por defecto de medidas (1.0 y 1): coinciden con el valor que Qt daba antes al acotar el 0 inicial al mínimo del rango. Revertir: git revert del commit.

## D-75

- **D-75:** M6 panel de coco: bloques en especificación y accept en métodos por bloque. Migrado: botones ±90° de rotación (COCO_ROTACION_PASOS) y pestañas Medidas, Estructura y Divisiones (COCO_PESTANAS: orden, titulo y contenedor). Accept de 8 líneas (firma incluida): el cuerpo llama a _escribir_coco (mismo orden de escritura y de llamadas que antes), _confirmar y _fallar_accept; _comprobar_divisiones contiene el aviso de overflow. Los métodos de escritura pasan a ui/coco_unified_escritura.py (CocoUnifiedEscrituraMixin); _asignar_chasis y _asignar_contenido se renombran _guardar_estructura y _guardar_divisiones. Excepciones restantes: contenido de Estructura (VDOChassisControllerWidget) y de Divisiones (DivisionesEditor), widgets propios; resumen (lbl_resumen con hoja de estilos, sin especificación); espacios e hijos (_crear_tab_espacios y _crear_grupo_hijos en ui/coco_unified_pestanas.py, sin llamadas desde el panel: no están en el árbol y no se migran ni se borran). Árbol idéntico (385 nodos, 0 diferencias). Accept normal, de error y de overflow idénticos a la versión anterior. Revertir: git revert del commit.

## D-76

- **D-76: setStyleSheet de ui/ movidos a ui/tema.py (MN-07).** Constantes con nombre por rol en tema.py; cada llamada pasa a `tema.aplicar_estilo(widget, tema.ESTILO_X)` (único setStyleSheet de ui/ fuera de tema). Conjunto de cadenas aplicadas idéntico: prueba de paneles (zócalo, panel, puerta, cajón, coco) con 32 cadenas distintas y 72 llamadas, igual que HEAD; comparación AST de todo ui/ con 81 llamadas, sin diferencias salvo las 5 expresiones f-string o de módulo (en 4 archivos) sustituidas por constantes de tema (verificadas por valor). Constantes de tema usadas: 63. Excepciones (literal de hoja fuera de tema.py, aplicado con tema.aplicar_estilo): ESTILO_WIDGET (box_hoja_estilos.py), _ESTILO_CHASSIS (chassis_estilos.py), hoja local `estilo` de vdo_hardware_manager.py y de reengrose_ui_construccion.py; son hojas de ventana completa y tema.py superaría 400 líneas (P5). Fuera de alcance (no son setStyleSheet): colores hex en SVG, HTML y QColor de ui/. Revertir: git revert del commit.

## D-77

- **D-77: M8 renombrado masivo (MN-09).** 65 archivos `freecad/vdo/**/vdo_<x>.py` renombrados a `<x>.py` con `git mv`. Mapeo en docs/archivo/mapeo_m8.md (copia en docs/mapeo_m8.md). Excluidos: ninguno por colisión, paquete existente o palabra reservada. Fuera del alcance: `tools/auditoria/verificar.py` (congelado; su línea 241 busca `vdo_<nombre>.py`). Reescritura: imports con ruta punteada y `from paquete import vdo_x`, usos del nombre, rutas en cadenas y comentarios de código, tests y tools. Golden module_specs y datos/modulos.json no cambian: ninguna ruta factory usa `vdo_*`, así que no hizo falta regenerar. Excepción: `tests/test_gui_wiring.py` y `tests/test_single_dock_convergence.py` tienen cambios sin commitear del usuario; en el commit solo entra el cambio de sus imports. Revertir: git revert del commit.

## D-78

- **D-78: M9 except que tragan errores: se añade registro con App.Console sin cambiar el flujo (P7).** Hallazgos al inicio: 87 (`minimalismo.py excepciones`). Registrados: 25 (`App.Console.PrintWarning` con el mensaje y la excepción; el `except` pasa a `as exc` cuando no lo tenía; mismo return y mismo estado). Restantes tras el cambio: 62 = 61 no tocados + 1 que ya registra. No tocados por motivo: core/ no importa FreeCAD (P4), decisión del director (19); guardas de import opcional al cargar el módulo (12); módulo sin `import FreeCAD as App`, añadirlo es cambio de dependencia (10); bucles que ignoran fila o valor mal formado a propósito (6); ya informan al usuario en etiqueta o QMessageBox (6); rutas de evento (ratón, arrastre, validador por pulsación, conversión en edición) donde registrar generaría ruido (5); `App` importado en `try` opcional, riesgo de NameError (2); fallback intencional con segundo intento (1). Revertir: git revert de los commits M9 de este registro.

## D-79

- **D-79: M9 resto de excepciones registradas. core/ usa logging de la biblioteca estandar (sin FreeCAD, P4). Flujo intacto (P7).** Modulos sin `import FreeCAD as App` (y core/) registran con `logging` (`_LOG = logging.getLogger(__name__)`); modulos con `App` registran con `App.Console`. Guardas de import opcional y rutas de evento, arrastre o validador usan `_LOG.debug`. Mismo return, mismo estado, misma propagacion. Excepcion justificada: `ui/coco_unified_task.py:297` ya registra en `_fallar_accept` (App.Console.PrintError); el conteo de `minimalismo.py excepciones` lo cuenta por el handler, no por la funcion. Revertir: git revert de los commits D-79.

## D-80

- **D-80: ruff a cero en alcance. os._exit -> sys.exit en los tests __main__ (cambios pendientes de sesion anterior, confirmados por el usuario que no hay otra sesion).** Alcance: freecad/, tests/, tools/. Paso 1: fixes seguros de ruff (sin --unsafe-fixes). `os._exit` salta la limpieza de Python; `sys.exit` la ejecuta. Revertir: git revert de los commits D-80.

## D-81

- **D-81: M9 ruff a cero en freecad/, tests/, tools/ salvo tools/auditoria/verificar.py (vetado). Excepciones con noqa y motivo en la linea.** Medido: 517 errores de linea base (`ruff check freecad tests tools --no-cache --statistics`). Automaticos seguros (87) en D-80. Manual: E402 (245 -> 0): import logging y _LOG movidos bajo los imports (D-79); en tests/ los imports tras mocks o rutas se mantienen con `noqa: E402` (83); en ui/ los imports tras la guarda de import opcional que usa _LOG se mantienen con `noqa: E402` (23). Defecto corregido: _LOG usado antes de su definicion en 5 modulos ui (NameError en tests, commit de corrección). RUF001 (47 lineas): signo tipografico (x o -) en etiquetas visibles al usuario; cambiarlo altera el texto mostrado; `noqa` con motivo. RUF002/003 (9): en comentarios y docstrings se cambio a ASCII (sin efecto en ejecucion). C901 (13 funciones con complejidad 13-20): `noqa` con motivo; dividirlas cambia el flujo sin goldens por rama, fuera del alcance de M9; pendiente de revision humana. B904: `raise ... from exc`. Resto: correcciones manuales sin cambio de salida (minimalismo.py: salida identica medida antes y despues). Pendiente: tools/auditoria/verificar.py tiene 9 errores (E741 x4, E501 x4, SIM102 x1) y no se toca por estar vetado; ruff no llega a 0 mientras no se decida. Revertir: git revert de los commits D-80 y D-81.

## D-82

- **D-82 (decisión del director): verificar.py se congela en reglas, no en estilo.** `tools/auditoria/verificar.py` no recibe reglas nuevas (P5, §5 del plan). Corregir solo estilo sin cambiar lógica, umbrales ni reglas sí está permitido.
  - **Paso 1 (commit 1f9a360):** ruff en verificar.py de 9 a 0 incidencias: 4 E741 (renombre de `l` a `ln`/`linea` solo dentro de su comprehension o bucle), 4 E501 (saltos de línea dentro de paréntesis, misma expresión), 1 SIM102 (if anidado plegado en la condición del `elif`, sin `else` en ninguno de los dos). Salida de `python3 -I tools/auditoria/verificar.py` comparada antes y después: idéntica salvo la línea `R10_ruff_check_cero`, que pasa de `FALLA valor=9` a `OK valor=0` (efecto esperado, la métrica mide ruff sobre el repo). Métricas falladas: 8 -> 7.
  - **Paso 2 (commit e3ba9c5):** `pyproject.toml`, eliminada la entrada `"freecad/vdo/app/vdo_api.py" = ["F401"]` en per-file-ignores (el directorio `app/` se eliminó en M5 y no existe). La entrada `packages` ya lista solo `freecad.vdo.core` y `freecad.vdo.cad`, sin cambio. No quedan referencias `vdo_*` en pyproject.
  - **Paso 3 (sin commit de código):** `mypy --strict freecad/vdo/core freecad/vdo/cad` = **1240 errores en 60 archivos**. Distribución: no-untyped-call 754, no-untyped-def 440, var-annotated 14, type-arg 14, arg-type 7, attr-defined 6, no-any-return 2, assignment 2, index 1. Umbral del paso (<= 60): no cumplido, no se corrige. Esfuerzo estimado alto (322 funciones sin tipar llamadas, ~440 firmas, con cascada). Queda como deuda técnica pendiente de decisión del director. Detalle en /tmp/ola71_mypy.txt.
  - **Gates tras el último commit:** nivel 1 `ejecutados=291 fallos=0 errores=0 skip=113`, 0 `FALLO golden`. Nivel 2 `ejecutados=289 fallos=0 errores=0 skip=26`.
  - **Nota de medición:** ruff 0.17.3 no imprime `Found N errors` con `--statistics` cuando no hay incidencias; el resultado en cero es salida vacía con código 0, y sin `--statistics` imprime `All checks passed!`.
  - Revertir: `git revert --no-edit` de 1f9a360 y e3ba9c5.
