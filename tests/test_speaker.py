import unittest
import time
from pidevices.actuators.speaker import Speaker


class TestSpeaker(unittest.TestCase):

    def test_write(self):
        speaker = Speaker()
        speaker.write('open-the-goddamn-door.wav', 40, loop=True)
        while True:
            time.sleep(0.2)
            print("sleep")


    def test_path(self):
        speaker = Speaker()
        speaker._fix_path('f')

if __name__ == "__main__":
    unittest.main()
