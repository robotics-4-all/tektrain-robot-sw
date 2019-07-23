import unittest
import time
from pidevices.sensors.icm_20948_imu import ICM_20948


class TestICM_20948(unittest.TestCase):

    def test_reset(self):
        imu = ICM_20948(0)


if __name__ == "__main__":
    unittest.main()
