import sys
import unittest
import time
from pidevices.actuators.speaker import Speaker


class TestSpeaker(unittest.TestCase):

    def test_one(self):
        speaker = Speaker(cardindex=2)
        speaker.write(cmd_par, 30, times=2)

    def test_pause(self):
        speaker = Speaker(cardindex=2)
        speaker.async_write('open-the-goddamn-door.wav', 15, times=10)
        time.sleep(4)
        speaker.pause()
        time.sleep(2)
        speaker.pause(False)
        time.sleep(13)

    def test_multi(self):
        speaker = Speaker(cardindex=2)
        speaker.async_write('open-the-goddamn-door.wav', 15, times=10)
        time.sleep(5)
        speaker.write('maybe-next-time-huh.wav', 40, times=2)
        #time.sleep(10)


    def test_path(self):
        speaker = Speaker(cardindex=2)
        speaker._fix_path('f')

if __name__ == "__main__":
    cmd_par = sys.argv[2]
    del sys.argv[2:]
    unittest.main()
