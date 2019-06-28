import unittest
import time
from pidevices.pca9685 import PCA9685 


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

        on_re_l = controller.hardware_interfaces[controller._i2c].read(controller.PCA_ADDRESS,
                                                                       controller.LED)
        on_re_h = controller.hardware_interfaces[controller._i2c].read(controller.PCA_ADDRESS,
                                                                       controller.LED + 1)
        off_re_l = controller.hardware_interfaces[controller._i2c].read(controller.PCA_ADDRESS,
                                                                        controller.LED + 2)
        off_re_h = controller.hardware_interfaces[controller._i2c].read(controller.PCA_ADDRESS,
                                                                        controller.LED + 3)

        self.assertEqual(on_re_l, on_l, "Should be {}".format(on_l))
        self.assertEqual(on_re_h, on_h, "Should be {}".format(on_h))
        self.assertEqual(off_re_l, off_l, "Should be {}".format(off_l))
        self.assertEqual(off_re_h, off_h, "Should be {}".format(off_h))

if __name__ == "__main__":
    unittest.main()
