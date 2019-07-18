import unittest
import time
from pidevices.sensors.gp2y0a21yk0f import GP2Y0A21YK0F_mcp3002


class TestGP2Y0A21YK0F(unittest.TestCase):


    def test_inter(self):
        m_sensor = GP2Y0A21YK0F_mcp3002(port=0, device=0, channel=0)
        self.assertAlmostEqual(m_sensor.f_int(1.8), 16, places=1,
                              msg="Should be almost 15")

if __name__ == "__main__":
    unittest.main()
