# Plan maestro de minimalismo VDO

**Estado:** vinculante. **Sustituye** a `docs/PLAN_MAESTRO_VDO.md` y a `docs/PLAN_CORRECCIONES_F19.md`. Esos dos planes midieron capas y cumplimiento de reglas, pero no midieron el volumen de información ni la redundancia. Este plan sí.

**Objetivo único:** que el código de VDO tenga **la menor cantidad de información posible** para expresar el mismo comportamiento de carpintería. Cada hecho del dominio se escribe una sola vez. Cada archivo tiene una estructura uniforme y tabular. El comportamiento (cifras de piezas, cortes, costos, geometría y flujos de creación) no cambia.

**No es objetivo:** cumplir una rúbrica de estilo, añadir funciones, ni reescribir la UI desde cero. Las reglas de estilo (ruff, mypy, límite de líneas) son herramientas para medir este objetivo, no fines en sí mismos. Se aplican donde reducen información, no en todo el repositorio por defecto.

---

## 0. Principios (vinculantes)

| # | Principio | Qué significa en la práctica |
|---|---|---|
| P1 | **Un hecho, un lugar** | Cada regla, catálogo, etiqueta, color, icono o valor por defecto se define en un solo sitio. Lo demás lo referencia. |
| P2 | **Datos antes que código** | Lo que es una tabla (especificaciones de módulos, catálogos, sistemas de apertura, etiquetas) vive en una tabla o en un archivo de datos. El código solo contiene comportamiento. |
| P3 | **Despacho tabular, no cadenas** | Una decisión sobre un valor del dominio con 4 o más ramas se escribe como tabla de despacho (`dict` valor → función o dato), no como `if/elif`. |
| P4 | **Una sola capa de decisión** | El cálculo vive en `core/` y no sabe de FreeCAD ni de Qt. La escritura en FreeCAD vive en `cad/`. La presentación vive en `ui/`. No hay capas intermedias sin lógica. |
| P5 | **Estructura de archivo uniforme** | Todo módulo sigue la plantilla de §4. Un concepto por archivo. |
| P6 | **Sin fachadas** | Un módulo que solo reexporta, traduce nombres o encadena llamadas sin decidir nada se elimina. |
| P7 | **Comportamiento congelado** | Ninguna fase cambia una cifra producida por el workbench sin que un golden lo apruebe explícitamente. |
| P8 | **Métrica antes que afirmación** | Cada fase cierra con cifras medidas por `tools/auditoria/minimalismo.py` y con la salida literal pegada en el registro. |

---

## 1. Línea base medida

Medido sobre `refactor/vdo-10` (HEAD `e4b10d3`). Los números de esta tabla son los que el plan debe reducir.

| Métrica | Línea base | Meta al cierre |
|---|---|---|
| Líneas Python en `freecad/vdo/` | **23.920** en 88 archivos | Reducción medida ≥ 30 % sin cambio de comportamiento |
| Líneas por capa | `core` 8.766 · `ui` 13.474 · `cad` 372 · `app` 518 | `ui` reducido a presentación; `app/` eliminado |
| Hechos de aperturas definidos en sitios distintos | **5** (`vdo_facade_contract`, `vdo_cajon_despiece`, `vdo_puerta_despiece` con mapa legado y `_normalizar_apertura`, `ui/vdo_puerta_task` con `APERTURA_LABELS`, `ui/vdo_cajon_task`) | **1** (tabla única) |
| Tablas idénticas duplicadas | **2** pares: `ANCLAJES` y `ANCLAJE_LABELS` (en `cad/propiedades.py` y `core/vdo_module_props.py`, con AST idéntico) | **0** |
| `LUCIDE_ICONS` (tabla de iconos) | **2** copias (19 y 72 líneas) | **1** |
| Catálogo de herrajes duplicado en código | `_FALLBACK_BISAGRA` (48) y `_FALLBACK_CORREDIZO` (34) en `vdo_hardware_hub.py`, mientras `vdo_hardware_catalog.json` ya contiene esos datos | **0** (un solo origen: el JSON) |
| Especificaciones de módulo escritas como código | `MODULE_SPECS` de 162 líneas en `core/vdo_module_specs.py` | Datos en tabla declarativa o JSON |
| Literales de valor de dominio repetidos | `"melamina_standar"` **26** usos, `"blum_tandem"` **14**, `"oculta"` 9, `"tirador"` 8 | **0** fuera de la tabla de datos |
| Funciones con ≥ 4 ramas por cadena literal | **16** (la mayor: `generar_tiras_perimetrales`, 19 ramas) | **0** (despacho tabular) |
| Módulos de más de 600 líneas | **10** (el mayor: `vdo_reengrose.py`, 1.846) | **0** |
| Bloques `__all__` de reexportación | 6 (33 a 47 líneas cada uno en varios casos) | **0** salvo `__init__.py` de paquete |
| Estilo y widgets | `setStyleSheet` **90**, `QLabel(` **171**, `addWidget` **401** | Estilos desde tabla de tema; widgets desde especificación |
| Funciones de más de 100 líneas | 25 | **0** (como consecuencia de P3 y P5, no como objetivo separado) |
| `ruff check` | 260 incidencias | **0** en el alcance del plan |

**Nota de método:** `ui` ocupa el 56 % del código. Por eso la mayor parte de la reducción esperada está allí, en los formularios repetidos, los estilos y los widgets construidos a mano.

---

## 2. Decisiones cerradas

| ID | Decisión | Motivo |
|---|---|---|
| MN-01 | **Se elimina `app/`** (518 líneas de casos de uso esqueleto y DTO) | Son una capa sin decisión propia. Las funciones que tengan lógica pasan a `core/` (decisión) o a `cad/` (escritura). Las que solo coordinan pasan a `commands.py`. |
| MN-02 | **Tres capas y entrada**: `core/` (datos y cálculo puro), `cad/` (escritura FreeCAD), `ui/` (Qt y presentación), `commands.py` + `Init.py` + `InitGui.py` (entrada) | Es el mínimo que separa lo que cambia por motivos distintos (dominio, plataforma, presentación). |
| MN-03 | **Reglas de dependencia**: `core` no importa nada del paquete. `cad` importa `core`. `ui` importa `core` y `cad`. `commands` importa todo. | Una sola dirección. Se verifica con `tests/test_arquitectura.py`, que ya existe. |
| MN-04 | **Datos en `freecad/vdo/datos/`**: JSON para catálogos y tablas de especificación; módulos `.py` de una sola tabla solo cuando el dato necesita referencias a código. | Un lugar para todo lo que es información y no comportamiento. |
| MN-05 | **Catálogo de herrajes: solo el JSON.** Se eliminan los `_FALLBACK_*`. Si el archivo falta, falla con error claro. | Hoy hay dos fuentes del mismo hecho. |
| MN-06 | **Tabla única de sistemas de apertura** en `core/aperturas` (datos: nombre, cantos, descuento de gola, bisel, expulsor, etiqueta, valor legado). Cajón y puerta la consultan. Los motores de cálculo siguen separados. | Son 5 definiciones de un mismo concepto. |
| MN-07 | **Tabla única de estilos y colores** en `ui/tema`. Ningún literal de color fuera. | 417 literales hex hoy. |
| MN-08 | **Formularios desde especificación** para los 5 paneles. Cada panel = una tabla de campos + un `accept` de pocas líneas. | Hoy cada panel repite construcción de widgets, señales y validación. |
| MN-09 | **Renombrado `vdo_*` → nombre sin prefijo**, último paso y mecánico. | El prefijo repite el nombre del paquete. |
| MN-10 | **Reglas de estilo medidas, no impuestas globalmente**: `ruff` en el alcance del plan (0 incidencias). `mypy --strict` solo en `core/` y `cad/`. Sin límite artificial de líneas: el límite de 400 líneas por archivo y de 60 por función sale de P5, no de una regla genérica. | Reduce el ruido de tipos y el trabajo sin reducir información. |
| MN-11 | **Documentación mínima:** `ARQUITECTURA.md` (estructura y reglas), `GLOSARIO.md` (términos), `DEUDA_TECNICA.md` (ítems con responsable). Los ADR solo para decisiones que cambian estructura (MN-01 a MN-06, MN-09). Los 24 ADR anteriores se descartan. | La documentación también es información. |
| MN-12 | **Un solo registro de progreso**: `docs/PROGRESO_MINIMALISMO.md`. Los anteriores se archivan en `docs/archivo/`. | Un lugar para el estado. |
| MN-13 | **Los planes anteriores quedan archivados** en `docs/archivo/`, con una línea que indique que fueron sustituidos. | Evitar que un agente ejecute dos planes a la vez. |
| D-04 | **Alcance de medición de ruff y mypy (fijado en M0).** *Ruff:* `ruff check .` desde la raíz, sin excluir carpetas, con ruff 0.17.3 de `.venv`. Medido: **299** incidencias (`freecad/` 147, `tests/` 86, `tools/` 58, `Init.py` + `InitGui.py` 8). *Mypy:* el paquete de `pyproject.toml` (`core`, `app`, `cad`), con mypy 2.4.1 de `.venv`. Medido: **1081** errores (`core` 1008, `app` 45, `cad` 28). `ui/` no entra en mypy. | Reducir el alcance para bajar la cifra oculta incidencias. Se mide siempre igual y se reporta el desglose. MN-10 dice "mypy solo en `core/` y `cad/`", pero la configuración incluye `app/`; se mantiene la configuración, porque quitar `app/` oculta 45 errores. Si se quiere quitarlo, es decisión humana. |

---

## 3. Plantilla de archivo (P5)

Todo módulo de `core/` y `cad/` sigue este orden, sin excepciones:

```
"""Una frase: qué concepto de dominio resuelve este archivo."""

# 1. DATOS — tablas constantes (dict, tuple, o carga de datos/*.json)
# 2. TIPOS — dataclasses inmutables de entrada y salida (plan)
# 3. CÁLCULO — funciones puras que devuelven planes; sin efectos
# 4. (solo cad/) APLICACIÓN — funciones que escriben un plan en el documento
```

Reglas:
- Un archivo = un concepto. Si un archivo tiene dos conceptos, se divide. Si dos archivos tienen el mismo concepto, se unen.
- Un archivo de más de 400 líneas se divide por concepto, no por tamaño.
- Ninguna función supera 60 líneas. Si una función necesita más, su lógica es una tabla o hay dos conceptos mezclados.
- Las funciones de despacho usan tablas (`TABLA[valor](args)`), no cadenas `if/elif`.

Plantilla de `ui/`:

```
"""Una frase: qué pantalla o widget construye."""
# 1. ESPECIFICACIÓN — tabla de campos (etiqueta, tipo, rango, valor por defecto, dependencias) desde datos/
# 2. CONSTRUCCIÓN — una función genérica que convierte la especificación en widgets (ui/formulario.py)
# 3. ACEPTAR — lee valores y llama a cad/ o core/; máximo 10 líneas
```

---

## 4. Anti-patrones prohibidos

Una fase no puede cerrar si introduce o deja cualquiera de estos:

| Anti-patrón | Detección |
|---|---|
| Dato de dominio como literal fuera de `datos/` | `minimalismo.py literales` |
| Misma tabla o misma regla en dos archivos | `minimalismo.py duplicados` (compara AST de tablas y de funciones) |
| Cadena `if/elif` con ≥ 4 ramas sobre un valor de dominio | `minimalismo.py ramas` |
| Módulo que solo reexporta o renombra | `minimalismo.py fachadas` |
| Archivo de más de 400 líneas | `minimalismo.py tamano` |
| Función de más de 60 líneas | `minimalismo.py tamano` |
| `except` que traga errores | `grep` y `minimalismo.py excepciones` |
| Estilo o color literal fuera de `ui/tema` | `minimalismo.py literales` |
| Import que viola MN-03 | `tests/test_arquitectura.py` |

---

## 5. Herramienta de medición

Se crea en M0: `tools/auditoria/minimalismo.py`, con subcomandos:

- `resumen`: líneas por capa, por archivo, número de módulos, número de funciones, tamaño de la API pública (`__all__` y símbolos sin prefijo `_`).
- `duplicados`: tablas constantes idénticas por AST y funciones con cuerpo idéntico entre archivos.
- `literales`: valores de dominio repetidos (lista de valores a vigilar en `datos/vigilados.json`).
- `ramas`: funciones con cadenas `if/elif` de 4 o más ramas.
- `fachadas`: módulos cuyo cuerpo son solo imports y reexportaciones.
- `tamano`: archivos > 400 líneas y funciones > 60 líneas.
- `excepciones`: `except` sin re-lanzamiento ni registro.

Salida: JSON y tabla. Código de salida 0 solo si el alcance de la fase cumple su meta.

`tools/auditoria/verificar.py` y sus reglas R1–R14 quedan **congelados**: no se añaden reglas nuevas. Sus valores se reportan como referencia, pero el cierre de fase se decide con `minimalismo.py`.

---

## 6. Fases

Cada fase lista: objetivo, pasos, **meta medida**, y **prueba de comportamiento**. Ninguna fase empieza sin que la anterior haya cerrado.

### M0 — Congelar comportamiento y medir

**Objetivo:** tener una referencia contra la que comparar cada cambio.

Pasos:
1. Crear `tools/auditoria/minimalismo.py` con los subcomandos de §5.
2. Ejecutar `resumen`, `duplicados`, `literales`, `ramas`, `fachadas`, `tamano`, `excepciones` sobre el estado actual. Guardar en `docs/metricas/minimalismo_base.json`.
3. Crear **goldens de comportamiento completos**: para cada flujo de creación (`crear_pieza`, `make_coco`, `make_zocalo`, `make_cajon`, `make_puerta`) y para cada módulo de cálculo puro, guardar salidas en `tests/golden/`. Los 9 goldens actuales se completan con los que falten. Generados desde el código actual, aprobados por el humano antes de commit.
4. Restaurar la suite de nivel 2 (reengrose, zócalo, comandos, creación) a `tests/` ejecutable por `freecadcmd`. Sin mover archivos fuera del runner. Sin reclasificar fallos.
5. Documentar el estado de partida en `docs/PROGRESO_MINIMALISMO.md`.

**Meta:** `minimalismo_base.json` existe; goldens de todos los flujos de creación y cálculo existen; nivel 2 corre sin fallos de comportamiento previo conocido, o los fallos están documentados con causa.

**Prueba de comportamiento:** el golden de cada flujo pasa en el estado actual.

---

### M1 — Inventario de hechos

**Objetivo:** saber cada hecho del dominio, dónde está definido y dónde se usa, antes de moverlo.

Pasos:
1. Generar `docs/INVENTARIO_HECHOS.md` con una fila por hecho: nombre, tipo (catálogo, regla, etiqueta, icono, valor por defecto, color, especificación), archivos donde se define, archivos donde se usa, destino propuesto.
2. Clasificar cada hecho duplicado (ver §1) y elegir el destino único según MN-04 a MN-07.
3. Listar archivos que son fachada o reexportación (salida de `minimalismo.py fachadas`) y su destino: eliminar o absorber.

**Meta:** inventario completo; cada hecho duplicado tiene un destino único decidido.

**Prueba de comportamiento:** ninguna (solo inventario). Los goldens siguen en verde.

---

### M2 — Un hecho, un lugar: datos

**Objetivo:** que ningún dato de dominio esté escrito dos veces ni como literal disperso.

Pasos:
1. `ANCLAJES` y `ANCLAJE_LABELS`: una sola definición en `datos/`. Eliminar la copia de `core/vdo_module_props.py` o de `cad/propiedades.py` según el destino del inventario.
2. `LUCIDE_ICONS`: una sola tabla en `ui/tema`. Eliminar la copia.
3. Catálogo de herrajes: eliminar `_FALLBACK_BISAGRA` y `_FALLBACK_CORREDIZO`. El JSON es la única fuente. Si el JSON falta, error explícito.
4. `MODULE_SPECS` (162 líneas): pasar a `datos/modulos.json` o a tabla declarativa de datos, sin lógica dentro.
5. Literales de dominio (`melamina_standar`, `blum_tandem`, `oculta`, `tirador`, ...): reemplazar por referencias a la tabla de datos o por constantes importadas desde un único módulo de datos.

**Meta:**
- `minimalismo.py duplicados` → 0 tablas idénticas.
- `minimalismo.py literales` → 0 literales vigilados fuera de `datos/`.
- Líneas de `core/vdo_hardware_hub.py` y `core/vdo_module_specs.py` reducidas en el importe medido.

**Prueba de comportamiento:** goldens de todos los flujos iguales. Si un valor cambia por unidades o redondeo, el cambio se declara y se aprueba.

---

### M3 — Un hecho, un lugar: sistemas de apertura

**Objetivo:** una sola tabla de sistemas de apertura.

Pasos:
1. Crear `core/aperturas` con una tabla: `sistema` → `{etiqueta, cantos_especiales, descuento_gola, bisel_45, expulsor, valor_legado}`.
2. Migrar `vdo_facade_contract`, `vdo_cajon_despiece` (constantes de clase y funciones `necesita_*`), `vdo_puerta_despiece` (`APERTURA_LEGADO_A_CONTRATO`, `APERTURA_DESCUENTO_ALTO`, `_normalizar_apertura`) y las etiquetas de `ui/vdo_puerta_task` y `ui/vdo_cajon_task` a consultas sobre esa tabla.
3. Eliminar las 5 definiciones antiguas.
4. Los motores de cálculo de cajón y puerta **no se unifican**: solo se unifica la tabla de reglas.

**Meta:** `minimalismo.py duplicados` sin reglas de apertura repetidas; una sola definición de cada sistema.

**Prueba de comportamiento:** golden de `cajon_despiece` y `puerta_despiece` idéntico. Los 13 snapshots actuales deben pasar sin cambio.

---

### M4 — Despacho tabular

**Objetivo:** las 16 funciones con cadenas `if/elif` pasan a tablas de despacho o a datos.

Pasos:
1. Por cada función de la lista de `minimalismo.py ramas`: identificar el valor que decide y reemplazar la cadena por `TABLA[valor]`.
2. Orden: primero las de `core/` (tienen golden), luego las de `ui/` (tienen prueba de nivel 2 o verificación visual).
3. `generar_tiras_perimetrales` (19 ramas) se reescribe como tabla de lados y reglas, no como cadena.

**Meta:** `minimalismo.py ramas` → 0.

**Prueba de comportamiento:** golden de cada función afectada igual.

---

### M5 — Capas y escritura en FreeCAD

**Objetivo:** cumplir MN-02 y MN-03 sin capas intermedias.

Pasos:
1. Eliminar `app/` (MN-01). Mover cada función con lógica de decisión a `core/` y cada función de escritura a `cad/`. Las funciones de coordinación se mueven a `commands.py` o a la UI que las llama.
2. Para cada `make_*` (`make_zocalo`, `make_panel`, `make_puerta`, `make_cajon`, `make_coco`): separar el plan (datos en `core/`) de la aplicación (escritura en `cad/`), con golden antes y después. Orden: zócalo, panel, puerta, cajón, coco.
3. La UI llama a `commands` o a `cad/`. Ningún módulo de `ui/` escribe propiedades de objetos FreeCAD ni importa `core` fuera de tablas de datos y funciones de cálculo puro.
4. Reconectar la colocación interactiva (`iniciar_colocacion`) en el flujo de creación. Es una regresión registrada: estaba conectada en `b78de04` por `core/vdo_creation_flow.py:124`.

**Meta:**
- `freecad/vdo/app/` no existe.
- `tests/test_arquitectura.py` en verde con las reglas MN-03.
- Ninguna escritura en FreeCAD fuera de `cad/` (`minimalismo.py` o grep equivalente, con lista de patrones).
- Flujo de creación con colocación probado en nivel 2.

**Prueba de comportamiento:** goldens de creación iguales, y el test de colocación pasa.

---

### M6 — Formularios tabulares

**Objetivo:** que los 5 paneles sean tablas de campos y un `accept` corto.

Pasos:
1. Crear `ui/formulario.py`: una función que convierte una especificación (lista de campos desde `datos/`) en widgets, con valores, rangos y dependencias.
2. Migrar en este orden: zócalo, panel, puerta, cajón, coco (el mayor, dividido en subformularios por bloque).
3. Cada panel migrado: su `_crear_widget` y su `accept` se reducen a llamadas a la función genérica y a la lectura de la especificación.
4. Estilos: los `setStyleSheet` pasan a una tabla de estilos en `ui/tema`. Los `QLabel(` y `addWidget` repetidos se reemplazan por la función genérica.

**Meta:**
- Cada panel: `accept` ≤ 10 líneas.
- `setStyleSheet` fuera de `ui/tema` → 0.
- `QLabel(` y `addWidget` en paneles migrados → reducidos por la función genérica (cifra medida antes y después, en el registro).
- Líneas de `ui/` reducidas en el importe medido.

**Prueba de comportamiento:** para cada panel, la especificación generada coincide con el golden de campos, valores por defecto y rangos capturado en M0. Verificación visual en nivel 3 si hay sesión gráfica disponible; si no, la fase queda con esa verificación pendiente y declarada.

---

### M7 — Estructura de archivos

**Objetivo:** que cada archivo cumpla P5 y que no haya archivos mezclados ni triviales.

Pasos:
1. Dividir los archivos de más de 400 líneas por concepto (lista de `minimalismo.py tamano`). Mayores: `vdo_reengrose.py` (1.846), `vdo_widgets_coco.py` (1.719), `vdo_universal_inspector.py` (1.604), `vdo_coco_unified_task.py` (1.314), `vdo_box_controller.py` (1.231), `vdo_chassis_widget.py` (1.151), `vdo_layout.py` (871), `vdo_reengrose_ui.py` (694), `vdo_coco_core.py` (629), `vdo_cajon_despiece.py` (628).
2. Unir archivos con el mismo concepto y menos de 80 líneas cada uno.
3. Eliminar los bloques `__all__` de reexportación fuera de `__init__.py` de paquete.
4. Aplicar la plantilla de §3 a cada archivo de `core/` y `cad/`, y la de §3 (ui) a cada panel.
5. Límite de función: 60 líneas. Las funciones que lo superan se dividen o se convierten en tabla.

**Meta:**
- `minimalismo.py tamano` → 0 archivos > 400 líneas, 0 funciones > 60 líneas.
- `minimalismo.py fachadas` → 0.
- Número de módulos reducido en el importe medido.

**Prueba de comportamiento:** goldens iguales.

---

### M8 — Nombres

**Objetivo:** MN-09.

Pasos:
1. Script `tools/auditoria/renombrar.py`: `vdo_<x>.py` → `<x>.py` en el paquete, con reescritura de imports en código, tests y documentación. Un commit único.
2. Verificación completa tras el renombrado: nivel 1, nivel 2, goldens, `test_arquitectura.py`.

**Meta:** ningún archivo dentro de `freecad/vdo/` empieza con `vdo_` (salvo los que MN-09 excluya, que deben enumerarse).

**Prueba de comportamiento:** todas las pruebas de M7 iguales.

---

### M9 — Excepciones y calidad mecánica

**Objetivo:** que los errores no se traguen y que el código pase los linters en su alcance.

Pasos:
1. Eliminar `except … pass` y `except` que traguen errores. Un error se re-lanza, o se registra con `App.Console` y se devuelve un valor explícito documentado.
2. `ruff check` → 0 en el alcance del plan (`freecad/`, `tests/`, `tools/`). Las correcciones automáticas primero; después a mano. Sin `noqa` sin motivo en la línea.
3. `mypy --strict` solo en `core/` y `cad/` → 0 errores.

**Meta:** `minimalismo.py excepciones` → 0; `ruff check` → 0; `mypy` en alcance → 0.

**Prueba de comportamiento:** goldens iguales. Un error antes silenciado que ahora aparezca se analiza: se corrige el origen o se documenta como comportamiento deseado.

---

### M10 — Verificación final

**Objetivo:** demostrar con medición que el objetivo se cumplió.

Pasos:
1. `minimalismo.py resumen` y todas las subcomandos → `docs/metricas/minimalismo_final.json`.
2. Nivel 1 y nivel 2 completos, con salida literal.
3. Verificación en FreeCAD GUI de cada flujo de creación (nivel 3), con capturas comparadas contra M0. Si no hay sesión gráfica revisable por una persona, la fase queda pendiente y se declara.
4. Instalación limpia con `tools/build_zip.py` en un HOME temporal.
5. Tabla antes/después en `PROGRESO_MINIMALISMO.md`, con cada cifra de §1 y su valor final.

**Meta:** cada cifra de §1 cumple su meta de cierre, o tiene una justificación por escrito aprobada por el humano.

---

### M11 — Documentación

Pasos:
1. `docs/ARQUITECTURA.md`: capas, reglas MN-02 y MN-03, plantilla de §3, mapa de archivos.
2. `docs/GLOSARIO.md`: términos del dominio y su tabla de datos.
3. `docs/DEUDA_TECNICA.md`: solo ítems con responsable y fecha. Si no hay, el documento lo dice.
4. ADR solo para MN-01 a MN-06 y MN-09 en `docs/adr/`.
5. Archivar los planes anteriores (MN-13) y los registros antiguos.

---

## 7. Reglas de ejecución

1. **Una fase, una meta medida.** Ninguna fase se da por cerrada sin la salida de `minimalismo.py` para su meta.
2. **Goldens:** se regeneran solo con aprobación humana del diff. Si un golden cambia, la fase se detiene.
3. **Ninguna reclasificación de fallos ni mover tests fuera del runner** para que una fase pase. Un SKIP solo por entorno detectado en tiempo de ejecución.
4. **Un commit por subfase**, en español, con `Co-Authored-By: Claude Haiku 5.5 <noreply@anthropic.com>`. Sin push, sin merge a `main`.
5. **Revertir si rompe:** si una subfase rompe un golden o una meta ya cumplida, se revierte solo esa subfase y se escribe el motivo.
6. **Sin funciones nuevas.** Si una fase encuentra un comportamiento que parece faltar, se documenta en `DEUDA_TECNICA.md` y no se implementa.
7. **Restricciones de entorno:** no cambiar el enlace `~/.local/share/FreeCAD/Mod/VDO`. Verificar con `readlink` al terminar.
8. **Honestidad del registro:** cada cifra del registro se pega desde la salida real del comando. Las cifras que no coincidan con la medición se corrigen en el mismo commit.

---

## 8. Riesgos

| Riesgo | Mitigación |
|---|---|
| Reducción de líneas a costa de comportamiento | Goldens de M0 antes de cualquier cambio. Meta de reducción solo cuenta si los goldens pasan. |
| Las tablas de datos ocultan lógica | Los datos no pueden contener código. Lo que necesite lógica se queda en funciones. |
| La UI genérica es más difícil de depurar | Especificación y widgets se prueban por separado. Verificación visual en M10. |
| Renombrado masivo rompe imports | M8 en un commit único, con todas las pruebas. |
| Sin sesión gráfica no hay verificación visual | Declarado en M6 y M10; no se da por cumplido. |

---

## 9. Lo que decide el humano

- Aprobar los goldens de M0 antes de cualquier commit de código nuevo.
- Aprobar cualquier cifra de comportamiento que cambie (redondeo, unidades).
- Aprobar el resultado de M10 y las capturas visuales.
- Confirmar los ítems de `DEUDA_TECNICA.md` y sus responsables.
