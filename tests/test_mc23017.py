import unittest
import time
from pidevices import MCP23017


class TestMCP23017(unittest.TestCase):

    def test_set_pin_dir(self):
        device = MCP23017(1, 0x20)
        device.set_pin_dir("A_0", 0)
        device.set_pin_dir("A_1", 0)
        device.set_pin_dir("B_5", 0)

        self.assertEqual(device.get_pin_dir("A_0"), 0, "Should be 0")
        self.assertEqual(device.get_pin_dir("A_1"), 0, "Should be 0")
        self.assertEqual(device.get_pin_dir("B_5"), 0, "Should be 0")

    def test_set_pin_pol(self):
        device = MCP23017(1, 0x20)
        device.set_pin_pol("A_0", 0)
        device.set_pin_pol("A_1", 0)
        device.set_pin_pol("B_5", 1)

        self.assertEqual(device.get_pin_pol("A_0"), 0, "Should be 0")
        self.assertEqual(device.get_pin_pol("A_1"), 0, "Should be 0")
        self.assertEqual(device.get_pin_pol("B_5"), 1, "Should be 1")

    def test_set_pin_int(self):
        device = MCP23017(1, 0x20)
        device.set_pin_int("A_0", 0)
        device.set_pin_int("A_1", 0)
        device.set_pin_int("B_5", 1)

        self.assertEqual(device.get_pin_int("A_0"), 0, "Should be 0")
        self.assertEqual(device.get_pin_int("A_1"), 0, "Should be 0")
        self.assertEqual(device.get_pin_int("B_5"), 1, "Should be 1")

    def test_set_pin_def_val(self):
        device = MCP23017(1, 0x20)
        device.set_pin_def_val("A_0", 0)
        device.set_pin_def_val("A_1", 0)
        device.set_pin_def_val("B_5", 1)

        self.assertEqual(device.get_pin_def_val("A_0"), 0, "Should be 0")
        self.assertEqual(device.get_pin_def_val("A_1"), 0, "Should be 0")
        self.assertEqual(device.get_pin_def_val("B_5"), 1, "Should be 1")

    def test_set_pin_intcon(self):
        device = MCP23017(1, 0x20)
        device.set_pin_intcon("A_0", 0)
        device.set_pin_intcon("A_1", 0)
        device.set_pin_intcon("B_5", 1)

        self.assertEqual(device.get_pin_intcon("A_0"), 0, "Should be 0")
        self.assertEqual(device.get_pin_intcon("A_1"), 0, "Should be 0")
        self.assertEqual(device.get_pin_intcon("B_5"), 1, "Should be 1")

    def test_set_bank(self):
        device = MCP23017(1, 0x20)
        device.set_bank(0)

        self.assertEqual(device.get_bank(), 0, "Should be 0")

    def test_set_mirror(self):
        device = MCP23017(1, 0x20)
        device.set_mirror(0)
        self.assertEqual(device.get_mirror(), 0, "Should be 0")
        device.set_mirror(1)
        self.assertEqual(device.get_mirror(), 1, "Should be 1")

    def test_set_seqop(self):
        device = MCP23017(1, 0x20)
        device.set_seqop(0)
        self.assertEqual(device.get_seqop(), 0, "Should be 0")
        device.set_seqop(1)
        self.assertEqual(device.get_seqop(), 1, "Should be 1")

    def test_set_disslw(self):
        device = MCP23017(1, 0x20)
        device.set_disslw(0)
        self.assertEqual(device.get_disslw(), 0, "Should be 0")
        device.set_disslw(1)
        self.assertEqual(device.get_disslw(), 1, "Should be 1")

    def test_set_odr(self):
        device = MCP23017(1, 0x20)
        device.set_odr(0)
        self.assertEqual(device.get_odr(), 0, "Should be 0")
        device.set_odr(1)
        self.assertEqual(device.get_odr(), 1, "Should be 1")

    def test_set_intpol(self):
        device = MCP23017(1, 0x20)
        device.set_intpol(0)
        self.assertEqual(device.get_intpol(), 0, "Should be 0")
        device.set_intpol(1)
        self.assertEqual(device.get_intpol(), 1, "Should be 1")

    def test_set_pin_pull_up(self):
        device = MCP23017(1, 0x20)
        device.set_pin_pull_up("A_0", 0)
        device.set_pin_pull_up("A_1", 0)
        device.set_pin_pull_up("B_5", 1)

        self.assertEqual(device.get_pin_pull_up("A_0"), 0, "Should be 0")
        self.assertEqual(device.get_pin_pull_up("A_1"), 0, "Should be 0")
        self.assertEqual(device.get_pin_pull_up("B_5"), 1, "Should be 1")

    def test_read_write(self):
        device = MCP23017(1, 0x20)
        device.set_pin_dir("A_0", 0)
        device.write("A_0", 1)
        self.assertEqual(device.read("A_0"), 1, "Should be 1")
        device.write("A_0", 0)
        self.assertEqual(device.read("A_0"), 0, "Should be 0")

        
if __name__ == "__main__":
    unittest.main()
