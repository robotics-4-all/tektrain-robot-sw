import unittest
import time
from pidevices.sensors.hc_sr04 import HcSr04RPiGPIO


class TestHcSr04(unittest.TestCase):

    def test_read(self):
        sonar = HcSr04RPiGPIO(echo_pin=24, trigger_pin=23)
        sonar.start()
        

        while True:
            t_s = time.time()
            distance = sonar.read()
            diff = time.time() - t_s
            print(distance)
            time.sleep(0.1)


if __name__ == "__main__":
    unittest.main()
