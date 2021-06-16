"""speaker.py"""

from pidevices.sensors.microphone import MicError, Microphone
import multiprocessing
import threading
import time

from collections import namedtuple
from enum import IntEnum
import queue
import random

import pathlib
import wave

class MsgMicType(IntEnum):
    Error = -1
    Ok = 0
    Record = 3
    AsyncRecord = 4
    Pause = 5
    Cancel = 6
    Stop = 7

class ResponeType(IntEnum):
    Error = -2
    Timeout = -1
    Ok = 0

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
    
    def __str__(self):
        return f"Msg id: {self.id} of type: {self.type} with data: {self.data}"
    
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
        if self.type == MsgMicType.Ok or self.type == MsgMicType.Error:
            if self._id == other._id:
                return True
        
        return False


class MicrophoneConsumer(Microphone):
    def __init__(self, dev_name, channels, name, max_data_length, parent_queue, child_queue):
        # initlaize base class constructor
        try:
            super(MicrophoneConsumer, self).__init__(dev_name, channels, name, max_data_length)
        except MicError as e:
            print("Caught exception")
            msg = Msg(msg_type=MsgMicType.Error, msg_data=e)
            parent_queue.put(msg, block=True)
        else:
            msg = Msg(msg_type=MsgMicType.Ok)
            parent_queue.put(msg, block=True)

            print("Init succesfully")

            self._thread = threading.Thread(target=self._manage_microphone, args=(parent_queue, child_queue), daemon=True)
            self._is_alive = True
            self._data = []
            self._thread.start()

            self._read_msg(parent_queue, child_queue)
            

    def _manage_microphone(self, parent_queue, child_queue): # ================== KEY ERROR FOR DICTIONARY
        try:
            while self._is_alive:
                if self._data:
                    ret = self.read(secs=self._data["secs"], 
                                    framerate=self._data["framerate"],
                                    file_flag=self._data["file_flag"],
                                    volume=self._data["volume"],     
                                    file_path=self._data["file_path"]) 
            
                    msg = Msg(msg_type=MsgMicType.Ok, msg_id=self._data["id"], msg_data=ret)
                    parent_queue.put(msg, block=True)

                    self._data = {}
                
                time.sleep(0.1)
                
        except MicError as e:
            msg = Msg(msg_type=MsgMicType.Error, 
                      msg_id=0)
            parent_queue.put(msg, block=True)

    def _read_msg(self, parent_queue, child_queue):
        is_alive = True
        
        try:
            while is_alive:
                msg = child_queue.get(block=True)

                if msg.type == MsgMicType.Record:
                    self._data = msg.data
                    self._data["id"] = msg.id

                elif msg.type == MsgMicType.AsyncRecord:
                    self._data = msg.data
                    self._data["id"] = msg.id

                    msg.type = MsgMicType.Ok
                    msg.data = {}
                    parent_queue.put(msg, block=True)

                elif msg.type == MsgMicType.Pause:
                    self.pause(enabled=msg.data["enabled"])

                    msg.type = MsgMicType.Ok
                    parent_queue.put(msg, block=True)
                    
                elif msg.type == MsgMicType.Cancel:
                    self.cancel()

                    msg.type = MsgMicType.Ok
                    parent_queue.put(msg, block=True)

                elif msg.type == MsgMicType.Stop:
                    self.stop()

                    is_alive = False
                    self._is_alive = False

                    msg.type = MsgMicType.Ok
                    parent_queue.put(msg, block=True)

        except SpeakerError as e:
            msg = Msg(msg_type=MsgMicType.Error, msg_data=e, msg_id=0)
            parent_queue.put(msg, block=True)


class Restore:
    def __init__(self, times, step, depth):
        self.times = times
        self.step = step
        self.depth = depth

# wrapper class that exposes the same API
class SafeMicrophone:
    RESTART_TIME = 3

    def __init__(self, dev_name, channels, name, max_data_length):
        # store initial setup values
        self._s_dev_name = dev_name
        self._s_channels = channels
        self._s_name = name
        self._s_max_data_length = max_data_length

        self._parent_queue = None
        self._child_queue = None
        self._process = None

        # internal state parameters
        self._is_init = False
        self._is_recording = False
        self._is_restarting = False

        self._last_async_msg = Msg(msg_type=MsgMicType.Error)
    
    @property
    def dev_name(self):
        """Alsa device name."""
        return self._s_dev_name

    @property
    def record(self):
        if self._is_init:
            if self._new_record:
                self._new_record = False
                
                return self._record

        return None

    @dev_name.setter
    def dev_name(self, dev_name):
        self._s_dev_name = dev_name

    @property
    def recording(self):
        """Flag indicating if the microphone is recording a sound"""
        if self._is_init:
            resp = self._wait_for_response(msg_req=self._last_async_msg)
            if resp["status"] == ResponeType.Error:
                print("Caught async error")
                self.restart()
            elif resp["status"] == ResponeType.Ok:
                self._is_recording = False

            return self._is_recording
            
        return False

    def _run_process(self, dev_name, channels, name, max_data_length, parent_queue, child_queue):
        
        MicrophoneConsumer(dev_name, channels, name, max_data_length, parent_queue, child_queue)
    
    def start(self):
        while not self._is_init:
            self._parent_queue = multiprocessing.Queue()
            self._child_queue = multiprocessing.Queue()
            self._last_async_msg = Msg(msg_type=MsgMicType.Ok, msg_data=None, msg_id=0)
            self.process = multiprocessing.Process(target=self._run_process, 
                                                   args=(self._s_dev_name, self._s_channels, self._s_name,
                                                         self._s_max_data_length, self._parent_queue, 
                                                         self._child_queue),
                                                   daemon=True)
            self.process.start()
            
            try:
                msg = self._parent_queue.get(block=True, timeout=0.5)
            except queue.Empty:
                print("Timout occured")
            else:
                if msg.type == MsgMicType.Ok:
                    # Re-initialize state variables

                    self._is_recording = False
                    self._is_init = True
                    continue
                else:
                    print(f"Error occured {msg.data}")
            
            # freeing resources
            del self._parent_queue
            del self._child_queue
            self.process.terminate()
            self.process.join()
            
            print(f"Retrying in {SafeMicrophone.RESTART_TIME} ...")
            time.sleep(SafeMicrophone.RESTART_TIME)
            

    def read(self, secs, framerate=44100, file_path=None, volume=100, file_flag=False):
        if self._is_init:
            resp = self._wait_for_response(msg_req=self._last_async_msg)
            if resp["status"] == ResponeType.Error:
                print("Caught async error")
                self.restart()
            elif resp["status"] == ResponeType.Ok:
                self._is_recording = False

            if self._is_recording:
                return

            self._is_recording = True

            msg_data = {
                "secs": secs,
                "framerate": framerate,
                "file_flag": file_flag,
                "file_path": file_path,
                "volume": volume
            }

            msg = Msg(msg_type=MsgMicType.Record, msg_data=msg_data)
            self._child_queue.put(msg, block=True)
            
            now =  time.time()
            resp = self._wait_for_response(msg_req=msg,
                                            block=True,
                                            timeout=(secs+2))

            if not resp["status"] == ResponeType.Ok:
                self.restart()
            
            # reset the restore state variables after a successful write
            self._is_recording = False
        
            return resp["data"]
    
    def async_read(self, secs, framerate, file_path=None, volume=100, file_flag=False):       
        if self._is_init:
            resp = self._wait_for_response(msg_req=self._last_async_msg)
            if resp["status"] == ResponeType.Error:
                print("Caught async error")
                self.restart()
            elif resp["status"] == ResponeType.Ok:
                self._is_recording = False
            
            if self._is_recording:
                return

            self._is_recording = True

            msg_data = {
                "secs": secs,
                "framerate": framerate,
                "file_flag": file_flag,
                "file_path": file_path,
                "volume": volume
            }

            msg = Msg(msg_type=MsgMicType.AsyncRecord, msg_data=msg_data)
            self._child_queue.put(msg, block=True)
            self._last_async_msg = msg
            
            resp = self._wait_for_response(msg_req=msg,
                                            block=True,
                                            timeout=0.6)

            if not resp["status"] == ResponeType.Ok:
                self.restart()
                
        return 0

    """
    Waits for a response to a msg of type "type", It also re-sends 
    not owned msgs to queue after a short random period of time
    
    Args:
        msg (Msg): msg request to which we wait a response
        type (MsgMicType): Type of response
        block (Boolean): Wait infinitely of not
        timeout (int): Time to wait for a response

    Returns:
        True if there is a valid response 
        False in case of error response of timeout (no response)
    """
    def _wait_for_response(self, msg_req, block=False, timeout=0.05):
        response = {
            "status": ResponeType.Timeout, 
            "data": None
        }

        now = time.time()
        while (time.time() - now) < timeout:
            try:
                ret = self._parent_queue.get(block=block, timeout=0.05)
            except queue.Empty as e:
                pass
            else:
                if ret.is_reply_of(msg_req):
                    if ret.type == MsgMicType.Ok:
                        print(f"Valid response {msg_req.type}")
                        response["status"] = ResponeType.Ok
                        response["data"] = ret.data

                        if msg_req.type == MsgMicType.AsyncRecord:
                            if response["data"] != None:
                                self._record = response["data"]
                                self._new_record = True

                        return response
                    else:
                        print(f"Caught error")
                        response["status"] = ResponeType.Error
                        response["data"] = ret.data
                        return response
                elif ret.id == 0 and ret.type == MsgMicType.Error:
                    response["status"] = ResponeType.Error
                    response["data"] = ret.data
                    return response
                else:
                    print("Got wrong msg, requeuing")
                    self._parent_queue.put(ret, block=True)
            
            time.sleep(random.uniform(0, 0.15))

        print("Time-out in response!")
        return response
        

    """
    Checks for an async error, then sends a pause msg to the speaker process

    Args:
        enabled (Boolean): True if we want to pause, False to unpause
    
    Restarts the process in case of an error or a delayed answer
    """
    def pause(self, enabled=True):
        if self._is_init:
            resp = self._wait_for_response(msg_req=self._last_async_msg)
            if resp["status"] == ResponeType.Error:
                print("Caught async error")
                self.restart()
                return

            msg = Msg(msg_type=MsgMicType.Pause, msg_data={"enabled":enabled})
            self._child_queue.put(msg, block=True)
            
            resp = self._wait_for_response(msg_req=msg,
                                            block=True,
                                            timeout=0.6)

            if not resp["status"] == ResponeType.Ok:
                self.restart()

    """
    Checks for an async error, then sends a cancel msg to the speaker process
    
    Restarts the process in case of an error or a delayed answer
    """
    def cancel(self):
        if self._is_init:
            resp = self._wait_for_response(msg_req=self._last_async_msg)
            if resp["status"] == ResponeType.Error:
                print("Caught async error")
                self.restart()
                return

            msg = Msg(msg_type=MsgMicType.Cancel)
            self._child_queue.put(msg, block=True)
            
            resp = self._wait_for_response(msg_req=msg,
                                            block=True,
                                            timeout=0.6)
                                            
            if not resp["status"] == ResponeType.Ok:
                self.restart()

    """
    Stops the speaker process by sending a termination msg. Then,
    it kills it violently, in case of not responding. It also resets
    the msg queues.

    """
    def stop(self):
        if self._is_init:
            # soft termination first via msg
            msg = Msg(msg_type=MsgMicType.Stop)
            self._child_queue.put(msg, block=True)
            
            resp = self._wait_for_response(msg_req=msg,
                                            block=True,
                                            timeout=0.6)
                                        
            # hard termination - force
            self.process.terminate()
            self.process.join()

            del self._parent_queue
            del self._child_queue

            self._is_init = False
            self._is_recording = False

    """
    It restarts the speaker process by calling the "stop" and "start" methods.
    It also uses a flag so as to avoid successive restarts in a multithreading env.

    """
    def restart(self):
        if not self._is_restarting:
            self._is_restarting = True
            self.stop()
            self.start()
            self._is_restarting = False
