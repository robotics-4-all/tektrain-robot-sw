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
    """Class representing a usb speaker extends :class:`Actuator`

    Args:
        dev_name (str): The alsa name of the device.
        channels (int): The number of channels from the custom recordings.
    """

    def __init__(self, dev_name='default', volume=50,
                 channels=1, card_index=2, name="", max_data_length=0):
        """Constructor"""

        super(Speaker, self).__init__(name, max_data_length)
        self.dev_name = dev_name
        self.channels = channels
        self._card_index = card_index
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
        self._device = alsaaudio.PCM(device=self._dev_name)
        mixers = alsaaudio.mixers(cardindex=self._card_index)
        if "PCM" in mixers:
            self._mixer = alsaaudio.Mixer(control='PCM', cardindex=self._card_index)
        else:
            self._mixer = None

        #Unmute if it is muted at first
        if self._mixer.getmute():
            self._mixer.setmute(0)

        self._playing = False
        self._paused = False
        self._canceled = False

    def write(self, source, times=1, file_flag=False):
        if self._playing or self._canceled:
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

        data = []

        if file_flag:
            # Open the wav file
            #f = wave.open(self._fix_path(source), 'rb')
            f = wave.open(source, 'rb')

            sample_width = f.getsampwidth()
            audio_format = self.selectFormat(sample_width)
            periodsize = f.getframerate() // 8
            channels = f.getnchannels()
            framerate = f.getframerate()

            sample = f.readframes(periodsize)
            while sample:
                # Read data from stdin
                data.append(sample)
                sample = f.readframes(periodsize)
            
            f.close()
        else:
            sample_width = 2
            audio_format = self.selectFormat(sample_width)
            periodsize = 256
            channels = self.channels
            framerate = 44100
            

            # Read data from encoded string
            n = len(source)
            step = sample_width * periodsize
            data = [source[i:i+step] for i in range(0, n, step)]


        self._device.setperiodsize(periodsize)
        self._device.setrate(framerate)
        self._device.setformat(audio_format)
        self._device.setchannels(channels)

        delay = periodsize / framerate
        delay -= 0.05 * delay
        
        counter = 1

        # Play the file
        for i in range(times):
            # Break the loop if another call is done
            if not self._playing:
                break
            
            for d in data:
                self._device.write(d)
                time.sleep(delay)
                print(counter)
                counter += 1
                # pause from another process
                while self._paused:
                    time.sleep(0.1)
                    # cancel while at pause
                    if self._canceled:    
                        self.pause(False)
                        self._playing = False        
                        break

                # terminate from outside
                if self._canceled:
                    self._playing = False 
                    break

        # terminate and reset after finishes playing the track or canceling
        self.restart()
        self._canceled = False
        
        

    def selectFormat(self, sample_width):
        format = None

        # 8bit is unsigned in wav files
        if sample_width == 1:
            format = alsaaudio.PCM_FORMAT_U8
        # Otherwise we assume signed data, little endian
        elif sample_width == 2:
            format = alsaaudio.PCM_FORMAT_S16_LE
        elif sample_width == 3:
            format = alsaaudio.PCM_FORMAT_S24_3LE
        elif sample_width == 4:
            format = alsaaudio.PCM_FORMAT_S32_LE
        else:
            raise ValueError('Unsupported format')
    
        return format

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
        if self._playing or self._canceled:
            warnings.warn("Already playing", RuntimeWarning)
            return None

        # Set playing flag
        self._playing = True

        thread.start()

    def cancel(self):
        """Cancel playaback"""
        if not self._canceled and self._playing: 
            self._canceled = True
            self._paused = False

    def pause(self, enabled=True):
        """Pause or resume the playback.

        Args:
            enabled (boolean): If it :data:`True` pauses the playback else
                it resumes it.
        """
        if self._playing:
            self._device.pause(enabled)
            self._paused = True if enabled == True else False

    def _fix_path(self, fil_path):
        """Make the path proper for reading the file."""

        wav_folder = '/wav_sounds/'
        ex_path = os.path.realpath(__file__)
        ex_path = '/'.join(ex_path.split('/')[:-3]) + wav_folder + fil_path

        return ex_path

    def stop(self):
        """Clean hardware and os reources."""      
        time.sleep(1)
        self._device.close()
        self._mixer.close()
        
        