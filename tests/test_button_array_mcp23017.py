import unittest
import time
from pidevices.sensors.button_array import ButtonArrayMcp23017


class TestButtonArrayMcp23017(unittest.TestCase):

    def test_read(self):
        array = ButtonArrayMcp23017(["B_0", "B_1", "B_2", "B_3", "B_4", "B_5",
                                     "B_6", "B_7", "A_0", "A_1", "A_2", "A_3"])

        pin = "B_0"
        print("Read button {} for 5s".format(pin))
        t_s = time.time()
        while time.time() - t_s < 5:
            print(array.read(pin))
            time.sleep(0.5)

        pin = "B_1"
        print("Read button {} for 5s".format(pin))
        t_s = time.time()
        while time.time() - t_s < 5:
            print(array.read(pin))
            time.sleep(0.5)

        pin = "B_2"
        print("Read button {} for 5s".format(pin))
        t_s = time.time()
        while time.time() - t_s < 5:
            print(array.read(pin))
            time.sleep(0.5)

        pin = "B_3"
        print("Read button {} for 5s".format(pin))
        t_s = time.time()
        while time.time() - t_s < 5:
            print(array.read(pin))
            time.sleep(0.5)

        pin = "B_4"
        print("Read button {} for 5s".format(pin))
        t_s = time.time()
        while time.time() - t_s < 5:
            print(array.read(pin))
            time.sleep(0.5)

        pin = "B_5"
        print("Read button {} for 5s".format(pin))
        t_s = time.time()
        while time.time() - t_s < 5:
            print(array.read(pin))
            time.sleep(0.5)

        pin = "B_6"
        print("Read button {} for 5s".format(pin))
        t_s = time.time()
        while time.time() - t_s < 5:
            print(array.read(pin))
            time.sleep(0.5)

        pin = "B_7"
        print("Read button {} for 5s".format(pin))
        t_s = time.time()
        while time.time() - t_s < 5:
            print(array.read(pin))
            time.sleep(0.5)

        pin = "A_0"
        print("Read button {} for 5s".format(pin))
        t_s = time.time()
        while time.time() - t_s < 5:
            print(array.read(pin))
            time.sleep(0.5)

        pin = "A_1"
        print("Read button {} for 5s".format(pin))
        t_s = time.time()
        while time.time() - t_s < 5:
            print(array.read(pin))
            time.sleep(0.5)

        pin = "A_2"
        print("Read button {} for 5s".format(pin))
        t_s = time.time()
        while time.time() - t_s < 5:
            print(array.read(pin))
            time.sleep(0.5)

        pin = "A_3"
        print("Read button {} for 5s".format(pin))
        t_s = time.time()
        while time.time() - t_s < 5:
            print(array.read(pin))
            time.sleep(0.5)

    def test_wait(self):
        array = ButtonArrayMcp23017(["B_0", "B_1", "B_2", "B_3", "B_4", "B_5",
                                     "B_6", "B_7", "A_0", "A_1", "A_2", "A_3"])
        button = "B_0"
        array.wait_for_press(button)
        print("Pressed {}".format(button))

        button = "B_1"
        array.wait_for_press(button)
        print("Pressed {}".format(button))

        button = "B_2"
        array.wait_for_press(button)
        print("Pressed {}".format(button))

        button = "B_3"
        array.wait_for_press(button)
        print("Pressed {}".format(button))

        button = "B_4"
        array.wait_for_press(button)
        print("Pressed {}".format(button))

        button = "B_5"
        array.wait_for_press(button)
        print("Pressed {}".format(button))

        button = "B_6"
        array.wait_for_press(button)
        print("Pressed {}".format(button))

        button = "B_7"
        array.wait_for_press(button)
        print("Pressed {}".format(button))

        button = "A_0"
        array.wait_for_press(button)
        print("Pressed {}".format(button))

        button = "A_1"
        array.wait_for_press(button)
        print("Pressed {}".format(button))

        button = "A_2"
        array.wait_for_press(button)
        print("Pressed {}".format(button))

        button = "A_3"
        array.wait_for_press(button)
        print("Pressed {}".format(button))

    def test_when_pressed(self):
        array = ButtonArrayMcp23017(["B_0", "B_1", "B_2", "B_3", "B_4", "B_5",
                                     "B_6", "B_7", "A_0", "A_1", "A_2", "A_3"])

        def f_0(pin):
            print("{} Interrupt on button {}")


if __name__ == "__main__":
    unittest.main()
