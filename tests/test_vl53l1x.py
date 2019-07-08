import unittest
import time
from pidevices.sensors.vl53l1x import VL53L1X


class TestVL53L1X(unittest.TestCase):

    def test_read(self):
        sensor = VL53L1X()
        sensor.start_ranging(1)
        for i in range(10):
            print(sensor.get_distance())
            time.sleep(1)


if __name__ == "__main__":
    unittest.main()
