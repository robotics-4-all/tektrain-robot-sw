import unittest
import time
from pidevices.sensors.button import Button


class TestButton(unittest.TestCase):

    def test_read(self):
        def test():
            print("skata")
        
        button = Button(23, test)
        while True:
            time.sleep(1)


if __name__ == "__main__":
    unittest.main()
