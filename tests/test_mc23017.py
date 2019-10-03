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

        
if __name__ == "__main__":
    unittest.main()
