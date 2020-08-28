import unittest
import time
from pidevices.sensors.icm_20948_imu import ICM_20948
 

class TestICM_20948(unittest.TestCase):

    def test_reset(self):
        imu = ICM_20948(0)

    def test_read(self):
        imu = ICM_20948(1)
        timeout = 10
        
        t_s = time.time()
        #while time.time() - t_s < timeout:
        while True:
            data = imu.read()
            print("Accl: x: {}, y: {}, z: {}".format(data.accel.x,
                                                     data.accel.y,
                                                     data.accel.z))
            print("Gyro: x: {}, y: {}, z: {}".format(data.gyro.x,
                                                     data.gyro.y,
                                                     data.gyro.z))
            print("Magn: x: {}, y: {}, z: {}".format(data.magne.x,
                                                     data.magne.y,
                                                     data.magne.z))
            print("Degrees: {}".format(imu.convert_to_degrees(data.magne.x,
                                                              data.magne.y,
                                                              data.magne.z)))
            #print("Temperature: {}".format(data.temp))

            time.sleep(1)


if __name__ == "__main__":
    unittest.main()
