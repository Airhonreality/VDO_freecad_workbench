# Herramientas de auditoría

Métricas reproducibles para comparar el estado del código antes y después de cada fase
del plan (`docs/PLAN_REFACTOR_VDO.md`).

- `ast_scan.py <carpeta>`: archivos más grandes, funciones de más de 120 líneas.
- `clones.py <carpeta>`: grupos de funciones con cuerpo AST idéntico.

Ejemplo (desde la raíz del repo):

    python3 -I tools/auditoria/ast_scan.py freecad
    python3 -I tools/auditoria/clones.py freecad

Las métricas grep de la línea base están en la sección 3 del plan.
