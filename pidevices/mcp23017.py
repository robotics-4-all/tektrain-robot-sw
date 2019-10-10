"""mcp23017.py"""

from .mcp23x17 import MCP23x17
import atexit


class MCP23017(MCP23x17):
    """Class representing mcp23017 chip
    
    Args:
        bus (int): The i2c bus
        address (int): The hardware defined address of the module.
    """

    def __init__(self, bus, address):
        """Constructor."""

        atexit.register(self.stop)
        super(MCP23017, self).__init__()
        self._bus = bus
        self._address = address
        self.start()

    @property
    def bus(self):
        """The i2c bus."""
        return self._bus

    @bus.setter
    def bus(self, value):
        self._bus = value

    @property
    def address(self):
        """The address of the module. First it must be defined by hardware."""
        return self._address
    
    @address.setter
    def address(self, value):
        self._address = value

    def start(self):
        """Init hardware and os resources."""

        self._i2c = self.init_interface('i2c', bus=self._bus)
    
    def _read_interface(self, address):
        return self.hardware_interfaces[self._i2c].read(self._address, address)

    def _write_interface(self, address, value):
        self.hardware_interfaces[self._i2c].write(self._address, address, value)

    def stop(self):
        """Free hardware and os resources."""

        if len(self.hardware_interfaces):
            self.set_bank(0)
            self.hardware_interfaces[self._i2c].close()
            del self.hardware_interfaces[self._i2c]
