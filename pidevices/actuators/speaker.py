"""speaker.py"""

import wave
import os
import threading
import base64
import warnings
from ..devices import Actuator
import alsaaudio
import time

class Speaker(Actuator):
    SAMPLE_WIDTH = 2
    """Class representing a usb speaker extends :class:`Actuator`

    Args:
        dev_name (str): The alsa name of the device.
        channels (int): The number of channels from the custom recordings.
    """

    def __init__(self, dev_name='dmix:CARD=Speaker,DEV=0', volume=50,
                 channels=1, framerate = 44100, name="", max_data_length=0):
        """Constructor"""

        super(Speaker, self).__init__(name, max_data_length)
        self.dev_name = dev_name
        self.channels = channels
        self.framerate = framerate
        self.start()

        # Set volume
        self.volume = volume

    @property
    def dev_name(self):
        """Alsa device name."""
        return self._dev_name

    @dev_name.setter
    def dev_name(self, dev_name):
        self._dev_name = dev_name

    @property
    def playing(self):
        """Flag indicating if the speaker is playing a sound"""
        return self._playing

    @property
    def volume(self):
        """The volume of the mixer if it exists."""
        vol = None
        if self._mixer:
            vol = self._mixer.getvolume()
        return vol

    @volume.setter
    def volume(self, value):
        if self._mixer:
            volume = min(max(0, value), 100)
            self._mixer.setvolume(volume)

    def start(self):
        """Initialize hardware and os resources."""

        # It uses the default card for speaker with the ~/.asoundrc config
        try: 
            self._device = alsaaudio.PCM(device=self.dev_name)
        except Exception as e:
            self._mixer = None
            print("Failled.....")
            raise Exception("Failed again")
            return

        # Find proper mixer using the card name.
        card_name = self._dev_name.split(":")[-1].split(",")[0].split("=")[-1]
        card_index = alsaaudio.cards().index(card_name)
        mixers = alsaaudio.mixers(cardindex=card_index)
        if "PCM" in mixers:
            self._mixer = alsaaudio.Mixer(control='PCM', cardindex=card_index)
        else:
            self._mixer = None

        # Unmute if it is muted at first
        if self._mixer.getmute():
            self._mixer.setmute(0)

        self._playing = False

    def write(self, source, times=1, file_flag=False):
        if self._playing:
            warnings.warn("Already playing", RuntimeWarning)
            return None

        # Set playing flag
        self._playing = True

        self._write(source, times, file_flag)

    def _write(self, source, times=1, file_flag=False):
        """Write data to the speaker. Actually it just plays a playback.

        Args:
            source: The file path of the file to be played. Currently it
                supports only wav file format. Or base64 ascii encoded string
            volume: Volume percenatage
            times: How many time to play the same file.
            file_flag: Flag indicating if read from file or from raw data.
        """

        periodsize = 256

        if file_flag:
            # Open the wav file
            f = wave.open(self._fix_path(source), 'rb')

            channels = f.getnchannels()
            framerate = f.getframerate()
            sample_width = f.getsampwidth()

            # Read data from file
            data = []
            sample = f.readframes(periodsize)
            while sample:
                data.append(sample)
                sample = f.readframes(periodsize)

            # Close file
            f.close()
        else:
            channels = self.channels
            framerate = self.framerate
            sample_width = self.SAMPLE_WIDTH

            # Read data from encoded string
            n = len(source)
            step = sample_width * periodsize
            data = [source[i:i+step] for i in range(0, n, step)]

        # Set Device attributes for playback
        self._device.setchannels(channels)
        self._device.setrate(framerate)
        
        # 8bit is unsigned in wav files
        if sample_width == 1:
            self._device.setformat(alsaaudio.PCM_FORMAT_U8)
        # Otherwise we assume signed data, little endian
        elif sample_width == 2:
            self._device.setformat(alsaaudio.PCM_FORMAT_S16_LE)
        elif sample_width == 3:
            self._device.setformat(alsaaudio.PCM_FORMAT_S24_3LE)
        elif sample_width == 4:
            self._device.setformat(alsaaudio.PCM_FORMAT_S32_LE)
        else:
            raise ValueError('Unsupported format')

        self._device.setperiodsize(periodsize)

        
        # Play the file
        try:
            for i in range(times):
                # Break the loop if another call is done
                if not self._playing:
                    break

                for d in data:
                    self._device.write(d)

                    if not self._playing:
                        break
        except:
            print("Caught exception")
            time.sleep(1)
            print("Leaving bey...")
            raise Exception("hahhaha")
            return

        self.restart()
        # Clear the playing flag
        self._playing = False

    def async_write(self, source, times=1, file_flag=False):
        """Async write data to the speaker. Actually it just plays a playback.

        Args:
            file_path: The file path of the file to be played. Currently it
                supports only wav file format.
            times: How many time to play the same file.
        """

        thread = threading.Thread(target=self._write,
                                  args=(source, times, file_flag,),
                                  daemon=True)

        # Check if another thread is running
        if self._playing:
            warnings.warn("Already playing", RuntimeWarning)
            return None

        # Set playing flag
        self._playing = True

        thread.start()

    def cancel(self):
        """Cancel playaback"""
        self._playing = False

    def pause(self, enabled=True):
        """Pause or resume the playback.

        Args:
            enabled (boolean): If it :data:`True` pauses the playback else
                it resumes it.
        """

        self._device.pause(enabled)

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
