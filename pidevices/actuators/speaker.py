"""speaker.py"""

import wave
import os
import threading
import base64
import warnings
from ..devices import Actuator
import alsaaudio
import time


# to add cases etc ...
class SpeakerError(Exception):
    """ Speaker custom exception class """
    pass


class Speaker(Actuator):
    RETRY = 5
    SAMPLE_WIDTH = 2
    PERIOD_SIZE = 256
    FRAMERATES = [8000, 16000, 44100, 48000, 96000]
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

        self._device = None
        self._mixer = None
        
        # extra state variables
        self._duration = None
        self._curr_step = 0
        self._curr_times = 0

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

    @property
    def framerate(self):
        return self._framerate

    @framerate.setter
    def framerate(self, value):
        if value in Speaker.FRAMERATES:
            self._framerate = value
        else:
            self._framerate = Speaker.FRAMERATES[2]

    def start(self):
        """Initialize hardware and os resources."""
        try:
            print("Initializing driver")
            self._device = alsaaudio.PCM(device=self.dev_name)

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
        except alsaaudio.ALSAAudioError as e:
            print(f"{type(e).__name__} occured!")
            print(f"With message: {e.args}... Failed to initialize speaker!")

            self._device = None
            self._mixer = None

            raise SpeakerError
        except Exception as e:
            print(f"Something unexpected happend! {e}")

            self._device = None
            self._mixer = None

            raise SpeakerError

    def write(self, source, times=1, file_flag=False, rs_times=None, rs_step=None):
        if self._playing:
            warnings.warn("Already playing", RuntimeWarning)
            return None

        # Set playing flag
        self._playing = True

        self._write(source, times, file_flag, rs_times, rs_step)

    def _write(self, source, times=1, file_flag=False, rs_times=None, rs_step=None):
        """Write data to the speaker. Actually it just plays a playback.

        Args:
            source: The file path of the file to be played. Currently it
                supports only wav file format. Or base64 ascii encoded string
            volume: Volume percenatage
            times: How many time to play the same file.
            file_flag: Flag indicating if read from file or from raw data.
        """
        # if the device isnt initialized properly
        if self._device is None or self._mixer is None:
            raise SpeakerError

        self._duration = None
        self._paused = False

        try:
            periodsize = Speaker.PERIOD_SIZE

            if file_flag:
                # Open the wav file
                f = wave.open(self._fix_path(source), 'rb')             # add error checking here

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
                data = [source[i:i+step] for i in range(0, n, step)]     # add error checking here

            # calculate the duration of the track
            packets = len(data)
            packet_duration = periodsize / self.framerate
            self._duration = round(packets * packet_duration)

            # Set Device attributes for playback
            self._device.setchannels(channels)                           # add error checking here
            self._device.setrate(framerate)
            self._device.setperiodsize(periodsize)
            
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

            # Play n times the data
            
            self._play(data, times, rs_times, rs_step)                                      # add error checking here
        except alsaaudio.ALSAAudioError as e:
            print(f"Caugh is write: {e}")
            raise SpeakerError

        except Exception as e:
            print(f"Caugh is write: {e}")
            raise SpeakerError

        
    def _play(self, data, times, rs_times=None, rs_step=None):
        """Plays the data n times, by invoking the speaker pyalsapy library.
           It also checks if we have a preemption request during the playback.

        Args:
            data: The sound data to be played
            times: The amound of times to repeat the track
        """
        if rs_times is None:
            rs_times = 0
        
        if rs_step is None:
            rs_step = 0

        for i in range(rs_times, times, 1):
            self._curr_times = i
            self._curr_step = 0
            for d in data:
                self._curr_step += 1

                if self._curr_step < rs_step:
                    continue

                if self._playing:
                    self._device.write(d)
                else:
                    break

                while self._paused:
                    time.sleep(0.1)

                rs_step = 0

        # terminate and reset after finishes playing the track or canceling
        self.restart()
        # Clear the playing flag
        self._playing = False

    def async_write(self, source, times=1, file_flag=False):
        """Async write data to the speaker. Actually it just plays a playback.

        Args:
            file_path: The file path of the file to be played. Currently it
                supports only wav file format.
            times: How many time to play the same file.
        
        Returns:
            duration: The total duration of the track which will be played asyc.
        """
        self.thread = threading.Thread(target=self._write,
                                        args=(source, times, file_flag,),
                                        daemon=True)

        # Check if another thread is running
        if self._playing or self._canceled:
            warnings.warn("Already playing", RuntimeWarning)
            return None

        # Set playing flag
        self._playing = True

        self.thread.start()

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
        if self._dev_name is None:
            raise SpeakerError

        #self._device.pause(enabled) that statement throws an exception
        self._paused = enabled

    def _fix_path(self, fil_path):
        """Make the path proper for reading the file."""

        wav_folder = '/wav_sounds/'
        ex_path = os.path.realpath(__file__)
        ex_path = '/'.join(ex_path.split('/')[:-3]) + wav_folder + fil_path

        return ex_path

    def stop(self):
        """Clean hardware and os reources."""
        if self._device is not None:
            self._device.close()
        
        if self._mixer is not None:
            self._mixer.close()
