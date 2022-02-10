"""neopixel_rgb.py"""

import time
from pixel_ring import pixel_ring
from pidevices.devices import Actuator


class LedError(Exception):
    """ Led custom exception class """
    pass

class LedRespeaker(Actuator):
    LED_COUNT = 12
    """Implementation for the Neopixel Programmable RGB LEDS. Extends 
    :class:`Actuator`.
    
    Args:
        led_brightness (int): Set to 0 for darkest and 255 for brightest
    """

    def __init__(self, led_brightness, name=""):
        """Constructor"""

        self._led_count = LedRespeaker.LED_COUNT
        self._led_brightness = led_brightness
        self._pixel_ring = pixel_ring

        # Set the id of the actuator
        super(LedRespeaker, self).__init__(name)

        self.start()

    @property
    def led_count(self):
        """Number of leds."""
        return self._led_count

    @property
    def led_brightness(self):
        """Set to 0 for darkest and 255 for brightest."""
        return self._led_brightness

    @property
    def pixel_ring(self):
        return self._pixel_ring

    @led_brightness.setter
    def led_brightness(self, x):
        self._led_brightness = x

    def start(self):
        """Initialize hardware and os resources."""
        self._pixel_ring.off()
        self._pixel_ring.set_brightness(self.led_brightness)
        
    def stop(self):
        """Free hardware and os resources."""
        self._pixel_ring.off()
        
    def write(self, data, wait_ms=50, wipe=False):
        """Write to the leds.
        
        Args:
            data: A list of lists of which each list corresponds to each led 
                and the values are [red, green, blue, brightness].
            wait_ms (int): Optional argument that has to be set when wipe is 
                :data:`True`. Defaults to :data:`50`.
            wipe: Flag for writting to all leds at once.
        """
        
        try:
            if wipe == True:
                self._color_wipe(data[0][0:3], data[0][3])
            else:
                pixel_pattern = []
                for d in data:
                    pixel_pattern.extend(d)

                print(pixel_pattern)

                self._pixel_ring.customize(pixel_pattern)
        except Exception as e:
            raise LedError(e)
        
    def rgb_to_hex(self, rgb_color):
        red = (rgb_color[0] << 16)
        green = (rgb_color[1] << 8)
        blue = rgb_color[2]

        hex_color = red + green + blue

        return hex_color 

    def _color_wipe(self, rgb_color=[0, 0, 255], wait_ms=50, brightness=60):
        """Wipe color across display a pixel at a time."""
        hex_color = self.rgb_to_hex(rgb_color)

        self._pixel_ring.set_brightness(int(self._led_brightness * 0.125))
        self._pixel_ring.mono(hex_color)


if __name__ == "__main__":
    leds = LedRespeaker(led_brightness=10, name='respeaker-leds')

    leds.write(data=[[255, 0, 0, 40]], wipe=True)
    time.sleep(2)
    leds.write(data=[[0, 255, 0, 100]], wipe=True)
    time.sleep(2)
    leds.write(data=[[0, 0, 255, 255]], wipe=True)
    time.sleep(2)

    pixel_ring.set_color_palette(0x00ff00, 0x0000ff)
    pixel_ring.think()
    time.sleep(2)

    data = []
    for i in range(12):
        data.append([255, 0, i * 12, 0])

    try:
        leds.write(data)
        time.sleep(2)
    except Exception as e:
        print(e)
    
    leds.stop()
