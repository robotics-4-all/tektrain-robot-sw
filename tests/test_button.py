import unittest
import time
from pidevices.sensors.button import Button


c = 0


class TestButton(unittest.TestCase):

    def test_read(self):
        button = Button(23)

        t_start = time.time()
        while time.time() - t_start < 10:
            print(button.read())
            time.sleep(0.2)

        button.stop()

    def test_wait(self):
        button = Button(23)
        button.wait_for_press()
        print("Pressed")
        button.stop()

    def test_when_pressed(self):
        def test(a1, a2):
            global c
            print("{} args {} {}".format(c, a1, a2))
            c += 1
        
        button = Button(23)
        button.when_pressed(test, 1, 2)
        t_start = time.time()
        while time.time() - t_start < 10:
            time.sleep(1)
        button.stop()

if __name__ == "__main__":
    unittest.main()
