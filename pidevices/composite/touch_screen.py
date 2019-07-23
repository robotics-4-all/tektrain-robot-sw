import os, pygame, sys, time
from pygame.locals import *
from evdev import InputDevice, list_devices
import threading
# from subprocess import *
# from ..devices import Composite
from omxplayer.player import OMXPlayer


#class TouchScreen(Composite):
class TouchScreen():
    """Class representing a touch screen."""

    def __init__(self, dev_name='touch_screen', name="", max_data_length=0):
        """Constructor"""

        #super(Composite, self).__init__(name, max_data_length)
        self.dev_name = dev_name
	self.screen_w = 800
	self.screen_h = 480
        self.start()

    def turnScreenOff(self):
	os.popen("vcgencmd display_power 0")

    def turnScreenOn(self):
	os.popen("vcgencmd display_power 1")

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

	#self.turnScreenOff()

    def write(self, file_path = None, time_enabled = None, touch_enabled = None, \
		color_rgb = None, color_hex = None, options = None, multiple_options = None, \
		time_window = None, text = None, show_image = False, show_color = False, \
		show_video = False, show_options = False):

	# Clears the events buffer
	#self.turnScreenOn()
	ret = None
	pygame.event.clear()
	if show_color == True:
		if color_rgb == None or time_enabled == None:
			self.turnScreenOff()
			raise Exception("show_color called without color or waiting time")
		ret = self._show_color(color_rgb, time_enabled, touch_enabled, text)
	elif show_image == True:
		if file_path == None or time_enabled == None:	
			self.turnScreenOff()
			raise Exception("show_image called without image URI or waiting time")
		ret = self._show_image(file_path, time_enabled, touch_enabled, text)		
	elif show_video == True:
		if file_path == None or time_window == None:	
			self.turnScreenOff()
			raise Exception("show_video called without video URI or waiting time")
		ret = self._show_video(file_path, time_window, touch_enabled, text)			
	elif show_options == True:
		if time_enabled == None or options == None:	
			self.turnScreenOff()
			raise Exception("show_options called without options or waiting time")
		ret = self._show_options(options, time_enabled, multiple_options)		


	#self.turnScreenOff()
	return ret

    def _show_image(self, image_uri, time_enabled, touch_enabled, text):
	try:
		img = pygame.image.load(image_uri)
	except Exception as e:
		raise Exception("Loading image failed with error: " + str(e))

	img_s = img.get_size()
	wr = self.screen_w * 1.0 / img_s[0]
	hr = self.screen_h * 1.0 / img_s[1]
	rate = wr
	if wr >= hr:
		rate = hr

	img = pygame.transform.scale(img, (int(img_s[0] * rate), int(img_s[1] * rate)))
	
	padding_w = 0
	padding_h = 0
	if wr >= hr:
		padding_w = (self.screen_w - int(img_s[0] * rate)) / 2
	else:
		padding_h = (self.screen_h - int(img_s[1] * rate)) / 2

	self.screen.blit(img, (padding_w, padding_h))
	pygame.display.flip()
	t_start = time.time()
	running = True
	while time.time() - t_start < time_enabled and running:
		for event in pygame.event.get():
			if event.type == pygame.MOUSEBUTTONDOWN and touch_enabled == True:
				running = False
				break
	self._show_black()
	return {'reaction_time': time.time() - t_start}
	

    def _show_black(self):
	self.background.fill((0,0,0))
	self.screen.blit(self.background, (0,0))
	pygame.display.flip()

    def _show_color(self, color_rgb, time_enabled, touch_enabled, text):
	self.background.fill(color_rgb)
	self.screen.blit(self.background, (0,0))
	pygame.display.flip()
	t_start = time.time()
	running = True
	while time.time() - t_start < time_enabled and running:
		for event in pygame.event.get():
			if event.type == pygame.MOUSEBUTTONDOWN and touch_enabled == True:
				running = False
				break
	self._show_black()
	return {'reaction_time': time.time() - t_start}
	

    def _show_video(self, video_uri, time_window, touch_enabled, text):
	pygame.display.flip()

	t_start = time.time()
	running = True
	try:
		player = OMXPlayer(video_uri)
		player.set_aspect_mode("stretch")
		while player.is_playing() == False:
			time.sleep(0.1)
	except Exception as e:
		raise Exception("Video not loaded. Error is: " + str(e))

	while time.time() - t_start < time_window and running:
		for event in pygame.event.get():
			if event.type == pygame.MOUSEBUTTONDOWN and touch_enabled == True:
				running = False
				player.quit()
				break
		try:
			if player.is_playing() == False:
				running = False
		except:
			running = False

	try:
		if player.is_playing() == True:
			player.quit()
	except:
		pass

	self._show_black()
	return {'reaction_time': time.time() - t_start}

    def _show_options(self, options, time_enabled, multiple):
	self._show_black()
	pygame.draw.line(self.screen, (255, 255, 255), \
		(0, self.screen_h / 2), (self.screen_w - 1, self.screen_h / 2), 1)
	pygame.draw.line(self.screen, (255, 255, 255), \
		(self.screen_w / 2, 0), (self.screen_w / 2, self.screen_h - 1), 1)

	pygame.font.init()
	myfont = pygame.font.SysFont('Comic Sans MS', 200)
	if len(options) >= 1:
		tw, th = myfont.size(options[0])
		wr = self.screen_w / 2 * 1.0 / tw
		hr = self.screen_h / 2 * 1.0 / th
		print tw, th, self.screen_w, self.screen_h
		rate = wr
		if wr >= hr:
			rate = hr
		rate *= 0.5
		padding_w = 0
		padding_h = 0
		if wr >= hr:
			padding_w = (self.screen_w / 2.0 - int(tw * rate)) / 2
		else:
			padding_h = (self.screen_h / 2.0 - int(th * rate)) / 2

		mytext = myfont.render(options[0], 1, (255, 255, 255))
		mytext = pygame.transform.scale(mytext, (int(tw * rate), int(th * rate)))
		self.screen.blit(mytext, (self.screen_w / 4 - tw * rate / 2, self.screen_h / 4 - th * rate / 2))
	if len(options) >= 2:
		tw, th = myfont.size(options[1])
		wr = self.screen_w / 2 * 1.0 / tw
		hr = self.screen_h / 2 * 1.0 / th
		print tw, th, self.screen_w, self.screen_h
		rate = wr
		if wr >= hr:
			rate = hr
		rate *= 0.5
		padding_w = 0
		padding_h = 0
		if wr >= hr:
			padding_w = (self.screen_w / 2.0 - int(tw * rate)) / 2
		else:
			padding_h = (self.screen_h / 2.0 - int(th * rate)) / 2

		mytext = myfont.render(options[1], 1, (255, 255, 255))
		mytext = pygame.transform.scale(mytext, (int(tw * rate), int(th * rate)))
		self.screen.blit(mytext, (3 * self.screen_w / 4 - tw * rate / 2, self.screen_h / 4 - th * rate / 2))
	if len(options) >= 3:
		tw, th = myfont.size(options[2])
		wr = self.screen_w / 2 * 1.0 / tw
		hr = self.screen_h / 2 * 1.0 / th
		print tw, th, self.screen_w, self.screen_h
		rate = wr
		if wr >= hr:
			rate = hr
		rate *= 0.5
		padding_w = 0
		padding_h = 0
		if wr >= hr:
			padding_w = (self.screen_w / 2.0 - int(tw * rate)) / 2
		else:
			padding_h = (self.screen_h / 2.0 - int(th * rate)) / 2

		mytext = myfont.render(options[2], 1, (255, 255, 255))
		mytext = pygame.transform.scale(mytext, (int(tw * rate), int(th * rate)))
		self.screen.blit(mytext, (self.screen_w / 4 - tw * rate / 2, 3 * self.screen_h / 4 - th * rate / 2))

	if len(options) >= 4:
		tw, th = myfont.size(options[3])
		wr = self.screen_w / 2 * 1.0 / tw
		hr = self.screen_h / 2 * 1.0 / th
		print tw, th, self.screen_w, self.screen_h
		rate = wr
		if wr >= hr:
			rate = hr
		rate *= 0.5
		padding_w = 0
		padding_h = 0
		if wr >= hr:
			padding_w = (self.screen_w / 2.0 - int(tw * rate)) / 2
		else:
			padding_h = (self.screen_h / 2.0 - int(th * rate)) / 2

		mytext = myfont.render(options[3], 1, (255, 255, 255))
		mytext = pygame.transform.scale(mytext, (int(tw * rate), int(th * rate)))
		self.screen.blit(mytext, (3 * self.screen_w / 4 - tw * rate / 2, 3 * self.screen_h / 4 - th * rate / 2))

	pygame.display.flip()
	t_start = time.time()
	running = True
	final_option = None
	while time.time() - t_start < time_enabled and running:
		for event in pygame.event.get():
			if event.type == pygame.MOUSEBUTTONDOWN:
				position = event.pos
				if event.pos[0] <= self.screen_w / 2 and event.pos[1] <= self.screen_h / 2:
					if len(options) >= 1:
						final_option = options[0]
				elif event.pos[0] >= self.screen_w / 2 and event.pos[1] <= self.screen_h / 2:
					if len(options) >= 2:
						final_option = options[1]
				elif event.pos[0] <= self.screen_w / 2 and event.pos[1] >= self.screen_h / 2:
					if len(options) >= 3:
						final_option = options[2]
				elif event.pos[0] >= self.screen_w / 2 and event.pos[1] >= self.screen_h / 2:
					if len(options) >= 4:
						final_option = options[3]
						
				running = False
				break
	self._show_black()
	return {
		'reaction_time': time.time() - t_start,
		'selected': final_option
	}

	

    def stop(self):
        """Clean hardware and os resources."""
	pygame.quit()
        #self.device.close()

if __name__ == "__main__":
    s = TouchScreen()
    print s.write(show_color = True, time_enabled = 2, color_rgb = (0, 255, 0))
    time.sleep(1)
    print s.write(show_color = True, time_enabled = 2, color_rgb = (255, 255, 0), touch_enabled = True)
    time.sleep(1)
    print s.write(show_image = True, file_path = "/home/pi/t.png", time_enabled = 5, touch_enabled = True)
    time.sleep(1)
    print s.write(show_video = True, file_path = "/home/pi/video.mp4", time_window = 10, touch_enabled = True)
    time.sleep(1)
    print s.write(show_options = True, options = ['1', '2', 'test', 'pikatsou'], time_enabled = 5, multiple_options = False) 
