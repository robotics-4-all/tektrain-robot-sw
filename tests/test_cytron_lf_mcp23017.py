import unittest
import time
from pidevices import CytronLfLSS05Mcp23017


class TestCytronLf(unittest.TestCase):

    def test_start(self):
        lf = CytronLfLSS05Mcp23017('B_0', 'B_1', 'B_2', 'B_3', 'B_4', cal='B_5',
                                   bus=4, address=0x22)

        number = 'B_0'
        self.assertEqual(lf.so_1, number, "Should be {}".format(number))
        number = 'B_1'
        self.assertEqual(lf.so_2, number, "Should be {}".format(number))
        number = 'B_2'
        self.assertEqual(lf.so_3, number, "Should be {}".format(number))
        number = 'B_3'
        self.assertEqual(lf.so_4, number, "Should be {}".format(number))
        number = 'B_4'
        self.assertEqual(lf.so_5, number, "Should be {}".format(number))
        number = 'B_5'
        self.assertEqual(lf.cal, number, "Should be {}".format(number))

        lf.stop()

    def test_mode(self):
        lf = CytronLfLSS05Mcp23017('B_0', 'B_1', 'B_2', 'B_3', 'B_4', cal='B_5',
                                   bus=4, address=0x22)
        print("Bright mode")
        lf.mode = 'bright'
        time.sleep(5)
        print("Dark mode")
        lf.mode = 'dark'
        lf.stop()

    def test_calibrate(self):
        lf = CytronLfLSS05Mcp23017('B_0', 'B_1', 'B_2', 'B_3', 'B_4', cal='B_5',
                                   bus=4, address=0x22)

        lf.calibrate()

    def test_read(self):
        lf = CytronLfLSS05Mcp23017('B_0', 'B_1', 'B_2', 'B_3', 'B_4', cal='B_5',
                                   bus=4, address=0x22)

        for i in range(20):
            print(lf.read())
            time.sleep(1)
        lf.stop()


if __name__ == "__main__":
    unittest.main()
