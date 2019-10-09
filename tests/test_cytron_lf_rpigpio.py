import unittest
import time
from pidevices.sensors.cytron_line_sensor_lss05_rpigpio import CytronLfLSS05Rpi


class TestCytronLf(unittest.TestCase):

    def test_start(self):
        lf = CytronLfLSS05Rpi(14, 15, 18, 23, 24, cal=25)

        number = 1
        self.assertEqual(lf.so_1, number, "Should be {}".format(number))
        number = 2
        self.assertEqual(lf.so_2, number, "Should be {}".format(number))
        number = 3
        self.assertEqual(lf.so_3, number, "Should be {}".format(number))
        number = 4
        self.assertEqual(lf.so_4, number, "Should be {}".format(number))
        number = 5
        self.assertEqual(lf.so_5, number, "Should be {}".format(number))
        number = 6
        self.assertEqual(lf.cal, number, "Should be {}".format(number))

        lf.stop()

    def test_mode(self):
        lf = CytronLfLSS05Rpi(14, 15, 18, 23, 24, cal=25)
        
        print("Bright mode")
        lf.mode = 'bright'
        time.sleep(5)
        print("Dark mode")
        lf.mode = 'dark'
        lf.stop()

    def test_calibrate(self):
        lf = CytronLfLSS05Rpi(14, 15, 18, 23, 24, cal=25)

        lf.calibrate()

    def test_read(self):
        lf = CytronLfLSS05Rpi(14, 15, 18, 23, 24, cal=25)

        for i in range(20):
            print(lf.read())
            time.sleep(1)


if __name__ == "__main__":
    unittest.main()
