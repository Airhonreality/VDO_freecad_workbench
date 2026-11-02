# ADR-005: Aislamiento de la QApplication y limpieza de widgets al salir

## Estado
aceptada (F19.2-bis / F19.3)

## Contexto
`freecadcmd tools/run_tests.py` (nivel 2) terminaba con código 139 (segfault) o
134 (`pure virtual method called` / `terminate called without an active
exception`) después de escribir el resumen. El fallo ya existía antes de F19.

Causa verificada: los tests crean widgets Qt (`CocoUnifiedTaskPanel`,
`PanelTaskPanel`, `DivisionesEditor`…) y varias `QApplication` distintas:
algunas en helpers y una a nivel de módulo (`test_vdo_chassis_widget`). Al
cerrar el intérprete, los widgets seguían vivos y Qt los destruía después de su
clase base, lo que aborta el proceso.

Medido (`freecadcmd /tmp/…/test_coco_reengrose_avanzado`): exit 139 sin
limpieza; exit 0 en 3 de 3 con una limpieza que cierra y libera los widgets de
nivel superior antes de salir.

Alternativas consideradas:
1. Excluir los tests que crean widgets. Descartado: oculta fallos (F19-D1).
2. Aislar cada archivo en su propio subproceso. Descartado por ahora: duplica
   el arranque de FreeCAD (≈3 s por archivo) y no resuelve la causa, que es el
   orden de destrucción de los widgets.
3. Limpieza al salir + una sola `QApplication` por proceso (elegida).

## Decisión
- `tests/soporte/qt.py::qapplication()` es el único punto que crea la
  `QApplication`. La instancia vive en un global hasta que termina el proceso.
  Sin pantalla usa la plataforma `offscreen`.
- Al crearla se registra `atexit` con `_cerrar_widgets()`: cierra y libera
  (`deleteLater`) los widgets de nivel superior y procesa eventos. Se ejecuta
  después de que el runner escribe su resumen, así que no altera el resultado.
- Los tests que construyen widgets llevan `@requiere_qt` y llaman a
  `qapplication()`. Los tests de geometría no tocan Qt.
- Si en el futuro un archivo sigue fallando al salir con esta limpieza, se
  aislará en subproceso y se actualizará este ADR (no se excluirá el test).

## Consecuencias
- Nivel 2 termina con código 0 (5 de 5 ejecuciones medidas en F19.2-bis).
- Todo test nuevo con widgets debe usar `qapplication()`; crear
  `QApplication` a mano en un test vuelve a reproducir el fallo.
- La limpieza solo cubre widgets de nivel superior. Un widget hijo retenido por
  un objeto Python global fuera de la app sigue siendo un riesgo.

## Referencia
- Plan de correcciones: F19.3 (H16) en `docs/PLAN_CORRECCIONES_F19.md`
- Plan maestro: sin M-NN; decisión derivada de F19-D1 (un fallo nunca se oculta).
- Commit: ver `git log` de `refactor/vdo-10`, subfase F19.2-bis F.
