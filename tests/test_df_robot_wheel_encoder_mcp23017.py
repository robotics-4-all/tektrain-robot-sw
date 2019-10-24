import unittest
import time
from pidevices import DfRobotWheelEncoderMcp23017


class TestDfRobotWheelEncoderMcp23017(unittest.TestCase):

    def test_read(self):
        encoder = DfRobotWheelEncoderMcp23017(pin='B_6', bus=3, address=0x22)

        counter = 0
        print("Five measurments with positive edge")
        f = True
        while f:
            val = encoder.read()
            print("Encoder value: {}".format(val))
            if val:
                counter += 1
            if counter > 4:
                f = False
            time.sleep(0.1)
        self.assertEqual(f, False, "Should be False")

        print("Five measurments with negative edge")
        while not f:
            val = encoder.read()
            print("Encoder value: {}".format(val))
            if not val:
                counter -= 1
            if counter < 1:
                f = True
            time.sleep(0.1)
        self.assertEqual(f, True, "Should be True")

        encoder.stop()

    def test_counter(self):
        encoder = DfRobotWheelEncoderMcp23017(pin='B_6', bus=3, address=0x22)
        
        value = 0
        limit = 10
        while True:
            value = encoder._counter
            print("Counter: {}".format(value))
            if (value > (limit - 1)):
                break
            time.sleep(0.1)
        self.assertEqual(value, limit, "Should be {}".format(limit))

        encoder.stop()

    def test_rpm(self):
        encoder = DfRobotWheelEncoderMcp23017(pin='B_6', bus=3, address=0x22)

        t_s = time.time()
        while time.time() - t_s < 60:
            print("RPM: {}".format(encoder.read_rpm()))
            time.sleep(1)

        encoder.stop()


if __name__ == "__main__":
    unittest.main()
