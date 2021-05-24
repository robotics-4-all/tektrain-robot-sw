import unittest
import time
from pidevices.sensors.microphone import Microphone


class TestMicrophone(unittest.TestCase):
    DEV_NAME = "Mic"
    CHANNELS = 6
    FRAMERATE = 44100

    def test_one(self):
        mic = Microphone(dev_name=self.DEV_NAME, channels=self.CHANNELS)
        
        audio = mic.read(secs=5, framerate=self.FRAMERATE, volume=100, 
                         file_path="test.wav", file_flag=True)

    def test_multi(self):
        mic = Microphone(dev_name=self.DEV_NAME, channels=self.CHANNELS)
        mic.async_read(file_path='test_one.wav', secs=4, volume=100)
        time.sleep(3)
        mic.read(file_path='test_two.wav', secs=2, volume=100)

        # Test if it is paused
        mic.async_read(file_path='test_one_p.wav', secs=4, volume=100)
        time.sleep(2)
        mic.pause()
        print("Pause")
        time.sleep(1)
        mic.read(file_path='test_two.wav', secs=2, volume=100)

    def test_pause(self):
        mic = Microphone(dev_name=self.DEV_NAME, channels=self.CHANNELS)
        mic.async_read(file_path='test.wav', secs=6, volume=100)
        time.sleep(2)
        mic.pause()
        print("Pause")
        time.sleep(1)
        print("Restart")
        mic.pause(False)
        time.sleep(6)

    def test_path(self):
        mic = Microphone()
        mic._fix_path('f')

if __name__ == "__main__":
    unittest.main()
