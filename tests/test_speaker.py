import unittest
import time
from pidevices.actuators.speaker import Speaker


class TestSpeaker(unittest.TestCase):

    def test_write(self):
        speaker = Speaker()
        speaker.write('open-the-goddamn-door.wav', 40, loop=True)
        c = 0
        while True:
            time.sleep(0.2)
            c += 1
            print("sleep")
            if c is 10 :
                speaker.pause()
            if c is 20 :
                speaker.pause(False)
            if c is 30:
                break


    def test_path(self):
        speaker = Speaker()
        speaker._fix_path('f')

if __name__ == "__main__":
    unittest.main()
