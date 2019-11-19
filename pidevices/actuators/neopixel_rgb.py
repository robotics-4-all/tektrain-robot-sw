"""neopixel_rgb.py"""

import time
from rpi_ws281x import Adafruit_NeoPixel, ws, Color
from ..devices import Actuator


class LedController(Actuator):
    """Implementation for the Neopixel Programmable RGB LEDS. Extends 
    :class:`Actuator`.
    
    It use's rpi_ws281x library.

    Args:
        led_count (int): Number of leds.
        led_pin (int): GPIO pin connected to the pixels.
        led_freq_hz (int): LED signal frequency in hertz (usually 800khz)
        led_brightness (int): Set to 0 for darkest and 255 for brightest
        led_dma (int): DMA channel to use for generating signal.
            Defaults to :data:`10`.
        led_invert (boolean): True to invert the signal 
            (when using NPN transistor level shift). Defaults to :data:`False`.
        led_channel (int): Set to '1' for GPIOs 13, 19, 41, 45 or 53. Defaults
            to :data:`0`.
        led_strip: Strip type and colour ordering. Defaults to 
            :data:`ws.WS2811_STRIP_RGB`.
    """

    def __init__(self, led_count, led_pin, led_freq_hz,
                 led_brightness, led_dma=10, led_invert=False,
                 led_channel=0, led_strip=ws.WS2811_STRIP_RGB, name=""):
        """Constructor"""

        self._led_count = led_count
        self._led_pin = led_pin
        self._led_freq_hz = led_freq_hz
        self._led_dma = led_dma
        self._led_brightness = led_brightness
        self._led_invert = led_invert
        self._led_channel = led_channel
        self._led_strip = led_strip

        # Set the id of the actuator
        super(LedController, self).__init__(name)

        self.start()

    @property
    def led_count(self):
        """Number of leds."""
        return self._led_count

    @led_count.setter
    def led_count(self, x):
        self._led_count = x

    @property
    def led_pin(self):
        """GPIO pin connected to the pixels."""
        return self._led_pin

    @led_pin.setter
    def led_pin(self, x):
        self._led_pin = x

    @property
    def led_freq_hz(self):
        """LED signal frequency in hertz."""
        return self._led_freq_hz

    @led_freq_hz.setter
    def led_freq_hz(self, x):
        self._led_freq_hz = x

    @property
    def led_brightness(self):
        """Set to 0 for darkest and 255 for brightest."""
        return self._led_brightness

    @led_brightness.setter
    def led_brightness(self, x):
        self._led_brightness = x

    @property
    def led_dma(self):
        """DMA channel to use for generating signal."""
        return self._led_dma

    @led_dma.setter
    def led_dma(self, x):
        self._led_dma = x

    @property
    def led_invert(self):
        """True to invert the signal."""
        return self._led_invert

    @led_invert.setter
    def led_invert(self, x):
        self._led_invert = x

    @property
    def led_channel(self):
        """Set to '1' for GPIOs 13, 19, 41, 45 or 53."""
        return self._led_channel

    @led_channel.setter
    def led_channel(self, x):
        self._led_channel = x

    @property
    def led_strip(self):
        """Strip type and color ordering."""
        return self._led_strip

    @led_strip.setter
    def led_strip(self, x):
        self._led_strip = x

    def start(self):
        """Initialize hardware and os resources."""
        # Create NeoPixel object with appropriate configuration.
        self.strip = Adafruit_NeoPixel(self.led_count, self.led_pin,
                                       int(self.led_freq_hz), self.led_dma,
                                       self.led_invert, self.led_brightness,
                                       self.led_channel, self.led_strip)

        # Intialize the library (must be called once before other functions).
        self.strip.begin()
        self.strip.show()

    def stop(self):
        """Free hardware and os resources."""
        # Turn-off led strip
        self.close()
        
    def write(self, data, wait_ms=50, wipe=False):
        """Write to the leds.
        
        Args:
            data: A list of lists of which each list corresponds to each led 
                and the values are [red, green, blue, brightness].
            wait_ms (int): Optional argument that has to be set when wipe is 
                :data:`True`. Defaults to :data:`50`.
            wipe: Flag for writting to all leds at once.
        """

        if wipe:
            self._color_wipe(data[0][:3], wait_ms=wait_ms, brightness=data[0][3])
        else:
            for (i, led) in enumerate(data):
                self.strip.setPixelColor(i, Color(led[1],
                                                  led[0],
                                                  led[2]))
                self.strip.setBrightness(led[3])
                self.strip.show()
                time.sleep(0.1)

    def close(self):
        """Free hardware and os resources."""

        for i in range(self.strip.numPixels()):
            self.strip.setPixelColor(i, Color(0, 0, 0))
            self.strip.show()
        
        self.strip._cleanup()
        del self.strip

    def _color_wipe(self, rgb_color=[0, 0, 255], wait_ms=50, brightness=60):
        """Wipe color across display a pixel at a time."""
        for i in range(self.strip.numPixels()):
            self.strip.setPixelColor(i, Color(rgb_color[1],
                                     rgb_color[0], rgb_color[2]))
            self.strip.setBrightness(brightness)
            self.strip.show()
            time.sleep(wait_ms/1000.0)
