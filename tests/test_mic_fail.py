from pidevices.sensors.microphone import Microphone
from pidevices.sensors.safe_microphone import SafeMicrophone

import time
import sys
import os
import threading


if __name__ == "__main__":
    microphone = SafeMicrophone(dev_name = "Mic",
                                channels = 1,
                                name = "Microphone Device",
                                max_data_length=0)

    time.sleep(3)
    
    microphone.start()
    print("Recording normal")

    ret = microphone.read(secs=1, framerate=44100, file_path="giorgos.wav", file_flag=False, volume=100)

    print("sizeof data: ", len(ret))

    time.sleep(1)

    print("Recording async")
    
    ret = microphone.async_read(secs=0.5, framerate=44100, file_path="giorgos.wav", file_flag=False, volume=100)
    
    microphone.pause(enabled=True)
    time.sleep(4)
    microphone.pause(enabled=False)

    while microphone.recording:
        time.sleep(0.1)
        
    print("sizeof data: ", microphone.record)

    microphone.stop()



    
    print("Finished")




