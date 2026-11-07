# Plan de la fase UI y reducción

**Estado a 2026-11-06.** Documento de plan. No cambia código. Cifras tomadas de `docs/DEUDA_TECNICA.md` (con su fecha de medición) y de `docs/METRICAS_WIDGETS.md` (medición F9, D-95). Las cifras que no están medidas se marcan como tales.

**Rama:** esta fase se hará en `minimalismo/ui-diseno`, que todavía **no existe**. Se crea desde el HEAD de la rama de trabajo cuando el usuario apruebe este plan (ver §4).

---

## 1. Principios

- **P1 (un hecho, un lugar).** Cada dato, color, tabla o función se define en un solo sitio. Los duplicados abiertos son B7 (a) `rotacion_z` y (b) cargador de `ANCLAJES` en `DEUDA_TECNICA.md`.
- **P2 (datos antes que código).** Lo que es configuración de un formulario, un menú o una tabla vive en `datos/` como especificación, no como llamadas a widgets.
- **P3 (despacho tabular).** Las decisiones de tipo se resuelven con una tabla, no con cadenas de `if` o `elif`.
- **P4 (una capa de decisión).** La lógica de decisión está en `core/` y `cad/`. `ui/` presenta y recoge la entrada del usuario. Hoy `ui/` importa de `core`/`cad` en 121 líneas y `core`/`cad` no importan de `ui` (medido 2026-11-06, ver §2).
- **P5 (estructura uniforme).** Un archivo no supera 400 líneas y una función no supera 60. Medido 2026-11-06: 0 archivos de más de 400 líneas fuera de `ui/tema.py` (458 líneas; ver §2). 0 funciones de más de 60 líneas (M10, DEUDA F7/F10).
- **P6 (sin fachadas).** No se añaden módulos que solo reenvían a otros. Un módulo nuevo se justifica por una responsabilidad propia.
- **P8 (todo widget se construye desde especificación).** Ningún widget de formulario se construye a mano. La excepción es la presentación pura (etiquetas de estado, canvas, árboles, cabeceras), que es la clase C de `METRICAS_WIDGETS.md`.
- **P9 (la UI se diseña en una sola rama con su propia prueba visual antes de fusionar).** La rama de UI no se fusiona a `main` sin la verificación visual del usuario (F-UI-5).

---

## 2. Diagnóstico actual (cifras medidas)

### 2.1 Líneas por capa

| Capa | Líneas (`.py`) | Fuente y fecha |
|---|---:|---|
| `freecad/vdo/core/` | 7.757 | `wc -l`, 2026-11-06 |
| `freecad/vdo/cad/` | 2.902 | `wc -l`, 2026-11-06 |
| `freecad/vdo/ui/` | 13.461 | `wc -l`, 2026-11-06 |
| `freecad/vdo/datos/` | 356 | `wc -l`, 2026-11-06 |

- Meta de reducción (plan §1, A1 de DEUDA): ≥ 30 %. Medido: 23.608 líneas en la base (`minimalismo_base.json`) y 25.171 en el final (`minimalismo_final.json`): **+6,6 %**. **No cumplida.**
- La cifra de la capa `ui` en DEUDA A2 (14.374, M11) no coincide con la medida hoy (13.461). El método no está explicado. Hay que fijar un solo método (DEUDA A3).

### 2.2 Construcción de widgets a mano

Fuente: `docs/METRICAS_WIDGETS.md` (F9, D-95). Medición estática.

| Clase | Funciones | Líneas actuales | Ahorro neto estimado |
|---|---:|---:|---:|
| A. Patrón de formulario | 28 | 584 | 233,5 |
| B. Mixta | 7 | 240 | 99,5 |
| C. Presentación | 89 | 1.563 | 0 |
| **Total** | **124** | **2.387** | **333** (2,47 % de `ui/`) |

- Las funciones medidas suman el 17,7 % de `ui/`.
- Llamadas medidas el 2026-11-06: `QLabel(` en 109 líneas y `addWidget(` en 239 líneas de `freecad/vdo/ui` (`grep -rc`, suma 348). En M11 eran 123 y 286 (DEUDA A2).
- Hay 8 tipos de campo que faltan en `FormBuilder` (METRICAS, «Tipos de campo que faltan»).

### 2.3 Colores

- Fuera de `ui/tema.py`, en `freecad/vdo/ui` y `freecad/vdo/cad`, medido 2026-11-06: literales hex `#RRGGBB`: **0**; `rgb(`: **0**; `QColor(` con literal numérico: **0**. Las 88 llamadas `QColor(` usan constantes `tema.*`.
- Quedan **32** ocurrencias hex en **11** archivos de `docs/`. No son código.
- D-94 movió 249 literales de color (73 valores distintos, 15 archivos) a `ui/tema.py`.

### 2.4 Dependencias UI hacia core/cad

- `ui/` → `core`/`cad`: 121 líneas de importación (medido 2026-11-06).
- `core`/`cad` → `ui`: 0.
- Ciclos en `ui/`: 3 componentes (DEUDA F: U-01 cutting list, U-02 inspector, U-03 coco / drag handles / view providers).

### 2.5 Otros datos que afectan a la fase

- `noqa` en `freecad/`, `tests/` y `tools/`: 164 líneas (E402 110, RUF001 40, C901 13; 1 sin código). DEUDA C1.
- `mypy --strict` solo cubre `core/` y `cad/` (DEUDA C4). `ui/` no entra.
- Verificación visual de M6 y M7 pendiente (DEUDA I1).
- Catálogos `vdo_*.json` en `core/` (DEUDA B8, abierto).

---

## 3. Fases propuestas

Cada fase tiene objetivo, entregables, criterio de aceptación medido y prueba. La prueba headless compara el árbol de widgets (tipo, nombre de objeto, texto, valor, visibilidad, anidación) antes y después. La prueba visual es captura en FreeCAD GUI revisada por el usuario.

### F-UI-0. Sistema de diseño

- **Objetivo.** Un solo lugar para tipografía, espaciado y paleta.
- **Entregables.** Constantes de tipografía y espaciado en `ui/tema.py`. Sin widgets nuevos. Sin cambios de comportamiento.
- **Criterio medido.** Literales hex fuera de `tema.py` = 0 (ya cumplido, §2.3). `setStyleSheet` fuera de `tema.py` = 0 (DEUDA A2, M11). El árbol de widgets de cada panel que se toca es idéntico.
- **Prueba.** Headless: árbol de widgets idéntico. Visual: captura antes y después de cada panel tocado.

### F-UI-1. Generador único de formularios desde especificación

- **Objetivo.** `FormBuilder` cubre los casos de la clase A y B sin construir a mano.
- **Entregables.** Los 8 tipos que faltan (METRICAS, sección «Tipos de campo que faltan»), en este orden: (1) fila horizontal con etiquetas intercaladas; (3) botón de acción dentro del formulario; (4) ancho fijo o máximo; (6) conexión de señales en la especificación; (7) botón de opción; (8) texto de sugerencia; (2) tabla filas × columnas; (5) campo de tipo dinámico. Cada tipo con su especificación en `datos/`.
- **Criterio medido.** Cada tipo tiene prueba headless propia. Un tipo se da por aceptado cuando su primera migración deja el árbol de widgets idéntico y reduce líneas según el método de METRICAS (bruto = líneas actuales − (1 + campos), neto = bruto / 2).
- **Prueba.** Headless: prueba del tipo y árbol idéntico. Visual: no requerida en esta fase, salvo que el tipo cambie la presentación.

### F-UI-2. Paneles de formulario migrados

- **Objetivo.** Migrar las funciones de la clase A y B de METRICAS, una por commit.
- **Orden.** El de METRICAS («Orden de migración recomendado»). Primero las A sin tipo nuevo: `panel_task._crear_grupo_reengrose` (17,5), `nesting_workflow._construir_tablero` (16,5), `reengrose_ui_construccion._construir_rejilla_esquinas` (14,0), `box_construccion._construir_panel_medidas` (13,5), `coco_construccion_widgets._construir_panel_puerta` (13,5). Después las B y las que necesitan la fila horizontal.
- **Entregables.** Un commit por panel. Cada commit con su prueba. Registro del ahorro medido en `docs/METRICAS_WIDGETS.md` (no en un documento nuevo).
- **Criterio medido.** Árbol de widgets idéntico en cada commit. Ahorro acumulado comparado con el estimado de 333 líneas. Ninguna función nueva por encima de 60 líneas.
- **Prueba.** Headless (árbol idéntico y pruebas existentes en verde con `freecadcmd tools/run_tests.py`). Visual solo si el panel cambia de disposición.

### F-UI-3. COCO: divisiones, espacios y estructura

- **Objetivo.** `DivisionesEditor` y el panel COCO unificado construidos desde especificación. Afecta a `coco_construccion_widgets.py`, `coco_unified_construccion.py` y `coco_reengrose_widgets.py`.
- **Entregables.** Divisiones, espacios y estructura como componentes con su especificación en `datos/`. Se elimina la duplicación de los combos de fabricación, choque y cara (METRICAS, limitaciones), que hoy están en `reengrose_ui_construccion.py` y en `coco_reengrose_widgets.py`.
- **Criterio medido.** Árbol idéntico. Duplicado de combos de fabricación = 0 (P1). Ningún ciclo nuevo en `ui/`.
- **Prueba.** Headless y visual del panel COCO completo (es el panel con más verificación pendiente, DEUDA I1).

### F-UI-4. Inspector y listas

- **Objetivo.** Inspector (`inspector_*`, `universal_inspector`), lista de corte (`cutting_list_*`) y gestor de herrajes (`hardware_manager`).
- **Entregables.** Migración de las funciones de clase A y B de esos archivos. Deshacer los ciclos U-01 y U-02 si el cambio lo permite, moviendo lógica a `core`, no solo datos.
- **Criterio medido.** Árbol idéntico. Ciclos en `ui/`: de 3 componentes a menos (medido con `python3 -I tools/auditoria/ciclos.py`).
- **Prueba.** Headless y visual del inspector y de la lista de corte.

### F-UI-5. Verificación visual completa

- **Objetivo.** Que una persona revise la UI completa en FreeCAD GUI antes de fusionar.
- **Entregables.** Capturas antes y después de cada panel tocado en F-UI-0 a F-UI-4, con el mismo documento y la misma escala. Lista de comprobación por panel. Cierre de DEUDA I1.
- **Criterio.** Aprobación explícita del usuario por panel. Sin aprobación no hay merge.
- **Prueba.** Visual, con capturas guardadas fuera del repo (`/tmp/` o carpeta del usuario).

### F-UI-6. Cierre

- **Objetivo.** Medir el resultado y actualizar la deuda.
- **Entregables.** Nueva medición de líneas por capa, de construcción a mano y de colores. Actualización de `docs/DEUDA_TECNICA.md` (B7, B8, C1, A2, D1). Decisión nueva en `docs/DECISIONES_DELEGADAS.md` con número nuevo.
- **Criterio medido.** Cifras de §2 recalculadas con la misma herramienta y el mismo método.
- **Prueba.** Las pruebas de F-UI-0 a F-UI-4 siguen en verde.

---

## 4. Estrategia de ramas

- La fase vive en la rama nueva `minimalismo/ui-diseno`, creada desde el HEAD actual de `minimalismo/noche-20261102`. Hoy no existe.
- Cada fase se hace en commits pequeños dentro de esa rama.
- La fusión a `main` solo tras la verificación visual del usuario (F-UI-5). Si el usuario no aprueba, la rama se queda sin fusionar.
- Este documento se commitea en la rama de trabajo actual, no en `minimalismo/ui-diseno`.

---

## 5. Reglas de conducta

- **Sin cambio de comportamiento** salvo defectos registrados en `docs/DEUDA_TECNICA.md` (sección B). Cualquier otro cambio se trata como error de la fase.
- **Cada commit con prueba.** Headless por defecto. Visual cuando la disposición cambie.
- **Decisiones** en `docs/DECISIONES_DELEGADAS.md` con número nuevo (D-xx). Ninguna decisión sin número.
- **Cifras medidas.** Ninguna cifra nueva sin medir. Si una cifra se toma de un documento, se cita ese documento y su fecha.
- **Verificación con FreeCAD.** Las pruebas se ejecutan con `VDO_TEST_DIR=tests VDO_TEST_OUT=<fuera del repo> freecadcmd tools/run_tests.py`.

---

## 6. Riesgos y mitigación

| Riesgo | Mitigación |
|---|---|
| La verificación visual depende de una persona y de FreeCAD GUI. | Capturas por panel con la misma escala. Lista de comprobación. Ninguna fusión sin aprobación del usuario (F-UI-5). |
| Dependencia de FreeCAD para ejecutar las pruebas. | Las pruebas corren con `freecadcmd`. Sin FreeCAD solo se ejecutan las pruebas de modo puro. El resultado se registra con su modo. |
| Widgets que no se pueden probar sin pantalla (pintado, QSS, tamaño real). | Prueba de árbol de widgets (tipo, nombre, texto, valor, visibilidad). Lo que el árbol no cubre se valida en la captura. |
| El ahorro estimado no es el real: la medición es estática. | Se mide de nuevo al cierre (F-UI-6). El ahorro de METRICAS está sobrestimado en los combos de fabricación duplicados (METRICAS, limitaciones). |
| Un cambio de tipo de `FormBuilder` rompe paneles ya migrados. | Un commit por panel. El árbol de widgets se compara con el de antes del commit. |
| La cifra de la capa `ui` no es coherente entre documentos (14.374 frente a 13.461). | Fijar un solo método de conteo antes de F-UI-2 (DEUDA A3, usuario). |

---

## 7. Qué NO entra en la fase

- No se borra funcionalidad sin decisión del usuario. Si una función sobra, se registra como propuesta.
- No se cambia la lógica de decisión de `core/` ni de `cad/` salvo para mover lógica desde `ui/` (F-UI-4).
- No se cambian formatos de documentos ya guardados (DEUDA G1).
- No se levanta el veto de `tools/auditoria/verificar.py` (DEUDA C3) ni se amplía `mypy` a `ui/` (DEUDA C4). Son decisiones del usuario.
- No se resuelve B4 (`nesting_presets`) ni B8 (catálogos) dentro de esta fase; cada uno tiene su propia decisión.
- No se hacen cambios de presentación fuera de `ui/tema.py` (P8, P9): la paleta y la tipografía se cambian solo en F-UI-0.
