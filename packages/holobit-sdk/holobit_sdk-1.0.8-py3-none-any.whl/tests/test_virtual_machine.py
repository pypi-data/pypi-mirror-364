import unittest
from holobit_sdk.assembler.virtual_machine import AssemblerVM
from holobit_sdk.core.holobit import Holobit


class TestAssemblerVM(unittest.TestCase):
    def setUp(self):
        self.vm = AssemblerVM()

    def test_run_simple_program(self):
        program = [
            "CREAR Q1 (0.0, 0.1, 0.2)",
            "CREAR Q2 (0.3, 0.4, 0.5)",
            "CREAR Q3 (0.6, 0.7, 0.8)",
            "CREAR Q4 (0.9, 1.0, 1.1)",
            "CREAR Q5 (1.2, 1.3, 1.4)",
            "CREAR Q6 (1.5, 1.6, 1.7)",
            "CREAR H1 {Q1, Q2, Q3, Q4, Q5, Q6}",
            "ROT H1 z 45",
        ]
        self.vm.run_program(program)
        self.assertIn("H1", self.vm.parser.holobits)
        holobit = self.vm.parser.holobits["H1"]
        self.assertIsInstance(holobit, Holobit)


if __name__ == "__main__":
    unittest.main()
