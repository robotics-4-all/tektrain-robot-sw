import unittest
import time
from pidevices.sensors.gp2y0a41sk0f import GP2Y0A41SK0F_mcp3002


class TestGP2Y0A41SK0F(unittest.TestCase):


    def test_inter(self):
        m_sensor = GP2Y0A41SK0F_mcp3002(port=0, device=0, channel=0)
        self.assertAlmostEqual(m_sensor.f_int(1.8), 7, places=1,
                              msg="Should be almost 7")

    def test_read(self):
        m_sensor = GP2Y0A41SK0F_mcp3002(port=0, device=0, channel=0)
        while True:
            print("Distance {} cm".format(m_sensor.read()))
            time.sleep(0.1)


if __name__ == "__main__":
    unittest.main()
