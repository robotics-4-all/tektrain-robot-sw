import unittest
import time
from pidevices.sensors.bme680 import BME680


class TestBME680(unittest.TestCase):

    def test_set_bits(self):
        sensor = BME680(0, 0)

        register = 0b10101110
        value = 0
        shift = 1
        bits = 3
        sensor._set_bits(register, value, bits, shift)
        pass


if __name__ == "__main__":
    unittest.main()
