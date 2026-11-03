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

## Revisión (F19.2-ter): el segfault seguía, y el disparador era el propio runner

Medido: el commit `8ede619` declaró el segfault resuelto. No lo estaba. Con
`freecadcmd tools/run_tests.py` cada una de 5 ejecuciones seguidas registró
`Program received signal SIGSEGV` durante la finalización del intérprete
(backtrace: `shiboken BindingManager::~BindingManager` → `QWidget::~QWidget`).

Reproducción aislada, sin el runner:
- Cada módulo de test que usa Qt, en su propio proceso: `rc=0`, sin SIGSEGV.
- Todos los módulos de test en un proceso con un cargador propio que termina de
  forma normal: `rc=0`, sin SIGSEGV.
- Ese mismo cargador con `sys.exit(0)` o `sys.exit(1)` al final: SIGSEGV en
  ambos casos.

Causa: `tools/run_tests.py` terminaba con `sys.exit(main())` (introducido en
`c7ad8fd`, para que el código de salida reflejara los fallos). Salir con
`SystemExit` mientras hay widgets PySide vivos dispara la destrucción de
shiboken durante la finalización, y ahí cae.

Decisión: el runner escribe el informe, vacía stdout/stderr y termina con
`os._exit(codigo)`. El código de salida sigue siendo el de los resultados
(0 si todo pasa, 1 si hay FALLO, ERROR o NO_EJECUTADO). Con `os._exit` no se
oculta ningún fallo: los resultados ya están en disco cuando termina `main()`.
Se omite solo la finalización del intérprete, que no forma parte de ningún test.

Medido tras el cambio: 5 de 5 ejecuciones de nivel 2 sin SIGSEGV y con código
1 (los 3 FALLO de `test_arquitectura`, que son trabajo pendiente de F19.4). Un
código 0 limpio solo se podrá medir cuando F19.4 cierre esos fallos.

Lo que no se hace: no se excluye ningún test ni se aísla cada módulo en su
propio proceso. El aislamiento por proceso sigue siendo una opción si el
segfault vuelve a aparecer con el runner en `os._exit`.
