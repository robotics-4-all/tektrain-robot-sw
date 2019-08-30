import unittest
import time
from pidevices.sensors.hc_sr04 import HcSr04


class TestHcSr04(unittest.TestCase):

    def test_read(self):
        sonar = HcSr04(echo_pin=23, trigger_pin=24)

        while True:
            print(sonar.read())
            time.sleep(0.1)


if __name__ == "__main__":
    unittest.main()
