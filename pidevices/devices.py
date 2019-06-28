from collections import deque
from importlib import import_module


class Device(object):
    """Base class for sensors and actuators."""

    _IMPLEMENTATIONS = {
        'GPIO': ["RPiGPIO"],
        'SPI': ["SPIimplementation"],
        'UART': [],
        'I2C': ["SMBus2"],
        'HPWM': ["HPWMPeriphery"]
    }

    _MODULES = {
        'GPIO': "pidevices.hardware_interfaces.gpio_implementations",
        'SPI': "pidevices.hardware_interfaces.spi_implementations",
        'UART': None,
        'I2C': "pidevices.hardware_interfaces.i2c_implementations",
        'HPWM': "pidevices.hardware_interfaces.hpwm_implementations"
    }

    def __init__(self, name="", max_data_length=100):
        if not isinstance(name, str):
            raise TypeError("Invalid name type, should be string.")
        if not isinstance(max_data_length, int):
            raise TypeError("Invalid max_data_length type, should be integer.")

        self._id = name
        self._max_data_length = max_data_length
        self.data = deque()
        self._hardware_interfaces = []

    # TODO: see if it is better practice to remove **kwargs from the function
    # and call the constructors with no arguments.
    def init_interface(self, interface: str, impl=None, **kwargs):
        """Choose an implementation for an interface.

        Args:
            name: The interface name.
            interface: String representing the hardware interface type, it should
                     be GPIO/gpio, SPI/spi, UART/uart, I2C/i2c or HPWM/hpwm
            impl: The specific implementation to be used. If it is none the 
                 first that is installed will be used.
            **kwargs: Keyword arguments for the constructor of the chosen 
                     interface.
        Returns:
            int: Representing the interface's index in the list.
        """

        if not isinstance(interface, str):
            raise TypeError("Wrong interface type, should be string.")

        interface = interface.upper()
        if interface not in self._MODULES:
            # Raise not supported interface
            pass

        if impl is not None:
            self._hardware_interfaces.append(self._unwrap(interface,
                                                          impl,
                                                          **kwargs))
        else:
            self._hardware_interfaces.append(self._choose_def(interface, 
                                                              **kwargs))

        return len(self._hardware_interfaces) - 1

    def _choose_def(self, interface, **kwargs):
        """Choose default implementation.
        
        Iterate through the implemtations and choose the first one that is 
        installed.

        Args:
            interface: String representing the hardware interface to be 
                     initialized.
            impl: The specific implementation to be used. If it is none the 
                 first that is installed will be used.
            **kwargs: Keyword arguments for the constructor of the chosen 
                     interface.
        """

        module = import_module(self._MODULES[interface])
        for impls in self._IMPLEMENTATIONS[interface]:
            try:
                return getattr(module, impls)(**kwargs)
            except ImportError:
                continue
        # Raise library not installed
        print("Not installed")

    def _unwrap(self, interface, impl, **kwargs):
        """From string impl get the implemented class.

        Args:
            interface: String representing the hardware interface to be 
                     initialized.
            impl: The specific implementation to be used. If it is none the 
                 first that is installed will be used.
            **kwargs: Keyword arguments for the constructor of the chosen 
                     interface.
        """

        if not isinstance(impl, str):
            raise TypeError("Wrong impl type, should be str.")

        if impl not in self._IMPLEMENTATIONS[interface]:
            # raise not supported
            pass

        return getattr(import_module(self._MODULES[interface]), impl)(**kwargs)

    def update_data(self, value):
        """Insert an element to the end of the data deque."""
        if len(self.data) < self.max_data_length:
            self.data.append(value)
        else:
            _ = self.data.popleft()
            self.data.append(value)

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

    @property
    def hardware_interfaces(self):
        return self._hardware_interfaces


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
