import unittest
import time
from pidevices.mcp23017 import MCP23017
from pidevices import Mcp23017GPIO
from pidevices.exceptions import NotInputPin


class TestMcp23017GPIO(unittest.TestCase):

    def test_add_pins(self):
        interface = Mcp23017GPIO(echo='A_1', trigger='B_2')
        self.assertEqual(interface.pins['echo'].pin_num, 1, "Should be 1")
        self.assertEqual(interface.pins['trigger'].pin_num, 10, "Should be 10")

    def test_remove_pins(self):
        interface = Mcp23017GPIO(echo='A_1', trigger='B_2')
        num_pins = len(interface.pins)
        self.assertEqual(num_pins, 2, "Len should be 2")
        interface.remove_pins("echo", "trigger")
        num_pins = len(interface.pins)
        self.assertEqual(num_pins, 0, "Len should be 1")

    def test_read(self):
        interface = Mcp23017GPIO(echo='A_1', trigger='B_2')
        interface.set_pin_function("echo", "input")
        value = interface.read("echo")
        #self.assertEqual(value, 1, "The read value should be 1.")

    def test_set_pin_function(self):
        interface = Mcp23017GPIO(echo='A_1', trigger='B_2')

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
        interface = Mcp23017GPIO(echo='A_1', trigger='B_2')

        pull = "up"
        pin = "echo"
        interface.init_input(pin, pull)
        self.assertEqual(interface.pins[pin].pull, pull, 
                         "Pull should be {}".format(pull))

        with self.assertRaises(TypeError):
            interface.set_pin_pull("echo", "aa")

        with self.assertRaises(NotInputPin):
            interface.set_pin_pull("trigger", "up")

    def test_set_pin_edge(self):
        interface = Mcp23017GPIO(echo='A_1', trigger='B_2')
        interface.init_input("echo", "down")
        
        # Test exception
        with self.assertRaises(TypeError):
            interface.set_pin_edge("echo", "aaa")
        
        pin_num = interface.PIN_NUMBER_MAP[interface.pins["echo"].pin_num]

        # Check rising
        interface.set_pin_edge("echo", "rising")
        intcon = interface._device.get_pin_intcon(pin_num)
        def_val = interface._device.get_pin_def_val(pin_num)
        self.assertEqual(intcon, 1, "Should be 1")
        self.assertEqual(def_val, 0, "Should be 0")

        # Check falling
        interface.set_pin_edge("echo", "falling")
        intcon = interface._device.get_pin_intcon(pin_num)
        def_val = interface._device.get_pin_def_val(pin_num)
        self.assertEqual(intcon, 1, "Should be 1")
        self.assertEqual(def_val, 1, "Should be 1")

        # Check both
        interface.set_pin_edge("echo", "both")
        intcon = interface._device.get_pin_intcon(pin_num)
        def_val = interface._device.get_pin_def_val(pin_num)
        self.assertEqual(intcon, 0, "Should be 0")
        self.assertEqual(def_val, 0, "Should be 0")

    def test_set_pin_bounce(self):
        interface = Mcp23017GPIO(echo='A_1', trigger='B_2')
        interface.init_input("echo", "down")
        
        # Test exception
        with self.assertRaises(TypeError):
            interface.set_pin_bounce("echo", 12.2)

        pin_num = interface.PIN_NUMBER_MAP[interface.pins["echo"].pin_num]
        
        val = 100
        interface.set_pin_bounce("echo", 100)
        bounce = interface._device._debounce[pin_num]
        self.assertEqual(bounce, val/1000, "Should be 100")

    def test_set_pin_event(self):
        interface = Mcp23017GPIO(echo='A_0', trigger='A_1')
        interface.init_input("echo", "down")
        interface.init_input("trigger", "down")

        def f(pin):
            print("{} Rising edge signal on pin {}.".format(f.c, pin))
            f.c += 1
        f.c = 0

        def f_1(pin):
            print("{} Falling edge signal on pin {}.".format(f_1.c, pin))
            f_1.c += 1
        f_1.c = 0
        
        echo_pin_num = interface.PIN_NUMBER_MAP[interface.pins["echo"].pin_num]
        trigger_pin_num = \
            interface.PIN_NUMBER_MAP[interface.pins["trigger"].pin_num]

        interface.set_pin_edge("echo", "rising")
        interface.set_pin_edge("trigger", "falling")

        interface.set_pin_bounce("echo", 200)
        interface.set_pin_bounce("trigger", 1000)

        interface.set_pin_event("echo", f, echo_pin_num)
        interface.set_pin_event("trigger", f_1, trigger_pin_num)

        interface.start_polling(["echo", "trigger"])
        time.sleep(15)
        interface.stop_polling()
        interface.close()

    def test_wait_pin_for_edge(self):
        interface = Mcp23017GPIO(echo='A_0', trigger='A_1')
        interface.init_input("echo", "down")
        interface.set_pin_edge("echo", "rising")
        val = interface.wait_pin_for_edge("echo")
        self.assertEqual(val, 1, "Should be 1")
        val = interface.wait_pin_for_edge("echo", timeout=2000)
        self.assertEqual(val, 0, "Should be 0")


if __name__ == "__main__":
    unittest.main()
