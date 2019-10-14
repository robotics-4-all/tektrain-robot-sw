"""mcp23017.py"""

from .mcp23x17 import MCP23x17
from sys import maxsize
import atexit
import time


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

    def poll_int(self, pin_nums, timeout=None):
        """Poll the interrupt bit for the specified pin.
        
        Args:
            pin_num (list): List with the pin number in format A_x or B_x,
                where A/B is the pin-chunk and x is the number. 
                See modules's datasheet.
            timeout (int): The time in s until stopping the polling.

        Returns:
            Boolean indicating if an interrupt occured the specified pin.
        """
        
        num_butes = 24  # How many bytes to read

        pin_nums = pin_nums if isinstance(pin_nums, list) else [pin_nums]

        self.set_seqop(1)

        bank = 1  # Bank 1 means only one register(A or B values)
        # Check if it need both registers or just one.
        prev = pin_nums[0].split('_')[0]
        for pin_num in pin_nums[1:]:
            if pin_num.split('_')[0] is not prev:
                bank = 0
                break
        self.set_bank(bank)

        # Get pin_nums and chunks
        nums_chunks = [self._get_chunk_number(pin_num) for pin_num in pin_nums]

        # Start register
        if bank:
            register = self.INTFA if nums_chunks[0][0] is 'A' else self.INTFB
        else:
            register = self.INTFA

        loc_timeout = maxsize if timeout is None else timeout  # Set timeout
        step = 1 if bank else 2
        both = step - 1  # Variable indicates if we need both registers, 0 for not

        # Init results
        results = [0 for i in pin_nums]

        # Poll register
        while True:
            t_start = time.time()
            while time.time() - t_start < loc_timeout:
                data = self.hardware_interfaces[self._i2c].read(self.address,
                                                                register,
                                                                num_butes)
                # Read for every register
                for i in range(0, num_butes, step):
                    for j, (chunk, num) in enumerate(nums_chunks):
                        index = (ord(chunk) - ord('A'))*both + i
                        value = self._get_bit(data[i], num+1)
                        results[j] = value  # TODO: Maybe be slow

                        # Break outer loop
                        loc_timeout = (value ^ 1) * loc_timeout  

            if timeout is not None or not loc_timeout:
                break

        return results

    def stop(self):
        """Free hardware and os resources."""

        if len(self.hardware_interfaces):
            self.set_bank(0)
            self.hardware_interfaces[self._i2c].close()
            del self.hardware_interfaces[self._i2c]
