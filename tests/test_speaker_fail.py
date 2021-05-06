from pidevices.actuators.speaker import Speaker
from pidevices.actuators.safe_speaker import SafeSpeaker

import time
import sys
import os
import threading



if __name__ == "__main__":
    speaker = SafeSpeaker(dev_name = "Speaker",
                            channels = 1,
                            framerate = 44100,
                            name = "Speaker Device",
                            volume = 50,
                            max_data_length=0)
    
    speaker.start()

    print("Started all good")
    

    if len(sys.argv) != 2:
        print("Wrong number of arguments! Require exactly one.")
        speaker.stop()
        sys.exit(-1)

    path_to_file = sys.argv[1]

    if not os.path.isfile(path_to_file):
        print("Invalid path! File does not exist.")
        speaker.stop()
        sys.exit(-2)

    
    time.sleep(2)

    

    def canceler(s):
        time.sleep(2)
        s.cancel()

    thread = threading.Thread(target=canceler, args=(speaker,), daemon=True)
    thread.start()

    speaker.write(path_to_file, file_flag=True)


    speaker.stop()




