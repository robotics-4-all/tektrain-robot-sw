import time
from neopixel import *
from ..devices import Actuator


class LedController(Actuator):
    """ Implementation for the Neopixel Programmable RGB LEDS"""

    def __init__(self, name="", led_count=16, led_pin=21, led_freq_hz=700000,
                 led_dma=10, led_brightness=60, led_invert=False,
                 led_channel=0, led_strip=ws.WS2811_STRIP_RGB):

        """ Default LED strip configuration:
        led_count = 12        Number of LEDs.
        led_pin = 21          GPIO pin connected to the pixels (18 uses PWM!).
        led_freq_hz = 700000  LED signal frequency in hertz (usually 800khz)
        led_dma = 5          DMA channel to use for generating signal (try 10)
        led_brightness = 255  Set to 0 for darkest and 255 for brightest
        led_invert = False
        True to invert the signal (when using NPN transistor level shift)
        led_strip = ws.WS2811_STRIP_RGB   Strip type and colour ordering
        led_channel = 0        set to '1' for GPIOs 13, 19, 41, 45 or 53
        """
        self._led_count = led_count
        self._led_pin = led_pin
        self.led_freq_hz = led_freq_hz
        self.led_dma = led_dma
        self._led_brightness = led_brightness
        self.led_invert = led_invert
        self._led_channel = led_channel
        self.led_strip = led_strip

        # Set the id of the actuator
        super(LedController, self).__init__(name)

        self.start()

    # Methods

    def start(self):
        """Initialize hardware and os resources."""
        # Create NeoPixel object with appropriate configuration.
        self.strip = Adafruit_NeoPixel(self.led_count, self.led_pin,
                                       self.led_freq_hz, self.led_dma,
                                       self.led_invert, self.led_brightness,
                                       self.led_channel, self.led_strip)

        # Intialize the library (must be called once before other functions).
        self.strip.begin()
        self.strip.show()

    def stop(self):
        """Free hardware and os resources."""
        # Turn-off led strip
        self.close()
        
    def write(self, data):
        """strip.setPixelColor(n, green, re)d, blue)"""
        for (i, led) in enumerate(data):
            self.strip.setPixelColor(i, Color(led[1],
                                              led[0],
                                              led[2]))
            self.strip.setBrightness(led[3])
            self.strip.show()
            time.sleep(0.1)

    def close(self):
        """ Disable Leds """
        for i in range(self.strip.numPixels()):
            self.strip.setPixelColor(i, Color(0, 0, 0))
            self.strip.show()

    def color_wipe(self, rgb_color=[0, 0, 255], wait_ms=50, brightness=60):
        """Wipe color across display a pixel at a time."""
        for i in range(self.strip.numPixels()):
            self.strip.setPixelColor(i, Color(rgb_color[1],
                                     rgb_color[0], rgb_color[2]))
            self.strip.setBrightness(brightness)
            self.strip.show()
            time.sleep(wait_ms/1000.0)

    # Setters and getters

    @property
    def led_pin(self):
            """ Get led_pin """
            return self._led_pin

    @property
    def led_count(self):
            """ Get led_pin """
            return self._led_count

    @property
    def led_brightness(self):
            """ Get led_pin """
            return self._led_brightness

    @property
    def led_channel(self):
            """ Get led_pin """
            return self._led_channel

    @property
    def led_freq_hz(self):
            """ Get led_pin """
            return self._led_freq_hz

    @led_freq_hz.setter
    def led_freq_hz(self, x):
            """set led_pin"""
            self._led_freq_hz = x

    @led_pin.setter
    def led_pin(self, x):
            """set led_pin"""
            self._led_pin = x

    @led_count.setter
    def led_count(self, x):
            """set led_pin"""
            self._led_count = x

    @led_brightness.setter
    def led_brightness(self, x):
            """set led_pin"""
            self._led_brightness = x

    @led_channel.setter
    def led_channel(self, x):
            """set led_pin"""
            self._led_channel = x
