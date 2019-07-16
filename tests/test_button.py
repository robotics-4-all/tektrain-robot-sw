import unittest
import time
from pidevices.sensors.button import Button

c = 0
class TestButton(unittest.TestCase):

    def test_read(self):
        def test(a1, a2):
            global c
            print("{} {} skata {}".format(c, a1, a2))
            c += 1
        
        button = Button(23)
        button.read(test, 10, "na fas")
        while True:
            time.sleep(1)


if __name__ == "__main__":
    unittest.main()
