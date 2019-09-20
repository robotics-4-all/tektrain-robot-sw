import wave
import os
import threading
from ..devices import Actuator
import alsaaudio


class Speaker(Actuator):
    """Class representing a usb speaker extends :class:`Actuator`

    Args:
        dev_name (str): The alsa name of the device.
    """

    def __init__(self, dev_name='speaker', name="", max_data_length=0):
        """Constructor"""

        super(Speaker, self).__init__(name, max_data_length)
        self.dev_name = dev_name
        self.start()
        self._init_thread()

    @property
    def dev_name(self):
        """Alsa device name."""
        return self._dev_name

    @dev_name.setter
    def dev_name(self, dev_name):
        self._dev_name = dev_name

    def start(self):
        """Initialize hardware and os resources."""
        
        # It uses the default card for speaker with the ~/.asoundrc config
        #self._device = alsaaudio.PCM(dev_name=self.dev_name)
        self._device = alsaaudio.PCM(device=self.dev_name)
        self._mixer = alsaaudio.Mixer(control='PCM', device=self.dev_name)

        # Unmute if it is muted at first
        if self._mixer.getmute():
            self._mixer.setmute(0)

    def _init_thread(self):
        self._playing_mutex = threading.Condition()
        self._playing = False
        self._paused = False

    def write(self, file_path, volume=50, times=1):
        """Write data to the speaker. Actually it just plays a playback.
        
        Args:
            file_path: The file path of the file to be played. Currently it
                supports only wav file format.
            volume: Volume percenatage
            times: How many time to play the same file.
        """

        # Get playing mutex
        self._playing_mutex.acquire()

        # Stop another playback if it is running
        if self._playing:
            # Mute for to play the last sector of previous file
            self._mixer.setmute(1)

            # Unstop at first
            if self._paused:
                self.pause(False)

            # Change kill flag
            self._playing = False
            self._playing_mutex.wait()

            # Unmute
            self._mixer.setmute(0)
        
        # Open the wav file
        f = wave.open(self._fix_path(file_path), 'rb')

        # Set Device attributes for playback
        self._device.setchannels(f.getnchannels())
        self._device.setrate(f.getframerate())

        # Set volume for channels
        self._mixer.setvolume(volume) 

        # 8bit is unsigned in wav files
        if f.getsampwidth() == 1:
            self._device.setformat(alsaaudio.PCM_FORMAT_U8)
        # Otherwise we assume signed data, little endian
        elif f.getsampwidth() == 2:
            self._device.setformat(alsaaudio.PCM_FORMAT_S16_LE)
        elif f.getsampwidth() == 3:
            self._device.setformat(alsaaudio.PCM_FORMAT_S24_3LE)
        elif f.getsampwidth() == 4:
            self._device.setformat(alsaaudio.PCM_FORMAT_S32_LE)
        else:
            raise ValueError('Unsupported format')

        periodsize = 256

        self._device.setperiodsize(periodsize)

        # Set playing flag
        self._playing = True      
        self._playing_mutex.release()

        # Play the file
        for i in range(times):
            # Break the loop if another call is done
            if not self._playing:
                break

            data = f.readframes(periodsize)
            while data:
                # Read data from stdin
                self._device.write(data)
                data = f.readframes(periodsize)

                # kill Thread
                self._playing_mutex.acquire()
                if not self._playing:
                    data = False
                self._playing_mutex.release()

            f.rewind()

        # Close file and restart device
        f.close()
        self.restart()

        self._playing_mutex.acquire()
        if self._playing:
            self._playing = False
        else:
            self._playing_mutex.notify()
        self._playing_mutex.release()
    
    def async_write(self, file_path, volume, times=1):
        """Async write data to the speaker. Actually it just plays a playback.
        
        Args:
            file_path: The file path of the file to be played. Currently it
                supports only wav file format.
            volume: Volume percenatage
            times: How many time to play the same file.
        """

        thread = threading.Thread(target=self.write, 
                                  args=(file_path, volume, times),
                                  daemon=True)
        thread.start()

    def pause(self, enabled=True):
        """Pause or resume the playback.

        Args:
            enabled (boolean): If it :data:`True` pauses the playback else
                it resumes it.
        """

        self._device.pause(enabled)
        self._paused = enabled

    def _fix_path(self, fil_path):
        """Make the path proper for reading the file."""

        wav_folder = '/wav_sounds/'
        ex_path = os.path.realpath(__file__)
        ex_path = '/'.join(ex_path.split('/')[:-3]) + wav_folder + fil_path

        return ex_path

    def stop(self):
        """Clean hardware and os reources."""

        self._device.close()
        self._mixer.close()
