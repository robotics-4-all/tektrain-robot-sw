from collections import deque
from importlib import import_module


class Device(object):
    """Base class for sensors and actuators."""

    _IMPLEMENTATIONS = {
        'GPIO': ["RPiGPIO"],
        'SPI': ["SPIimplementation"],
        'UART': [],
        'I2C': [],
        'HPWM': ["HPWMPeriphery"]
    }

    _MODULES = {
        'GPIO': "pidevices.gpio_implementations",
        'SPI': "pidevices.spi_implementations",
        'UART': None,
        'I2C': None,
        'HPWM': "pidevices.hpwm_implementations"
    }

    def __init__(self, name="", max_data_length=100):
        if not isinstance(name, str):
            raise TypeError("Invalid name type, should be string.")
        if not isinstance(max_data_length, int):
            raise TypeError("Invalid max_data_length type, should be integer.")

        self._id = name
        self._max_data_length = max_data_length
        self.data = deque()
        self._hardware_interfaces = {
            'GPIO': None,
            'SPI': None,
            'UART': None,
            'I2C': None,
            'HPWM': None,
        }

    # TODO: see if it is better practice to remove **kwargs from the function
    # and call the constructors with no arguments.
    def init_interface(self, interface: str, impl=None, **kwargs):
        """Choose an implementation for an interface.

        Args:
            interface: String representing the hardware interface to be 
                     initialized.
            impl: The specific implementation to be used. If it is none the 
                 first that is installed will be used.
            **kwargs: Keyword arguments for the constructor of the chosen 
                     interface.
        """

        if not isinstance(interface, str):
            raise TypeError("Wrong interface type, should be string.")

        interface = interface.upper()
        if interface not in self._hardware_interfaces:
            # Raise not supported interface
            pass

        if impl is not None:
            self._hardware_interfaces[interface] = self._unwrap(interface,
                                                                impl,
                                                                **kwargs)
        else:
            self._hardware_interfaces[interface] = self._choose_def(interface,
                                                                    **kwargs)

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
    def gpio(self):
        """Get GPIO instance."""
        return self._hardware_interfaces["GPIO"]

    @property
    def spi(self):
        """Get SPI instance."""
        return self._hardware_interfaces["SPI"]

    @property
    def uart(self):
        """Get UART instance."""
        return self._hardware_interfaces["UART"]

    @property
    def i2c(self):
        """Get I2C instance."""
        return self._hardware_interfaces["I2C"]

    @property
    def hpwm(self):
        """Get HPWM instance."""
        return self._hardware_interfaces["HPWM"]


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
