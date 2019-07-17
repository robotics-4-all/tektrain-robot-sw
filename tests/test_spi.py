import unittest
import time
from pidevices.hardware_interfaces.spi_implementations import SPIimplementation


class TestSPI(unittest.TestCase):


    def test_write(self):
        dev = SPIimplementation(0, 0)
        while True:
            data = [23]
            dev.write(data)

    def test_read(self):
        dev = SPIimplementation(0, 0)
        while True:
            print(dev.read(3))
            time.sleep(0.5)

if __name__ == "__main__":
    unittest.main()
