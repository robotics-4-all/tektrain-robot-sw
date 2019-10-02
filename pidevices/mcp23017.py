"""mcp23017.py"""

from .mcp23x17 import MCP23x17


class MCP23017(MCP23x17):
    """Class representing mcp23017 chip"""

    def __init__(self, bus, address):
        """Constructor."""

        self._bus = bus
        self._address = address
        self.start()

    def start(self):
        """Init hardware and os resources."""

        self._i2c = self.init_interface('i2c', bus=self._bus)
    
    def read(self, address):
        return self.hardware_interfaces[self._i2c].read(self._address, address)

    def write(self, address, value):
        self.hardware_interfaces[self._i2c].write(self._address, address, value)
