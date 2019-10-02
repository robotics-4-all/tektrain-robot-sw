import unittest
import time
from pidevices.mcp23x17 import MCP23x17


class TestMCP23x17(unittest.TestCase):

    def test_get_chunk(self):
        device = MCP23x17()

        address, number = device._get_chunk_number("A_2")
        self.assertEqual(address, "A", "It should be A")
        self.assertEqual(number, 2, "It should be 2")

        with self.assertRaises(TypeError):
            device._get_chunk_number(12)

        with self.assertRaises(TypeError):
            device._get_chunk_number("A_c")

        with self.assertRaises(ValueError):
            device._get_chunk_number("A_12")

        with self.assertRaises(ValueError):
            device._get_chunk_number("C_12")

        with self.assertRaises(ValueError):
            device._get_chunk_number("a_12")
        

if __name__ == "__main__":
    unittest.main()
