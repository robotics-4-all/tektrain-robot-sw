"""speaker.py"""

from pidevices.actuators.speaker import SpeakerError, Speaker
import multiprocessing
import threading
import time

from collections import namedtuple
from enum import IntEnum
import queue
import random

import pathlib
import wave

class MsgSpeakerType(IntEnum):
    Error = -1
    Ok = 0
    Volume = 1
    Framerate = 2
    Write = 3
    AsyncWrite = 4
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
        if self.type == MsgSpeakerType.Ok or self.type == MsgSpeakerType.Error:
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
            msg = Msg(msg_type=MsgSpeakerType.Error, msg_data=e)
            parent_queue.put(msg, block=True)
        else:
            msg = Msg(msg_type=MsgSpeakerType.Ok)
            parent_queue.put(msg, block=True)

            print("Init succesfully")

            self._thread = threading.Thread(target=self._manage_speaker, args=(parent_queue, child_queue), daemon=True)
            self._is_alive = True
            self._data = []
            self._thread.start()

            self._read_msg(parent_queue, child_queue)
            

    def _manage_speaker(self, parent_queue, child_queue): # ================== KEY ERROR FOR DICTIONARY
        try:
            while self._is_alive:
                if self._data:
                    self.write(source=self._data["source"], 
                                times=self._data["times"], 
                                file_flag=self._data["file_flag"],
                                rs_times=self._data["restored_times"],
                                rs_step=self._data["restored_step"])      
            
                    msg = Msg(msg_type=MsgSpeakerType.Ok, msg_id=self._data["id"])
                    parent_queue.put(msg, block=True)

                    self._data = {}
                
                time.sleep(0.1)
                
        except SpeakerError as e:
            msg = Msg(msg_type=MsgSpeakerType.Error, 
                      msg_data={"times_to_restore": self._curr_times,
                                "step_to_restore": self._curr_step},
                      msg_id=0)
            parent_queue.put(msg, block=True)

    def _read_msg(self, parent_queue, child_queue):
        is_alive = True
        
        try:
            while is_alive:
                msg = child_queue.get(block=True)

                if msg.type == MsgSpeakerType.Write:
                    self._data = msg.data
                    self._data["id"] = msg.id

                elif msg.type == MsgSpeakerType.AsyncWrite:
                    self._data = msg.data
                    self._data["id"] = msg.id

                    while self._duration is None:
                        time.sleep(0.1)
                    
                    msg.type = MsgSpeakerType.Ok
                    msg.data = {"duration": self._duration}
                    parent_queue.put(msg, block=True)
                
                elif msg.type == MsgSpeakerType.Volume:
                    self.volume = msg.data["volume"]

                    msg.type = MsgSpeakerType.Ok
                    parent_queue.put(msg, block=True)
                
                elif msg.type == MsgSpeakerType.Framerate:
                    self.framerate = msg.data["framerate"]

                    msg.type = MsgSpeakerType.Ok
                    parent_queue.put(msg, block=True)

                elif msg.type == MsgSpeakerType.Pause:
                    self.pause(enabled=msg.data["enabled"])

                    msg.type = MsgSpeakerType.Ok
                    parent_queue.put(msg, block=True)
                    
                elif msg.type == MsgSpeakerType.Cancel:
                    self.cancel()

                    msg.type = MsgSpeakerType.Ok
                    parent_queue.put(msg, block=True)

                elif msg.type == MsgSpeakerType.Stop:
                    self.stop()

                    is_alive = False
                    self._is_alive = False

                    msg.type = MsgSpeakerType.Ok
                    parent_queue.put(msg, block=True)

        except SpeakerError as e:
            msg = Msg(msg_type=MsgSpeakerType.Error, msg_data=e, msg_id=0)
            parent_queue.put(msg, block=True)


class Restore:
    def __init__(self, times, step, depth):
        self.times = times
        self.step = step
        self.depth = depth

# wrapper class that exposes the same API
class SafeSpeaker:
    RESTART_TIME = 3
    MAX_RESTORE_DEPTH = 3
    FRAMERATES = [8000, 16000, 44100, 48000, 96000]

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
        self._is_playing = False
        self._is_restarting = False

        self._restore_values = Restore(times=0, step=0, depth=0)
    
    @property
    def dev_name(self):
        """Alsa device name."""
        return self._s_dev_name

    @dev_name.setter
    def dev_name(self, dev_name):
        self._s_dev_name = dev_name

    @property
    def playing(self):
        """Flag indicating if the speaker is playing a sound"""
        if self._is_init:
            resp = self._wait_for_response(msg_req=self._last_async_msg)
            if resp["status"] == ResponeType.Error:
                print("Caught async error")
                self.restart()
            elif resp["status"] == ResponeType.Ok:
                self._is_playing = False

            return self._is_playing
            
        return False
    
    @property
    def volume(self):
        """The volume of the mixer if it exists."""
        return self._s_volume

    @volume.setter
    def volume(self, value):
        if self._is_init:
            self._s_volume = min(max(0, value), 100)

            resp = self._wait_for_response(msg_req=self._last_async_msg)
            if resp["status"] == ResponeType.Error:
                self.restart()
                return

            for i in range(SafeSpeaker.MAX_RESTORE_DEPTH):
                msg = Msg(msg_type=MsgSpeakerType.Volume, msg_data={"volume": self._s_volume})
                self._child_queue.put(msg, block=True)

                resp = self._wait_for_response(msg_req=msg,
                                                block=True,
                                                timeout=0.3)

                if not resp["status"] == ResponeType.Ok:
                    self.restart()
                else:
                    return

    @property
    def framerate(self):
        return self._s_framerate

    @framerate.setter
    def framerate(self, value):
        if self._is_init:
            if value in SafeSpeaker.FRAMERATES:
                self._s_framerate = value
            else:
                self._s_framerate = Speaker.FRAMERATES[2]

            resp = self._wait_for_response(msg_req=self._last_async_msg)
            if resp["status"] == ResponeType.Error:
                self.restart()
                return

            for i in range(SafeSpeaker.MAX_RESTORE_DEPTH):
                msg = Msg(msg_type=MsgSpeakerType.Framerate, msg_data={"framerate": self._s_framerate})
                self._child_queue.put(msg, block=True)

                resp = self._wait_for_response(msg_req=msg,
                                                block=True,
                                                timeout=0.3)

                if not resp["status"] == ResponeType.Ok:
                    self.restart()
                else:
                    return

    def _run_process(self, dev_name, channels, framerate, name, volume, max_data_length,
            parent_queue, child_queue):
        
        SpeakerConsumer(dev_name, channels, framerate, name, volume, max_data_length, parent_queue, child_queue)
    
    def start(self):
        while not self._is_init:
            self._parent_queue = multiprocessing.Queue()
            self._child_queue = multiprocessing.Queue()
            self._last_async_msg = Msg(msg_type=MsgSpeakerType.Ok, msg_data=None, msg_id=0)
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
                if msg.type == MsgSpeakerType.Ok:
                    # Re-initialize state variables
                    self._restore_values.times = 0
                    self._restore_values.step = 0
                    self._restore_values.depth = 0

                    self._is_playing = False
                    self._is_init = True
                    continue
                else:
                    print(f"Error occured {msg.data}")
            
            # freeing resources
            del self._parent_queue
            del self._child_queue
            self.process.terminate()
            self.process.join()
            
            print(f"Retrying in {SafeSpeaker.RESTART_TIME} ...")
            time.sleep(SafeSpeaker.RESTART_TIME)
            

    def write(self, source, times=1, file_flag=False, restore=False, timeout=60):
        if self._is_init:
            resp = self._wait_for_response(msg_req=self._last_async_msg)
            if resp["status"] == ResponeType.Error:
                print("Caught async error")
                self.restart()
            elif resp["status"] == ResponeType.Ok:
                self._is_playing = False

            if self._is_playing:
                return

            if not self._is_source_valid(source, file_flag):
                return

            self._is_playing = True

            msg_data = {
                "source": source,
                "times": times,
                "file_flag": file_flag,
                "restored_times": self._restored_times,
                "restored_step": self._restored_step
            }

            msg = Msg(msg_type=MsgSpeakerType.Write, msg_data=msg_data)
            self._child_queue.put(msg, block=True)
            
            now =  time.time()
            resp = self._wait_for_response(msg_req=msg,
                                            block=True,
                                            timeout=timeout)

            if not resp["status"] == ResponeType.Ok:
                dt = time.time() - now
                self.restart()

                if restore == True and self._restore_depth < SafeSpeaker.MAX_RESTORE_DEPTH:
                    self._restore_values.depth += 1

                    try:
                        self._restore_values.times = resp["data"]["times_to_restore"]
                        self._restore_values.step = resp["data"]["step_to_restore"]
                    except KeyError as e:
                        print("Exception in write: ", e)
                        self._restore_values.times = 0
                        self._restore_values.step = 0

                    # reduce time-out in each recursion   
                    new_timeout = timeout - dt
                    if new_timeout > 0:
                        self.write(source, times, file_flag, True, new_timeout)  
            
            # reset the restore state variables after a successful write
            self._restore_values.depth = 0
            self._restore_values.times = 0
            self._restore_values.step = 0

            self._is_playing = False
    
    def async_write(self, source, times=1, file_flag=False):        
        if self._is_init:
            resp = self._wait_for_response(msg_req=self._last_async_msg)
            if resp["status"] == ResponeType.Error:
                print("Caught async error")
                self.restart()
            elif resp["status"] == ResponeType.Ok:
                self._is_playing = False
            
            if self._is_playing:
                return

            if not self._is_source_valid(source, file_flag):
                return

            self._is_playing = True

            msg_data = {
                "source": source,
                "times": times,
                "file_flag": file_flag,
                "restored_times": 0,
                "restored_step": 0
            }

            for i in range(SafeSpeaker.MAX_RESTORE_DEPTH):

                msg = Msg(msg_type=MsgSpeakerType.AsyncWrite, msg_data=msg_data)
                self._child_queue.put(msg, block=True)
                self._last_async_msg = msg
                
                resp = self._wait_for_response(msg_req=msg,
                                                block=True,
                                                timeout=0.6)

                if not resp["status"] == ResponeType.Ok:
                    self.restart()
                else:
                    try:
                        return resp["data"]["duration"]
                    except KeyError as e:
                        print("Exception in asyn write: ", e)
                        return 0
        return 0
    
    def _is_source_valid(self, source, file_flag):
        if file_flag:
            file = pathlib.Path(source)
            if file.exists():
                return True
            else:
                return False
        else:
            return True
    
    """
    Waits for a response to a msg of type "type", It also re-sends 
    not owned msgs to queue after a short random period of time
    
    Args:
        msg (Msg): msg request to which we wait a response
        type (MsgSpeakerType): Type of response
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
                    if ret.type == MsgSpeakerType.Ok:
                        print(f"Valid response {msg_req.type}")
                        response["status"] = ResponeType.Ok
                        response["data"] = ret.data
                        return response
                    else:
                        print(f"Caught error")
                        response["status"] = ResponeType.Error
                        response["data"] = ret.data
                        return response
                elif ret.id == 0 and ret.type == MsgSpeakerType.Error:
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

            msg = Msg(msg_type=MsgSpeakerType.Pause, msg_data={"enabled":enabled})
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

            msg = Msg(msg_type=MsgSpeakerType.Cancel)
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
            msg = Msg(msg_type=MsgSpeakerType.Stop)
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
            self._is_playing = False

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
