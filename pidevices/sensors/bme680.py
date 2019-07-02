from .humidity_sensor import HumiditySensor
from .temperature_sensor import TemperatureSensor
from .gas_sensor import GasSensor
from .pressure_sensor import PressureSensor


class BME680(HumiditySensor, TemperatureSensor, GasSensor, PressureSensor):
    """Class implementing BME680 sensor."""

    # I2C Registers
    STATUS = 0x73
    RESET = 0xE0
    ID = 0xD0
    CONFIG = 0x75
    CTRL_MEAS = 0x74
    CTRL_HUM = 0x72
    CTRL_GAS_1 = 0x71
    CTRL_GAS_0 = 0x70
    GAS_WAIT = 0x6D   # 9 registers(0x6D..0x64) gas_wait_x, starting from 0
    RES_HEAT = 0x63   # 9 registers(0x63..0x5A) res_heat_x, starting from 0
    IDAC_HEAT = 0x59   # 9 registers(0x59..0x50) idac_heat_x, starting from 0
    GAS_LSB = 0x2B
    GAS_MSB = 0x2A
    HUM_LSB = 0x26
    HUM_MSB = 0x25
    TEMP_XLSB = 0x24
    TEMP_LSB = 0x23
    TEMP_MSB = 0x22
    PRESS_XLSB = 0x21
    PRESS_LSB = 0x20
    PRESS_MSB = 0x1F
    EAS_STATUS_0 = 0x1D

    # Bits to shift for setting/reading bits in registers

    # CONFIG register
    SPI_3W_EN = 1
    SPI_3W_EN_BITS = 1
    FILTER = 2
    FILTER_BITS = 3

    # CTRL_MEAS register
    MODE = 0
    MODE_BITS = 2
    OSRS_P = 2
    OSRS_P_BITS = 3
    OSRS_T = 5
    OSRS_T_BITS = 3

    # CTRL_HUM
    OSRS_H = 0
    OSRS_H_BITS = 3
    SPI_3W_INT_EN = 6
    SPI_3W_INT_EN_BITS = 1

    # CTRL_GAS_1
    NB_CONV = 0
    NB_CONV_BITS = 4
    RUN_GUS = 4
    RUN_GUS_BITS = 1
    
    # CTRL_GAS_0
    HEAT_OFF = 3
    HEAT_OFF_BITS = 1

    # GAS_R_LSB
    GAS_RANGE_R = 0
    GAS_RANGE_R_BITS = 4
    HEAF_STAB_R = 4
    HEAF_STAB_R_BITS = 1
    GAS_VALID_R = 5
    GAS_VALID_R_BITS = 1
    GAS_R_0_1 = 6
    GAS_R_0_1_BITS = 2

    # TEMP_XLSB 
    TEMP_XLSB_7_4 = 4
    TEMP_XLSB_7_4_BITS = 4

    # EAS_STATUS
    GAS_MEAS_INDEX = 0
    GAS_MEAS_INDEX_BITS = 4
    MEASURING = 5
    MEASURING_BITS = 1
    GAS_MEASURING = 6
    GAS_MEASURING_BITS = 1
    NEW_DATA_0 = 7
    NEW_DATA_0_BITS = 1

    def __init__(self, bus, slave, name="", max_data_lenght=1):
        """Constructor

        Args:
            bus: The i2c bus.
            slave: The slave address. Should be 0 or 1
        """

        super(BME680, self).__init__(name, max_data_lenght)
        self._bus = bus

        # TODO check slave values
        self.BME_ADDRESS = 0x76 + slave
        self.start()

    def start(self):
        """Initialize hardware and os resources."""
        
        self._i2c = self.init_interface("i2c", bus=self._bus)

    def read(self, measurement):
        pass

    def stop(self):
        pass

    def _set_bits(self, register, value, num_bits, shift):
        """Set shift bits from start of register with value.

        Args:
            register:
            value:
            num_bits: Integer indicating how many bits to set.
            shift: Integer indicating the starting bit in the number.
        """

        # Zero target bits
        mask = ((0xFF << (num_bits + shift)) | ((1<<shift) - 1)) & 0xFF
        register = register & mask

        return register | (value << shift)

    def _get_bits(self, register, num_bits, shift):
        pass

    def _set_mode(self, value):
        """Set chip mode.

        The mode could be sleep mode (0) or forced mode (1)
        Args:
            value: An integer indicating the mode.
        """
        ctrl_meas = self.hardware_interfaces[self._i2c].read(self.BME_ADDRESS,
                                                             self.CTRL_MEAS)
        self._set_bits(self, ctrl_meas, value, self.MODE)
