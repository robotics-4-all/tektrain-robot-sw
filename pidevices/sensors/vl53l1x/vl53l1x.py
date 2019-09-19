from ..distance_sensor import DistanceSensor

# MIT License
#
# Copyright (c) 2017 John Bryan Moore
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from ctypes import CDLL, CFUNCTYPE, POINTER, c_int, c_uint, pointer, c_ubyte
from ctypes import c_uint8, c_uint32
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
_I2C_READ_FUNC = CFUNCTYPE(c_int, c_ubyte, c_ubyte, POINTER(c_ubyte), c_ubyte)
_I2C_WRITE_FUNC = CFUNCTYPE(c_int, c_ubyte, c_ubyte, POINTER(c_ubyte), c_ubyte)

# Load VL53L1X shared lib
_POSSIBLE_LIBRARY_LOCATIONS = [os.path.dirname(os.path.realpath(__file__))]

try:
    _POSSIBLE_LIBRARY_LOCATIONS += site.getsitepackages()
except AttributeError:
    pass

try:
    _POSSIBLE_LIBRARY_LOCATIONS += [site.getusersitepackages()]
except AttributeError:
    pass

dir_path = os.path.dirname(os.path.realpath(__file__))
_TOF_LIBRARY = CDLL(dir_path + '/test.so')


# TODO: Document args.
class VL53L1X(DistanceSensor):
    """VL53L1X ToF extends :class:`DistanceSensor`

    Hardware: 
        - voltage: 2.6V-5.5V
        - max_distance: 4m

    The VL53L1X offers three distance modes: short, medium, and long. Long
    distance mode allows the longest possible ranging distance of 4 m, but the
    maximum range is significantly affected by ambient light. Short distance
    mode is mostly immune to ambient light, but the maximum ranging distance is
    typically limited to 1.3 m (4.4 ft). The maximum sampling rate in short
    distance mode is 50 Hz while the maximum sampling rate for medium and long
    distance modes is 30 Hz. Performance can be improved in all modes by using
    lower sampling rates and longer timing budgets. 

    First call start_ranging function and then read.

    Args:
        bus (int): The i2c bus.
        VL53L1X_ADDRESS (int): It is the i2c address of the device. Defaults to
            0x29.
        tca9548a_num (int):
        tca9548a_addr (int):
    """

    def __init__(self, bus=1, VL53L1X_ADDRESS=0x29, 
                 tca9548a_num=255, tca9548a_addr=0):
        """Initialize the VL53L1X ToF Sensor from ST"""
        super(VL53L1X, self).__init__(name='', max_data_length=0)
        self.max_distance = 4
        self.min_distance = 0.04

        self._bus = bus
        self.VL53L1X_ADDRESS = VL53L1X_ADDRESS
        self._tca9548a_num = tca9548a_num
        self._tca9548a_addr = tca9548a_addr
        self._dev = None
        # Resgiter Address
        self.ADDR_UNIT_ID_HIGH = 0x16  # Serial number high byte
        self.ADDR_UNIT_ID_LOW = 0x17  # Serial number low byte
        # Write serial number high byte for I2C address unlock
        self.ADDR_I2C_ID_HIGH = 0x18  
        # Write serial number low byte for I2C address unlock
        self.ADDR_I2C_ID_LOW = 0x19  
        self.ADDR_I2C_SEC_ADDR = 0x8a  # Write new I2C address after unlock

        self.start()

    def start(self):
        """Init hardware and os resources."""

        self._i2c = self.init_interface('i2c', bus=self._bus)
        self._configure_i2c_library_functions()
        self._dev = _TOF_LIBRARY.initialise(self.VL53L1X_ADDRESS)

    def stop(self):
        """Free hardware and os resources."""

        self.hardware_interfaces[self._i2c].close()
        self._dev = None

    def _configure_i2c_library_functions(self):
        # I2C bus read callback for low level library.
        def _i2c_read(address, reg, data_p, length):
            ret_val = 0

            register = reg >> 8
            data = reg & 0xFF
            res = self.hardware_interfaces[self._i2c].read_write(address,
                                                                 register,
                                                                 data,
                                                                 length)

            if ret_val == 0:
                for index in range(length):
                    data_p[index] = res[index]

            return ret_val

        # I2C bus write callback for low level library.
        def _i2c_write(address, reg, data_p, length):
            ret_val = 0
            data = []

            for index in range(length):
                data.append(data_p[index])

            register = reg >> 8
            data = [reg & 0xFF] + data
            self.hardware_interfaces[self._i2c].write_i2c(address,
                                                          register,
                                                          data)

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

    def read(self):
        """Get distance from VL53L1X ToF Sensor"""
        return _TOF_LIBRARY.getDistance(self._dev)

    # This function included to show how to access the ST library directly
    # from python instead of through the simplified interface
    #def get_timing(self):
    #    budget = c_uint(0)
    #    budget_p = pointer(budget)
    #    status = _TOF_LIBRARY.VL53L1_GetMeasurementTimingBudgetMicroSeconds(\
    #            self._dev, budget_p)
    #    if status == 0:
    #        return budget.value + 1000
    #    else:
    #        return 0

    def change_address(self, new_address):
        _TOF_LIBRARY.setDeviceAddress(self._dev, new_address)
