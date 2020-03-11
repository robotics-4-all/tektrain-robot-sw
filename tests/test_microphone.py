import unittest
import time
from pidevices.sensors.microphone import Microphone


class TestMicrophone(unittest.TestCase):

    def test_one(self):
        mic = Microphone(dev_name="dsnoop:CARD=Mic,DEV=0", channels=1,
                         periodsize=256)
        audio = mic.read(secs=5, volume=100, 
                         file_path="test.wav", file_flag=True)

    def test_multi(self):
        mic = Microphone()
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
        mic = Microphone()
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
