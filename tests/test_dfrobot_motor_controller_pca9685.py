import unittest
import time
import sys
from pidevices.actuators import DfrobotMotorControllerPCA


speed_1 = 0
speed_2 = 0


class TestDfrobotMotorControllerPCA(unittest.TestCase):

    def test_write(self):
        controller = DfrobotMotorControllerPCA(bus=0, E1=6, M1=7, E2=12, M2=13)

        print("Left full speed")
        controller.write(speed_1=1, speed_2=1)
        time.sleep(2)

        print("Right full speed")
        controller.write(speed_1=-1, speed_2=-1)
        time.sleep(2)

        print("Forward full speed")
        controller.write(speed_1=1, speed_2=-1)
        time.sleep(2)

        print("Backward full speed")
        controller.write(speed_1=-1, speed_2=1)
        time.sleep(2)

        controller.write(speed_1=0, speed_2=0)
        controller.stop()

    def test_args(self):
        controller = DfrobotMotorControllerPCA(bus=0, E1=6, M1=7, E2=12, M2=13)
        print(speed_1, speed_2)
        controller.write(speed_1, speed_2)


if __name__ == "__main__":
    speed_1 = float(sys.argv[2])
    speed_2 = float(sys.argv[3])
    del sys.argv[2:]
    unittest.main()
