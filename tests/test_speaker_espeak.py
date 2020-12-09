import unittest
import time
from espeakng import ESpeakNG
from pidevices import Speaker


class TestSpeakerEspeak(unittest.TestCase):

    def test_one(self):
        esng = ESpeakNG()
        esng.voice = 'en'
        esng.speed = 10
        esng.pitch = 50
        path = "/home/pi/new_infrastructure/tektrain-robot-sw/wav_sounds/test.wav"
        esng._espeak_exe(["Test now", "-w", path], sync=True)
        #print(audio)

        speak = Speaker()
        speak.write("/home/pi/new_infrastructure/tektrain-robot-sw/wav_sounds/test.wav", file_flag=True)


if __name__ == "__main__":
    unittest.main()
