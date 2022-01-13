from pidevices.sensors.generic_microphone import PyAudioMic
from enum import IntEnum
import time

from collections import deque, Counter
from scipy.fft import fft
import numpy as np
import wave

CHANNELS = 1
FRAMERATE = 16000


class BlockState(IntEnum):
    IDLE = 0
    SPEAKING = 1


class Block:
    index = 0

    def __init__(self, data, state):
        self._data = data
        self._state = state
        self._index = Block.index

        Block.index += 1
     
    @property
    def data(self):
        return self._data
        
    def __eq__(self, other):
        if isinstance(other, int):
            if self._state == other:
                return True
            else:
                return False
        else:
            print("Not implemented!")
            
    def __str__(self):
        return f"Block = (Index: {self._index}, Data: {self._data}, State: {self._state})"


class BlockQueue(deque):
    def __init__(self, size):
        super().__init__(maxlen=size)

    @property
    def is_quite(self):
        if self.count(BlockState.SPEAKING) == 0:
            return True
        else:
            return False

    @property
    def has_speech(self):
        if self.count(BlockState.SPEAKING) >= 2:
            return True
        else:
            return False

    @property
    def size(self):
        return len(self)

    def index(self, state):
        index = 0
        for i in self:
            if i._state == state:
                break
            
            index += 1
        
        return index

    def nodrop_append(self, block):
        prev_block = None

        if len(self) == self.maxlen:
            prev_block = self.popleft()
            
        self.append(block)

        return prev_block


class VAD:
    P_SIZE = 4
    C_SIZE = 10
    BLOCK_SIZE = 1024
    SPEECH_THRESHOLD = 1
    SENTENCE_THRESHOLD = 2
    IMPORTANT_INDEXES = [8, 7, 6, 21, 22, 25, 9, 30, 29, 79, 24, 28, 27, 26, 14]

    def __init__(self):
        # queue holding previous blocks and their state
        self._previous_block = BlockQueue(size=9)
        self._current_block = BlockQueue(size=7)

        self._block_to_add = 5

        # list holding recorded block containing sound
        self._recording = bytearray()

        # sound energy threshold
        self._energy_threshold = 380

        # important frequencies of speech during training
        self._speech_important_freq = np.array(VAD.IMPORTANT_INDEXES)
        
        self._counter = 0

    def _fft(self, data):
        window = np.frombuffer(data, dtype="int16")
        window = window - np.average(window)
        weights = np.hanning(len(window))
        block_freq = np.absolute(fft(window * weights))[0:512]

        return block_freq

    def _is_speaking(self, block_freq):
        energy_level = np.average(block_freq)

        if energy_level > self._energy_threshold:
            block_important_freq = (-block_freq).argsort()[:8]
            dom_freq = np.argmax(block_freq)

            matched_freq = len(np.intersect1d(block_important_freq,
                                              self._speech_important_freq))

            if matched_freq >= 4 and (dom_freq in range(6, 39)):
                print("Speaking")
                return True

        print("Idle")
        return False

    # def _curr_block_has_speech(self):
    #     if self._current_blocks_state.count(1) >= VAD.SPEECH_THRESHOLD:
    #         return True
    #     else:
    #         return False

    # def _curr_block_has_sentences(self):
    #     if self._current_blocks_state.count(1) >= VAD.SENTENCE_THRESHOLD:
    #         return True
    #     else:
    #         return False

    def update(self, data, timestamp):
        # calculate frequencies of data block
        block_freq = self._fft(data)

        state = self._is_speaking(block_freq)
        
        block = Block(data=data, state=state)

        self._current_block.append(block)
        self._previous_block.append(block)

        if self._current_block.has_speech:
            while self._previous_block.size != 0:
                self._recording.extend(self._previous_block.popleft().data)
            
            if state == 1:
                self._block_to_add = 0
            else:
                self._block_to_add += 1
        else:
            if self._block_to_add <= 3:
                self._recording.extend(self._previous_block.pop().data)
                self._block_to_add += 1

        if not self._current_block.is_quite:
            while self._current_block.index(BlockState.SPEAKING) > 2:
                self._current_block.popleft()
            
            while self._previous_block.index(BlockState.SPEAKING) > 2:
                self._previous_block.popleft()


if __name__ == "__main__":
    mic = PyAudioMic(channels=CHANNELS,
                     framerate=FRAMERATE,
                     name="mic",
                     max_data_length=1)

    vad = VAD()

    recording = mic.async_read(secs=10, file_path="yolo2.wav", stream_cb=vad.update)
    
    while mic.recording():
        time.sleep(0.1)
    
    f = wave.open("yolo2.wav", 'wb')

    f.setnchannels(1)
    f.setframerate(FRAMERATE)
    f.setsampwidth(2)
    f.setnframes(256)

    f.writeframes(vad._recording)
    
    f.close()

    print("Recording size: ", len(vad._recording))
    mic.stop()


