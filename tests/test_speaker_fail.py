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
    print("Speaker started successfully")
    

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

    #speaker.write(source=path_to_file, times=2, file_flag=True, restore=True)

    # def canceler(s, t):
    #     time.sleep(t)
    #     print("Pausing")
    #     s.pause(enabled=True)

    #     time.sleep(2)
        
    #     print("Unpasing")
    #     s.pause(enabled=False)

    #     time.sleep(1)

    #     print("Canceling")
    #     s.cancel()

    # thread = threading.Thread(target=canceler, args=(speaker, 2), daemon=True)
    # thread.start()
    # speaker.write(path_to_file, file_flag=True)

    # print("Testing async")
    # resp = speaker.async_write(path_to_file, file_flag=True)
    # print(f"Sleeping for {resp['data']}")
    # time.sleep(resp["data"])


    # speaker.write(path_to_file, file_flag=True)


    # print("Stopping")
    # speaker.stop()

    resp = speaker.async_write(path_to_file, file_flag=True)
    time.sleep(resp["data"] + 0.1)

    

    speaker.write(path_to_file, file_flag=True)


    print("Finished")




