"""touch_screen.py"""

import os
import pygame
import sys
import time
from pygame.locals import *
from evdev import InputDevice, list_devices
import threading
# from subprocess import *
from ..devices import Actuator
from omxplayer.player import OMXPlayer
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"


#class TouchScreen(Composite):
class TouchScreen(Actuator):
    """Class representing a touch screen extends :class:`Actuator`."""

    def __init__(self, name="", max_data_length=0):
        """Constructor"""

        super(TouchScreen, self).__init__(name, max_data_length)
        self.screen_w = 480
        self.screen_h = 800
        self.start()

    def start(self):
        """Initialize hardware and os resources."""
        devices = map(InputDevice, list_devices())
        self.eventX = ""
        for dev in devices:
            if dev.name == "ADS7846 Touchscreen":
                self.eventX = dev.path

        #pygame.init()
        pygame.font.init()
        pygame.display.init()

        #self.turnScreenOff()

    def turnScreenOff(self):
        os.popen("vcgencmd display_power 0")

    def turnScreenOn(self):
        os.popen("vcgencmd display_power 1")

    def write(self, file_path=None, 
              time_enabled=None, touch_enabled=None,
              color_rgb=None, color_hex=None,
              options=None, multiple_options=False,
              time_window=None, text=None,
              show_image=False, show_color=False, 
              show_video=False, show_options=False):
        """Write to the screen

        Args:
            file_path: Optional argument specifying the path of an image. 
                Defaults to :data:`None`.
            time_enabled: Time in secs specifying the duration of the preview.
            touch_enabled: Enable touch mode.
            color_rgb: Color in rgb value.
            color_hex: Color in hex value.
            options (list): A list with the options text.
            multiple_options (boolean): Flag to preview multiple options.
            time_window:
            text: Single text for preview.
            show_image (boolean): Flag for showing an image.
            show_color (boolean): Flag for showing just color.
            show_video (boolean): Flag for showing a video.
            show_options (boolean): Flag for showing a menu with options.

        Raises:
            Exception: 
        """

        # Init screen
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

        self.background = pygame.Surface(self.screen.get_size())
        self.background = self.background.convert()

        # Makes the cursor invisible
        pygame.mouse.set_cursor((8, 8), 
                                (0, 0), 
                                (0, 0, 0, 0, 0, 0, 0, 0),
                                (0, 0, 0, 0, 0, 0, 0, 0))

        os.environ["SDL_FBDEV"] = "/dev/fb1"
        os.environ["SDL_MOUSEDRV"] = "TSLIB"
        os.environ["SDL_MOUSEDEV"] = self.eventX
        self.backupEvent = self.eventX

        # Clears the events buffer
        #self.turnScreenOn()
        ret = None
        pygame.event.clear()
        if show_color:
            if color_rgb is None or time_enabled is None:
                self.turnScreenOff()
                raise Exception("show_color called without color or waiting time")
            ret = self._show_color(color_rgb, time_enabled, touch_enabled, text)
        elif show_image:
            if file_path is None or time_enabled is None:	
                self.turnScreenOff()
                raise Exception("show_image called without\
                                 image URI or waiting time")
            ret = self._show_image(file_path, time_enabled,
                                   touch_enabled, text)		
        elif show_video:
            if file_path is None or time_window is None:	
                self.turnScreenOff()
                raise Exception("show_video called without video\
                                 URI or waiting time")
            ret = self._show_video(file_path, time_window, touch_enabled, text)			
        elif show_options:
            if time_enabled is None or options is None:	
                self.turnScreenOff()
                raise Exception("show_options called without\
                                 options or waiting time")
            ret = self._show_options(options, time_enabled, multiple_options)		

        #self.turnScreenOff()

        # Deactivate screen
        pygame.display.quit()

        return ret

    def _show_image(self, image_uri, time_enabled, touch_enabled, text):
        try:
            img = pygame.image.load(image_uri)
        except Exception as e:
            raise Exception("Loading image failed with error: " + str(e))
            
            # Load image from string
            # img = pygame.image.fromstring(image_uri, (640, 480), "JPG")
        
        img_s = img.get_rect()
        
        temp = (self.screen_w - img_s.width) * (self.screen_h - img_s.height)
        if temp < 0:
            img = pygame.transform.rotate(img, -90)

        img_s = img.get_rect()
        
        w_rate = self.screen_w * (1.0 / img_s.width)
        h_rate = self.screen_h * (1.0 / img_s.height)

        rate = w_rate if w_rate < h_rate else h_rate
        offset_x = (self.screen_w - rate * img_s.width) / 2
        offset_y = (self.screen_h - rate * img_s.height) / 2

        scaled_image = pygame.transform.scale(img, (int(img_s.width * rate), int(img_s.height * rate)))

        self.screen.blit(scaled_image, (offset_x, offset_y))
        
        pygame.display.flip()
        t_start = time.time()
        running = True
        while time.time() - t_start < time_enabled and running:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN and touch_enabled:
                    running = False
                    break
        self._show_black()
        return {'reaction_time': time.time() - t_start}

    def _show_black(self):
        self.background.fill((0, 0, 0))
        self.screen.blit(self.background, (0, 0))
        pygame.display.flip()

    def _show_color(self, color_rgb, time_enabled, touch_enabled, text):
        self.background.fill(color_rgb)
        self.screen.blit(self.background, (0, 0))
        pygame.display.flip()
        t_start = time.time()
        running = True
        while time.time() - t_start < time_enabled and running:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN and touch_enabled:
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
            while not player.is_playing():
                time.sleep(0.1)
        except Exception as e:
            raise Exception("Video not loaded. Error is: " + str(e))

        while time.time() - t_start < time_window and running:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN and touch_enabled:
                    running = False
                    player.quit()
                    break
            try:
                if not player.is_playing():
                    running = False
            except Exception as e:
                running = False

        try:
            if player.is_playing():
                player.quit()
        except Exception as e:
            pass

        self._show_black()
        return {'reaction_time': time.time() - t_start}

    def _show_options(self, options, time_enabled, multiple):
        self._show_black()
        pygame.draw.line(self.screen,
                         (255, 255, 255),
                         (0, self.screen_h / 2),
                         (self.screen_w - 1, self.screen_h / 2),
                         1)
        pygame.draw.line(self.screen,
                         (255, 255, 255),
                         (self.screen_w / 2, 0),
                         (self.screen_w / 2, self.screen_h - 1),
                         1)

        pygame.font.init()
        myfont = pygame.font.SysFont('Comic Sans MS', 200)
        if len(options) >= 1:
            tw, th = myfont.size(options[0])
            rate = self._compute_rate(tw, th)

            mytext = myfont.render(options[0], 1, (255, 255, 255))
            mytext = pygame.transform.scale(mytext, 
                                            (int(tw * rate), int(th * rate)))
            self.screen.blit(mytext, 
                             (self.screen_w / 4 - tw * rate / 2,
                              self.screen_h / 4 - th * rate / 2))
        if len(options) >= 2:
            tw, th = myfont.size(options[1])
            rate = self._compute_rate(tw, th)

            mytext = myfont.render(options[1], 1, (255, 255, 255))
            mytext = pygame.transform.scale(mytext,
                                            (int(tw * rate), int(th * rate)))
            self.screen.blit(mytext, 
                             (3 * self.screen_w / 4 - tw * rate / 2,
                              self.screen_h / 4 - th * rate / 2))
        if len(options) >= 3:
            tw, th = myfont.size(options[2])
            rate = self._compute_rate(tw, th)

            mytext = myfont.render(options[2], 1, (255, 255, 255))
            mytext = pygame.transform.scale(mytext,
                                            (int(tw * rate), int(th * rate)))
            self.screen.blit(mytext, 
                             (self.screen_w / 4 - tw * rate / 2,
                              3 * self.screen_h / 4 - th * rate / 2))

        if len(options) >= 4:
            tw, th = myfont.size(options[3])
            rate = self._compute_rate(tw, th)

            mytext = myfont.render(options[3], 1, (255, 255, 255))
            mytext = pygame.transform.scale(mytext,
                                            (int(tw * rate), int(th * rate)))
            self.screen.blit(mytext,
                             (3 * self.screen_w / 4 - tw * rate / 2,
                              3 * self.screen_h / 4 - th * rate / 2))

        pygame.display.flip()
        t_start = time.time()
        running = True
        final_option = None
        while time.time() - t_start < time_enabled and running:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    position = event.pos
                    if event.pos[0] <= self.screen_w / 2\
                            and event.pos[1] <= self.screen_h / 2:
                        if len(options) >= 1:
                            final_option = options[0]
                    elif event.pos[0] >= self.screen_w / 2\
                            and event.pos[1] <= self.screen_h / 2:
                        if len(options) >= 2:
                            final_option = options[1]
                    elif event.pos[0] <= self.screen_w / 2\
                            and event.pos[1] >= self.screen_h / 2:
                        if len(options) >= 3:
                            final_option = options[2]
                    elif event.pos[0] >= self.screen_w / 2 \
                            and event.pos[1] >= self.screen_h / 2:
                        if len(options) >= 4:
                            final_option = options[3]
                                    
                    running = False
                    break
        self._show_black()
        if final_option is None:
            final_option = ""
        return { 
            'reaction_time': time.time() - t_start,
            'selected': final_option
        }

    def _compute_rate(self, tw, th):
        """Compute screen rate."""

        wr = self.screen_w / 2 * 1.0 / tw
        hr = self.screen_h / 2 * 1.0 / th
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

        return rate

    def stop(self):
        """Clean hardware and os resources."""
        pygame.quit()
        #self.device.close()


#if __name__ == "__main__":
#    s = TouchScreen()
#    print(s.write(show_color=True, time_enabled=2, color_rgb=(0, 255, 0)))
#    time.sleep(1)
#    print(s.write(show_color=True, time_enabled=2,
#                  color_rgb=(255, 255, 0), touch_enabled=True))
#    time.sleep(1)
#    print s.write(show_image=True, file_path="/home/pi/t.png", 
#                  time_enabled=5, touch_enabled=True)
#    time.sleep(1)
#    print s.write(show_video=True, file_path="/home/pi/video.mp4", 
#                  time_window=10, touch_enabled=True)
#    time.sleep(1)
#    print s.write(show_options=True,
#                  options=['Option 1', 'Just 2', 'PikaPikaTsou'],
#                  time_enabled=5,
#                  multiple_options=False) 
