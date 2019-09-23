"""i2c_implementations.py"""

from .hardware_interfaces import I2C

try:
    from smbus2 import SMBus, i2c_msg
except ImportError:
    SMBus = None


class SMBus2(I2C):
    """Wrapper for smbus2 library extends :class:`I2C`
    
    Args:
        bus (int): The i2c bus of the raspberry pi. The pi has two buses.
    """

    def __init__(self, bus):
        """Constructor"""

        self.bus = bus
        if SMBus is None:
            raise ImportError("failed to import smbus2")
        self._smbus = SMBus(bus)

    def read(self, address, register, byte_num=1):
        """Read using the smbus protocol.

        Args:
            address: The address of the spi slave
            register: The register's address.
            byte_num: How many bytes to read from the device. Max 32

        Returns:
            A list with byte_num elements.
        """
        
        byte_num = min(byte_num, 32)
        if byte_num > 1:
            data = self._smbus.read_i2c_block_data(address, register, byte_num)
        else:
            data = self._smbus.read_byte_data(address, register)

        return data

    def write(self, address, register, data):
        """Write using the smbus protocol.

        Args:
            address: The address of the spi slave
            register: The address of the register inside the slave.
            data: A list or a single byte, if it is a list max length 32 bytes.
                It is error prone so write less and make consecutive calls.
        """

        write_func = self._smbus.write_i2c_block_data\
            if isinstance(data, list) else self._smbus.write_byte_data

        write_func(address, register, data)
    
    def write_i2c(self, address, register, data):
        """Write using the i2c protocol

        Args:
            address: The address of the spi slave
            register: The address of the register inside the slave.
            data: A list or a single byte, if it is a list max length 32 bytes.
        """
        data = data if isinstance(data, list) else [data]
        msg = i2c_msg.write(address, [register] + data)
        self._smbus.i2c_rdwr(msg)

    def read_i2c(self, address, byte_num):
        """Read using the i2c protocol.

        Args:
            address: The address of the spi slave
            byte_num: How many bytes to read from the device. Max 32

        Returns:
            A list with byte_num elements.
        """

        msg = i2c_msg.read(address, byte_num)
        self._smbus.i2c_rdwr(msg)
        res = [ord(read.buf[i]) for i in range(byte_num)]

        return res

    def read_write(self, address, register, data, byte_num):
        """Combined read and write command using the i2c protocol.
        
        Args:
            address: The address of the spi slave
            register: The address of the register inside the slave.
            data: A list or a single byte, if it is a list max length 32 bytes.
            byte_num: How many bytes to read from the device. Max 32

        Returns:
            A list with byte_num elements.
        """

        data = data if isinstance(data, list) else [data]
        write = i2c_msg.write(address, [register] + data)
        read = i2c_msg.read(address, byte_num)
        
        self._smbus.i2c_rdwr(write, read)
        res = [ord(read.buf[i]) for i in range(byte_num)]

        return res

    def close(self):
        self._smbus.close()

    def _set_bus(self, bus):
        self._bus = bus

    def _get_bus(self):
        return self._bus
