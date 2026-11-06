"""Resolución de la matriz a medidas y piezas (resolve_layout) con extras de reengrose."""

from freecad.vdo.core import vdo_reengrose_geometria as VDO_RE_GEOMETRIA
from freecad.vdo.core import vdo_reengrose_interferencias as VDO_RE_INTERFERENCIAS
from freecad.vdo.core.vdo_layout_matriz import Layout
from freecad.vdo.core.vdo_layout_modelo import AXIS_X, AXIS_Y, EPS, Track
from freecad.vdo.core.vdo_layout_resuelto import (
    PanelPiece,
    ResolvedCell,
    ResolvedLayout,
    ResolvedTrack,
)


def _extras_modificador(reengroses, clave, espesor):
    mod = (reengroses or {}).get(clave)
    if not mod:
        return (0.0, 0.0)
    return VDO_RE_GEOMETRIA.extras_por_cara(mod, espesor)


def _extras_borde(reengroses, clave, espesor):
    positivo, negativo = _extras_modificador(reengroses, clave, espesor)
    return (negativo, positivo)


def _extra_shell(reengroses, clave, espesor, lado):
    positivo, negativo = _extras_modificador(reengroses, clave, espesor)
    if lado in ("izquierda", "inferior"):
        return positivo
    return negativo


def _fijos_resueltos(tracks, etiqueta, warnings):
    """Medida fija de cada vano (None si es libre); los negativos pasan a 0."""
    fijos = []
    for track in tracks:
        if track.fixed is None:
            fijos.append(None)
        else:
            valor = float(track.fixed)
            if valor < 0:
                warnings.append(
                    f"{etiqueta}/{track.id}: medida fija negativa; se usa 0.")
                valor = 0.0
            fijos.append(valor)
    return fijos


def _tamanos_track(fijos, disponible, n, etiqueta, warnings):
    """Tamano de cada vano y desbordamiento. Devuelve (tamanos, overflow)."""
    suma_fijos = sum(v for v in fijos if v is not None)
    overflow = 0.0

    if suma_fijos > disponible + EPS:
        overflow = suma_fijos - disponible
        warnings.append(
            f"{etiqueta}: las medidas fijas ({suma_fijos:.1f} mm) "
            f"exceden el espacio útil ({disponible:.1f} mm).")
        factor = disponible / suma_fijos if suma_fijos > 0 else 0.0
        fijos = [None if v is None else v * factor for v in fijos]
        suma_fijos = disponible

    libres = [i for i, v in enumerate(fijos) if v is None]
    if libres:
        resto = max(0.0, disponible - suma_fijos)
        cuota = resto / len(libres)
        tamanos = [cuota if v is None else v for v in fijos]
    elif fijos:
        tamanos = list(fijos)
        tamanos[-1] += max(0.0, disponible - suma_fijos)
    else:
        tamanos = [0.0] * n
    return tamanos, overflow


def _resolver_track(tracks, total, espesor, etiqueta, warnings,
                    extras_internos=None, extra_borde_izq=0.0,
                    extra_borde_der=0.0):
    n = len(tracks)
    total = max(0.0, float(total))
    espesor = max(0.0, float(espesor))
    extras_internos = list(extras_internos or [])
    separadores = max(0, n - 1) * espesor
    disponible = total - separadores

    if disponible < -EPS:
        warnings.append(
            f"{etiqueta}: el espesor de los separadores "
            f"({separadores:.1f} mm) excede el espacio ({total:.1f} mm).")
        disponible = 0.0

    fijos = _fijos_resueltos(tracks, etiqueta, warnings)
    tamanos, overflow = _tamanos_track(
        fijos, disponible, n, etiqueta, warnings)

    resultado = []
    cursor = 0.0
    for i, track in enumerate(tracks):
        extra_izq = (
            float(extra_borde_izq) if i == 0
            else float(extras_internos[i - 1][1]))
        extra_der = (
            float(extra_borde_der) if i == n - 1
            else float(extras_internos[i][0]))
        neto = {"ancho": tamanos[i], "alto": 0.0}
        if extra_izq > EPS:
            neto = VDO_RE_INTERFERENCIAS.calcular_vano_neto_con_reengrose(
                neto, {"lado_afectado": "izquierda",
                       "espesor_extra": extra_izq})
        if extra_der > EPS:
            neto = VDO_RE_INTERFERENCIAS.calcular_vano_neto_con_reengrose(
                neto, {"lado_afectado": "derecha",
                       "espesor_extra": extra_der})
        clear_size = neto["ancho"]
        if tamanos[i] - extra_izq - extra_der < -EPS:
            warnings.append(
                f"{etiqueta}/{track.id}: el reengrose consume todo el vano.")
        resultado.append(ResolvedTrack(
            track, cursor, tamanos[i], overflow,
            clear_start=cursor + extra_izq,
            clear_size=clear_size,
            extra_izq=extra_izq,
            extra_der=extra_der))
        cursor += tamanos[i]
        if i < n - 1:
            cursor += espesor
    return resultado


def _resolver_celda(cell, x, z, w, h, espesor, pieces, warnings,
                    level, seq, nominal_x=None, nominal_z=None,
                    nominal_w=None, nominal_h=None, reengroses=None):
    nominal_x = x if nominal_x is None else nominal_x
    nominal_z = z if nominal_z is None else nominal_z
    nominal_w = w if nominal_w is None else nominal_w
    nominal_h = h if nominal_h is None else nominal_h
    resuelto = ResolvedCell(
        cell, x, z, w, h, level=level,
        nominal_x=nominal_x, nominal_z=nominal_z,
        nominal_w=nominal_w, nominal_h=nominal_h)
    if not cell.axis or not cell.children:
        return resuelto

    axis = cell.axis
    tracks = [
        Track(f"{cell.px}.{i + 1}" if axis == AXIS_X
              else f"{cell.py}.{i + 1}", child.fixed)
        for i, child in enumerate(cell.children)
    ]
    extras = []
    for i in range(1, len(tracks)):
        path = (f"x{cell.px}.{i + 1}" if axis == AXIS_X
                else f"y{cell.py}.{i + 1}")
        clave = f"division_{'x' if axis == AXIS_X else 'y'}:{path}"
        extras.append(_extras_borde(reengroses, clave, espesor))

    etiqueta = f"vano {cell.label} eje {axis}"
    total = nominal_w if axis == AXIS_X else nominal_h
    resueltos = _resolver_track(
        tracks, total, espesor, etiqueta, warnings, extras_internos=extras)

    for i, child in enumerate(cell.children):
        track = resueltos[i]
        if axis == AXIS_X:
            child_res = _resolver_celda(
                child, x + track.clear_start, z, track.clear_size, h,
                espesor, pieces, warnings, level + 1, seq,
                nominal_x=nominal_x + track.start,
                nominal_z=nominal_z,
                nominal_w=track.size,
                nominal_h=nominal_h,
                reengroses=reengroses)
        else:
            child_res = _resolver_celda(
                child, x, z + track.clear_start, w, track.clear_size,
                espesor, pieces, warnings, level + 1, seq,
                nominal_x=nominal_x,
                nominal_z=nominal_z + track.start,
                nominal_w=nominal_w,
                nominal_h=track.size,
                reengroses=reengroses)
        resuelto.children.append(child_res)

    for i in range(1, len(resueltos)):
        prev = resueltos[i - 1]
        path = (f"x{cell.px}.{i + 1}" if axis == AXIS_X
                else f"y{cell.py}.{i + 1}")
        safe = path.replace(".", "_")
        seq[0] += 1
        if axis == AXIS_X:
            pieces.append(PanelPiece(
                AXIS_X, "nested", path,
                nominal_x + prev.end, nominal_z,
                espesor, nominal_h, espesor,
                f"Division_X_{safe}_{seq[0]:03d}"))
        else:
            pieces.append(PanelPiece(
                AXIS_Y, "nested", path,
                nominal_x, nominal_z + prev.end,
                nominal_w, espesor, espesor,
                f"Repisa_Y_{safe}_{seq[0]:03d}"))
    return resuelto


def _normalizar_entrada_layout(layout):
    """Acepta Layout, texto JSON o nada y devuelve un Layout normalizado."""
    if isinstance(layout, str):
        layout = Layout.loads(layout)
    if not isinstance(layout, Layout):
        layout = Layout()
    if isinstance(layout.to_dict().get("cells"), dict):
        layout._normalizar()
    return layout


def _extras_divisiones(layout, reengroses, thickness):
    """Espesores extra de cada division interior (columnas y filas)."""
    extras_columnas = [
        _extras_borde(
            reengroses, f"division_x:x{i + 1}", thickness)
        for i in range(1, len(layout.columns))
    ]
    extras_filas = [
        _extras_borde(
            reengroses, f"division_y:y{j + 1}", thickness)
        for j in range(1, len(layout.rows))
    ]
    return extras_columnas, extras_filas


def _piezas_divisiones(columns, rows, inner_h, thickness):
    """Paneles de division vertical (X) y repisas horizontales (Y)."""
    pieces = []
    for i in range(1, len(columns)):
        prev = columns[i - 1]
        pieces.append(PanelPiece(
            AXIS_X, "root", f"x{i + 1}",
            prev.end, 0.0, thickness, inner_h, thickness,
            f"Division_X_col_{i + 1:03d}"))

    for j in range(1, len(rows)):
        prev = rows[j - 1]
        for i, col in enumerate(columns):
            pieces.append(PanelPiece(
                AXIS_Y, "root", f"y{j + 1}_x{i + 1}",
                col.start, prev.end, col.size, thickness, thickness,
                f"Repisa_Y_row_{j + 1:03d}_col_{i + 1:03d}"))
    return pieces


def _celdas_resueltas(layout, columns, rows, thickness, pieces, warnings,
                      seq, reengroses):
    """Resuelve cada celda ocupada de la matriz sobre las pistas dadas."""
    cells = []
    for row in rows:
        for col in columns:
            cell = layout.cells.get(Layout.key(col.id, row.id))
            if cell is None:
                continue
            cells.append(_resolver_celda(
                cell, col.clear_start, row.clear_start,
                col.clear_size, row.clear_size,
                thickness, pieces, warnings, 0, seq,
                nominal_x=col.start, nominal_z=row.start,
                nominal_w=col.size, nominal_h=row.size,
                reengroses=reengroses))
    return cells


def resolve_layout(layout, inner_w, inner_h, thickness, reengroses=None):
    """Resuelve la matriz completa y devuelve cajas/paneles locales.

    ``reengroses`` es un dict clave_pieza -> modificador. Las divisiones y
    laterales con reengrose reducen la luz clara del vano afectado; la
    geometria nominal queda disponible para el recorte/mocheo de repisas.
    """
    layout = _normalizar_entrada_layout(layout)
    inner_w = max(0.0, float(inner_w))
    inner_h = max(0.0, float(inner_h))
    thickness = max(0.0, float(thickness))
    reengroses = reengroses or {}
    warnings = []

    extra_izq = _extra_shell(
        reengroses, "lateral_izquierdo", thickness, "izquierda")
    extra_der = _extra_shell(
        reengroses, "lateral_derecho", thickness, "derecha")
    extra_inf = _extra_shell(
        reengroses, "base", thickness, "inferior")
    extra_sup = _extra_shell(
        reengroses, "techo", thickness, "superior")
    extras_columnas, extras_filas = _extras_divisiones(
        layout, reengroses, thickness)

    columns = _resolver_track(
        layout.columns, inner_w, thickness, "columnas", warnings,
        extras_internos=extras_columnas,
        extra_borde_izq=extra_izq,
        extra_borde_der=extra_der)
    rows = _resolver_track(
        layout.rows, inner_h, thickness, "filas", warnings,
        extras_internos=extras_filas,
        extra_borde_izq=extra_inf,
        extra_borde_der=extra_sup)

    pieces = _piezas_divisiones(columns, rows, inner_h, thickness)
    # seq cuenta una pieza por cada division o repisa creada.
    seq = [len(pieces)]
    cells = _celdas_resueltas(
        layout, columns, rows, thickness, pieces, warnings, seq, reengroses)

    return ResolvedLayout(
        inner_w, inner_h, thickness, columns, rows, cells, pieces, warnings)
