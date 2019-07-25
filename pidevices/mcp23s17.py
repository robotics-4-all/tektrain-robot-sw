from .mcp23x17 import MCP23x17


class MCP23017(MCP23x17):
    """Class representing mcp23017 chip"""

    def __init__(self, port, device):
        """Constructor."""

        self._port = port
        self._device = device
        #self._address = address
        self.start()

    def start(self):
        """Init hardware and os resources."""

        self._spi = self.init_interface('spi',
                                        port=self._port,
                                        device=self._device)
    
    def read(self, address):
        pass

    def write(self, address, value):
        pass
