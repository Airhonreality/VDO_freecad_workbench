"""Tablas de presentación del gestor de herrajes (UI).

Familias, etiquetas legibles de las claves técnicas y claves booleanas.
Movido sin cambios desde ui/hardware_manager.py (M7, D-52).
"""

FAMILIAS = {
    "bisagra_cazoleta": "Bisagras de Cazoleta",
    "sistema_corredizo": "Sistemas Corredizos",
}

# Mapeo clave tecnica -> etiqueta legible
ETIQUETAS = {
    "diametro_cazoleta": "Ø Cazoleta (mm)",
    "profundidad_cazoleta": "Profundidad cazoleta (mm)",
    "cota_k_default": "Cota K (mm)",
    "solape_nominal": "Solape nominal (mm)",
    "holgura_perimetral_min": "Holgura perím. mín. (mm)",
    "descuento_altura_hoja": "Descuento altura hoja (mm)",
    "traslape_minimo": "Traslape mín. (mm)",
    "ancho_piso_riel_doble": "Ancho riel doble (mm)",
    "espesor_hoja_min": "Espesor hoja mín. (mm)",
    "capacidad_peso_kg": "Capacidad peso (kg)",
    "ancho_minimo_hoja": "Ancho hoja mín. (mm)",
    "espesor_vidrio_max": "Espesor vidrio máx. (mm)",
    "luz_cerrada_sin_cenefa": "Luz cerrada sin cenefa",
    "distancia_base_frente": "Distancia base-frente (mm)",
    "separacion_tornillos_base": "Sep. tornillos base (mm)",
    "holgura_luz": "Holgura luz (mm)",
}

# Claves que se editan como casilla de verificacion (booleano)
CLAVES_BOOL = ("luz_cerrada_sin_cenefa",)
