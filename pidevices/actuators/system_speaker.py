from pidevices.devices import Actuator
from pidevices.hardware_interfaces.gpio_implementations import PiGPIO
from pidevices.actuators.max98306 import Max98306

import time
import wave
import os

import subprocess
import threading
import psutil


class SystemSpeaker(Actuator):
    TMP_WAV_PATH = "/tmp/tmp.wav"
    SAMPLE_PERIOD = 256
    SAMPLE_WIDTH = 2

    def __init__(self, volume=50, channels=1, framerate=44100, amp=None, name="", max_data_length=0):
        super(SystemSpeaker, self).__init__(name, max_data_length)
        
        self._amp = amp
        self._volume = volume
        self._channels = channels
        self._framerate = framerate
        self._sample_width = SystemSpeaker.SAMPLE_WIDTH
        
        self._subprocess = None
        self._ps_process = None

        self._is_playing = False

    @property 
    def volume(self):
        return self._volume

    @volume.setter
    def volume(self, value):
        if (0 <= value) and (value <= 100):
            self._volume = value

            subprocess.run(["amixer", "-D", "pulse", "sset", "Master", str(self._volume)+"%"])

    @property
    def playing(self):
        if self._is_playing:
            return True

        return False

    def _save_to_wav(self, source):
        f = wave.open(SystemSpeaker.TMP_WAV_PATH, 'w')

        channels = source['channels'] if "channels" in source else self._channels
        framerate = source['framerate'] if "framerate" in source else self._framerate
        sample_width = source['sample_width'] if "sample_width" in source else self._sample_width
        data = source['data'] if "data" in source else bytearray()

        f.setnchannels(channels)
        f.setframerate(framerate)
        f.setsampwidth(sample_width)
        f.setnframes(SystemSpeaker.SAMPLE_PERIOD)
        f.writeframes(data)
        f.close()

    def _write(self, source, file_flag=False):
        self._is_playing = True

        try:
            if self._amp is not None:
                self._amp.enable()

            if file_flag:
                if os.path.isfile(source):
                    self._subprocess = subprocess.Popen(args=["aplay", source], stdout=subprocess.PIPE)
            else:
                self._save_to_wav(source)
                self._subprocess = subprocess.Popen(args=["aplay", SystemSpeaker.TMP_WAV_PATH], stdout=subprocess.PIPE)
            
            if self._subprocess is not None:
                self._ps_process = psutil.Process(pid=self._subprocess.pid)
                
                time.sleep(0.1)

                while self._subprocess.poll() is None:
                    time.sleep(0.1)
            
            if self._amp is not None:
                self._amp.disable()
            
        except Exception as e:
            if self._amp is not None:
                    self._amp.disable()

        self._subprocess = None
        self._ps_process = None
        
        self._is_playing = False

    def write(self, source, file_flag=False):
        if not self._is_playing:
            self._write(source=source, file_flag=file_flag)

    def async_write(self, source, file_flag=False):
        if not self._is_playing:
            thread = threading.Thread(target=self._write, args=(source, file_flag), daemon=True)
            thread.start()
    
    def cancel(self):
        if self._is_playing:
            self._is_playing = False

            if self._subprocess is not None:
                self._subprocess.terminate()
            
            if self._amp is not None:
                self._amp.disable()

    def pause(self, enabled=True):
        if enabled:
            if self._amp is not None:
                self._amp.disable()

            if self._is_playing:
                if self._ps_process is not None:
                    self._ps_process.suspend()
        else:
            if self._amp is not None:
                self._amp.enable()

            if self._is_playing:
                if self._ps_process is not None:
                    self._ps_process.resume()



if __name__ == "__main__":
    SOURCE = "/home/pi/temp.wav"

    amp = Max98306()
    speaker = SystemSpeaker(amp=amp)
    
    print("Setting volume to {}".format(70))
    speaker.volume = 70

    print("Playing in blocking mode!")
    try:
        speaker.write(source=SOURCE, file_flag=True)
    except KeyboardInterrupt as e:
        speaker.cancel()

    print("SPEAKER STATUS: ", speaker.playing)


    time.sleep(1)

    f = wave.open('/home/pi/dev/example.wav', 'rb')
    channels = f.getnchannels()
    framerate = f.getframerate()
    sample_width = f.getsampwidth()
    data = bytearray()
    sample = f.readframes(256)
    while sample:
        for s in sample:
            data.append(s)
        sample = f.readframes(256)
    f.close()

    print(channels, framerate, sample_width)

    source = {
        "channels": channels,
        "framerate": framerate,
        "sample_width": sample_width,
        "data": data
    }

    print("Playing is async mode!")
    speaker.async_write(source=source)

    time.sleep(3)
    speaker.pause()
    time.sleep(2)
    speaker.pause(False)
    
    
    try:
        while speaker.playing:
            time.sleep(0.1)

    except KeyboardInterrupt as e:
        pass

    speaker.cancel() 
