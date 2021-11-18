#!/usr/bin/env python

from pidevices.sensors.generic_microphone import PyAudioMic
import time

CHANNELS = 1
FRAMERATE = 16000

if __name__ == "__main__":
    mic = PyAudioMic(channels=CHANNELS,
                     framerate=FRAMERATE,
                     name="mic",
                     max_data_length=1)

    recording = mic.async_read(duration=5, file_path="yolo.wav")

    time.sleep(2)

    mic.pause()

    time.sleep(2)
    mic.cancel()
    mic.pause(False)

    while mic.recording():
        time.sleep(0.1)

    print("Finished")

    mic.stop()
