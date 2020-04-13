import sys
import unittest
import time
from pidevices.actuators.speaker import Speaker


class TestSpeaker(unittest.TestCase):

    def test_one(self):
        speaker = Speaker()
        speaker.write(cmd_par, times=1, file_flag=True)

    def test_volume(self):
        speaker = Speaker()
        speaker.write(cmd_par, times=1, file_flag=True)
        time.sleep(1)

        speaker.volume = 30
        self.assertEqual(speaker.volume[0], 30, "Must be 30")
        speaker.write(cmd_par, times=1, file_flag=True)
        time.sleep(1)

        speaker.volume = 80
        speaker.write(cmd_par, times=1, file_flag=True)

    def test_async(self):
        speaker = Speaker()
        speaker.async_write(cmd_par, times=1, file_flag=True)
        time.sleep(10)

    def test_pause(self):
        speaker = Speaker()
        speaker.async_write(cmd_par, times=1, file_flag=True)
        time.sleep(2)
        speaker.pause()
        print("Pause")
        time.sleep(2)
        print("continue")
        speaker.pause(False)
        time.sleep(6)

    def test_multi(self):
        speaker = Speaker()
        speaker.async_write(cmd_par, times=1, file_flag=True)
        #time.sleep(4)
        while speaker.playing:
            #time.sleep(0.1)
            pass
        speaker.async_write(cmd_par, times=1, file_flag=True)
        while speaker.playing:
            #time.sleep(0.1)
            pass

    def test_cancel(self):
        speaker = Speaker()
        speaker.async_write(cmd_par, times=3, file_flag=True)
        time.sleep(4)
        speaker.cancel()
        #while speaker.playing:
        #    #time.sleep(0.1)
        #    pass
        speaker.async_write(cmd_par, times=1, file_flag=True)
        while speaker.playing:
            #time.sleep(0.1)
            pass

    def test_path(self):
        speaker = Speaker()
        speaker._fix_path('f')


if __name__ == "__main__":
    cmd_par = sys.argv[2]
    del sys.argv[2:]
    unittest.main()
