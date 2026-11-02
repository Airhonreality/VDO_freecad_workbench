# -*- coding: utf-8 -*-
"""Registro de piezas de interfaz para el motor (inversión de dependencias, D24).

El motor (core/) nunca importa ui/. Cuando necesita un panel, una vista o una acción de
interfaz, la pide aquí por clave. ui/vdo_registro.py rellena el registro al cargar la GUI.

Sin GUI el registro está vacío: `obtener` devuelve None y el motor sigue sin interfaz.
Cada entrada es un cargador perezoso (callable sin argumentos); la importación real ocurre
en el primer `obtener`, así que cargar el registro no carga Qt.
"""

_cargadores = {}
_cache = {}


def registrar(clave, cargador):
    """Asocia una clave con un cargador perezoso (callable que devuelve la pieza)."""
    _cargadores[clave] = cargador
    _cache.pop(clave, None)


def obtener(clave):
    """Devuelve la pieza registrada, o None si no hay registro (p. ej. sin GUI)."""
    if clave not in _cargadores:
        return None
    if clave not in _cache:
        try:
            _cache[clave] = _cargadores[clave]()
        except Exception:
            return None
    return _cache[clave]


def registrado(clave):
    return clave in _cargadores


def limpiar():
    """Vacía el registro (útil en pruebas)."""
    _cargadores.clear()
    _cache.clear()


def adjuntar_vista(tipo, vobj):
    """Adjunta el ViewProvider VDO del tipo indicado (p. ej. 'coco', 'panel').

    Sin GUI no hay fábrica registrada y no hace nada. Devuelve el proxy o None.
    """
    fabrica = obtener("vista." + tipo)
    if fabrica is None:
        return None
    return fabrica(vobj)
