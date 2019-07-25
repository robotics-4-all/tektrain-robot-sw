from .devices import Device


class MCP23x17(Device): 
    """Class representing mcp23x17 chips."""

    # Registers
    # They control the direction of pins
    IODIRA = 0x00
    IODIRB = 0x01
    IPOLA = 0x02
    IPOLB = 0x03
    GPINTENA = 0x04
    GPINTENB = 0x05
    DEFVALA = 0x06
    DEFVALB = 0x07
    INTCONA = 0x08
    INTCONB = 0x09
    IOCON = 0x0A   # This register is shared between the two ports
    GPPUA = 0x0C
    GPPUB = 0x0D
    INTFA = 0x0E
    INTFB = 0x0F
    INTCAPA = 0x10
    INTCAPB = 0x11
    # Read from GPIOn reads the value on the port, write to them causes a 
    # write to the latches OLATn
    GPIOA = 0x12
    GPIOB = 0x13
    OLATA = 0x14
    OLATB = 0x15

    _FUNCTION = {'input': 1, 'output': 0}
    _POLARITY = {'same': 0, 'reverse': 1}

    def __init__(self):
        pass

    def set_pin_dir(self, pin_num, function, chunk='A'):
        """Set pin direction

        Args:
            pin_num: The number of pin [0, 7]
            function: String representing the output of the pin. Possible values
                    are 'input' or 'output'
            chunk: From which team of pins to use. Could be 'A'
        """
        
        address = self.IODIRA if chunk is 'A' else self.IODIRB
        self._set_bit_register(address, pin_num+1, self._FUNCTION[function])

    def set_pin_pol(self, pin_num, polarity, chunk='A'):
        """Set pin polarity

        Args:
            pin_num: The number of pin [0, 7]
            Polarity: String representing the polarity of the pin. Possible values
                    are 'same' or 'reverse'
            chunk: From which team of pins to use. Could be 'A'
        """

        address = self.IPOLA if chunk is 'A' else self.IPOLB
        self._set_bit_register(address, pin_num+1, self._POLARITY[polarity])

    def set_pin_int(self, pin_num, interrupt, chunk='A'):
        """Set pin interrupt on change.

        In order to work the DEFVAL and INTCON registers must be set.

        Args:
            pin_num: The number of pin [0, 7]
            interrupt: Boolean representing the polarity of the pin.
            chunk: From which team of pins to use. Could be 'A'
        """

        address = self.GPINTENA if chunk is 'A' else self.GPINTENB
        self._set_bit_register(address, pin_num+1, int(interrupt))

    def set_pin_def_val(self, pin_num, def_val, chunk='A'):
        """Set pin default value for comparison.

        The value of each bits will be compared with the value of the associate
        pin and if they are different then an interrupt will happen.

        Args:
            pin_num: The number of pin [0, 7]
            def_val: Int representing the compare value. Should be 0 or 1.
            chunk: From which team of pins to use. Could be 'A'
        """

        address = self.DEFVALA if chunk is 'A' else self.DEFVALB
        self._set_bit_register(address, pin_num+1, def_val)

    def set_pin_intcon(self, pin_num, value, chunk='A'):
        """Set pin intcon value.

        If the corresponding pin's bit is set the the value is compared with 
        the associate bit in the DEFVAL register. Else is compared against the
        previous value.

        Args:
            pin_num: The number of pin [0, 7]
            value: Int representing the value. Should be 0 or 1.
            chunk: From which team of pins to use. Could be 'A'
        """

        address = self.INTCONA if chunk is 'A' else self.INTCONB
        self._set_bit_register(address, pin_num+1, value)
    
    def set_bank(self, value):
        """Set bank bit.

        It changes the registers mapping. Currenty it only sets it to 0.

        Args:
            value: Int represents the value.
        """

        self._set_bit_register(self.IOCON, 8, 0)

    def set_mirror(self, value):
        """Set mirror bit.

        If it is set the INTn pins are functionally OR'ed. 

        Args:
            value: Int represents the value.
        """

        self._set_bit_register(self.IOCON, 7, value)

    def set_seqop(self, value):
        """Set SEQOP bit.

        It changes the sequential operation. It is usefull for polling

        Args:
            value: Int represents the value.
        """

        self._set_bit_register(self.IOCON, 6, value)

    def set_disslw(self, value):
        """Set DISSLW bit.

        It controls the slew rate of SDA pin

        Args:
            value: Int represents the value.
        """

        self._set_bit_register(self.IOCON, 5, value)

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

    def set_intpol(self, value):
        """Set INTPOL bit.

        It sets the polarity of the INT pin.

        Args:
            value: Int represents the value.
        """

        self._set_bit_register(self.IOCON, 2, value)

    def set_pin_pull_up(self, pin_num, enabled, chunk='A'):
        """Set the pull up of a pin.

        Args:
            pin_num: The number of pin [0, 7]
            enabled: Boolean.
            chunk: From which team of pins to use. Could be 'A'
        """

        address = self.GPPUA if chunk is 'A' else self.GPPUB
        self._set_bit_register(address, pin_num+1, int(enabled))

    def get_intf(self, pin_num, chunk='A'):
        """Get the pin interrupt flag.

        It reflects if the pin caused the interrupt.
        
        Args:
            pin_num: The number of pin [0, 7]
            chunk: From which team of pins to use. Could be 'A'

        Returns:
            The flag value.
        """

        address = self.INTFA if chunk is 'A' else self.INTFB

        return self._get_bit_register(address, pin_num+1)

    def get_intcap(self, pin_num, chunk='A'):
        """Get the pin's state when the interrupt occured.

        Args:
            pin_num: The number of pin [0, 7]
            chunk: From which team of pins to use. Could be 'A'

        Returns:
            The flag value.
        """

        address = self.INTCAPA if chunk is 'A' else self.INTCAPB

        return self._get_bit_register(address, pin_num+1)

    def read(self, pin_num, chunk='A'):
        """Read the pins state.
        
        Args:
            pin_num: The number of pin [0, 7]
            chunk: From which team of pins to use. Could be 'A'
        
        Returns:
            The pin's state.
        """

        address = self.GPIOA if chunk is 'A' else self.GPIOB

        return self._get_bit_register(address, pin_num+1)

    def write(self, pin_num, value, chunk='A'):
        """Write to the pin
        
        Args:
            pin_num: The number of pin [0, 7]
            value: Int could be 0 or 1.
            chunk: From which team of pins to use. Could be 'A'
        """

        address = self.GPIOA if chunk is 'A' else self.GPIOB
        self._set_bit_register(address, pin_num+1, value)
    
    def read_olat(self, pin_num, chunk='A'):
        """Read the olat register.

        Args:
            pin_num: The number of pin [0, 7]
            chunk: From which team of pins to use. Could be 'A'
        """

        address = self.OLATA if chunk is 'A' else self.OLATB

        return self._get_bit_register(address, pin_num+1)

    def write_olat(self, pin_num, value, chunk='A'):
        """Write to the pin olat
        
        Args:
            pin_num: The number of pin [0, 7]
            value: Int could be 0 or 1.
            chunk: From which team of pins to use. Could be 'A'
        """

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

    def _get_bit_register(self, address):
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

        bit -= 1
        max_val = 2**res - 1
        mask = ((max_val << bit) | ((0x1 << bit) - 1)) & max_val
        register &= mask

        return register | (value << bit)
    
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
