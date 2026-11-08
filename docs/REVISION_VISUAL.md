# REVISIÓN VISUAL DE LA FASE UI (F-UI-5)

**Propósito:** lista de comprobación para que una persona revise la UI completa en FreeCAD GUI por la mañana, antes de cualquier fusión a `main`. Cada panel se abre, se ejecuta una acción y se verifica lo que se ve (pintado, QSS, tamaño real, foco de teclado) — lo que las pruebas automáticas no cubren.

**Rama de trabajo:** `minimalismo/ui-diseno`. **No se fusiona a `main` sin la aprobación explícita del usuario por panel.**

---

## Regla vinculante (sección 8 del plan)

El visor 2D de coco (`CocoPreview2D`) y el editor de divisiones interactivo **no se eliminan ni se reemplazan por formularios estáticos**. Su interacción (clics, arrastre, selección de celdas) se conserva. Solo la construcción de los controles de formulario de esos paneles podía pasar a especificación; en esta fase ni siquiera eso se hace: los paneles reactivos de coco se dejan sin cambios de código (decisión D-120).

La lógica de clics, el modelo de datos y el dibujo del visor 2D quedan intactos. Si la fase dañara el visor, se corrige; no se quita la función.

---

## Paneles a revisar

| # | Panel | Qué abrió / cómo llegar | Qué acción hacer | Qué verificar (visual) | Estado |
|---|-------|------------------------|------------------|------------------------|--------|
| 1 | Nesting - pestaña "Tablero" | Task Panel de Nesting (`nesting_workflow`), pestaña "Tablero" | Cambiar preset, ancho, alto y espaciado | Etiquetas, valores, alineación de los campos, sin solapamientos | Migrado (F-UI-2a, D-111) |
| 2 | Nesting - pestaña "Algoritmo de Optimización" | Task Panel de Nesting, pestaña "Algoritmo de Optimización" | Cambiar algoritmo y generaciones | Combo y spin muestran el valor, etiquetas alineadas | Migrado (F-UI-2c, D-113) |
| 3 | Box - panel de medidas | Task Panel del box de reengrose (`box_construccion`), panel de medidas | Editar ancho tira, offset canto y espesor | Sufijos mm, rangos, alineación de campos | Migrado (F-UI-2b, D-112) |
| 4 | Inspector cabecera - micro-header de dimensiones | Inspector (`inspector_cabecera`), micro-header | Editar W, H, D | "×" intercalada, ancho fijo, sufijos W/H/D, espesor | Migrado (F-UI-2d, D-115) |
| 5 | Inspector vano - panel de subdivisión | Inspector de vano (`inspector_pagina_vano`), panel de subdivisión | Cambiar eje, partes, modo y clic en "Aplicar Subdivisión" | Botón visible, filas etiqueta+campo, orden de filas | Migrado (F-UI-2e, D-117) |
| 6 | Coco - visor 2D | Task Panel del COCO, visor 2D (`coco_preview2d`) | Seleccionar celda, panel y reengrose | Matriz de vanos, selección de celdas/paneles/reengroses, colores, tooltips, sin solapamientos | Sin cambios de código (protegido, D-119) |
| 7 | Coco - editor de divisiones | Task Panel del COCO, editor de divisiones (`coco_construccion_widgets`) | Abrir selector de contenido y elegir vacía/subdivisión/puerta/cajón | Árbol de vanos, inspector, paneles reactivos (subdivisión/puerta/cajón), reengrose, aparición/desaparición de paneles | Sin cambios de código (protegido, D-120) |
| 8 | Task panels restantes sin tocar | Task Panel de cajón, puerta, zócalo, chassis, optimizador, lista de corte, inspector universal | Cambiar un valor representativo en cada uno | Se ven igual que antes de la fase: etiquetas, valores, alineación, colores, sin solapamientos | Sin cambios de código |

### Detalle por panel

**1. Nesting - pestaña "Tablero"** (migrado, árbol de widgets idéntico)
- Abrir: Task Panel de Nesting, pestaña "Tablero".
- Acción: cambiar el preset, editar ancho, alto y espaciado.
- Verificar: etiquetas de cada campo, valores leídos, alineación vertical de las filas, sin solapamientos entre etiqueta y spin.

**2. Nesting - pestaña "Algoritmo de Optimización"** (migrado, árbol de widgets idéntico)
- Abrir: Task Panel de Nesting, pestaña "Algoritmo de Optimización".
- Acción: cambiar algoritmo y generaciones.
- Verificar: combo y spin muestran el valor elegido, etiquetas alineadas, sin recortes de texto.

**3. Box - panel de medidas** (migrado, árbol de widgets idéntico)
- Abrir: Task Panel del box de reengrose, panel de medidas.
- Acción: editar ancho tira, offset canto y espesor.
- Verificar: sufijos "mm", rangos respetados, alineación de campos, sin solapamientos.

**4. Inspector cabecera - micro-header de dimensiones** (migrado, árbol de widgets idéntico)
- Abrir: Inspector, micro-header de dimensiones.
- Acción: editar W, H, D y espesor.
- Verificar: símbolo "×" intercalado entre las tres medidas, ancho fijo de los spins, sufijos "W"/"H"/"D", valor del espesor.

**5. Inspector vano - panel de subdivisión** (migrado, árbol de widgets idéntico)
- Abrir: Inspector de vano, panel de subdivisión.
- Acción: cambiar eje, número de partes, modo y pulsar "Aplicar Subdivisión".
- Verificar: botón de acción visible, filas etiqueta+campo en orden, sin solapamientos, el botón ejecuta la acción esperada.

**6. Coco - visor 2D** (sin cambios de código, protegido por D-119 y pruebas de imagen D-119/F-UI-3a)
- Abrir: Task Panel del COCO, visor 2D.
- Acción: seleccionar una celda, un panel y un reengrose.
- Verificar: matriz de vanos dibujada, selección resaltada con color, tooltips de celdas/paneles/reengroses, colores de fondo y tiras, sin solapamientos visuales, clic en celda emite `cellClicked`.

**7. Coco - editor de divisiones** (sin cambios de código, protegido por D-120)
- Abrir: Task Panel del COCO, editor de divisiones.
- Acción: abrir el selector de contenido del vano y elegir vacía / subdivisión / puerta / cajón.
- Verificar: árbol de vanos, inspector, paneles reactivos de subdivisión/puerta/cajón que aparecen y desaparecen según el contenido, reengrose, colores y alineación, sin solapamientos.

**8. Task panels restantes sin tocar** (sin cambios de código)
- Abrir: cada Task Panel de cajón, puerta, zócalo, chassis, optimizador, lista de corte e inspector universal.
- Acción: cambiar un valor representativo en cada panel.
- Verificar: se ven igual que antes de la fase UI; etiquetas, valores, alineación, colores, sin solapamientos.

---

## Nota sobre las pruebas automáticas

Las pruebas de árbol de widgets y la huella de píxeles del visor 2D ya pasaron en nivel 1 y nivel 2 (`RESUMEN ... fallos=0`, 0 `FALLO golden`). Esta revisión es la **capa visual humana** que las pruebas no cubren: pintado real, hojas de estilo QSS, tamaño real en pantalla y foco de teclado.

---

## Criterio de cierre

El usuario aprueba **explícitamente cada panel** de la tabla. Sin aprobación de un panel, no hay merge a `main`.
