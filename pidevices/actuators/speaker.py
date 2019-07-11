import wave
import os
import threading
from ..devices import Actuator
import alsaaudio


class Speaker(Actuator):
    """Class representing a usb speaker."""

    def __init__(self, cardindex=1, name="", max_data_length=0):
        """Constructor"""

        super(Speaker, self).__init__(name, max_data_length)
        self.cardindex = cardindex
        self.start()
        self._init_thread()

    def start(self):
        """Initialize hardware and os resources."""

        self._device = alsaaudio.PCM(cardindex=self.cardindex)
        self._mixer = alsaaudio.Mixer(control='PCM', cardindex=self.cardindex)

    def _init_thread(self):
        self._kill_cond = threading.Condition()
        self._playing = False
        self._kill = False

    def write(self, fil, volume=50, loop=False):
        """Write data
        
        Args:
            fil: The file path of the file to be played. Currently it supports
                only wav file format.
            volume: Volume percenatage
            loop: Run the same file in a loop.
        """

        # Open the wav file
        f = wave.open(self._fix_path(fil), 'rb')

        # Stop another playback if it is running
        if self.playing:
            # Mute for to play the last sector of previous file
            self.mixer.setmute(1)

            # Unstop at first
            self.pause(False)

            # Change kill flag
            self.kill_cond.acquire()
            self.kill = True
            self.kill_cond.wait()
            self.kill_cond.release()

            # Unmute
            self.mixer.setmute(0)
            

        # Set Device attributes for playback
        self.device.setchannels(f.getnchannels())
        self.device.setrate(f.getframerate())

        # Set volume for channels
        self.mixer.setvolume(volume, 0) 

        # 8bit is unsigned in wav files
        if f.getsampwidth() == 1:
            self.device.setformat(alsaaudio.PCM_FORMAT_U8)
        # Otherwise we assume signed data, little endian
        elif f.getsampwidth() == 2:
            self.device.setformat(alsaaudio.PCM_FORMAT_S16_LE)
        elif f.getsampwidth() == 3:
            self.device.setformat(alsaaudio.PCM_FORMAT_S24_3LE)
        elif f.getsampwidth() == 4:
            self.device.setformat(alsaaudio.PCM_FORMAT_S32_LE)
        else:
            raise ValueError('Unsupported format')

        periodsize = round(f.getframerate() / 8)

        self.device.setperiodsize(periodsize)
        
        thread = threading.Thread(target=self._async_write, 
                                  args=(f, loop, periodsize),
                                  daemon=True)
        thread.start()
        self.playing = True
    
    def _async_write(self, f, loop, periodsize):
        """Read from the file."""

        cond = True
        while cond:
            cond = loop
            data = f.readframes(periodsize)
            while data:
                # Read data from stdin
                self.device.write(data)
                data = f.readframes(periodsize)

                # kill Thread
                self.kill_cond.acquire()
                if self.kill:
                    data = False
                    cond = False
                self.kill_cond.release()

            f.rewind()

        self.restart()

        if self.kill:
            self.kill_cond.acquire()
            self.kill = False
            self.kill_cond.notify()
            self.kill_cond.release()

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
        self.mixer.close()

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
