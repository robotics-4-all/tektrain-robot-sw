import wave
import os
import threading
from ..devices import Actuator
import alsaaudio


class Speaker(Actuator):
    """Class representing a usb speaker."""

    def __init__(self, cardindex, name="", max_data_length=0):
        """Constructor"""

        super(Speaker, self).__init__(name, max_data_length)
        self.cardindex = cardindex
        self.start()
        self._init_thread()

    def start(self):
        """Initialize hardware and os resources."""
        
        # It uses the default card for speaker with the ~/.asoundrc config
        #self._device = alsaaudio.PCM(cardindex=self.cardindex)
        self._device = alsaaudio.PCM()
        self._mixer = alsaaudio.Mixer(control='PCM', cardindex=self.cardindex)

        # Unmute if it is muted at first
        if self.mixer.getmute():
            self.mixer.setmute(0)

    def _init_thread(self):
        self._playing_mutex = threading.Condition()
        self._playing = False
        self._paused = False

    def write(self, file_path, volume=50, times=1):
        """Write data
        
        Args:
            file_path: The file path of the file to be played. Currently it
                     supports only wav file format.
            volume: Volume percenatage
            loop: Run the same file in a loop.
        """

        # Get playing mutex
        self.playing_mutex.acquire()

        # Stop another playback if it is running
        if self.playing:
            # Mute for to play the last sector of previous file
            self.mixer.setmute(1)

            # Unstop at first
            if self.paused:
                self.pause(False)

            # Change kill flag
            self.playing = False
            self.playing_mutex.wait()

            # Unmute
            self.mixer.setmute(0)
        
        # Open the wav file
        f = wave.open(self._fix_path(file_path), 'rb')

        # Set Device attributes for playback
        self.device.setchannels(f.getnchannels())
        self.device.setrate(f.getframerate())

        # Set volume for channels
        self.mixer.setvolume(volume) 

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

        periodsize = 256

        self.device.setperiodsize(periodsize)

        # Set playing flag
        self.playing = True      
        self.playing_mutex.release()

        # Play the file
        for i in range(times):
            # Break the loop if another call is done
            if not self.playing:
                break

            data = f.readframes(periodsize)
            while data:
                # Read data from stdin
                self.device.write(data)
                data = f.readframes(periodsize)

                # kill Thread
                self.playing_mutex.acquire()
                if not self.playing:
                    data = False
                self.playing_mutex.release()

            f.rewind()

        # Close file and restart device
        f.close()
        self.restart()

        self.playing_mutex.acquire()
        if self.playing:
            self.playing = False
        else:
            self.playing_mutex.notify()
        self.playing_mutex.release()
    
    def async_write(self, file_path, volume, times=1):
        """Asynchronous write
        
        Args:
            file_path: The file path of the file to be played. Currently it
                     supports only wav file format.
            volume: Volume percenatage
            loop: Run the same file in a loop.
        """

        thread = threading.Thread(target=self.write, 
                                  args=(file_path, volume, times),
                                  daemon=True)
        thread.start()

     
    def pause(self, enabled=True):
        """Pause or resume the playback."""

        self.device.pause(enabled)
        self.paused = enabled

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
    def playing_mutex(self):
        return self._playing_mutex

    @property
    def playing(self):
        return self._playing

    @playing.setter
    def playing(self, value):
        self._playing = value


    @property
    def paused(self):
        return self._paused

    @paused.setter
    def paused(self, value):
        self._paused = value
