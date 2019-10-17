import unittest
import time
from pidevices.sensors.button import ButtonRPiGPIO


class TestButton(unittest.TestCase):

    def test_read(self):
        button = ButtonRPiGPIO(23)

        t_start = time.time()
        while time.time() - t_start < 10:
            print(button.read())
            time.sleep(0.2)

        button.stop()

    def test_wait(self):
        button = ButtonRPiGPIO(23)
        button.wait_for_press()
        print("Pressed")
        button.stop()

    def test_when_pressed(self):
        def test(a1, a2):
            print("{} args {} {}".format(test.c, a1, a2))
            test.c += 1
        test.c = 0 
        button = ButtonRPiGPIO(23)
        button.when_pressed(test, 1, 2)
        t_start = time.time()
        while time.time() - t_start < 10:
            time.sleep(1)
        button.stop()


if __name__ == "__main__":
    unittest.main()
