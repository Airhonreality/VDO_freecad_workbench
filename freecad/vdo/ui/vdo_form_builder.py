# -*- coding: utf-8 -*-
# =====================================================================
# vdo_form_builder.py
# Constructor declarativo de formularios para los Task Panels VDO (D-15).
#
# Un formulario se define como una lista de campos (especificacion
# declarativa). El builder crea los widgets Qt correspondientes y expone
# metodos para leer/escribir valores por clave. El panel conserva la
# propiedad de las senales (valueChanged, toggled, etc.) y de la logica
# de negocio; el builder solo construye la UI de los campos.
#
# Campo:
#   {
#     "tipo": "double_spin" | "spin" | "checkbox" | "combo" | "label",
#     "etiqueta": str,           # etiqueta mostrada
#     "clave": str,              # clave para leer/escribir el valor
#     "valor_defecto": any,      # valor por defecto
#     "rango": (min, max) | None,# rango para spinners
#     "decimales": int | None,   # decimales (double_spin)
#     "sufijo": str | None,      # sufijo mostrado (p. ej. " mm")
#     "unidades": str | None,    # unidades (informativo)
#     "tooltip": str | None,
#     "items": [(label, data), ...] | None,  # para combo
#     "dependencias": [(clave, callable), ...],  # callbacks de dependencia
#   }
# =====================================================================

from freecad.vdo.qt_compat import QtCore, QtGui, QtWidgets


class FormField:
    """Un campo de formulario con su widget y metadatos."""

    def __init__(self, espec):
        self.tipo = espec["tipo"]
        self.etiqueta = espec.get("etiqueta", "")
        self.clave = espec["clave"]
        self.valor_defecto = espec.get("valor_defecto")
        self.rango = espec.get("rango")
        self.decimales = espec.get("decimales")
        self.sufijo = espec.get("sufijo")
        self.tooltip = espec.get("tooltip")
        self.items = espec.get("items")
        self.widget = None

    def crear_widget(self, parent=None):
        """Crea el widget Qt del campo segun su tipo."""
        if self.tipo == "double_spin":
            w = QtWidgets.QDoubleSpinBox(parent)
            if self.rango:
                w.setRange(*self.rango)
            if self.decimales is not None:
                w.setDecimals(self.decimales)
            if self.sufijo:
                w.setSuffix(self.sufijo)
            w.setValue(float(self.valor_defecto or 0.0))
        elif self.tipo == "spin":
            w = QtWidgets.QSpinBox(parent)
            if self.rango:
                w.setRange(*self.rango)
            w.setValue(int(self.valor_defecto or 0))
            if self.sufijo:
                w.setSuffix(self.sufijo)
        elif self.tipo == "checkbox":
            w = QtWidgets.QCheckBox(self.etiqueta or "", parent)
            w.setChecked(bool(self.valor_defecto or False))
        elif self.tipo == "combo":
            w = QtWidgets.QComboBox(parent)
            for label, data in (self.items or []):
                w.addItem(label, data)
            w.setCurrentIndex(0)
        elif self.tipo == "label":
            w = QtWidgets.QLabel(str(self.valor_defecto or ""), parent)
        else:
            raise ValueError(f"Tipo de campo no soportado: {self.tipo!r}")

        if self.tooltip:
            w.setToolTip(self.tooltip)
        self.widget = w
        return w

    # -----------------------------------------------------------------
    # Lectura / escritura de valor
    # -----------------------------------------------------------------
    def valor(self):
        if self.widget is None:
            return self.valor_defecto
        if self.tipo in ("double_spin", "spin"):
            return self.widget.value()
        if self.tipo == "checkbox":
            return self.widget.isChecked()
        if self.tipo == "combo":
            return self.widget.currentData()
        if self.tipo == "label":
            return self.widget.text()
        return self.valor_defecto

    def set_valor(self, valor):
        if self.widget is None:
            return
        if self.tipo in ("double_spin", "spin"):
            self.widget.setValue(valor)
        elif self.tipo == "checkbox":
            self.widget.setChecked(bool(valor))
        elif self.tipo == "combo":
            idx = self.widget.findData(valor)
            if idx >= 0:
                self.widget.setCurrentIndex(idx)
        elif self.tipo == "label":
            self.widget.setText(str(valor))


class FormBuilder:
    """Construye un formulario a partir de una lista de especificaciones."""

    def __init__(self, parent=None):
        self.parent = parent
        self.campos = {}  # clave -> FormField
        self.orden = []   # claves en orden de declaracion

    def agregar(self, espec):
        """Agrega un campo a partir de su especificacion y devuelve el Field."""
        campo = FormField(espec)
        clave = campo.clave
        self.campos[clave] = campo
        self.orden.append(clave)
        return campo

    def widget(self, clave):
        """Devuelve el widget Qt de un campo."""
        return self.campos[clave].widget

    def valor(self, clave):
        return self.campos[clave].valor()

    def set_valor(self, clave, valor):
        self.campos[clave].set_valor(valor)

    def valores(self):
        return {clave: self.campos[clave].valor() for clave in self.orden}

    def set_valores(self, valores):
        for clave, valor in valores.items():
            if clave in self.campos:
                self.campos[clave].set_valor(valor)

    def campos_decl(self):
        """Devuelve la lista de claves declaradas (en orden)."""
        return list(self.orden)


__all__ = ["FormBuilder", "FormField"]
