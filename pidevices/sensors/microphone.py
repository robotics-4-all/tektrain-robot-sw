"""microphone.py"""

import wave
import time
import os
import sys
import threading
import warnings
from ..devices import Sensor
import alsaaudio


class Microphone(Sensor):
    """Class representing a microphone. Extends :class:`Sensor`. 
    
    It uses pyalsaaudio library.
    It captures from the microphone and saves the record to a file. Currently
    supports only wav files.

    Args:
        dev_name (str): Alsa name of the device.
        channels (int): The number of channels of the device.
    """

    def __init__(self, dev_name, channels, periodsize,
                 name="", max_data_length=0):
        """Constructor"""

        super(Microphone, self).__init__(name, max_data_length)
        self._dev_name = dev_name
        self._channels = channels
        self._periodsize = periodsize
        self.start()

    @property
    def recording_mutex(self):
        return self._recording_mutex

    @property
    def recording(self):
        return self._recording

    @recording.setter
    def recording(self, value):
        self._recording = value
    
    @property
    def record(self):
        while self._record is None:
            time.sleep(0.1)
        return self._record

    def start(self):
        """Initialize hardware and os resources."""

        # Initializa alsa device
        self._device = alsaaudio.PCM(type=alsaaudio.PCM_CAPTURE,
                                     device=self._dev_name)

        # Find proper mixer using the card name.
        card_name = self._dev_name.split(":")[-1].split(",")[0].split("=")[-1]
        card_index = alsaaudio.cards().index(card_name)
        mixers = alsaaudio.mixers(cardindex=card_index)
        if "Mic" in mixers:
            self._mixer = alsaaudio.Mixer(control='Mic', cardindex=card_index)
        else:
            self._mixer = None

        self._recording = False
        self._cancelled = False
        self._record = None

    def read(self, secs, framerate=44100, 
             file_path=None, volume=100, file_flag=False):
        """Read data from microphone
        
        Also set self.recording for use in a threaded environment

        Args:
            secs (float): The time in seconds of the capture.
            framerate (int): The framerate of the recording.
            file_path (str): The file path of the file to be played. Currently 
                it supports only wav file format.
            volume (int): Volume percenatage if the sound card support setting
                the volume.
            file_flag (bool): Boolean indicating if the recording will be saved
                to a file.

        Returns:
            (bytearray): The data in raw bytes.

        Raises:
            RuntimeError: If already recording
        """

        if self._recording:
            warnings.warn("Already recording", RuntimeWarning)
            return None

        self._record = None

        # Set attributes
        channels = self._channels
        sample_width = 2

        # Set Device attributes for playback
        self._device.setchannels(channels)
        self._device.setrate(framerate)

        # Set volume for channels
        if self._mixer:
            self._mixer.setvolume(volume) 

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

        self._device.setperiodsize(self._periodsize)
        
        self.recording = True

        # Start recording
        t_start = time.time()
        audio = bytearray() 
        while time.time() - t_start < secs and self.recording:
            # Get data from device
            l, data = self._device.read()
            if l:
                for d in data:
                    audio.append(d)

        # Save to file
        if file_flag:
            # Open the wav file
            f = wave.open(self._fix_path(file_path), 'wb')

            # Set file attributes
            f.setnchannels(channels)
            f.setframerate(framerate)
            f.setsampwidth(sample_width)
            f.setnframes(self._periodsize)

            for sample in audio:
                f.writeframes(sample)

            f.close()
            ret = self._fix_path(file_path)
        else:
            # Encode to base64
            ret = audio

        self.restart()
        
        self._record = ret

        return ret
    
    def async_read(self, secs, file_path=None, volume=100, file_flag=False):
        """Async read data from microphone
        
        Args:
            secs: The time in seconds of the capture.
            file_path: The file path of the file to be played. Currently it
                     supports only wav file format.
            volume: Volume percenatage

        Returns:
            It doesn't return a value but it saves the recording to a file.
        """
       
        thread = threading.Thread(target=self.read, 
                                  args=(secs, file_path, volume, file_flag,),
                                  daemon=True)
        thread.start()

    def pause(self, enabled=True):
        """Pause or resume the playback."""

        self._device.pause(enabled)
    
    def cancel(self):
        """Cancel recording"""

        self._recording = False

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
