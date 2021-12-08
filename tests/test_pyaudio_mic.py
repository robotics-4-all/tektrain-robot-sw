#!/usr/bin/env python

from pidevices.sensors.generic_microphone import PyAudioMic
import time

CHANNELS = 1
FRAMERATE = 44100


from collections import deque, Counter
from enum import Enum

from scipy.fft import fft
import numpy as np
import wave


class TrainState(Enum):
    START = 1
    QUITE = 2
    SPEECH = 3
    FINISH = 4

class VAD:
    def __init__(self):
        # recording
        self._quite = True
        self._add_after_quite = 0

        self._recording = []
        self._previous_data = deque(maxlen=4)
        self._filter = deque(maxlen=10)

        # training
        self._train_state = TrainState.FINISH
        self._energy_threshold = 0
        self._train_counter = 0
        self._important_indencies = []
        self._doms = []

        self._counter = 0

    def reset(self):
        self._recording.clear()
        self._previous_data.clear()
        self._filter.clear()

    def update_train(self, data, timestamp):
        freq = self._fft(data)
        energy_level = np.average(freq)

        if self._train_state == TrainState.START:
            self._train_quite_timer = time.time()
            self._train_counter = 0
            self._energy_threshold = 0
            self._train_state = TrainState.QUITE

            print("Train has started! Please be quite for 3 seconds")
        elif self._train_state == TrainState.QUITE:
            if (time.time() - self._train_quite_timer) < 3:
                self._energy_threshold += energy_level
                self._train_counter += 1
            else:
                self._train_state = TrainState.SPEECH

                if self._train_counter != 0:
                    self._energy_threshold /= self._train_counter
                    self._energy_threshold *= (3/2)
                    self._train_speech_timer = time.time()

                    print("Energy threshold: ", self._energy_threshold)
        elif self._train_state == TrainState.SPEECH:
            if (time.time() - self._train_speech_timer) < 10:
                if energy_level > self._energy_threshold:
                    # process sound data
                    self._filter.append(1)
                else:
                    self._filter.append(0)
                    self._previous_data.append(freq)

                if self._filter.count(1) > 4:
                    if self._quite:
                        while len(self._previous_data) > 0:
                            self._recording.append(self._previous_data.popleft())

                        self._recording.append(freq)
                        self._add_after_quite = 0
                    else:
                        self._recording.append(freq)

                    print("Speaking")
                else:
                    if self._add_after_quite < 4:
                        self._add_after_quite += 1
                        self._recording.append(freq)
                        print("Speaking")
                    else:
                        self._previous_data.append(freq)
                        print("idle")

                    self._quite = True
            else:
                print("Processing")

                self._train_state = TrainState.FINISH

                data_length = len(self._recording)
                freq_of_freq = np.zeros(1024)
                doms = []

                for t in self._recording:
                    important_indecies = (-t).argsort()[:15]
                    doms.append(np.argmax(t))

                    for i in important_indecies:
                        freq_of_freq[i] += 1

                self._important_freq_index = (-freq_of_freq).argsort()[:15]

                counter = Counter(doms)
                print(counter.most_common(10))

                for i in counter.most_common(10):
                    self._doms.append(i[0])

                print("Ref: ", self._important_freq_index)

    def _is_speaking(self, freq):
        energy_level = np.average(freq)

        if energy_level > self._energy_threshold:
            important_indecies = (-freq).argsort()[:7]

            dom = np.argmax(freq)

            matched = len(np.intersect1d(important_indecies, self._important_freq_index))

            print(matched, dom)

            if matched >= 3 and (dom > 5 and dom <= 38):
                return True

        return False

    def update(self, data, timestamp):
        freq = self._fft(data)

        if self._is_speaking(freq):
            # process sound data
            self._filter.append(1)
            print("Speaking", self._counter)
            self._counter += 1

        else:
            self._filter.append(0)
            self._previous_data.append(freq)
            # print("idle")

        if self._filter.count(1) > 4:
            if self._quite:
                while len(self._previous_data) > 0:
                    self._recording.append(self._previous_data.popleft())

                self._recording.append(freq)
                self._add_after_quite = 0
            else:
                self._recording.append(freq)

            # print("Speaking")
        else:
            if self._add_after_quite < 4:
                self._add_after_quite += 1
                self._recording.append(freq)
                # print("Speaking")
            else:
                self._previous_data.append(freq)
                # print("idle")

            self._quite = True

    def _fft(self, data):
        window = np.frombuffer(data, dtype="int16")
        window = window - np.average(window)
        weights = np.hanning(len(window))
        freq = np.absolute(fft(window * weights))[0:512]

        return freq

    def train(self):
        self._train_state = TrainState.START


    def get(self):
        pass


if __name__ == "__main__":
    mic = PyAudioMic(channels=CHANNELS,
                     framerate=FRAMERATE,
                     name="mic",
                     max_data_length=1)

    # vad = VAD()

    # vad.train()

    # recording = mic.async_read(duration=15, file_path="yolo.wav", stream_cb=vad.update_train)

    # while mic.recording():
    #     time.sleep(0.1)

    # time.sleep(1)

    # vad.reset()

    recording = mic.async_read(secs=3, file_path="yolo.wav")

    while mic.recording():
        time.sleep(0.1)


    f = wave.open("yolo2.wav", 'wb')

    f.setnchannels(1)
    f.setframerate(44100)
    f.setsampwidth(2)
    f.setnframes(256)

    #for sample in audio:
    f.writeframes(mic.record)

    f.close()



    mic.stop()
