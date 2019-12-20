import unittest
import time
from pidevices.sensors.icm_20948_imu import ICM_20948


class TestICM_20948(unittest.TestCase):

    def test_reset(self):
        imu = ICM_20948(0)

    def test_read(self):
        imu = ICM_20948(3)
        timeout = 5
        
        t_s = time.time()
        while time.time() - t_s < timeout:
            data = imu.read()
            print("Accel: {}".format(data.accel))
            print("Magnetometer: {}".format(data.magne))
            print("Gyroscope: {}".format(data.gyro))
            print("Temperature: {}".format(data.temp))


if __name__ == "__main__":
    unittest.main()
