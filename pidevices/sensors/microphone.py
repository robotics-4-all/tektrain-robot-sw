"""microphone.py"""

import wave
import time
import os
import threading
from ..devices import Sensor
import alsaaudio


class Microphone(Sensor):
    """Class representing a usb microphone. Extends :class:`Sensor`. 
    
    It uses pyalsaaudio library.
    It captures from the microphone and saves the record to a file. Currently
    supports only wav files.
    For consistent naming a udev rule has been written for identifing the device
    and an example asoundrc file.

    Args:
        dev_name: Alsa name of the device.
    """

    def __init__(self, dev_name='mic', name="", max_data_length=0):
        """Constructor"""

        super(Microphone, self).__init__(name, max_data_length)
        self.dev_name = dev_name
        self.start()
        self._init_thread()

    @property
    def dev_name(self):
        """The alsa name of the device."""
        return self._dev_name

    @dev_name.setter
    def dev_name(self, dev_name):
        self._dev_name = dev_name

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
    def paused(self):
        return self._paused

    @paused.setter
    def paused(self, value):
        self._paused = value

    def start(self):
        """Initialize hardware and os resources."""

        self._device = alsaaudio.PCM(type=alsaaudio.PCM_CAPTURE,
                                     device=self.dev_name)
        self._mixer = alsaaudio.Mixer(control='Mic', device=self.dev_name)

    def _init_thread(self):
        self._recording_mutex = threading.Condition()
        self._recording = False
        self._paused = False

    def read(self, secs, file_path, volume=100):
        """Read data from microphone
        
        Args:
            secs: The time in seconds of the capture.
            file_path: The file path of the file to be played. Currently it
                     supports only wav file format.
            volume: Volume percenatage

        Returns:
            It doesn't return a value but it saves the recording to a file.
        """

        # Get recording mutex
        self.recording_mutex.acquire()

        # Wait for another record to stop
        if self.recording:

            if self.paused:
                self.pause(False)

            # Change record flag
            self.recording = False
            self.recording_mutex.wait()
            
        # Open the wav file
        f = wave.open(self._fix_path(file_path), 'wb')

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
        self._device.setchannels(channels)
        self._device.setrate(framerate)

        # Set volume for channels
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

        self._device.setperiodsize(periodsize)
        
        self.recording = True
        self.recording_mutex.release()

        # Start recording
        t_start = time.time()
        while time.time() - t_start < secs:
            l, data = self._device.read()
            #print(len(data))
            #data_int = int.from_bytes(data, byteorder='little')
            #print(data_int)
            #data_str = str(data_int)
            #data_bytes = (int(data_str).to_bytes(512, byteorder='little'))
            #c = 0
            #for d, b in zip(data, data_bytes):
            #    if d != b:
            #        c += 1
            #print(c)
            if l:
                f.writeframes(data)

        f.close()
        self.restart()

        # Notify the other recording
        self.recording_mutex.acquire()
        if self.recording:
            self.recording = False
        else:
            self.recording_mutex.notify()
        self.recording_mutex.release()
    
    def async_read(self, secs, file_path, volume=100):
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
                                  args=(secs, file_path, volume,),
                                  daemon=True)
        thread.start()

    def pause(self, enabled=True):
        """Pause or resume the playback."""

        self._device.pause(enabled)
        self.paused = True

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
