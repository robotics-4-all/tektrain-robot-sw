import sys
import unittest
import time
from pidevices.actuators.speaker import Speaker


class TestSpeaker(unittest.TestCase):

    def test_one(self):
        speaker = Speaker()
        speaker.write(cmd_par, 85, times=1)

    def test_pause(self):
        speaker = Speaker()
        speaker.async_write('open-the-goddamn-door.wav', 15, times=6)
        time.sleep(4)
        speaker.pause()
        time.sleep(2)
        speaker.pause(False)
        time.sleep(5)

    def test_multi(self):
        speaker = Speaker()

        # In the middle of the playback change
        speaker.async_write('open-the-goddamn-door.wav', 15, times=5)
        time.sleep(5)
        speaker.write('maybe-next-time-huh.wav', 30, times=2)

        # In the end of the playback change
        speaker.async_write('open-the-goddamn-door.wav', 15, times=1)
        time.sleep(5)
        speaker.write('maybe-next-time-huh.wav', 30, times=2)

        # In the start of the playback
        speaker.async_write('open-the-goddamn-door.wav', 15, times=2)
        speaker.async_write('maybe-next-time-huh.wav', 30, times=2)
        time.sleep(5)

        # Change with pause
        speaker.async_write('open-the-goddamn-door.wav', 15, times=5)
        time.sleep(2)
        speaker.pause()
        speaker.write('maybe-next-time-huh.wav', 30, times=2)


    def test_path(self):
        speaker = Speaker()
        speaker._fix_path('f')

if __name__ == "__main__":
    cmd_par = sys.argv[2]
    del sys.argv[2:]
    unittest.main()
