"""mcp23x17.py"""

from abc import abstractmethod, ABCMeta
from .devices import Device


class MCP23x17(Device): 
    """Class representing mcp23x17 chips.
    
    Steps for interrupts:
        - Enable interrupt on pin through GPINTEN register
        - Define which type of signal will cause the interrupt through registers
          INTCON and DEFVAL
        - When an interrupt occur the bit in INT register is set.
        - The interrupt bit remains active until the intcap register(the value
          of gpio when the interrupt occured) or the gpio register is read.
        - The first interrupt event causes the port contents to becopied into 
          the INTCAP register. Subsequent interruptconditions on the port
          will not cause an interrupt tooccur as long as the interrupt is 
          not cleared by a readof INTCAP or GPIO.
    """

    def __init__(self):
        super(MCP23x17, self).__init__(name="", max_data_length=0)
        self._set_registers(0)
    
    def _set_registers(self, bank):
        """Set the registers address."""

        # Registers
        if bank:
            # They control the direction of pins
            self.IODIRA = 0x00
            self.IODIRB = 0x10
            self.IPOLA = 0x01
            self.IPOLB = 0x11
            self.GPINTENA = 0x02
            self.GPINTENB = 0x12
            self.DEFVALA = 0x03
            self.DEFVALB = 0x13
            self.INTCONA = 0x04
            self.INTCONB = 0x14
            self.IOCON = 0x05   # This register is shared between the two ports
            self.GPPUA = 0x06
            self.GPPUB = 0x16
            self.INTFA = 0x07
            self.INTFB = 0x17
            self.INTCAPA = 0x08
            self.INTCAPB = 0x18
            # Read from GPIOn reads the value on the port, write to them causes a 
            # write to the latches OLATn
            self.GPIOA = 0x09
            self.GPIOB = 0x19
            self.OLATA = 0x0A
            self.OLATB = 0x1A
        else:
            # They control the direction of pins
            self.IODIRA = 0x00
            self.IODIRB = 0x01
            self.IPOLA = 0x02
            self.IPOLB = 0x03
            self.GPINTENA = 0x04
            self.GPINTENB = 0x05
            self.DEFVALA = 0x06
            self.DEFVALB = 0x07
            self.INTCONA = 0x08
            self.INTCONB = 0x09
            self.IOCON = 0x0A   # This register is shared between the two ports
            self.GPPUA = 0x0C
            self.GPPUB = 0x0D
            self.INTFA = 0x0E
            self.INTFB = 0x0F
            self.INTCAPA = 0x10
            self.INTCAPB = 0x11
            # Read from GPIOn reads the value on the port, write to them causes a 
            # write to the latches OLATn
            self.GPIOA = 0x12
            self.GPIOB = 0x13
            self.OLATA = 0x14
            self.OLATB = 0x15

    def _get_chunk_number(self, pin_num):
        """Split a string like "A_12" to A and 12.
        
        Args:
            pin_num (str): The pin number, it must be in the form of A_x or 
                B_x.

        Returns:
            A tuple that has the "chunk" and the number of the pin.

        Raises:
            TypeError: Error if the pin_num is not a string. Also if in A_x the
                x is not int.
            ValueError: Error when in A_x the A(thing) is not A or B and 
                if the x(ting) is not a number smaller than 8.
        """

        if not isinstance(pin_num, str):
            raise TypeError("Wrong type of pin_num, must be str.")

        # Check format of pin_num
        pin_num = pin_num.split('_')
        if len(pin_num) != 2:
            raise ValueError("Wrong format of pin_num, should be A_x or B_x")

        chunk = pin_num[0]
        if chunk != 'A' and chunk != 'B':
            raise ValueError("Wrong value of 'chunk', must be A or B")

        if pin_num[1].isnumeric():
            number = int(pin_num[1])
            if number > 7:
                raise ValueError("Wrong pin number, it must be [0, 7]")
        else:
            raise TypeError("Wrong type of A_x, x must be int")
        
        return chunk, number

    def set_pin_dir(self, pin_num, function):
        """Set pin direction

        Args:
            pin_num (str): The pin number in format A_x or B_x, where A/B is 
                the pin-chunk and x is the number. See modules's datasheet.
            function: Boolean, it could be 1 for input and 0 for output.
        """
        
        chunk, pin_num = self._get_chunk_number(pin_num)
        address = self.IODIRA if chunk is 'A' else self.IODIRB
        self._set_bit_register(address, pin_num+1, int(function))

    def get_pin_dir(self, pin_num):
        """Get pin direction

        Args:
            pin_num (str): The pin number in format A_x or B_x, where A/B is 
                the pin-chunk and x is the number. See modules's datasheet.
        """
        
        chunk, pin_num = self._get_chunk_number(pin_num)
        address = self.IODIRA if chunk is 'A' else self.IODIRB

        return self._get_bit_register(address, pin_num+1)

    def set_pin_pol(self, pin_num, polarity):
        """Set pin polarity

        Args:
            pin_num (str): The pin number in format A_x or B_x, where A/B is 
                the pin-chunk and x is the number. See modules's datasheet.
            polarity (boolean): It could be 1 for reverse and 0 for same. 
        """

        chunk, pin_num = self._get_chunk_number(pin_num)
        address = self.IPOLA if chunk is 'A' else self.IPOLB
        self._set_bit_register(address, pin_num+1, int(polarity))

    def get_pin_pol(self, pin_num):
        """Get pin polarity

        Args:
            pin_num (str): The pin number in format A_x or B_x, where A/B is 
                the pin-chunk and x is the number. See modules's datasheet.

        Returns:
            An integer indicating the polarity of the pin. 0 is for same and 
            1 for reverse.
        """

        chunk, pin_num = self._get_chunk_number(pin_num)
        address = self.IPOLA if chunk is 'A' else self.IPOLB

        return self._get_bit_register(address, pin_num+1)

    def set_pin_int(self, pin_num, interrupt):
        """Set pin interrupt on change.

        In order to work the DEFVAL and INTCON registers must be set.

        Args:
            pin_num (str): The pin number in format A_x or B_x, where A/B is 
                the pin-chunk and x is the number. See modules's datasheet.
            interrupt: Boolean representing the interrupt status of the pin.
        """

        chunk, pin_num = self._get_chunk_number(pin_num)
        address = self.GPINTENA if chunk is 'A' else self.GPINTENB
        self._set_bit_register(address, pin_num+1, int(interrupt))

    def get_pin_int(self, pin_num):
        """Get pin interrupt on change.

        In order to work the DEFVAL and INTCON registers must be set.

        Args:
            pin_num (str): The pin number in format A_x or B_x, where A/B is 
                the pin-chunk and x is the number. See modules's datasheet.

        Returns:
            An integer indicating the interrupt status of the pin.
        """

        chunk, pin_num = self._get_chunk_number(pin_num)
        address = self.GPINTENA if chunk is 'A' else self.GPINTENB

        return self._get_bit_register(address, pin_num+1)

    def set_pin_def_val(self, pin_num, def_val):
        """Set pin default value for comparison.

        The value of each bits will be compared with the value of the associate
        pin and if they are different then an interrupt will happen.

        Args:
            pin_num (str): The pin number in format A_x or B_x, where A/B is 
                the pin-chunk and x is the number. See modules's datasheet.
            def_val: Int representing the compare value. Should be 0 or 1.
        """

        chunk, pin_num = self._get_chunk_number(pin_num)
        address = self.DEFVALA if chunk is 'A' else self.DEFVALB
        self._set_bit_register(address, pin_num+1, int(def_val))

    def get_pin_def_val(self, pin_num):
        """Get pin default value for comparison.

        The value of each bits will be compared with the value of the associate
        pin and if they are different then an interrupt will happen.

        Args:
            pin_num (str): The pin number in format A_x or B_x, where A/B is 
                the pin-chunk and x is the number. See modules's datasheet.

        Returns:
            Int representing the compare value. Should be 0 or 1.
        """

        chunk, pin_num = self._get_chunk_number(pin_num)
        address = self.DEFVALA if chunk is 'A' else self.DEFVALB

        return self._get_bit_register(address, pin_num+1)

    def set_pin_intcon(self, pin_num, value):
        """Set pin intcon value.

        If the corresponding pin's bit is set the the value is compared with 
        the associate bit in the DEFVAL register. Else is compared against the
        previous value.

        Args:
            pin_num (str): The pin number in format A_x or B_x, where A/B is 
                the pin-chunk and x is the number. See modules's datasheet.
            value: Int representing the value. Should be 0 or 1.
        """

        chunk, pin_num = self._get_chunk_number(pin_num)
        address = self.INTCONA if chunk is 'A' else self.INTCONB
        self._set_bit_register(address, pin_num+1, value)
    
    def get_pin_intcon(self, pin_num):
        """Get pin intcon value.

        If the corresponding pin's bit is set the the value is compared with 
        the associate bit in the DEFVAL register. Else is compared against the
        previous value.

        Args:
            pin_num (str): The pin number in format A_x or B_x, where A/B is 
                the pin-chunk and x is the number. See modules's datasheet.

        Returns:
            Int representing the value. Should be 0 or 1.
        """

        chunk, pin_num = self._get_chunk_number(pin_num)
        address = self.INTCONA if chunk is 'A' else self.INTCONB

        return self._get_bit_register(address, pin_num+1)
    
    def set_bank(self, value):
        """Set bank bit.

        It changes the registers mapping. Currenty it only sets it to 0.

        Args:
            value: Int represents the value.
        """

        self._set_bit_register(self.IOCON, 8, value)
        self._set_registers(value)

    def get_bank(self):
        """Get bank bit.

        It changes the registers mapping. Currenty it only sets it to 0.

        Returns:
            Int represents the value.
        """

        return self._get_bit_register(self.IOCON, 8)

    def set_mirror(self, value):
        """Set mirror bit.

        If it is set the INTn pins are functionally OR'ed. 

        Args:
            value: Int represents the value.
        """

        self._set_bit_register(self.IOCON, 7, value)

    def get_mirror(self):
        """Get mirror bit.

        If it is set the INTn pins are functionally OR'ed. 

        Returns:
            Int represents the value.
        """

        return self._get_bit_register(self.IOCON, 7)

    def set_seqop(self, value):
        """Set SEQOP bit.

        It changes the sequential operation. It is usefull for polling

        Args:
            value: Int represents the value.
        """

        self._set_bit_register(self.IOCON, 6, value)

    def get_seqop(self):
        """Get SEQOP bit.

        It changes the sequential operation. It is usefull for polling

        Returns:
            Int represents the value.
        """

        return self._get_bit_register(self.IOCON, 6)

    def set_disslw(self, value):
        """Set DISSLW bit.

        It controls the slew rate of SDA pin

        Args:
            value: Int represents the value.
        """

        self._set_bit_register(self.IOCON, 5, value)

    def get_disslw(self):
        """Get DISSLW bit.

        It controls the slew rate of SDA pin

        Returns:
            Int represents the value.
        """

        return self._get_bit_register(self.IOCON, 5)

    def set_haen(self, value):
        """It is usefull only in the mcp23s17."""
        #"""Set HAEN bit.

        #If it set the hardware address is controlled from A2 A1 A0. I

        #Args:
        #    value: Int represents the value.
        #"""

        #self._set_bit_register(self.IOCON, 4, value)
        pass

    def set_odr(self, value):
        """Set ODR bit.

        It enables the int pin for open drain configuration. It overrides the 
        INTPOL bit.

        Args:
            value: Int represents the value.
        """

        self._set_bit_register(self.IOCON, 3, value)

    def get_odr(self):
        """Get ODR bit.

        It enables the int pin for open drain configuration. It overrides the 
        INTPOL bit.

        Returns:
            Int represents the value.
        """

        return self._get_bit_register(self.IOCON, 3)

    def set_intpol(self, value):
        """Set INTPOL bit.

        It sets the polarity of the INT pin.

        Args:
            value: Int represents the value.
        """

        self._set_bit_register(self.IOCON, 2, value)

    def get_intpol(self):
        """Get INTPOL bit.

        It sets the polarity of the INT pin.

        Returns:
            Int represents the value.
        """

        return self._get_bit_register(self.IOCON, 2)

    def set_pin_pull_up(self, pin_num, pull):
        """Set the pull up of a pin.

        Args:
            pin_num (str): The pin number in format A_x or B_x, where A/B is 
                the pin-chunk and x is the number. See modules's datasheet.
            pull (boolean): It could be 0 for down and 1 for up.
        """

        chunk, pin_num = self._get_chunk_number(pin_num)
        address = self.GPPUA if chunk is 'A' else self.GPPUB
        self._set_bit_register(address, pin_num+1, int(pull))

    def get_pin_pull_up(self, pin_num):
        """Get the pull up of a pin.

        Args:
            pin_num (str): The pin number in format A_x or B_x, where A/B is 
                the pin-chunk and x is the number. See modules's datasheet.

        Returns:
            Int indicating the pin pull up resistor could be 0 for down and 
            1 for up.
        """

        chunk, pin_num = self._get_chunk_number(pin_num)
        address = self.GPPUA if chunk is 'A' else self.GPPUB

        return self._get_bit_register(address, pin_num+1)

    def get_intf(self, pin_num):
        """Get the pin interrupt flag.

        It reflects if the pin caused the interrupt.
        
        Args:
            pin_num (str): The pin number in format A_x or B_x, where A/B is 
                the pin-chunk and x is the number. See modules's datasheet.

        Returns:
            The flag value.
        """

        chunk, pin_num = self._get_chunk_number(pin_num)
        address = self.INTFA if chunk is 'A' else self.INTFB

        return self._get_bit_register(address, pin_num+1)

    def get_mult_intf(self, pin_num):
        """Get the pin interrupt flag with more bytes
        
        It reflects if the pin caused the interrupt.

        Args:
            pin_num (str): The pin number in format A_x or B_x, where A/B is 
                the pin-chunk and x is the number. See modules's datasheet.

        Returns:
            A list with the flag value.
        """

        chunk, pin_num = self._get_chunk_number(pin_num)
        address = self.INTFA if chunk is 'A' else self.INTFB
        data = self._read_sequential(address, 32)
        print(data)
        data = [self._get_bit(register, pin_num+1) for register in data]

        return data

    def get_intcap(self, pin_num):
        """Get the pin's state when the interrupt occured.

        Args:
            pin_num (str): The pin number in format A_x or B_x, where A/B is 
                the pin-chunk and x is the number. See modules's datasheet.

        Returns:
            The flag value.
        """

        chunk, pin_num = self._get_chunk_number(pin_num)
        address = self.INTCAPA if chunk is 'A' else self.INTCAPB

        return self._get_bit_register(address, pin_num+1)

    def read(self, pin_num):
        """Read the pins state.
        
        Args:
            pin_num (str): The pin number in format A_x or B_x, where A/B is 
                the pin-chunk and x is the number. See modules's datasheet.
        
        Returns:
            The pin's state.
        """

        chunk, pin_num = self._get_chunk_number(pin_num)
        address = self.GPIOA if chunk is 'A' else self.GPIOB

        return self._get_bit_register(address, pin_num+1)

    def write(self, pin_num, value):
        """Write to the pin
        
        Args:
            pin_num (str): The pin number in format A_x or B_x, where A/B is 
                the pin-chunk and x is the number. See modules's datasheet.
            value: Int could be 0 or 1.
        """

        chunk, pin_num = self._get_chunk_number(pin_num)
        address = self.GPIOA if chunk is 'A' else self.GPIOB
        self._set_bit_register(address, pin_num+1, value)
    
    def read_olat(self, pin_num):
        """Read the olat register.

        Args:
            pin_num (str): The pin number in format A_x or B_x, where A/B is 
                the pin-chunk and x is the number. See modules's datasheet.
        """

        chunk, pin_num = self._get_chunk_number(pin_num)
        address = self.OLATA if chunk is 'A' else self.OLATB

        return self._get_bit_register(address, pin_num+1)

    def write_olat(self, pin_num, value):
        """Write to the pin olat
        
        Args:
            pin_num (str): The pin number in format A_x or B_x, where A/B is 
                the pin-chunk and x is the number. See modules's datasheet.
            value: Int could be 0 or 1.
        """

        chunk, pin_num = self._get_chunk_number(pin_num)
        address = self.OLATA if chunk is 'A' else self.OLATB
        self._set_bit_register(address, pin_num+1, value)
    
    def _read_interface(self, address):
        """Wrapper to interface read function."""
        pass

    def _write_interface(self, address, value):
        """Wrapper to interface write function."""
        pass

    def _set_bit_register(self, address, bit, value):
        """Set i'th bit in from register in address.

        Args:
            address:
            bit:
            value:
        """

        register = self._read_interface(address)
        register = self._set_bit(register, bit, value)
        self._write_interface(address, register)

    def _get_bit_register(self, address, bit):
        """Get i'th bit in from register in address.

        Args:
            address:
            bit:
        
        Returns:
            The i'th bit from register.
        """

        register = self._read_interface(address)
        
        return self._get_bit(register, bit)

    def _set_bit(self, register, bit, value, res=8):
        """Set value for specific bit in register in 8bit registers.

        Args:
            register: The 8 bit value.
            bit: The i'th bit to be changed. It should be 1 to res.
            value: 0 or 1.
            res: The bit resolution of the register

        Returns:
            The new value of register.
        """

        if bit < 1 or bit > res:
            # raise exception
            pass

        max_val = 2**res - 1
        mask = ((max_val << bit) | ((0x1 << (bit-1)) - 1)) & max_val
        register &= mask

        return register | (value << (bit-1))
    
    def _get_bit(self, register, bit):
        """Get the value of a specific bit from register.

        Args:
            register: The value
            bit: The i'th bit to be read. The value should be between

        Returns: 
            The value of the i'th bit of register.
        """

        if bit < 1:
            # raise exception
            pass
        bit -= 1

        return (register & (0x1 << bit)) >> bit
