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
    
    def _read_interface(self, address):
        return self.hardware_interfaces[self._i2c].read(self._address, address)

    def _write_interface(self, address, value):
        self.hardware_interfaces[self._i2c].write(self._address, address, value)

    def _poll_int(self, pin_nums):
        """Poll the interrupt bit for the specified pin.
        
        Args:
            pin_nums (list): List with the pin number in format A_x or B_x,
                where A/B is the pin-chunk and x is the number. 
                See modules's datasheet.

        Returns:
            List of integers indicating if an interrupt occured at 
            the specified pin.
        """
        
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

        # Save previous flags
        prev = [0 for i in pin_nums]

        # Poll register
        c = 0
        while True:
            data = self.hardware_interfaces[self._i2c].read(self.address,
                                                            register,
                                                            num_butes)
            print(data)
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

                    #if value:
                    #    print("INT pin {}".format(pin_nums[j]))
                    #    print(value, prev[j], value ^ prev[j])

                    #    if c < 1:
                    #        print("READ")
                    #        time.sleep(1)
                    #        self.read('A_0')
                    #        self.read('A_1')
                    #        data = self.hardware_interfaces[self._i2c].read(self.address,
                    #                                                        register,
                    #                                                        num_butes)
                    #        print(data)
                    #        sys.exit()
                    #    c += 1

                    if value and (value ^ prev[j]):
                        print("INT pin {}".format(pin_nums[j]))
                        # Create a thread with the handling function
                        threading.Thread(target=self._int_handlers[pin_nums[j]],
                                         args=()).start()
                        #self._int_handlers[pin_nums[j]]()
                        #self.read(pin_nums[j])

                    prev[j] = value

    def _int_handler(self, pin_num):
        """Handle interrupt occurences
        
        Call for every pin the handling function. In the handling function 
        check for the debounce time and clear the register.
        """
        pass
    
    def _A_0_handler(self):
        pass

    def _A_1_handler(self):
        pass

    def _A_2_handler(self):
        pass

    def _A_3_handler(self):
        pass

    def _A_4_handler(self):
        pass

    def _A_5_handler(self):
        pass

    def _A_6_handler(self):
        pass

    def _A_7_handler(self):
        pass

    def stop(self):
        """Free hardware and os resources."""

        if len(self.hardware_interfaces):
            self.set_bank(0)
            self.hardware_interfaces[self._i2c].close()
            del self.hardware_interfaces[self._i2c]
