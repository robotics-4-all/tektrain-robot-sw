from ...devices import Sensor


from ctypes import CDLL, CFUNCTYPE, POINTER, c_int, c_uint, pointer,\
    c_ubyte, c_uint8, c_uint32
import os
import site
import glob


class VL53L1xError(RuntimeError):
    pass


class VL53L1xDistanceMode:
    SHORT = 1
    MEDIUM = 2
    LONG = 3


# Read/write function pointer types.
_I2C_READ_FUNC = CFUNCTYPE(c_int, c_ubyte,
                           c_ubyte, POINTER(c_ubyte),
                           c_ubyte)
_I2C_WRITE_FUNC = CFUNCTYPE(c_int, c_ubyte, c_ubyte, POINTER(c_ubyte), c_ubyte)

# Load VL53L1X shared lib
dir_path = os.path.dirname(os.path.realpath(__file__))
_TOF_LIBRARY = CDLL(dir_path + '/libvl53l1_api.a')


class VL53L1X(Sensor):
    """VL53L1X ToF."""

    def __init__(self, bus=1, tca9548a_num=255, tca9548a_addr=0):
        """Initialize the VL53L1X ToF Sensor from ST"""
        super(VL53L1X, self).__init__(name="", max_data_length=1)
        self._bus = bus
        self.VL53L1X_ADDRESS = 0x29
        self._tca9548a_num = tca9548a_num
        self._tca9548a_addr = tca9548a_addr

        # Resgiter Address
        self.ADDR_UNIT_ID_HIGH = 0x16  # Serial number high byte
        self.ADDR_UNIT_ID_LOW = 0x17  # Serial number low byte
        self.ADDR_I2C_ID_HIGH = 0x18  # Write serial number high byte for I2C 
        self.ADDR_I2C_ID_LOW = 0x19  # Write serial number low byte for I2C 
        self.ADDR_I2C_SEC_ADDR = 0x8a  # Write new I2C address after unlock

        self.start()

    def start(self):
        """Init hardware and os resources."""
        self._i2c = self.init_interface('i2c', bus=self._bus)
        self._configure_i2c_library_functions()
        self._dev = _TOF_LIBRARY.initialise(self.i2c_address)

    def stop(self):
        self.hardware_interfaces[self._i2c].close()

    def _configure_i2c_library_functions(self):
        # I2C bus read callback for low level library.
        def _i2c_read(address, reg, data_p, length):

            data = [reg >> 8, reg & 0xFF]
            data_p = self.hardware_interfaces[self._i2c].read_write(address,
                                                                    data,
                                                                    length)

        # I2C bus write callback for low level library.
        def _i2c_write(address, reg, data_p, length):
            ret_val = 0
            data = []

            for index in range(length):
                data.append(data_p[index])

            register = reg >> 8
            data = [reg & 0xFF] + data
            self.hardware_interfaces[self._i2c].write(address, register, data)

            return ret_val

        # Pass i2c read/write function pointers to VL53L1X library.
        self._i2c_read_func = _I2C_READ_FUNC(_i2c_read)
        self._i2c_write_func = _I2C_WRITE_FUNC(_i2c_write)
        _TOF_LIBRARY.VL53L1_set_i2c(self._i2c_read_func, self._i2c_write_func)

    def start_ranging(self, mode=VL53L1xDistanceMode.LONG):
        """Start VL53L1X ToF Sensor Ranging"""
        _TOF_LIBRARY.startRanging(self._dev, mode)

    def stop_ranging(self):
        """Stop VL53L1X ToF Sensor Ranging"""
        _TOF_LIBRARY.stopRanging(self._dev)

    def get_distance(self):
        """Get distance from VL53L1X ToF Sensor"""
        return _TOF_LIBRARY.getDistance(self._dev)

    # This function included to show how to access the ST library directly
    # from python instead of through the simplified interface
#    def get_timing(self):
#        budget = c_uint(0)
#        budget_p = pointer(budget)
#status = _TOF_LIBRARY.VL53L1_GetMeasurementTimingBudgetMicroSeconds(self._dev,
#                                                                     budget_p)
#        if status == 0:
#            return budget.value + 1000
#        else:
#            return 0
#
#    def change_address(self, new_address):
#        _TOF_LIBRARY.setDeviceAddress(self._dev, new_address)
