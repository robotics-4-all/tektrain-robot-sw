import unittest
import time
from pidevices.sensors.microphone import Microphone
from pidevices import Speaker


class TestMicSpeak(unittest.TestCase):

    def test_one(self):
        mic = Microphone()
        speak = Speaker()
        print("Record")
        audio = mic.read(secs=5, volume=100)
        print("Playback")
        speak.write(audio, volume=55)

    def test_async_read(self):
        mic = Microphone()
        speak = Speaker()
        print("Record")
        audio = mic.async_read(secs=4, volume=100)
        time.sleep(6)
        print("Playback")
        speak.write(mic.record, volume=55)

    def test_cancel(self):
        mic = Microphone()
        speak = Speaker()
        print("Record")
        audio = mic.async_read(secs=10, volume=100)
        time.sleep(2)
        mic.cancel()
        print("Playback")
        speak.write(mic.record, volume=55)

    def test_multi_read(self):
        mic = Microphone()
        speak = Speaker()
        print("Record")
        audio = mic.async_read(secs=4, volume=100)
        time.sleep(2)
        audio = mic.read(secs=10, volume=100)
        self.assertEqual(audio, None, "Should be none")
        time.sleep(4)
        print("Playback")
        speak.write(mic.record, volume=55)

    def test_pause(self):
        mic = Microphone()
        speak = Speaker()
        print("Record")
        audio = mic.async_read(secs=6, volume=100)
        time.sleep(2)
        mic.pause()
        print("Pause")
        time.sleep(2)
        print("Continue")
        mic.pause(False)
        print("Playback")
        speak.write(mic.record, volume=55)

    def test_path(self):
        mic = Microphone()
        mic._fix_path('f')


if __name__ == "__main__":
    unittest.main()
