import sys
import unittest
import time
from pidevices.actuators.speaker import Speaker


class TestSpeaker(unittest.TestCase):

    def test_one(self):
        speaker = Speaker()
        speaker.write(cmd_par, 80, times=1, file_flag=True)

    def test_async(self):
        speaker = Speaker()
        speaker.async_write(cmd_par, 10, times=1, file_flag=True)
        time.sleep(10)

    def test_pause(self):
        speaker = Speaker()
        speaker.async_write(cmd_par, 10, times=1, file_flag=True)
        time.sleep(2)
        speaker.pause()
        print("Pause")
        time.sleep(2)
        print("continue")
        speaker.pause(False)
        time.sleep(6)

    def test_multi(self):
        speaker = Speaker()
        speaker.async_write(cmd_par, 10, times=1, file_flag=True)
        time.sleep(2)
        speaker.async_write(cmd_par, 10, times=1, file_flag=True)
        time.sleep(5)

    def test_path(self):
        speaker = Speaker()
        speaker._fix_path('f')


if __name__ == "__main__":
    cmd_par = sys.argv[2]
    del sys.argv[2:]
    unittest.main()
