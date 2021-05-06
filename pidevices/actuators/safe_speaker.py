"""speaker.py"""

from pidevices.actuators.speaker import SpeakerError, Speaker
import multiprocessing
import threading
import time

from enum import IntEnum
import queue
import random

class MsgType(IntEnum):
    Error = -1
    Ok = 0
    Write = 1
    WriteAsync = 2
    Pause = 3
    Cancel = 4
    Stop = 5


class Msg:
    MIN_ID = 0
    MAX_ID = 100000
    def __init__(self, msg_type, msg_data=None, msg_id=None):      
        self._type = msg_type
        self._data = msg_data

        random.seed(time.time())
        
        if msg_id is None:
            self._id = random.randint(Msg.MIN_ID, Msg.MAX_ID)
        else: 
            self._id = msg_id
       

    @property
    def id(self):
        return self._id

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        self._data = value

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, value):
        self._type = value

    def is_reply_of(self, other):
        if self.type == MsgType.Ok or self.type == MsgType.Error:
            if self._id == other._id:
                return True
        
        return False




class SpeakerConsumer(Speaker):
    def __init__(self, dev_name, channels, framerate, name, volume, max_data_length, parent_queue, child_queue):
        # initlaize base class constructor
        try:
            super(SpeakerConsumer, self).__init__(dev_name, volume, channels, framerate, name, max_data_length)
        except SpeakerError as e:
            print("Caught exception")
            msg = Msg(msg_type=MsgType.Error, msg_data=e)
            parent_queue.put(msg, block=True)
        else:
            msg = Msg(msg_type=MsgType.Ok)
            parent_queue.put(msg, block=True)

            print("Init succesfully")

            self._thread = threading.Thread(target=self._manage_speaker, args=(parent_queue, child_queue), daemon=True)
            self._is_alive = True
            self._data = []
            self._thread.start()

            self._read_msg(parent_queue, child_queue)
            

    def _manage_speaker(self, parent_queue, child_queue):
        print("Sub sub started")

        try:
            while self._is_alive:
                if self._data:
                    self.write(source=self._data[0], 
                                    times=self._data[1], 
                                    file_flag=self._data[2])

                    if len(self._data) == 4:
                        msg = Msg(msg_type=MsgType.Ok, msg_id=self._data[3])
                        parent_queue.put(msg, block=True)

                    self._data = []
                
                time.sleep(0.1)
                
        except SpeakerError as e:
            msg = Msg(msg_type=MsgType.Error, msg_data=e)
            parent_queue.put(msg, block=True)


    def _read_msg(self, parent_queue, child_queue):
        is_alive = True
        print("Sub sub started")

        try:
            while is_alive:
                msg = child_queue.get(block=True)

                if msg.type == MsgType.Write:
                    print("write")
                    self._data = msg.data
                    self._data.append(msg.id)

                elif msg.type == MsgType.WriteAsync:
                    print("Playing Async")
                    self._data = msg.data
                    msg.type = MsgType.Ok
                    parent_queue.put(msg, block=True)

                elif msg.type == MsgType.Pause:
                    print("Pause")
                    self.pause(enabled=msg.data[0])
                    msg.type = MsgType.Ok
                    parent_queue.put(msg, block=True)
                    
                elif msg.type == MsgType.Cancel:
                    print("Cancel")
                    self.cancel()
                    msg.type = MsgType.Ok
                    parent_queue.put(msg, block=True)

                elif msg.type == MsgType.Stop:
                    print("Stop")
                    self.stop()
                    msg.type = MsgType.Ok
                    parent_queue.put(msg, block=True)

                    is_alive = False
                    self._is_alive = False

        except SpeakerError as e:
            msg = Msg(msg_type=MsgType.Error, msg_data=e)
            parent_queue.put(msg, block=True)



# wrapper class that exposes the same API
class SafeSpeaker:
    def __init__(self, dev_name, channels, framerate, name, volume, max_data_length):
        # store initial setup values
        self._s_dev_name = dev_name
        self._s_channels = channels
        self._s_framerate = framerate
        self._s_name = name
        self._s_volume = volume
        self._s_max_data_length = max_data_length

        self._parent_queue = None
        self._child_queue = None
        self._process = None

        # internal state parameters
        self._is_init = False

    def _run_process(self, dev_name, channels, framerate, name, volume, max_data_length,
            parent_queue, child_queue):
        
        SpeakerConsumer(dev_name, channels, framerate, name, volume, max_data_length, parent_queue, child_queue)
    
    def start(self):
        while not self._is_init:
            self._parent_queue = multiprocessing.Queue()
            self._child_queue = multiprocessing.Queue()
            self.process = multiprocessing.Process(target=self._run_process, 
                                                args=(self._s_dev_name, self._s_channels, self._s_framerate,
                                                        self._s_name, self._s_volume, self._s_max_data_length,
                                                        self._parent_queue, self._child_queue),
                                                daemon=True)
            self.process.start()
            
            try:
                msg = self._parent_queue.get(block=True, timeout=0.5)
            except queue.Empty:
                print("Timout occured")
            else:
                if msg.type == MsgType.Ok:
                    print("All good")
                    self._is_init = True
                    continue
                else:
                    print(f"Error occured {msg.data}")
            
            # freeing resources
            del self._parent_queue
            del self._child_queue
            self.process.terminate()
            self.process.join()
            
            time.sleep(3)
            print("Retrying...")

    def write(self, source, times=1, file_flag=False):
        if self._is_init:
            self._check_asyn_error()

            msg = Msg(msg_type=MsgType.Write, msg_data=[source, times, file_flag])
            self._child_queue.put(msg, block=True)
            
            ret = self._parent_queue.get(block=True)

            while not ret.is_reply_of(msg): # or timeout
                print("Resending")
                self._parent_queue.put(ret, block=True)
                time.sleep(0.1)
                ret = self._parent_queue.get(block=True)

            if ret.type == MsgType.Ok:
                print("All good 2")
            else:
                print("Restarting")
                self.restart()
           


    def async_write(self, source, times=1, file_flag=False):
        if self._is_init:
            self._check_asyn_error()

            msg = Msg(msg_type=MsgType.WriteAsync, msg_data=[source, times, file_flag])
            self._child_queue.put(msg, block=True)
            
            ret = self._parent_queue.get(block=True)
            if ret.is_reply_of(msg):
                if ret.type == MsgType.Ok:
                    print("All good 2")
                else:
                    self.restart()

    def _check_asyn_error(self):
        if self._is_init:
            try:
                ret = self._parent_queue.get(block=False)
            except queue.Empty as e:
                return
            else:
                if ret.type == MsgType.Error:
                    print("Caugh async error ahaha ")
                    self.restart()
                else:
                    self._parent_queue.put(ret, block=True)


    def pause(self, enabled=True):
        if self._is_init:
            self._check_asyn_error()

            msg = Msg(msg_type=MsgType.Pause, msg_data=[enabled])
            self._child_queue.put(msg, block=True)

            ret = self._parent_queue.get(block=True)
            if ret.is_reply_of(msg):
                if ret.type == MsgType.Ok:
                    print("All good 2 pause")
                else:
                    self.restart()
    
    def cancel(self):
        if self._is_init:
            self._check_asyn_error()

            msg = Msg(msg_type=MsgType.Cancel)
            self._child_queue.put(msg, block=True)

            ret = self._parent_queue.get(block=True)
            if ret.is_reply_of(msg):
                if ret.type == MsgType.Ok:
                    print("All good 2 cancel")
                else:
                    self.restart()

    def stop(self):
        if self._is_init:
            # soft stop first (via msg)

            # hard stop
            self.process.terminate()
            self.process.join()

            del self._parent_queue
            del self._child_queue

            self._is_init = False

    def restart(self):
        self.stop()
        self.start()
