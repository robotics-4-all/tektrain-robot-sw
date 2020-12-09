import sys
import unittest
import time
from pidevices.actuators.speaker import Speaker
import threading

class TestSpeaker(unittest.TestCase):
    # def test_one(self):
    #     print("Test one")
    #     speaker = Speaker()
    #     speaker.write(cmd_par, times=1, file_flag=True)
    #     speaker.stop()

    # def test_many(self):
    #     print("Test many")
    #     speaker = Speaker()
    #     speaker.write(cmd_par, times=3, file_flag=True)
    #     speaker.stop()

    # def test_volume(self):
    #     print("Test volume")
    #     speaker = Speaker()
    #     speaker.write(cmd_par, times=1, file_flag=True)
    #     time.sleep(1)

    #     speaker.volume = 30
    #     self.assertEqual(speaker.volume[0], 30, "Must be 30")
    #     speaker.write(cmd_par, times=1, file_flag=True)
    #     time.sleep(1)

    #     speaker.volume = 80
    #     speaker.write(cmd_par, times=1, file_flag=True)
    #     speaker.stop()

    # def test_async(self):
    #     print("Test async")
    #     speaker = Speaker()
    #     speaker.async_write(cmd_par, times=1, file_flag=True)
    #     time.sleep(3)
    #     speaker.stop()

    # def test_pause(self):
    #     print("test pause")
    #     speaker = Speaker()
    #     speaker.async_write(cmd_par, times=1, file_flag=True)
        
    #     time.sleep(5)
    #     speaker.pause()
    #     print("Pause")
    #     time.sleep(2)
    #     print("Unpause")
    #     speaker.pause(False)
    #     time.sleep(4)
    #     speaker.stop()

    def test_cancel(self):
        print("test cancel")
        speaker = Speaker()
        speaker.async_write(cmd_par, times=1, file_flag=True)
        
        time.sleep(5)

        print("pause pressed")
        #speaker.pause()
        print("cancel pressed")
        speaker.cancel()
        
        # time.sleep(4)
        # speaker.async_write(cmd_par, times=1, file_flag=True)

        # time.sleep(2)

        # speaker.cancel()
        time.sleep(3)

        speaker.stop()



    # def test_multi(self):
    #     speaker = Speaker()
    #     speaker.async_write(cmd_par, times=1, file_flag=True)
    #     #time.sleep(4)
    #     while speaker.playing:
    #         #time.sleep(0.1)
    #         pass
    #     speaker.async_write(cmd_par, times=1, file_flag=True)
    #     while speaker.playing:
    #         #time.sleep(0.1)
    #         pass

    # def test_cancel(self):
    #     speaker = Speaker()
    #     speaker.async_write(cmd_par, times=1, file_flag=True)
    #     time.sleep(5)
    #     speaker.pause()
    #     time.sleep(2)
    #     speaker.pause(False)
    #     time.sleep(2)
    #     speaker.cancel()
    #     # speaker.async_write(cmd_par, times=1, file_flag=True)
    #     while speaker.playing:
    #         time.sleep(0.1)
    #         pass
    #     speaker.stop()


if __name__ == "__main__":
    cmd_par = "/home/pi/new_infrastructure/tektrain-robot-sw/wav_sounds/file_example_WAV_1MG.wav"
    #cmd_par = "/home/pi/new_infrastructure/tektrain-robot-sw/wav_sounds/english_sentence.wav"

    # speaker = Speaker()
    # speaker.volume = 70

    # speaker.write(cmd_par, times=1, file_flag=True)
    
    

    # print(f"Given: {cmd_par}")
    # del sys.argv[2:]
    unittest.main()
