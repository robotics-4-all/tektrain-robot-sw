import unittest
import time
from pidevices.sensors.hc_sr04 import HcSr04Mcp23017


class TestHcSr04(unittest.TestCase):

    def test_read(self):
        sonar = HcSr04Mcp23017(echo_pin="B_6", trigger_pin="B_7", bus=1,
                               address=0x21)

        while True:
            t_s = time.time()
            distance = sonar.read()
            diff = time.time() - t_s
            print(distance)
            time.sleep(0.1)


if __name__ == "__main__":
    unittest.main()
