import unittest
import time
from pidevices.actuators.neopixel_rgb import LedController


class TestLedController(unittest.TestCase):

    def test_write(self):
        led_count = 30
        led_controller = LedController(led_count, 13, 700000, 255, led_channel=1)

        print("Color wipe red")
        led_controller.write([[255, 0, 0, 150]], wipe=True)
        
        time.sleep(5)
        led_controller.write([[0, 0, 0, 150]], wipe=True)
        print("All colors per three led.")

        r = [255, 0, 0, 150]
        g = [0, 255, 0, 150]
        b = [0, 0, 255, 150]
        white = [0, 0, 0, 105]
        r_index = 0
        g_index = 1
        b_index = 2

        data = [white for i in range(led_count)] 
        for j in range(2*led_count):
            data[r_index] = r
            data[g_index] = g
            data[b_index] = b
            led_controller.write(data)
            time.sleep(1)
            data[r_index] = white
            data[g_index] = white
            data[b_index] = white
            r_index = (r_index+1) % led_count
            g_index = (g_index+1) % led_count
            b_index = (b_index+1) % led_count


if __name__ == "__main__":
    unittest.main()
