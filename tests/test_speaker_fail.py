from pidevices.actuators.speaker import Speaker
from pidevices.actuators.safe_speaker import SafeSpeaker

import time
import sys
import os


import threading
import multiprocessing
from alsaaudio import ALSAAudioError
import random

# from enum import IntEnum
# class MsgType(IntEnum):
#     ERROR = -1
#     REQ = 0
#     REP = 1


# class Msg:
#     MIN_ID = 0
#     MAX_ID = 100000
#     def __init__(self, msg_data, msg_type, msg_id=None):
#         random.seed(time.time())
        
#         if msg_id is None:
#             self._id = random.randint(Msg.MIN_ID, Msg.MAX_ID)
#         else: 
#             self._id = msg_id
        
#         self._data = msg_data
#         self._type = msg_type

#     @property
#     def id(self):
#         return self._id

#     @property
#     def data(self):
#         return self._data

#     @ property
#     def type(self):
#         return self._type

#     def is_reply(self, other):
#         if self.type == MsgType.REQ:
#             if other.type == MsgType.REP or other.type == MsgType.ERROR:
#                 if self._id == other._id:
#                     return True
        
#         return False
        
        




# class SafeSpeakerConsumer(Speaker):
#     def __init__(self, dev_name, channels, framerate, name, volume, max_data_length, parent_queue, child_queue):
#         # initlaize base class constructor
#         super(SafeSpeakerConsumer, self).__init__(dev_name, volume, channels, framerate, name, max_data_length)

#         # set communication module
#         self._thread = threading.Thread(target=self._run, args=(parent_queue, child_queue), daemon=True)
#         self._thread.start()
#         print("Consumer ok")

#     def _run(self, parent_queue, child_queue):
#         msg = Msg(msg_data=["ok"], msg_type=MsgType.REP)
#         parent_queue.put(msg, block=True)
#         print("Thread ok: ")

#         is_alive = True
        
#         # here happens all the communication
#         while is_alive:
#             msg = child_queue.get(block=True)
#             print("Executing: ", msg)

#             if msg.data[0] == "write":
#                 rep = Msg(msg_data=["ok"], msg_type=MsgType.REP, msg_id=msg.id)
#                 parent_queue.put(rep)

#             time.sleep(0.1)




# class SafeSpeaker:
#     ACK = 1
#     NACK = -1
#     def __init__(self, dev_name, channels, framerate, name, volume, max_data_length):
#         # store initial setup values
#         self._s_dev_name = dev_name
#         self._s_channels = channels
#         self._s_framerate = framerate
#         self._s_name = name
#         self._s_volume = volume
#         self._s_max_data_length = max_data_length

#         # initialize read and write queue
#         self.parent_queue = multiprocessing.Queue()
#         self.child_queue = multiprocessing.Queue()
#         self.process = None

#         # state variables
#         self._is_init = False

#         self.start()
    
#     def start(self):
#         # create a process to run the mic
#         self._is_init = False

#         while not self._is_init:
#             self.process = multiprocessing.Process(target=self._run_process, args=(), daemon=True)
#             self.process.start()

#             msg = self.parent_queue.get(block=True)
#             print("Got answer: ", msg)

#             if msg.data[0] == "ok":
#                 self._is_init = True

#             print("Start all good")


#     def _run_process(self, dev_name, channels, framerate, name, volume, max_data_length,
#             parent_queue, child_queue):
#         # initialize module that handles speaker and communication


#     def write(self, source, times=1, file_flag=False):
#         msg = Msg(msg_data=["write"], msg_type=MsgType.REQ)
#         self.child_queue.put(msg)

#         rep = self.parent_queue.get(block=True)
#         if msg.is_reply(rep):
#             print("Success yeaaaaaaaa {msg.data}")

#     def async_write(self, source, times=1, file_flag=False):
#         self.child_queue.put("async")

#     def pause(self):
#         self.child_queue.put("pause")
    
#     def cancel(self):
#         self.child_queue.put("cancel")

#     def stop(self):
#         if self._is_init:
#             self.process.terminate()
#             self.process.join()

#     def restart(self):
#         self.stop()
#         self.start()






        













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

    speaker.write(path_to_file, file_flag=True)

    speaker.stop()
















# def run_speaker_to_fail():
#     speaker = Speaker(dev_name = "Speaker",
#                       channels = 1,
#                       framerate = 44100,
#                       name = "Speaker Device",
#                       volume = 50)

#     if len(sys.argv) != 2:
#         print("Wrong number of arguments! Require exactly one.")
#         speaker.stop()
#         sys.exit(-1)

#     path_to_file = sys.argv[1]

#     if not os.path.isfile(path_to_file):
#         print("Invalid path! File does not exist.")
#         speaker.stop()
#         sys.exit(-2)

#     print(f"Now playing file {path_to_file}")

#     speaker.volume = 60

#     speaker.async_write(source = path_to_file, 
#                                   times = 1,
#                                   file_flag = True)

#     now = time.time()
#     while (time.time() - now) < 5:
#         if speaker.error == 1:
#             print("fuck")
            
#             break
#         time.sleep(0.2)

#     print("Finished playing. Bye!")
