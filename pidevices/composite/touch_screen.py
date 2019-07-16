import os, pygame, sys, time
from pygame.locals import *
from evdev import InputDevice, list_devices
import threading
#from ..devices import Composite


#class TouchScreen(Composite):
class TouchScreen():
    """Class representing a touch screen."""

    def __init__(self, dev_name='touch_screen', name="", max_data_length=0):
        """Constructor"""

        #super(Composite, self).__init__(name, max_data_length)
        self.dev_name = dev_name
        self.start()

    def start(self):
        """Initialize hardware and os resources."""
        devices = map(InputDevice, list_devices())
	self.eventX = ""
	for dev in devices:
		if dev.name == "ADS7846 Touchscreen":
			self.eventX = dev.fn
	
	pygame.init()
	self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
	
	self.background = pygame.Surface(self.screen.get_size())
	self.background = self.background.convert()

	# Makes the cursor invisible
	pygame.mouse.set_cursor((8,8),(0,0),(0,0,0,0,0,0,0,0),(0,0,0,0,0,0,0,0))

	os.environ["SDL_FBDEV"] = "/dev/fb1"
	os.environ["SDL_MOUSEDRV"] = "TSLIB"
	os.environ["SDL_MOUSEDEV"] = self.eventX
	self.backupEvent = self.eventX

    def write(self, file_path = None, time_enabled = None, touch_enabled = None, \
		color_rgb = None, color_hex = None, options = None, multiple_options = None, \
		time_window = None, text = None, show_image = False, show_color = False, \
		show_video = False, show_options = False):

	# Clears the events buffer
	pygame.event.clear()
	if show_color == True:
		if color_rgb == None or time_enabled == None:
			raise Exception("show_color called without color or waiting time")
		return self._show_color(color_rgb, time_enabled, touch_enabled, text)

    def _show_image(self, image_uri, time_enabled, touch_enabled, text):
	pass

    def _show_black(self):
	self.background.fill((0,0,0))
	self.screen.blit(self.background, (0,0))
	pygame.display.flip()

    def _show_color(self, color_rgb, time_enabled, touch_enabled, text):
	print("I'm in print color")
	self.background.fill(color_rgb)
	self.screen.blit(self.background, (0,0))
	pygame.display.flip()
	t_start = time.time()
	running = True
	while time.time() - t_start < time_enabled and running:
		for event in pygame.event.get():
			print event
			if event.type == pygame.MOUSEBUTTONDOWN and touch_enabled == True:
				print("Touched")
				running = False
				break
	self._show_black()
	return time.time() - t_start
	

    def _show_video(self, video_uri, time_window, touch_enabled, text):
	pass

    def _show_options(self, options, time_enabled, multiple):
	pass

    def stop(self):
        """Clean hardware and os resources."""
	pygame.quit()
        #self.device.close()

if __name__ == "__main__":
    s = TouchScreen()
    print s.write(show_color = True, time_enabled = 2, color_rgb = (0, 255, 0))
    time.sleep(2)
    print s.write(show_color = True, time_enabled = 2, color_rgb = (255, 255, 0), touch_enabled = True)
    
