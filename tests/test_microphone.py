import unittest
import time
from pidevices.sensors.microphone import Microphone


class TestMicrophone(unittest.TestCase):

    def test_one(self):
        mic = Microphone()
        mic.read(file_path='test.wav', secs=4, volume=100)

    def test_write(self):
        mic = Microphone()
        mic.write('open-the-goddamn-door.wav', 15, loop=True)
        c = 0
        while True:
            time.sleep(0.2)
            c += 1
            #print("sleep")
            if c is 10 :
                mic.pause()
            if c is 20 :
                #mic.pause(False)
                mic.write('maybe-next-time-huh.wav', 40, loop=True)
            if c is 30:
                break

    def test_multi(self):
        mic = Microphone()
        mic.write('open-the-goddamn-door.wav', 30, loop=True)
        c = 0
        while True:
            time.sleep(0.2)
            c += 1
            if c is 20:
                mic.write('maybe-next-time-huh.wav', 40, loop=True)
            if c is 30:
                break


    def test_path(self):
        mic = Microphone()
        mic._fix_path('f')

if __name__ == "__main__":
    unittest.main()
