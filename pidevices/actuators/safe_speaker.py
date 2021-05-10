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
    AsyncWrite = 2
    Pause = 3
    Cancel = 4
    Stop = 5

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
                                file_flag=self._data[2],
                                rs_times=self._data[3],
                                rs_step=self._data[4])

                    
                    msg = Msg(msg_type=MsgType.Ok, msg_id=self._data[5])
                    parent_queue.put(msg, block=True)

                    self._data = []
                
                time.sleep(0.1)
                
        except SpeakerError as e:
            msg = Msg(msg_type=MsgType.Error, msg_data=[self._curr_times, self._curr_step], msg_id=0)
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

                elif msg.type == MsgType.AsyncWrite:
                    print("Playing Async")
                    self._data = msg.data
                    self._data.append(msg.id)
                    while self._duration is None:
                        time.sleep(0.1)
                    msg.type = MsgType.Ok
                    msg.data = self._duration
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
            msg = Msg(msg_type=MsgType.Error, msg_data=e, msg_id=0)
            parent_queue.put(msg, block=True)


# wrapper class that exposes the same API
class SafeSpeaker:
    MAX_RESTORE_DEPTH = 3

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

        self._restored_step = 0
        self._restored_times = 0
        self._restore_depth = 0

    def _run_process(self, dev_name, channels, framerate, name, volume, max_data_length,
            parent_queue, child_queue):
        
        SpeakerConsumer(dev_name, channels, framerate, name, volume, max_data_length, parent_queue, child_queue)
    
    def start(self):
        while not self._is_init:
            self._last_async_msg = Msg(msg_type=MsgType.Ok, msg_data=None, msg_id=0)
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
                    self._restore_depth = 0
                    self._restored_step = 0
                    self._restored_times = 0
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
            
            time.sleep(3)
            print("Retrying...")

    def write(self, source, times=1, file_flag=False, restore=False):
        if self._is_init:
            resp = self._wait_for_response(msg_req=self._last_async_msg)
            if resp["status"] == ResponeType.Error:
                print("Caught async error")
                self.restart()
            elif resp["status"] == ResponeType.Ok:
                self._is_playing = False

            if self._is_playing:
                return
            
            self._is_playing = True

            msg_data = [source, times, file_flag]

            if restore == True:
                if self._restored_times != 0 or self._restored_step != 0:
                    msg_data.append(self._restored_times)
                    msg_data.append(self._restored_step)
            else:
                msg_data.append(0)
                msg_data.append(0)
                
            print(f"msg data: {msg_data}")
            msg = Msg(msg_type=MsgType.Write, msg_data=msg_data)
            self._child_queue.put(msg, block=True)
            
            resp = self._wait_for_response(msg_req=msg,
                                            block=True,
                                            timeout=60)

            if not resp["status"] == ResponeType.Ok:
                self.restart()

                if restore == True and self._restore_depth < SafeSpeaker.MAX_RESTORE_DEPTH:
                    self._restore_depth += 1
                    self._restored_times = resp["data"][0]      # more safe check size etc
                    self._restored_step = resp["data"][1]
                    print(f"Restoring {self._restored_times}/{self._restored_step}")
                    self.write(source, times, file_flag, True)
                    
            
            # reset these after a successful write
            self._restored_step = 0
            self._restored_times = 0
            self._restore_depth = 0
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

            self._is_playing = True

            msg_data = [source, times, file_flag, 0, 0]
            msg = Msg(msg_type=MsgType.AsyncWrite, msg_data=msg_data)
            self._child_queue.put(msg, block=True)
            self._last_async_msg = msg
            
            resp = self._wait_for_response(msg_req=msg,
                                            block=True,
                                            timeout=0.6)

            if not resp["status"] == ResponeType.Ok:
                self.restart()

            return resp
    
    """
    Waits for a response to a msg of type "type", It also re-sends 
    not owned msgs to queue after a short random period of time
    
    Args:
        msg (Msg): msg request to which we wait a response
        type (MsgType): Type of response
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
                print("Time-out in response!")
                pass
            else:
                if ret.is_reply_of(msg_req):
                    if ret.type == MsgType.Ok:
                        print(f"All good {msg_req.type}")
                        response["status"] = ResponeType.Ok
                        response["data"] = ret.data
                        return response
                    else:
                        print(f"Caught error")
                        response["status"] = ResponeType.Error
                        response["data"] = ret.data
                        return response
                elif ret.id == 0 and ret.type == MsgType.Error:
                    response["status"] = ResponeType.Error
                    response["data"] = ret.data
                    return response
                else:
                    print("Got wrong msg, requeuing")
                    self._parent_queue.put(ret, block=True)
            
            time.sleep(random.uniform(0, 0.1))

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

            msg = Msg(msg_type=MsgType.Pause, msg_data=[enabled])
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

            msg = Msg(msg_type=MsgType.Cancel)
            self._child_queue.put(msg, block=True)
            
            resp = self._wait_for_response(msg_req=msg,
                                            block=True,
                                            timeout=0.6)
                                            
            if not resp["status"] == ResponeType.Ok:
                self.restart()

    """
    Stops the speaker process by sending a termination msg. If not responding,
    it kills it violently. It also reset the msg queues.

    """
    def stop(self):
        if self._is_init:
            # soft stop first (via msg)
            
            # hard stop
            self.process.terminate()
            self.process.join()

            del self._parent_queue
            del self._child_queue

            self._is_init = False

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


# add is playing flag  - 2 ack msgs in 
# make code prettier
# document
# add volume control

