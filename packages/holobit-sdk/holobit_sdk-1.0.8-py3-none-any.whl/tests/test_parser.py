import unittest
from holobit_sdk.assembler.parser import AssemblerParser
from holobit_sdk.core.quark import Quark


class TestAssemblerParser(unittest.TestCase):
    def setUp(self):
        """
        Configuración inicial antes de cada prueba.
        """
        self.parser = AssemblerParser()

    def test_crear_quark(self):
        """
        Prueba la creación de un quark.
        """
        line = "CREAR Q1 (0.1, 0.2, 0.3)"
        self.parser.parse_line(line)
        self.assertIn("Q1", self.parser.holobits)
        self.assertIsInstance(self.parser.holobits["Q1"], Quark)

    def test_crear_quark_coordenadas_invalidas(self):
        invalid_coords = [
            "CREAR Q1 (0.1, 0.2)",  # Faltan coordenadas
            "CREAR Q1 (0.1, 0.2, texto)",  # Coordenada no numérica
            "CREAR Q1 (0.1,)",  # Coordenada incompleta
            "CREAR Q1 0.1, 0.2, 0.3",  # Sin paréntesis
            "CREAR Q1 ()",  # Vacío
            "CREAR Q1 (0.1 0.2, 0.3)"  # Falta coma
        ]
        for line in invalid_coords:
            with self.assertRaises(ValueError):
                self.parser.parse_line(line)

    def test_crear_holobit(self):
        for i in range(1, 7):
            self.parser.parse_line(f"CREAR Q{i} ({i * 0.1:.1f}, {i * 0.2:.1f}, {i * 0.3:.1f})")
        self.parser.parse_line("CREAR H1 {Q1, Q2, Q3, Q4, Q5, Q6}")

    def test_crear_holobit_referencias_invalidas(self):
        """
        Prueba un Holobit con referencias inexistentes.
        """
        line = "CREAR H1 {Q1, Q2, Q3, Q4, Q5, Q6}"  # Sin crear los quarks
        with self.assertRaises(KeyError):
            self.parser.parse_line(line)

    def test_instruccion_invalida(self):
        """
        Prueba una instrucción no reconocida.
        """
        with self.assertRaises(ValueError):
            self.parser.parse_line("INVALID H1")

    def test_rotar_holobit(self):
        """
        Prueba la rotación de un Holobit.
        """
        # Crear quarks necesarios
        for i in range(1, 7):
            self.parser.parse_line(f"CREAR Q{i} ({i * 0.1}, {i * 0.2}, {i * 0.3})")

        # Crear Holobit
        self.parser.parse_line("CREAR H1 {Q1, Q2, Q3, Q4, Q5, Q6}")

        # Rotar Holobit
        self.parser.parse_line("ROT H1 z 90")
        self.assertIn("H1", self.parser.holobits)

    def test_rotar_holobit_angulo_invalido(self):
        """
        Prueba la rotación de un Holobit con un ángulo inválido.
        """
        # Crear quarks necesarios
        for i in range(1, 7):
            self.parser.parse_line(f"CREAR Q{i} ({i * 0.1}, {i * 0.2}, {i * 0.3})")

        # Crear Holobit
        self.parser.parse_line("CREAR H1 {Q1, Q2, Q3, Q4, Q5, Q6}")

        with self.assertRaises(ValueError):
            self.parser.parse_line("ROT H1 z texto")  # Ángulo no numérico

    def test_rotar_holobit_eje_invalido(self):
        """
        Prueba la rotación de un Holobit con un eje inválido.
        """
        # Crear quarks necesarios
        for i in range(1, 7):
            self.parser.parse_line(f"CREAR Q{i} ({i * 0.1}, {i * 0.2}, {i * 0.3})")

        # Crear Holobit
        self.parser.parse_line("CREAR H1 {Q1, Q2, Q3, Q4, Q5, Q6}")

        with self.assertRaises(ValueError):
            self.parser.parse_line("ROT H1 invalid 90")  # Eje inválido

    def test_rotar_holobit_invalido(self):
        """
        Prueba la rotación de un Holobit inexistente.
        """
        line = "ROT H1 z 90"  # Holobit no creado
        with self.assertRaises(KeyError):
            self.parser.parse_line(line)

    def test_entrelazar(self):
        """Prueba el registro de entrelazamiento."""
        # Crear quarks para dos Holobits
        for i in range(1, 13):
            self.parser.parse_line(f"CREAR Q{i} ({i * 0.1}, {i * 0.2}, {i * 0.3})")
        self.parser.parse_line("CREAR H1 {Q1, Q2, Q3, Q4, Q5, Q6}")
        self.parser.parse_line("CREAR H2 {Q7, Q8, Q9, Q10, Q11, Q12}")
        self.parser.parse_line("ENTR H1 H2")
        self.assertIn(("H1", "H2"), self.parser.entanglements)


if __name__ == "__main__":
    unittest.main()
