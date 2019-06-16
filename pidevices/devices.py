from collections import deque


class Device(object):
    """Abstract base class for sensors and actuators."""

    def __init__(self, name="", max_data_length=100):
        if not isinstance(name, str):
            raise TypeError("Invalid name type, should be string.")
        if not isinstance(max_data_length, int):
            raise TypeError("Invalid max_data_length type, should be integer.")

        self._id = name
        self._max_data_length = max_data_length
        self.data = deque()

    def update_data(self, value):
        """Insert an element to the end of the data deque."""
        if len(self.data) < self.max_data_length:
            self.data.append(value)
        else:
            _ = self.data.popleft()
            self.data.append(value)

    # Setters and getters

    @property
    def max_data_length(self):
        """Get max data length."""
        return self._max_data_length

    @max_data_length.setter
    def max_data_length(self, max_data_length):
        """Set max data length."""
        if not isinstance(max_data_length, int):
            raise TypeError("Invalid max_data_length type, should be integer.")
        self._max_data_length = max_data_length

    @property
    def id(self):
        """Get id."""
        return self._id

    @id.setter
    def id(self, name):
        """Set id."""
        if not isinstance(name, str):
            raise TypeError("Invalid name type, should be string.")
        self._id = name

    def start(self):
        """Empty function for starting devices, which will be
            overloaded.
        """
        pass

    def stop(self):
        """Empty function for stopping devices, which will be
            overloaded.
        """
        pass

    def restart(self):
        """Empty function for restarting devices, which will be overloaded."""
        """Function for restarting devices."""
        self.stop()
        self.start()


class Sensor(Device):

    def read(self):
        """Empty function for reading from devices, which will be
            overloaded.
        """
        pass


class Actuator(Device):
    """ Docstring for actuator class"""

    def write(self):
        """Abstact method for driving an actuator."""
        pass
