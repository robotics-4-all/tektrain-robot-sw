from collections import deque
from importlib import import_module
from .exceptions import NotSupportedInterface, NotInstalledInterface


class Device(object):
    """Base class for sensors and actuators.
    
    Attributes:
        data: A deque that saves the latest measurments or commands.

    """

    """ Dictionary with the implemented implementations for every 
    hardware interface.
    """
    _IMPLEMENTATIONS = {
        'GPIO': ["RPiGPIO"],
        'SPI': ["SPIimplementation"],
        'UART': [],
        'I2C': ["SMBus2"],
        'HPWM': ["HPWMPeriphery"]
    }

    # Dictionary with implementation modules.
    _MODULES = {
        'GPIO': "pidevices.hardware_interfaces.gpio_implementations",
        'SPI': "pidevices.hardware_interfaces.spi_implementations",
        'UART': None,
        'I2C': "pidevices.hardware_interfaces.i2c_implementations",
        'HPWM': "pidevices.hardware_interfaces.hpwm_implementations"
    }

    def __init__(self, name="", max_data_length=100):
        """Constructor of the class.
        
        Args:
            name (str): The optional name of the device.
            max_dat_length (int): The max length of the data deque.
        """

        if not isinstance(name, str):
            raise TypeError("Invalid name type, should be string.")
        if not isinstance(max_data_length, int):
            raise TypeError("Invalid max_data_length type, should be integer.")

        self._id = name
        self._max_data_length = max_data_length
        self.data = deque()

        # A list with the hardware interfaces objects.
        self._hardware_interfaces = []  

    # TODO: see if it is better practice to remove **kwargs from the function
    # and call the constructors with no arguments.
    def init_interface(self, interface: str, impl=None, **kwargs):
        """Choose an implementation for an interface.

        Args:
            interface: String representing the hardware interface type,
                it should be GPIO-gpio, SPI-spi, UART-uart, I2C-i2c or HPWM-hpwm.
            impl: The specific implementation to be used. If it is none the 
                first that is installed will be used.
            **kwargs: Keyword arguments for the constructor of the chosen 
                interface.

        Returns:
            int: Representing the interface's index in the list.

        Raises:
            TypeError: Wrong interface type.

            NotSupportedInterface: An error occured accessing modules.

            NotInstalledInterface: An error occured when there isn't any 
                supported library installed for the current interface.

        """

        if not isinstance(interface, str):
            raise TypeError("Wrong interface type, should be string.")

        interface = interface.upper()
        if interface not in self._MODULES:
            raise NotSupportedInterface("{} is invalid name "
                                        "for interface.".format(interface))

        module = import_module(self._MODULES[interface])
        obj = None
        if impl is not None:
            obj = getattr(module, impl)(**kwargs)
        else:
            for impls in self._IMPLEMENTATIONS[interface]:
                try:
                    obj = getattr(module, impls)(**kwargs)
                except ImportError:
                    continue

            if obj is None:
                # Raise not installed error.
                raise NotInstalledInterface("A supported library in not found"
                                            " for the {}"
                                            " interface".format(interface))

        self._hardware_interfaces.append(obj)

        return len(self._hardware_interfaces) - 1

    def update_data(self, value):
        """Insert an element to the end of the data deque."""
        if len(self.data) < self.max_data_length:
            self.data.append(value)
        else:
            _ = self.data.popleft()
            self.data.append(value)

    def start(self):
        """Empty function for starting devices, which will be overloaded."""
        pass

    def stop(self):
        """Empty function for stopping devices, which will be overloaded."""
        pass

    def restart(self):
        """Empty function for restarting devices, which will be overloaded."""
        self.stop()
        self.start()

    @property
    def max_data_length(self):
        """The max length of the data deque."""
        return self._max_data_length

    @max_data_length.setter
    def max_data_length(self, max_data_length):
        """Set max data length."""
        if not isinstance(max_data_length, int):
            raise TypeError("Invalid max_data_length type, should be integer.")
        self._max_data_length = max_data_length

    @property
    def id(self):
        """The name of the device."""
        return self._id

    @id.setter
    def id(self, name):
        """Set id."""
        if not isinstance(name, str):
            raise TypeError("Invalid name type, should be string.")
        self._id = name

    @property
    def hardware_interfaces(self):
        """A list with the objects of the device's used hardware interfaces."""
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


class Composite(Device):
    """ Docstring for composite class"""

    def write(self):
        """Abstact method for driving and reading from a composite device."""
        pass
