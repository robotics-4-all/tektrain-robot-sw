import unittest
import time
from pidevices.mcp23017 import MCP23017
from pidevices import Mcp23x17GPIO
from pidevices.exceptions import NotInputPin


class TestMcp23x17GPIO(unittest.TestCase):

    def test_add_pins(self):
        device = MCP23017(bus=1, address=0x20)
        interface = Mcp23x17GPIO(device=device, echo='A_1', trigger='B_2')
        self.assertEqual(interface.pins['echo'].pin_num, 1, "Should be 1")
        self.assertEqual(interface.pins['trigger'].pin_num, 10, "Should be 10")

    def test_read_write(self):
        device = MCP23017(bus=1, address=0x20)
        interface = Mcp23x17GPIO(device=device, echo='A_1', trigger='B_2')
        #interface.write("echo", 1)
        #value = interface.read("echo")
        #self.assertEqual(value, 1, "The read value should be 1.")

    def test_set_pin_function(self):
        device = MCP23017(bus=1, address=0x20)
        interface = Mcp23x17GPIO(device=device, echo='A_1', trigger='B_2')

        function = "input"
        interface.set_pin_function("echo", function)
        self.assertEqual(interface.pins["echo"].function, function, 
                         "Should be {}".format(function))

        function = "output"
        interface.set_pin_function("trigger", function)
        self.assertEqual(interface.pins["trigger"].function, function, 
                         "Should be {}".format(function))

        with self.assertRaises(TypeError):
            interface.set_pin_function("trigger", "aa")

    def test_set_pin_pull(self):
        device = MCP23017(bus=1, address=0x20)
        interface = Mcp23x17GPIO(device=device, echo='A_1', trigger='B_2')

        pull = "up"
        pin = "echo"
        interface.init_input(pin, pull)
        self.assertEqual(interface.pins[pin].pull, pull, 
                         "Pull should be {}".format(pull))

        with self.assertRaises(TypeError):
            interface.set_pin_pull("echo", "aa")

        with self.assertRaises(NotInputPin):
            interface.set_pin_pull("trigger", "up")


if __name__ == "__main__":
    unittest.main()
