from .hardware_interfaces import I2C

try:
    from smbus2 import SMBus, i2c_msg
except ImportError:
    SMBus = None


class SMBus2(I2C):
    """Wrapper for smbus2 library."""

    def __init__(self, bus):
        """Constructor"""

        self.bus = bus
        if SMBus is None:
            raise ImportError("failed to import smbus2")
        self._smbus = SMBus(bus)

    def read(self, address, register, byte_num=1):
        """Read

        Args:
            address:
            register:
            byte_num: How many bytes to read from the device. Max 32
        """
        
        byte_num = min(byte_num, 32)
        if byte_num > 1:
            data = self.smbus.read_i2c_block_data(address, register, byte_num)
        else:
            data = self.smbus.read_byte_data(address, register)

        return data

    def write(self, address, register, data):
        """Write

        Args:
            address: The address of the spi slave
            data: A list or a single byte, if it is a list max length 32 bytes.
                It is error prone so write less and make consecutive calls.
        """

        write_func = self.smbus.write_i2c_block_data\
            if isinstance(data, list) else self.smbus.write_byte_data

        write_func(address, register, data)
    
    def write_i2c(self, address, register, data):
        data = data if isinstance(data, list) else [data]
        msg = i2c_msg.write(address, [register] + data)
        self.smbus.i2c_rdwr(msg)

    def read_i2c(self, address, byte_num):
        msg = i2c_msg.read(address, byte_num)
        self.smbus.i2c_rdwr(msg)
        res = [ord(read.buf[i]) for i in range(byte_num)]

        return res

    def read_write(self, address, register, data, byte_num):
        """Combined read and write command."""

        data = data if isinstance(data, list) else [data]
        write = i2c_msg.write(address, [register] + data)
        read = i2c_msg.read(address, byte_num)
        
        self.smbus.i2c_rdwr(write, read)
        res = [ord(read.buf[i]) for i in range(byte_num)]

        return res

    def close(self):
        self.smbus.close()

    def _set_bus(self, bus):
        self._bus = bus

    def _get_bus(self):
        return self._bus

    @property
    def smbus(self):
        return self._smbus
