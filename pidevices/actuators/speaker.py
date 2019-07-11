import wave
import os
from ..devices import Actuator
import alsaaudio


class Speaker(Actuator):
    """Class representing a usb speaker."""

    def __init__(self, cardindex=1, name="", max_data_length=0):
        """Constructor"""

        super(Speaker, self).__init__(name, max_data_length)
        self.cardindex = cardindex
        self.start()

    def start(self):
        """Initialize hardware and os resources."""

        self._device = alsaaudio.PCM(cardindex=self.cardindex)
        self._mixer = alsaaudio.Mixer(control='PCM', cardindex=self.cardindex)

    def write(self, fil, volume=50):
        """Write data
        
        Args:
            fil: The file path of the file to be played. Currently it supports
                only wav file format.
        """

        # Open the wav file
        f = wave.open(self._fix_path(fil), 'rb')

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
        
        data = f.readframes(periodsize)
        while data:
            # Read data from stdin
            self.device.write(data)
            data = f.readframes(periodsize)

        f.close()

    def _fix_path(self, fil_path):
        """Make the path proper for reading the file."""

        wav_folder = '/wav_sounds/'
        ex_path = os.path.realpath(__file__)
        ex_path = '/'.join(ex_path.split('/')[:-3]) + wav_folder + fil_path

        return ex_path

    def stop(self):
        """Clean hardware and os reources."""
        pass

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
