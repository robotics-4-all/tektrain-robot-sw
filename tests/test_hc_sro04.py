import unittest
import time
from pidevices.sensors.hc_sr04 import HcSr04


class TestHcSr04(unittest.TestCase):

    def test_read(self):
        sonar = HcSr04(echo_pin=23, trigger_pin=24)

        while True:
            distance = sonar.read()
            if distance < 20 and distance > 0:
                print(distance)
            time.sleep(0.07)


if __name__ == "__main__":
    unittest.main()
