import sys
import unittest
import time
from pidevices import TouchScreen


class TestTouchScreen(unittest.TestCase):

    def test_one(self):
        scr = TouchScreen()
        scr.write(show_color=True, time_enabled=5, color_rgb=(0, 255, 0))


if __name__ == "__main__":
    unittest.main()
