"""camera.py"""
import time
import atexit
from threading import Thread, Event, Lock
from io import BytesIO
from collections import namedtuple, deque
from picamera import PiCamera
from .devices import Sensor


# Dimensions tuple
Dims = namedtuple('Dims', ['width', 'height'])

# Camera data tuple
CameraData = namedtuple('CameraData', ['frame', 'timestamp'])


class TimeStampedStream(BytesIO):
    """A BytesIO with a timestamp."""

    def write(self, s):
        """Write the output and the timestamp."""
        super(TimeStampedStream, self).write(s)
        self.timestamp = time.time()


class Camera(Sensor):
    """Camera driver."""

    def __init__(self,
                 name="",
                 max_data_length=20,
                 framerate=30,
                 resolution=Dims(width=640, height=480)):
        """Constructor of a Camera object."""
        # Init name and max data length.
        atexit.register(self.stop)
        super(Camera, self).__init__(name, max_data_length)

        # Init instance's attributes.
        self._framerate = framerate
        self._resolution = resolution
        self.start()

    def start(self):
        """Initialize os resources."""
        self._camera = PiCamera()
        self._camera.framerate = self.framerate
        self._camera.resolution = self.resolution

        # Init an event for thread communication
        self._thread_event = Event()

        # Allow module to settle
        time.sleep(1)

    def stop(self):
        """Free os resources."""
        # Clear the flag to stop
        self.thread_event.clear()

        # Wait until the flag is set again
        self.thread_event.wait(0.2)

        # Close the camera object
        self.camera.close()

    # For formats that are raw we need to know the collumns of the image
    def read(self, batch=1, image_dims=None, image_format='rgb', SAVE=True):
        """Take a batch frames from camera.

           Arguments:
           batch -- the number of frames to capture
           image_dims -- a dims tuple or a simple tuple with width, height
                         values
           image_format -- the image image_format
           SAVE -- flag for appending the stream to the data deque

           Return:
           A deque with CameraData objects.
        """
        # Initialize frame buffers.
        raw_captures = [TimeStampedStream() for i in range(batch)]

        # Capture the frames
        self.camera.capture_sequence(raw_captures, resize=image_dims,
                                     format=image_format, use_video_port=True)

        # Make a deque with the frames and the timestamps
        frames = deque()
        for capture in raw_captures:
            frames.append(CameraData(frame=capture.getvalue(),
                                     timestamp=capture.timestamp))
            capture.close()

        # Append frame to data
        if SAVE:
            for frame in frames:
                self.update_data(frame)

        return frames

    def read_continuous_async(self, batch=1, image_dims=None, image_format='rgb'):
        """Run a thread for continuous capturing"""
        # Initialize the frame buffers
        raw_captures = [TimeStampedStream() for i in range(batch)]

        while self.thread_event.is_set():
            # Capture the frames
            self.camera.capture_sequence(raw_captures,
                                         resize=image_dims,
                                         format=image_format,
                                         use_video_port=True)

            # Append data to deque
            for capture in raw_captures:
                self.update_data(CameraData(frame=capture.getvalue(),
                                            timestamp=capture.timestamp))

                # Empty the stream
                capture.truncate(0)
                capture.seek(0)

        # Clean up
        for capture in raw_captures:
            capture.close()

        # Set the thread event for synchronization
        self.thread_event.set()

    def read_continuous(self, batch=1, image_dims=None, image_format='rgb'):
        """Start the thread for reading continuous"""
        thread = Thread(target=self.read_continuous_async,
                        args=(batch, image_dims, image_format, ))
        self.thread_event.set()
        thread.start()

        # Give time to start
        time.sleep(1)

    def stop_continuous(self):
        """Stop the running thread."""
        # Clear the flag to stop
        self.thread_event.clear()

        # Wait until the flag is set again
        self.thread_event.wait()

    def get_frame(self):
        """Return the last frame captured"""
        return self.data[-1]

    # Setters and getters

    @property
    def resolution(self):
        """Get camera's resolution."""
        return self._resolution

    @resolution.setter
    def resolution(self, resolution):
        """Set camera's resolution."""
        self._resolution = resolution

    @property
    def framerate(self):
        """Get camera's framerate."""
        return self._framerate

    @framerate.setter
    def framerate(self, framerate):
        """Set camera's framerate."""
        self._framerate = framerate

    @property
    def camera(self):
        """Get camera object."""
        return self._camera

    @property
    def thread_event(self):
        """Get event object."""
        return self._thread_event
