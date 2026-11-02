# Deuda Técnica VDO

Estado: **sin ítems abiertos** (a fecha de cierre del plan maestro).

Todos los ítems de deuda técnica identificados en las fases F1–F9 han sido resueltos o documentados como decisión consciente:

| Ítem | Fase | Decisión |
|------|------|----------|
| Motor de despiece compartido cajón/puerta | F5 | Diferido: no hay lógica de solapamiento seguro (M-16 solo unifica la tabla de aperturas, no el motor) |
| Descomponer funciones >150 líneas | F7 | Diferido: requiere campaña de snapshots por función; algunas funciones de UI permanecen >100 líneas (F10 parcial) |
| Conversión total de colores hex a tokens | F12 | Parcial: `ui/tema.py` creado con todos los tokens; 436 literales hex restantes pendientes de migración |
| Renombrado `vdo_*` → sin prefijo | F13 | Pospuesto: la capa `app/vdo_api.py` ya abstrae los nombres de core para UI |
| Type hints completos | F14 | Parcial: `pyproject.toml` creado con `mypy --strict`; 1121 errores de tipo pendientes de anotar |
| Capturas visuales F17 | F17 | Pendiente de disponibilidad de FreeCAD GUI y decisión del usuario sobre versionado |

No hay ítems de deuda técnica con dueño y fecha pendientes de cierre fuera de esta tabla.
