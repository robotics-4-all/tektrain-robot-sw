import unittest
import time
from pidevices.sensors.bme680 import BME680


class TestBME680(unittest.TestCase):

    def test_set_bits(self):
        sensor = BME680(1, 0)
        register = 0b11111111
        value = 0
        shift = 3
        bits = 3
        register = sensor._set_bits(register, value, bits, shift)
        print(bin(register))

    def test_get_bits(self):
        sensor = BME680(1, 0)
        register = 0b00011100
        shift = 4
        bits = 3
        register = sensor._get_bits(register, bits, shift)
        print(bin(register))

if __name__ == "__main__":
    unittest.main()
