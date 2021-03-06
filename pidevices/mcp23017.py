"""mcp23017.py"""

from .mcp23x17 import MCP23x17
from sys import maxsize
import sys
import atexit
import time
import threading


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
        self.clear_ints()
    
    def _read_interface(self, address):
        return self.hardware_interfaces[self._i2c].read(self._address, address)

    def _write_interface(self, address, value):
        self.hardware_interfaces[self._i2c].write(self._address, address, value)

    def clear_ints(self):
        """Disable interrupts on every pin."""
        self.hardware_interfaces[self._i2c].write(self._address,
                                                  self.GPINTENA,
                                                  0)
        self.hardware_interfaces[self._i2c].write(self._address,
                                                  self.GPINTENB,
                                                  0)

    def poll_int(self, pin_nums):
        """Poll the interrupt bit for the specified pin.
        
        Args:
            pin_nums (list): List with the pin number in format A_x or B_x,
                where A/B is the pin-chunk and x is the number. 
                See modules's datasheet.

        Returns:
            List of integers indicating if an interrupt occured at 
            the specified pin.
        """
        
        self._poll_flag = True
        self._poll_end = False

        num_butes = 25  # How many bytes to read

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

        step = 1 if bank else 2
        both = step - 1  # Variable indicates if we need both registers, 0 for not

        # Poll register
        while self._poll_flag:
            data = self.hardware_interfaces[self._i2c].read(self.address,
                                                            register,
                                                            num_butes)
            # Or all the values in order to not having to skip a 1 after finding
            # it. For example if the byte 2 is 01... then until byte 23 it would
            # be 01 and will have to call it again.
            for d, d_ in zip(data[::step], data[1::step]):
                data[0] |= d
                data[1] |= d_
            
            for i in range(0, step, step):
                # Read for every register
                for j, (chunk, num) in enumerate(nums_chunks):
                    index = (ord(chunk) - ord('A'))*both + i    

                    value = self._get_bit(data[index], num+1)

                    #if chunk is 'A' and num is 0:
                    #    print("Num {} and value {}".format(num, value))
                    if value: 
                        # Create a thread with the handling function
                        threading.Thread(target=self._int_handlers[pin_nums[j]],
                                         args=()).start()

        self.set_seqop(0)
        self.set_bank(0)
        self._poll_end = True

    def wait_pin_for_edge(self, pin_num, timeout=None):
        """Wait for an edge signal on a pin.
        
        Args:
            pin_num (str): The pin number in format A_x or B_x,
                where A/B is the pin-chunk and x is the number. 
            timeout (int): The time of waiting in ms. If it is none will wait 
                until the edge signal occur. Defaults to :data:`None`.

        Return:
            An integer indicating if the interrupt occured.
        """

        # Enable interrupts
        self.set_pin_int(pin_num, 1)

        self.set_seqop(1)
        self.set_bank(1)

        chunk, pin_num = self._get_chunk_number(pin_num)
        address = self.INTFA if chunk is 'A' else self.INTFB

        num_butes = 24

        # Use timeout
        if timeout is None:
            timeout = maxsize
        else:
            timeout /= 1000

        iter_flag = 0
        t_s = time.time()
        while (not iter_flag) and (time.time() - t_s < timeout):
            data = self.hardware_interfaces[self._i2c].read(self.address,
                                                            address,
                                                            num_butes)
            for d in data:
                iter_flag = self._get_bit(d, pin_num+1)

        val = 1
        while val:
            data = self.hardware_interfaces[self._i2c].read(self.address,
                                                            address,
                                                            num_butes)
            for d in data:
                val = self._get_bit(d, pin_num+1)
                self.read(chunk + "_" + str(pin_num))

        # Disable interrupts
        self.set_pin_int(chunk + "_" + str(pin_num), 0)

        self.set_seqop(0)
        self.set_bank(0)

        return iter_flag

    def stop(self):
        """Free hardware and os resources."""

        self.stop_poll_int_async()

        if len(self.hardware_interfaces):
            self.set_seqop(0)
            self.set_bank(0)
            self.hardware_interfaces[self._i2c].close()
            del self.hardware_interfaces[self._i2c]
