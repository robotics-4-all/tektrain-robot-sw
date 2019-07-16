import os, pygame, sys, time
from pygame.locals import *
from evdev import InputDevice, list_devices
import threading
from ..devices import Composite


class TouchScreen(Composite):
    """Class representing a touch screen."""

    def __init__(self, dev_name='touch_screen', name="", max_data_length=0):
        """Constructor"""

        super(Composite, self).__init__(name, max_data_length)
        self.dev_name = dev_name
        self.start()

    def start(self):
        """Initialize hardware and os resources."""
        devices = map(InputDevice, list_devices())
	self.eventX = ""
	for dev in devices:
		if dev.name == "ADS7846 Touchscreen":
		eventX = dev.fn
	
	os.environ["SDL_FBDEV"] = "/dev/fb1"
	os.environ["SDL_MOUSEDRV"] = "TSLIB"
	os.environ["SDL_MOUSEDEV"] = eventX

	pygame.init()
	self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
	
	background = pygame.Surface(screen.get_size())
	background = background.convert()

    def write(self, file_path = None, time_enabled = None, touch_enabled = None, \
		color_rgb = None, color_hex = None, options = None, multiple_options = None \
		time_window = None, text = None):
	pass

    def _show_image(self, image_uri, time_enabled, touch_enabled, text):
	pass

    def _show_color(self, color_rgb, time_enabled, touch_enabled, text):
	pass

    def _show_video(self, video_uri, time_window, touch_enabled, text):
	pass

    def _show_options(self, options, time_enabled, multiple):
	pass

    def stop(self):
        """Clean hardware and os reources."""

        self.device.close()

