import unittest
import time
from pidevices import PCA9685 


class TestPCA9685(unittest.TestCase):

    def test_restart(self):
        """Test restart function."""

        controller = PCA9685(bus=1, frequency=50)
        on_l = 0x00
        on_h = 0x00
        off_l = 0x00
        off_h = 0x10

        controller.write(0, 0.02)

        time.sleep(1)

        controller.restart()

        on_re_l = controller.hardware_interfaces[controller._i2c].read(
            controller.PCA_ADDRESS,
            controller.LED)
        on_re_h = controller.hardware_interfaces[controller._i2c].read(
            controller.PCA_ADDRESS,
            controller.LED + 1)
        off_re_l = controller.hardware_interfaces[controller._i2c].read(
            controller.PCA_ADDRESS,
            controller.LED + 2)
        off_re_h = controller.hardware_interfaces[controller._i2c].read(
            controller.PCA_ADDRESS,
            controller.LED + 3)

        self.assertEqual(on_re_l, on_l, "Should be {}".format(on_l))
        self.assertEqual(on_re_h, on_h, "Should be {}".format(on_h))
        self.assertEqual(off_re_l, off_l, "Should be {}".format(off_l))
        self.assertEqual(off_re_h, off_h, "Should be {}".format(off_h))

    def test_angle(self):
        kit = PCA9685(1, 50)

        angle = 90
        self.assertEqual(kit._angle_to_dc(angle), 0.075, "Should be 0.075")

    def test_write(self):
        channels = 2
        kit = PCA9685(5, 50)
        print("0 degrees to 180")

        for i in range(channels):
            channel = i

            kit.write(channel, 0, degrees=True)
            time.sleep(1)

            kit.write(channel, 10, degrees=True)
            time.sleep(1)

            kit.write(channel, 30, degrees=True)
            time.sleep(1)

            kit.write(channel, 40, degrees=True)
            time.sleep(1)

            kit.write(channel, 50, degrees=True)
            time.sleep(1)

            kit.write(channel, 60, degrees=True)
            time.sleep(1)

            kit.write(channel, 70, degrees=True)
            time.sleep(1)

            kit.write(channel, 80, degrees=True)
            time.sleep(1)

            kit.write(channel, 90, degrees=True)
            time.sleep(1)

            kit.write(channel, 100, degrees=True)
            time.sleep(1)

            kit.write(channel, 110, degrees=True)
            time.sleep(1)

            kit.write(channel, 120, degrees=True)
            time.sleep(1)

            kit.write(channel, 130, degrees=True)
            time.sleep(1)

            kit.write(channel, 140, degrees=True)
            time.sleep(1)

            kit.write(channel, 150, degrees=True)
            time.sleep(1)

            kit.write(channel, 160, degrees=True)
            time.sleep(1)

            kit.write(channel, 170, degrees=True)
            time.sleep(1)

            kit.write(channel, 180, degrees=True)
            time.sleep(1)

        print("Drive two channels with same value")
        kit.write([0, 1], 100, degrees=True)


if __name__ == "__main__":
    unittest.main()
