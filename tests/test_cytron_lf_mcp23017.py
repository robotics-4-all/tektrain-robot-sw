import unittest
import time
from pidevices import CytronLfLSS05Mcp23017


class TestCytronLf(unittest.TestCase):

    def test_start(self):
        lf = CytronLfLSS05Mcp23017('A_2', 'A_3', 'A_4', 'A_5', 'A_6', cal='A_7',
                                   bus=1, address=0x22)

        number = 'A_2'
        self.assertEqual(lf.so_1, number, "Should be {}".format(number))
        number = 'A_3'
        self.assertEqual(lf.so_2, number, "Should be {}".format(number))
        number = 'A_4'
        self.assertEqual(lf.so_3, number, "Should be {}".format(number))
        number = 'A_5'
        self.assertEqual(lf.so_4, number, "Should be {}".format(number))
        number = 'A_6'
        self.assertEqual(lf.so_5, number, "Should be {}".format(number))
        number = 'A_7'
        self.assertEqual(lf.cal, number, "Should be {}".format(number))

        lf.stop()

    def test_mode(self):
        lf = CytronLfLSS05Mcp23017('A_2', 'A_3', 'A_4', 'A_5', 'A_6', cal='A_7',
                                   bus=1, address=0x22)
        print("Bright mode")
        lf.mode = 'bright'
        time.sleep(10)
        print("Dark mode")
        lf.mode = 'dark'
        lf.stop()

    def test_calibrate(self):
        lf = CytronLfLSS05Mcp23017('A_2', 'A_3', 'A_4', 'A_5', 'A_6', cal='A_7',
                                   bus=1, address=0x22)

        lf.calibrate()

    def test_read(self):
        lf = CytronLfLSS05Mcp23017('A_2', 'A_3', 'A_4', 'A_5', 'A_6', cal='A_7',
                                   bus=1, address=0x22)

        for i in range(20):
            print(lf.read())
            time.sleep(1)
        lf.stop()


if __name__ == "__main__":
    unittest.main()
