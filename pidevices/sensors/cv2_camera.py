import time
import atexit

from io import BytesIO
from threading import Thread, Event, Lock
from collections import namedtuple, deque

import cv2
import imutils

from pidevices.sensors import Sensor
import numpy as np

# Dimensions tuple
Dims = namedtuple('Dims', ['width', 'height'])

# Camera data tuple
CameraData = namedtuple('CameraData', ['frame', 'timestamp'])


class VirtualCameraError(Exception):
    def __init__(self, vdevice, message="Error in virtual Camera"):
        self._vdevice = vdevice
        self._message = message
        super().__init__(self._message)

    def __str__(self):
        return f'{self._vdevice} -> {self._message}'

class VirtualCameraUnavailable(VirtualCameraError):
    pass

class VirtualCameraReadError(VirtualCameraError):
    pass

class VirtualCameraConvertionError(VirtualCameraError):
    pass

class VirtualCamera(Sensor):
    def __init__(self, 
                 vdevice = 1,
                 framerate = 30,
                 resolution = Dims(width = 640, 
                                   height = 480),
                 name = "", 
                 max_data_length = 10):

        atexit.register(self.stop)
        super(VirtualCamera, self).__init__(name, max_data_length)

        self._vdevice = vdevice
        self._framerate = framerate
        self._resolution = resolution

        self._vcamera = None
        self._thread = None
        self._thread_event = Event()

        self.start()

    def start(self):
        self._vcamera = cv2.VideoCapture(self._vdevice)
        self._vcamera.set(cv2.CAP_PROP_FPS, self._framerate)
        print(self._vcamera.get(cv2.CAP_PROP_FPS))

        if not self._vcamera.isOpened():
            raise VirtualCameraUnavailable(self._vdevice,
                "Error opening virtual camera device!")

    def read(self, image_dims = None, image_format = 'jpg', save = False):
        retval, frame = self._vcamera.read()

        if not retval:
            raise VirtualCameraReadError(self._vdevice, 
                "Error reading from virtual camera device!")

        _width = self._resolution.width
        _height = self._resolution.height
        if image_dims is not None:
            _width = image_dims.width
            _height = image_dims.height

        # convert to appropriate resolution
        frame = imutils.resize(frame, width = _width , height = _height)

        self._shape = frame.shape

        # convert to appropriate format
        retval, image = cv2.imencode(f".{image_format}", frame)
        

        if not retval:
            raise VirtualCameraConvertionError(self._vdevice, 
                f"Error converting frame array to image format {image_format}")


        image = cv2.imdecode(image, cv2.IMREAD_COLOR)

        # convert to bytes
        self._shape = image.shape
        image_bytes = image.tobytes()

        image_array = np.frombuffer(image_bytes, dtype = image.dtype)
        image_array.reshape(self._shape)

        camera_data = CameraData(frame = image,
                                 timestamp = time.time())
        
        if save:
            self.update_data(camera_data)

        return camera_data

    def _read_continuous_async(self, image_dims = None, image_format = "jpg"):
        while self._thread_event.is_set():
            try:
                self.read(image_dims, image_format, True)
            except Exception as e:
                # kill self
                self._thread_event.clear()
            
    def read_continuous(self, image_dims = None, image_format = "jpg"):
        self._thread = Thread(target = self._read_continuous_async,
                              args = (image_dims, image_format))

        self._thread_event.set()
        self._thread.start()

        time.sleep(1)
    
    def stop(self):
        """Free hardware and os resources."""
        # Clear the flag to stop
        self.stop_continuous()

        # Close the camera object
        self._vcamera.release()

    def stop_continuous(self):
        """Stop the running thread."""
        # Clear the flag to stop
        self._thread_event.clear()

        # Wait until the flag is set again
        if self._thread is not None:
            self._thread.join()

    def get_frame(self):
        """Return the last frame captured"""
        return self.data[-1]

