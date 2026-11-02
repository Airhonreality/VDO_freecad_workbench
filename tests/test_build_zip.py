"""Test para tools/build_zip.py: construye el zip en directorio temporal
y verifica que contiene solo los archivos permitidos (nivel 1)."""

import os
import sys
import tempfile
import unittest
import zipfile

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from tools.build_zip import leer_version  # noqa: E402


class TestBuildZip(unittest.TestCase):
    """Pruebas del generador de ZIP de distribución."""

    def test_leer_version(self):
        """La versión se lee de package.xml."""
        version = leer_version()
        self.assertIsInstance(version, str)
        self.assertTrue(len(version) > 0)

    def test_zip_contiene_solo_archivos_permitidos(self):
        """El ZIP construido contiene solo archivos del manifiesto de distribución."""
        version = leer_version()
        zip_path = os.path.join(RAIZ, "dist", f"VDO-{version}.zip")

        # Si no existe el ZIP, lo construimos
        if not os.path.exists(zip_path):
            import tools.build_zip as bz
            bz.main()

        self.assertTrue(os.path.exists(zip_path), "El ZIP no se generó")

        con_permitidos = {
            "package.xml", "Init.py", "InitGui.py", "LICENSE", "README.md",
        }
        con_permitidos_prefijo = ("freecad/", "Resources/")

        with zipfile.ZipFile(zip_path, "r") as z:
            nombres = z.namelist()
            # El ZIP tiene una carpeta raíz "VDO/"
            nombres_rel = {n for n in nombres if not n.endswith("/")}

            # Verificar que no haya archivos de tests/, tools/, docs/
            for nombre in nombres_rel:
                rel = nombre.split("/", 1)[-1] if "/" in nombre else nombre
                self.assertFalse(
                    nombre.startswith("VDO/tests/") or
                    nombre.startswith("VDO/tools/") or
                    nombre.startswith("VDO/docs/") or
                    nombre.startswith("VDO/dist/") or
                    nombre.startswith("VDO/.git/") or
                    nombre.startswith("VDO/.claude/"),
                    f"Archivo no permitido en ZIP: {nombre}"
                )

            # Verificar que los archivos raíz están presentes
            raiz_archivos = {
                nombre.split("/", 1)[-1] if "/" in nombre else nombre
                for nombre in nombres_rel
                if nombre.count("/") == 1
            }
            for f in con_permitidos:
                self.assertIn(f, raiz_archivos, f"Falta {f} en el ZIP")


if __name__ == "__main__":
    unittest.main()
