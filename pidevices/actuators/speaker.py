"""speaker.py"""

import os
import wave
import time
import threading
import base64
import warnings
import alsaaudio

from pidevices.devices import Actuator
from pidevices.hardware_interfaces.gpio_implementations import PiGPIO
from enum import IntEnum
import subprocess


# to add cases etc ...
class SpeakerError(Exception):
    """ Speaker custom exception class """
    pass

class AmpState(IntEnum):
    ENABLED = 0
    DISSABLED = 1

class Speaker(Actuator):
    RETRY = 5
    SAMPLE_WIDTH = 2
    PERIOD_SIZE = 256
    FRAMERATES = [8000, 16000, 44100, 48000, 96000]
    MIN_VOLUME = 0
    MAX_VOLUME = 100
    """Class representing a usb speaker extends :class:`Actuator`

    Args:
        dev_name (str): The alsa name of the device.
        channels (int): The number of channels from the custom recordings.
    """

    def __init__(self, dev_name='pulse', volume=50,
                 channels=1, framerate=44100, shutdown_pin=None, mixer_ctrl='Master', 
                 name="", max_data_length=0):
        """Constructor"""

        super(Speaker, self).__init__(name, max_data_length)
        self.dev_name = dev_name
        self.mixer_ctrl = mixer_ctrl
        self.framerate = framerate
        self._channels = channels

        self._playing = False
        self._device = None
        self._mixer = None
        
        self._amp_iface = None
        if shutdown_pin is not None:
            if isinstance(shutdown_pin, int):
                self._amp_iface = self.init_interface(interface='gpio', 
                                                      impl="RPiGPIO",
                                                      shutdown=shutdown_pin)

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
    def mixer_ctrl(self):
        """Mixer Control."""
        return self._mixer_ctrl

    @dev_name.setter
    def mixer_ctrl(self, ctrl):
        self._mixer_ctrl = ctrl

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
            volume = int(min(max(Speaker.MIN_VOLUME, value), Speaker.MAX_VOLUME))
            self._mixer.setvolume(volume)

    def set_amplifier(self, state):
        if self._amp_iface is not None:
            self.hardware_interfaces[self._amp_iface].write('shutdown', state)

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
            self.hardware_interfaces[self._amp_iface].set_pin_function('shutdown', 'output')

            pcms = alsaaudio.pcms()
            mixers = alsaaudio.mixers()
            #print(f'Available PCMs: {pcms}')
            #print(f'Available Mixers: {mixers}')
            self._device = alsaaudio.PCM(device=self._dev_name)
            self._mixer = alsaaudio.Mixer(device=self._dev_name, control=self._mixer_ctrl)

            # Unmute if it is muted at first
            if self._mixer.getmute():
                self._mixer.setmute(0)
        except alsaaudio.ALSAAudioError as e:
            print(f"{type(e).__name__} occured!")
            print(f"With message: {e.args}... Failed to initialize Mixer!")
            self._mixer = None
        except Exception as e:
            print(f"Something unexpected happend! {e}")
            self._mixer = None

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
        if self._device is None:
            raise SpeakerError

        self._duration = None
        self._paused = False
        self._canceled = False

        self.set_amplifier(AmpState.ENABLED)

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
                channels = self._channels
                framerate = self.framerate
                sample_width = self.SAMPLE_WIDTH

                # Read data from encoded string
                n = len(source)
                step = sample_width * periodsize
                data = [source[i:i+step] for i in range(0, n, step)]     # add error checking here

            # calculate the duration of the track
            packets = len(data)
            packet_duration = periodsize / self.framerate
            self._duration = (packets * packet_duration)

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
            self.set_amplifier(AmpState.DISSABLED)
        except alsaaudio.ALSAAudioError as e:
            self.set_amplifier(AmpState.DISSABLED)

            print(f"Caugh is write: {e}")
            raise SpeakerError

        except Exception as e:
            self.set_amplifier(AmpState.DISSABLED)

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

                if self._canceled:
                    self._canceled = False
                    break

                rs_step = 0

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
        if self._playing:
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

        if self._paused:
            self.set_amplifier(AmpState.DISSABLED)
        else:
            self.set_amplifier(AmpState.ENABLED)

    def _fix_path(self, fil_path):
        """Make the path proper for reading the file."""

        return fil_path
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
        
        self.set_amplifier(AmpState.DISSABLED)


if __name__ == '__main__':
    import time
    ctrl = Speaker(dev_name='default')
    #ctrl.async_write('/home/pi/Wav_868kb.wav', file_flag=True)

    #time.sleep(5)
    #ctrl.cancel()
    #time.sleep(1)
    #ctrl.stop()
    ctrl.write('/home/pi/Wav_868kb.wav', file_flag=True)
