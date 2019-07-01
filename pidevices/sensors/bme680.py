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
    FILTER = 2

    # CTRL_MEAS register
    MODE = 0
    OSRS_P = 2
    OSRS_T = 5

    # CTRL_HUM
    OSRS_H = 0
    SPI_3W_INT_EN = 6

    # CTRL_GAS_1
    NB_CONV = 0
    RUN_GUS = 4
    
    # CTRL_GAS_0
    HEAT_OFF = 3

    # GAS_R_LSB
    GAS_RANGE_R = 0
    HEAF_STAB_R = 4
    GAS_VALID_R = 5
    GAS_R_0_1 = 6

    # TEMP_XLSB 
    TEMP_XLSB_7_4 = 4

    # EAS_STATUS
    GAS_MEAS_INDEX = 0
    MEASURING = 5
    GAS_MEASURING = 6
    NEW_DATA_0 = 7

    def _set_bits(self, register, value, shift):
        pass

    def _get_bits(self, register, shift):
        pass
