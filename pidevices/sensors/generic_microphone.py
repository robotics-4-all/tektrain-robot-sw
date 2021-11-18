"""microphone.py"""

import time
import wave
import os
import sys
import threading
import warnings
from ..devices import Sensor
import pyaudio


class GenericMicrophone(Sensor):
    ''' 
        Generic Microphone API
    '''
    CHUNK = 1024
    
    def __init__(self, channels, framerate, sample_width, name="", max_data_length=0):
        
        super(GenericMicrophone, self).__init__(name, max_data_length)

        # setting up device & configuration parameters
        self._device = None
        self._channels = channels
        self._framerate = framerate
        self._sample_width = sample_width

        # state control variables
        self._thread = None
        self._recording = threading.Lock()
        self._cancelled = threading.Event()
        self._paused = threading.Event()

        self.start()

    def start(self):
        self._start_device()
        
    def stop(self):
        self._stop_device()

    def recording(self):
        return self._recording.locked()

    def read(self, duration=3, file_path=None):
        self._recording.acquire() 

        # reset cancel & pause flag
        self._cancelled.clear()
        self._paused.clear()

        record = bytearray()
        t_start = time.time()
        while (time.time() - t_start) < duration and (not self._cancelled.is_set()):
            data = self._read_device()
            
            if data is not None:
                record.extend(data)
            else:
                break

            # wait untill unpaused while checking the cancelling flag
            if self._paused.is_set():
                recorded_time = time.time() - t_start
                duration -= recorded_time

                while self._paused.is_set():
                    if self._cancelled.is_set():
                        break
                    time.sleep(0.05)

                t_start = time.time()
        
        self._recording.release()       # to handle already unlocked ecxeption
        self._cancelled.clear()
        self._paused.clear()
       
        if file_path is not None:        # to check if file path exist
            self._save_to_file(file_path, record)

        return record

    def async_read(self, duration=3, file_path=None):
        self._thread = threading.Thread(target=self.read,
                                        args=(duration, file_path),
                                        daemon=True)

        self._thread.start()

    def pause(self, enabled=True):
        if enabled:
            self._paused.set()
        else:
            self._paused.clear()

    def cancel(self):
        self._cancelled.set()

    def _save_to_file(self, file_path, recordings):
        try:
            # Open the wav file
            f = wave.open(file_path, 'wb')

            f.setnchannels(self._channels)
            f.setframerate(self._framerate)
            f.setsampwidth(self._sample_width)
            f.setnframes(self.CHUNK)

            #for sample in audio:
            f.writeframes(recordings)
            
            f.close()
        except wave.Error as e:
            print("Error writing wav file")

    ''' 
        Implementors
    '''
    def _start_device(self):
        pass
    
    def _stop_device(self):
        pass

    def _read_device(self):
        pass

class PyAudioMic(GenericMicrophone):
    FORMAT = pyaudio.paInt16

    def __init__(self, channels, framerate, name="", max_data_length=0):        
        self._audio = pyaudio.PyAudio()

        sample_width = self._audio.get_sample_size(format=PyAudioMic.FORMAT)

        super(PyAudioMic, self).__init__(channels, framerate, sample_width, name, max_data_length)
    
    def _start_device(self):
        self._device = self._audio.open(format=PyAudioMic.FORMAT,
                                        channels=self._channels,
                                        rate=self._framerate,
                                        input=True,
                                        frames_per_buffer=PyAudioMic.CHUNK)
        
        self._device.start_stream()

    def _stop_device(self):
        if self._device is not None:
            self._device.stop_stream()
            self._device.close()

        self._audio.terminate()

    def _read_device(self):
        data = None
        if self._device is not None:
            try:
                data = self._device.read(PyAudioMic.CHUNK)
            except Exception as e:
                print(e)
                
        return data

