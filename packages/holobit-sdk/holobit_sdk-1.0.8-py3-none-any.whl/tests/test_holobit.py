import unittest
from holobit_sdk.core.quark import Quark
from holobit_sdk.core.holobit import Holobit


class TestHolobit(unittest.TestCase):
    def test_repr_incluye_listas(self):
        quarks = [Quark(i, i + 1, i + 2) for i in range(6)]
        hb = Holobit(quarks, list(reversed(quarks)))
        rep = repr(hb)
        self.assertIn("quarks", rep)
        self.assertIn("antiquarks", rep)
        self.assertIn("Holobit", rep)


if __name__ == "__main__":
    unittest.main()
