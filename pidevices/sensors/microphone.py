import wave
import time
import os
import threading
from ..devices import Sensor
import alsaaudio


class Microphone(Sensor):
    """Class representing a usb microphone."""

    def __init__(self, cardindex=1, name="", max_data_length=0):
        """Constructor"""

        super(Microphone, self).__init__(name, max_data_length)
        self.cardindex = cardindex
        self.start()
        self._init_thread()

    def start(self):
        """Initialize hardware and os resources."""

        self._device = alsaaudio.PCM(type=alsaaudio.PCM_CAPTURE,
                                     cardindex=self.cardindex)
        #self._mixer = alsaaudio.Mixer(control='PCM', cardindex=self.cardindex)

    def _init_thread(self):
        self._kill_cond = threading.Condition()
        self._playing = False
        self._kill = False

    def read(self, secs, file_path, volume=50):
        """Read data from microphone
        
        Args:
            secs: The time in seconds of the capture.
            file_path: The file path of the file to be played. Currently it
                     supports only wav file format.
            volume: Volume percenatage
        """

        # Open the wav file
        f = wave.open(self._fix_path(file_path), 'wb')

        # Stop another playback if it is running
        #if self.playing:
        #    # Mute for to play the last sector of previous file
        #    self.mixer.setmute(1)

        #    # Unstop at first
        #    self.pause(False)

        #    # Change kill flag
        #    self.kill_cond.acquire()
        #    self.kill = True
        #    self.kill_cond.wait()
        #    self.kill_cond.release()

        #    # Unmute
        #    self.mixer.setmute(0)
            
        # Set attributes
        channels = 1
        framerate = 44100 
        sample_width = 2
        periodsize = 256

        # Set file attributes
        f.setnchannels(channels)
        f.setframerate(framerate)
        f.setsampwidth(sample_width)
        f.setnframes(periodsize)

        # Set Device attributes for playback
        self.device.setchannels(channels)
        self.device.setrate(framerate)

        # Set volume for channels
        #self.mixer.setvolume(volume, 0) 

        # 8bit is unsigned in wav files
        if sample_width == 1:
            self.device.setformat(alsaaudio.PCM_FORMAT_U8)
        # Otherwise we assume signed data, little endian
        elif sample_width == 2:
            self.device.setformat(alsaaudio.PCM_FORMAT_S16_LE)
        elif sample_width == 3:
            self.device.setformat(alsaaudio.PCM_FORMAT_S24_3LE)
        elif sample_width == 4:
            self.device.setformat(alsaaudio.PCM_FORMAT_S32_LE)
        else:
            raise ValueError('Unsupported format')

        self.device.setperiodsize(periodsize)
        
        #thread = threading.Thread(target=self._async_read, 
        #                          args=(f, periodsize),
        #                          daemon=True)
        #thread.start()
        #self.playing = True
        self._async_read(f, secs)
    
    def _async_read(self, f, secs):
        """Read from the file."""

        t_start = time.time()
        while time.time() - t_start < secs:

            l, data = self.device.read()

            if l:
                f.writeframes(data)

            # kill Thread
            #self.kill_cond.acquire()
            #if self.kill:
            #    data = False
            #    cond = False
            #self.kill_cond.release()

        f.close()
        self.restart()

        #if self.kill:
        #    self.kill_cond.acquire()
        #    self.kill = False
        #    self.kill_cond.notify()
        #    self.kill_cond.release()

    def pause(self, enabled=True):
        """Pause or resume the playback."""

        self.device.pause(enabled)

    def _fix_path(self, fil_path):
        """Make the path proper for reading the file."""

        wav_folder = '/wav_sounds/'
        ex_path = os.path.realpath(__file__)
        ex_path = '/'.join(ex_path.split('/')[:-3]) + wav_folder + fil_path

        return ex_path

    def stop(self):
        """Clean hardware and os reources."""

        self.device.close()
        #self.mixer.close()

    @property
    def cardindex(self):
        return self._cardindex

    @cardindex.setter
    def cardindex(self, cardindex):
        self._cardindex = cardindex

    @property
    def device(self):
        return self._device

    @property
    def mixer(self):
        return self._mixer

    @property
    def write_lock(self):
        return self._write_lock

    @property
    def kill_cond(self):
        return self._kill_cond

    @property
    def playing(self):
        return self._playing

    @playing.setter
    def playing(self, value):
        self._playing = value

    @property
    def kill(self):
        return self._kill

    @kill.setter
    def kill(self, value):
        self._kill = value
