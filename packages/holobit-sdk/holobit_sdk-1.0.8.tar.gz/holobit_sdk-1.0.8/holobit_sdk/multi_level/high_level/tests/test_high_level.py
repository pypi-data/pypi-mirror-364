import unittest
from holobit_sdk.multi_level.high_level.hololang_parser import HoloLangParser
from holobit_sdk.multi_level.high_level.compiler import HoloLangCompiler
from holobit_sdk.multi_level.high_level.debugger import HoloLangDebugger



class TestHighLevel(unittest.TestCase):
    """
    Pruebas unitarias para el Nivel Alto del SDK Holobit.
    """

    def setUp(self):
        self.parser = HoloLangParser()
        self.compiler = HoloLangCompiler()
        self.debugger = HoloLangDebugger()

    def test_crear_variable(self):
        """ Prueba la creación de variables en HoloLang. """
        resultado = self.parser.interpretar("CREAR H1 (0.1, 0.2, 0.3)")
        self.assertEqual(resultado, "Variable H1 creada con valores (0.1, 0.2, 0.3)")

    def test_imprimir_variable(self):
        """ Prueba la impresión de variables en HoloLang. """
        self.parser.interpretar("CREAR H2 (0.4, 0.5, 0.6)")
        resultado = self.parser.interpretar("IMPRIMIR H2")
        self.assertEqual(resultado, "H2 = (0.4, 0.5, 0.6)")

    def test_compilar_y_ejecutar(self):
        """ Prueba la compilación y ejecución de código HoloLang. """
        resultado = self.compiler.compilar_y_ejecutar("CREAR H3 (0.7, 0.8, 0.9)")
        self.assertEqual(resultado, "Variable H3 creada con valores (0.7, 0.8, 0.9)")

    def test_parser_estructura(self):
        res = self.parser.interpretar("CREAR_ESTRUCTURA S1 {H1, H2}")
        self.assertIn("Estructura S1", res)
        self.assertIn("S1", self.parser.structures)

    def test_debugger_pausa(self):
        """ Prueba la adición de puntos de ruptura en el depurador. """
        self.debugger.agregar_punto_de_ruptura(2)
        self.assertIn(2, self.debugger.break_points)


if __name__ == "__main__":
    unittest.main()
