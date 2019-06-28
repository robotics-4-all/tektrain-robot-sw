import unittest
import time
from pidevices.actuators.servo_kit import ServoKit


class TestServoKit(unittest.TestCase):

    def test_angle(self):
        kit = ServoKit(50, 2)

        angle = 90
        self.assertEqual(kit._angle_to_dc(angle), 0.075, "Should be 0.05")

    def test_write(self):
        kit = ServoKit(50, 2)
        channel = 1
        kit.write(channel, 0)
        time.sleep(1)

        kit.write(channel, 10)
        time.sleep(1)

        kit.write(channel, 30)
        time.sleep(1)

        kit.write(channel, 40)
        time.sleep(1)

        kit.write(channel, 50)
        time.sleep(1)

        kit.write(channel, 60)
        time.sleep(1)

        kit.write(channel, 70)
        time.sleep(1)

        kit.write(channel, 80)
        time.sleep(1)

        kit.write(channel, 90)
        time.sleep(1)

        kit.write(channel, 100)
        time.sleep(1)

        kit.write(channel, 110)
        time.sleep(1)

        kit.write(channel, 120)
        time.sleep(1)

        kit.write(channel, 130)
        time.sleep(1)

        kit.write(channel, 140)
        time.sleep(1)

        kit.write(channel, 150)
        time.sleep(1)

        kit.write(channel, 160)
        time.sleep(1)

        kit.write(channel, 170)
        time.sleep(1)

        kit.write(channel, 180)
        time.sleep(1)

if __name__ == "__main__":
    unittest.main()
