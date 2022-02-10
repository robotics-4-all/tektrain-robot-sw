import unittest
import time
from pidevices.actuators.respeaker_rgb import LedRespeaker


class TestLedController(unittest.TestCase):

    def test_write(self):
        led_controller = LedRespeaker(led_brightness=50)
        led_count = led_controller.led_count

        print(led_count)

        print("Color wipe red")
        led_controller.write([[255, 0, 0, 150]], wipe=True)
 
        time.sleep(3)
        led_controller.write([[0, 0, 0, 150]], wipe=True)

        #led_controller.restart()
        print("All colors per three led.")

        r = [255, 0, 0, 150]
        g = [0, 255, 0, 150]
        b = [0, 0, 255, 150]
        white = [0, 0, 0, 105]
        r_index = 0
        g_index = 1
        b_index = 2

        data = [white for i in range(led_count)] 
        for j in range(led_count):
            data[r_index] = r
            data[g_index] = g
            data[b_index] = b
            led_controller.write(data)
            time.sleep(0.5)
            data[r_index] = white
            data[g_index] = white
            data[b_index] = white
            r_index = (r_index+1) % led_count
            g_index = (g_index+1) % led_count
            b_index = (b_index+1) % led_count

        led_controller.write([[0, 0, 0, 150]], wipe=True)


if __name__ == "__main__":
    unittest.main()
