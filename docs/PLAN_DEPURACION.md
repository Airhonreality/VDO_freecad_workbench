# Plan de depuración (minimalismo)

**Estado: plan vinculante de esta fase.** Cada fase se ejecuta en orden. Tras cada fase se re-miden las métricas de líneas y se reportan (F8).

- F1 cajón montaje: esta ola. Corregir el accept del cajón con la opción por defecto (TipoMontaje, D-87).
- F2 guardado atómico en accept: validar antes de escribir, en puerta, cajón, coco y paneles.
- F3 zócalo volumen 0.0: investigar si es artefacto de prueba o defecto.
- F4 SIGSEGV al cerrar nivel 2: localizar y corregir.
- F5 código muerto: coco espacios/hijos y otras funciones sin llamadas.
- F6 duplicación: funciones con cuerpo idéntico o casi idéntico, consolidadas en una sola.
- F7 colores hex fuera de tema.
- F8 métricas de líneas: re-medir y reportar después de cada fase.
