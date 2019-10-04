"""bme680.py"""

import time
from math import ceil
from .humidity_sensor import HumiditySensor
from .temperature_sensor import TemperatureSensor
from .gas_sensor import GasSensor
from .pressure_sensor import PressureSensor
from collections import namedtuple


t_cal = namedtuple('t_cal', ['par_t1', 'par_t2', 'par_t3'])
p_cal = namedtuple('p_cal', ['par_p1', 'par_p2', 'par_p3', 'par_p4', 'par_p5',
                             'par_p6', 'par_p7', 'par_p8', 'par_p9', 'par_p10'])
h_cal = namedtuple('h_cal', ['par_h1', 'par_h2', 'par_h3', 
                             'par_h4', 'par_h5', 'par_h6',
                             'par_h7'])
g_cal = namedtuple('g_cal', ['par_g1', 'par_g2', 'par_g3', 'res_heat_range',
                             'res_heat_val'])

bme680_data = namedtuple('bme680_data', ['temp', 'pres', 'hum', 'gas'])


class BME680(HumiditySensor, TemperatureSensor, GasSensor, PressureSensor):
    """Class implementing BME680 sensor.
    
    Args:
        bus: The i2c bus.
        slave: The slave address. Should be 0 or 1
        t_oversample (int): How many measurements to average for temperature
            , valid values 0(no measurment), 1, 2, 4, 8, 16. Defaults to 1.
        p_oversample (int): How many measurements to average for pressure
            , valid values 0(no measurment), 1, 2, 4, 8, 16. Defaults to 0.
        h_oversample (int): How many measurements to average for humidity
            , valid values 0(no measurment), 1, 2, 4, 8, 16. Defaults to 0.
        iir_coef (int): Coefficient for hardware iir filter. Valid values
            0, 1, 2, 3, 7, 15, 31, 63, 127.
        gas_status (int): 0 or 1 for activating gas measurment.
    """

    # I2C Registers
    STATUS = 0x73
    RESET = 0xE0
    ID = 0xD0
    CONFIG = 0x75
    CTRL_MEAS = 0x74
    CTRL_HUM = 0x72
    CTRL_GAS_1 = 0x71
    CTRL_GAS_0 = 0x70
    GAS_WAIT = 0x64   # 9 registers(0x6D..0x64) gas_wait_x, starting from 0
    RES_HEAT = 0x5A   # 9 registers(0x63..0x5A) res_heat_x, starting from 0
    IDAC_HEAT = 0x50   # 9 registers(0x59..0x50) idac_heat_x, starting from 0
    GAS_R_LSB = 0x2B
    GAS_MSB = 0x2A
    HUM_LSB = 0x26
    HUM_MSB = 0x25
    TEMP_XLSB = 0x24
    TEMP_LSB = 0x23
    TEMP_MSB = 0x22
    PRESS_XLSB = 0x21
    PRESS_LSB = 0x20
    PRESS_MSB = 0x1F
    MEAS_STATUS_0 = 0x1D

    # Calibration registers
    PAR_T1_l = 0xE9
    PAR_T2_l = 0x8A
    PAR_T3 = 0x8C
    PAR_P1_l = 0x8E
    PAR_P2_l = 0x90
    PAR_P3 = 0x92
    PAR_P4_l = 0x94
    PAR_P5_l = 0x96
    PAR_P6 = 0x99
    PAR_P7 = 0x98
    PAR_P8_l = 0x9C
    PAR_P9_l = 0x9E
    PAR_P10 = 0xA0
    PAR_H1_l = 0xE2
    PAR_H1_h = 0xE3
    PAR_H2_l = 0xE2
    PAR_H2_h = 0xE1
    PAR_H3 = 0xE4
    PAR_H4 = 0xE5
    PAR_H5 = 0xE6
    PAR_H6 = 0xE7
    PAR_H7 = 0xE8
    PAR_G1 = 0xED
    PAR_G2_L = 0xEB
    PAR_G3 = 0xEE
    RES_HEAT_RANGE = 0x02
    RES_HEAT_VAL = 0x00

    # Bits to shift for setting/reading bits in registers

    # CONFIG register
    SPI_3W_EN = 0
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

    # PRESS_XLSB
    PRESS_XLSB_7_4 = 4
    PRESS_XLSB_7_4_BITS = 4

    # EAS_STATUS
    GAS_MEAS_INDEX = 0
    GAS_MEAS_INDEX_BITS = 4
    MEASURING = 5
    MEASURING_BITS = 1
    GAS_MEASURING = 6
    GAS_MEASURING_BITS = 1
    NEW_DATA_0 = 7
    NEW_DATA_0_BITS = 1

    MODES = {"sleep": 0, "forced": 1}
    OVERSAMPLING = {0: 0, 1: 1, 2: 2, 4: 3, 8: 4, 16: 5}
    IIR = {0: 0, 1: 1, 3: 2, 7: 3, 15: 4, 31: 5, 63: 6, 127: 7}

    # TODO: Make it one list
    lookupTable1 = [2147483647, 2147483647, 2147483647, 2147483647,
                    2147483647, 2126008810, 2147483647, 2130303777, 2147483647,
                    2147483647, 2143188679, 2136746228, 2147483647, 2126008810,
                    2147483647, 2147483647]

    lookupTable2 = [4096000000, 2048000000, 1024000000, 512000000,
                    255744255, 127110228, 64000000, 32258064,
                    16016016, 8000000, 4000000, 2000000,
                    1000000, 500000, 250000, 125000]

    def __init__(self, bus,
                 slave, t_oversample=1, 
                 p_oversample=0, h_oversample=0,
                 iir_coef=0, gas_status=0,
                 name="", max_data_length=1):
        """Constructor"""

        super(BME680, self).__init__(name, max_data_length)
        self._bus = bus
        # TODO check slave values
        self.BME_ADDRESS = 0x76 + slave
        self.start()

        # Initialize measurements parameters
        self.h_oversample = h_oversample
        self.t_oversample = t_oversample
        self.p_oversample = p_oversample
        self.iir_coef = iir_coef
        self.gas_status = gas_status
        self._get_calibration_pars()

        # TODO fix it
        self.ambient_temperature = None

    @property
    def t_oversample(self):
        """
        How many measurements to average for temperature. Valid values
        0(no measurment), 1, 2, 4, 8, 16.
        """
        return self._t_oversample

    @t_oversample.setter
    def t_oversample(self, value):
        self._t_oversample = value

        # Set osrs_t
        self._set_register(self.CTRL_MEAS, self.OSRS_T_BITS,
                           self.OSRS_T, self.OVERSAMPLING[value])

    @property
    def p_oversample(self):
        """
        How many measurements to average for pressure. Valid values
        0(no measurment), 1, 2, 4, 8, 16.
        """
        return self._p_oversample

    @p_oversample.setter
    def p_oversample(self, value):
        self._p_oversample = value

        # Set osrs_p
        self._set_register(self.CTRL_MEAS, self.OSRS_P_BITS,
                           self.OSRS_P, self.OVERSAMPLING[value])

    @property
    def h_oversample(self):
        """
        How many measurements to average for humidity. Valid values
        0(no measurment), 1, 2, 4, 8, 16.
        """
        return self._h_oversample

    @h_oversample.setter
    def h_oversample(self, value):
        self._h_oversample = value

        # Set osrs_h
        self._set_register(self.CTRL_HUM, self.OSRS_H_BITS,
                           self.OSRS_H, self.OVERSAMPLING[value])

    @property
    def iir_coef(self):
        """
        Coefficient for hardware iir filter. Valid values 0, 1, 2, 3, 7, 15,
        31, 63, 127.
        """
        return self._iir_coef

    @iir_coef.setter
    def iir_coef(self, value):
        self._iir_coef = value

        # Set osrs_t
        self._set_register(self.CONFIG, self.FILTER_BITS,
                           self.FILTER, self.IIR[value])

    @property
    def gas_status(self):
        """Enable or disable gas measurment."""
        return self._gas_status

    @gas_status.setter
    def gas_status(self, value):
        self._gas_status = value

        # Set register
        self._set_register(self.CTRL_GAS_1, self.RUN_GUS_BITS,
                           self.RUN_GUS, value)

    @property
    def bus(self):
        """The i2c bus."""
        return self._bus
    
    @bus.setter
    def bus(self, value):
        self._bus = value

    @property
    def slave(self):
        """The i2c slave."""
        return self._slave
    
    @slave.setter
    def slave(self, value):
        self._slave = value

    @property
    def t_calib(self):
        return self._t_calib

    @property
    def p_calib(self):
        return self._p_calib

    @property
    def h_calib(self):
        return self._h_calib

    @property
    def g_calib(self):
        return self._g_calib

    @property
    def res_heat_range(self):
        return self._res_heat_range

    def start(self):
        """Initialize hardware and os resources."""
        
        self._i2c = self.init_interface("i2c", bus=self._bus)

    def read(self, temp=True, hum=True, pres=True, gas=True):
        """Get a measurment.
        
        Args:
            temp (boolean): Flag for enabling temperature measurment.
                Defaults to :data:`True`.
            hum (boolean): Flag for enabling humidity measurment.
                Defaults to :data:`True`.
            pres (boolean): Flag for enabling pressure measurment.
                Defaults to :data:`True`.
            gas (boolean): Flag for enabling gas measurment.
                Defaults to :data:`True`.
        
        Returns:
            A named tuple of type (temp, pres, hum, gas)
        """

        if not hum:
            h_oversample_bak = self.h_oversample
            self.h_oversample = 0
        if not temp:
            t_oversample_bak = self.t_oversample
            self.t_oversample = 0
        if not pres:
            p_oversample_bak = self.p_oversample
            self.p_oversample = 0
        if not gas:
            self.gas_status = 0

        self._set_register(self.CTRL_MEAS, self.MODE_BITS,
                           self.MODE, self.MODES['forced'])

        # Wait for measurements to finish
        while self._get_register(self.MEAS_STATUS_0, self.MEASURING_BITS,
                                 self.MEASURING):
            time.sleep(0.01)

        # Read results
        temp = self._read_temp_pre(self.TEMP_MSB, self.t_oversample,
                                   self.TEMP_XLSB_7_4_BITS, self.TEMP_XLSB_7_4,
                                   self._calc_temp)
        pres = self._read_temp_pre(self.PRESS_MSB, self.p_oversample,
                                   self.PRESS_XLSB_7_4_BITS, self.PRESS_XLSB_7_4,
                                   self._calc_pres)
        humi = self._read_humi()
        gas = self._read_gas()

        data = bme680_data(temp=temp/100, pres=pres/100, hum=humi/1000, gas=gas)

        # Restore values
        if not hum:
            self.h_oversample = h_oversample_bak 
        if not temp:
            self.t_oversample = t_oversample_bak 
        if not pres:
            self.p_oversample = p_oversample_bak 
        if not gas:
            self.gas_status = 0

        return data

    # TODO: check if multiple returns is a good practice
    def _read_gas(self):
        """Read gas temperature"""

        if not self.gas_status:
            return 0

        # Check if the heater temperature is stable for gas measurment
        heat_stab = self._get_register(self.GAS_R_LSB,
                                       self.HEAF_STAB_R_BITS,
                                       self.HEAF_STAB_R)
        if not heat_stab:
            return 0

        # Get measurment
        gas_range = self._get_register(self.GAS_R_LSB,
                                       self.GAS_RANGE_R_BITS,
                                       self.GAS_RANGE_R)
        range_error = self._get_bytes(0x04, 4, signed=True)
        adc = self._get_bytes(self.GAS_MSB, 10, rev=True)

        return self._calc_gas(adc, gas_range, range_error)

    def _read_humi(self):
        """Read humidity measurment."""

        if not self.h_oversample:
            return 0

        adc = self._get_bytes(self.HUM_MSB, 16, rev=True)

        return self._calc_humi(adc)

    def _read_temp_pre(self, register, oversample, bits, shift, calculator):
        """Read pressure or temperature measurement.
        
        Args:
            register: The result msb
            calculator: the function for computing the result from adc
        """
        
        # If iir is enable then the result resolution is 20 bits
        if self.iir_coef and oversample:
            last_byte = 4
        # if iir is not enabled the resultion is 16 + (osrt_f - 1)
        elif not self.iir_coef and oversample:
            last_byte = self.OVERSAMPLING[oversample] - 1
        # If oversample is 0 the measurment is skipped
        else:
            return 0
        resolution = 16 + last_byte

        adc = self._get_bytes(register, resolution, rev=True)

        return calculator(adc)

    def _calc_temp(self, temp_adc, INT=True):
        """Calculate temperature from adc value."""
        var_1 = (temp_adc >> 3) - (self.t_calib.par_t1 << 1)
        var_2 = (var_1*self.t_calib.par_t2) >> 11
        var_3 = ((var_1 >> 1) * (var_1 >> 1)) >> 12
        var_3 = ((var_3) * (self.t_calib.par_t3 << 4)) >> 14
        self._t_fine = var_2 + var_3

        return ((self._t_fine * 5) + 128) >> 8

    def _calc_pres(self, pres_adc, INT=True):
        """Convert the raw pressure using calibration data."""

        var_1 = ((self._t_fine) >> 1) - 64000
        var_2 = ((((var_1 >> 2) * (var_1 >> 2)) >> 11) * self.p_calib.par_p6) >> 2
        var_2 = var_2 + ((var_1 * self.p_calib.par_p5) << 1)
        var_2 = (var_2 >> 2) + (self.p_calib.par_p4 << 16)
        var_1 = (((((var_1 >> 2) * (var_1 >> 2)) >> 13)
                 * ((self.p_calib.par_p3 << 5)) >> 3)
                 + ((self.p_calib.par_p2 * var_1) >> 1))
        var_1 = var_1 >> 18

        var_1 = ((32768 + var_1) * self.p_calib.par_p1) >> 15
        calc_pressure = 1048576 - pres_adc
        calc_pressure = ((calc_pressure - (var_2 >> 12)) * (3125))

        if calc_pressure >= (1 << 31):
            calc_pressure = ((calc_pressure // var_1) << 1)
        else:
            calc_pressure = ((calc_pressure << 1) // var_1)

        var_1 = (self.p_calib.par_p9 * (((calc_pressure >> 3) 
                                         * (calc_pressure >> 3)) >> 13)) >> 12
        var_2 = ((calc_pressure >> 2) * self.p_calib.par_p8) >> 13
        var_3 = ((calc_pressure >> 8) * (calc_pressure >> 8) 
                 * (calc_pressure >> 8) * self.p_calib.par_p10) >> 17

        calc_pressure = (calc_pressure) + ((var_1 + var_2 + var_3 +
                                           (self.p_calib.par_p7 << 7)) >> 4)

        return calc_pressure

    def _calc_humi(self, humidity_adc, INT=True):
        """Convert the raw humidity using calibration data."""
        temp_scaled = ((self._t_fine * 5) + 128) >> 8
        var_1 = (humidity_adc - ((self.h_calib.par_h1 * 16))) 
        var_1 -= (((temp_scaled * self.h_calib.par_h3) // (100)) >> 1)
        var_2 = (self.h_calib.par_h2
                 * (((temp_scaled * self.h_calib.par_h4) // (100)) 
                    + (((temp_scaled * ((temp_scaled * self.h_calib.par_h5)
                                        // (100))) >> 6)
                    // (100)) + (1 * 16384))) >> 10
        var_3 = var_1 * var_2
        var_4 = self.h_calib.par_h6 << 7
        var_4 = ((var_4) + ((temp_scaled * self.h_calib.par_h7) // (100))) >> 4
        var_5 = ((var_3 >> 14) * (var_3 >> 14)) >> 10
        var_6 = (var_4 * var_5) >> 1
        calc_hum = (((var_3 + var_6) >> 10) * (1000)) >> 12

        return min(max(calc_hum, 0), 100000)

    def _calc_gas(self, adc, gas_range, range_error):
        """Convert the raw gas resistance using calibration data."""

        var_1 = ((1340 + (5 * range_error))
                 * (self.lookupTable1[gas_range])) >> 16
        var_2 = (((adc << 15) - (16777216)) + var_1)
        var_3 = ((self.lookupTable2[gas_range] * var_1) >> 9)
        calc_gas_res = ((var_3 + (var_2 >> 1)) / var_2)

        if calc_gas_res < 0:
            calc_gas_res = (1 << 32) + calc_gas_res

        return calc_gas_res

    def stop(self):
        """Free hardware and os resources."""
        self._reset()
        self.hardware_interfaces[self._i2c].close()
    
    def set_idac_heat(self, indexes, values):
        """Set idac_heat_x registers.
        
        Args:
            values: List with the values
            indexes: List with indexes
        """

        for val, i in zip(values, indexes):
            self._set_register(self.IDAC_HEAT+i, 0, 0, val)

    def set_heating_temp(self, indexes, values):
        """Set res_heat_x registers.
        
        Args:
            values: List with the values
            indexes: List with indexes
        """

        for val, i in zip(values, indexes):
            val = self._calc_res_heat(val)
            self._set_register(self.RES_HEAT+i, 8, 0, int(val))

    # TODO: dont calculate if the temperature isn't set
    def _calc_res_heat(self, temperature):
        """Calculate resistance heat
        
        Args:
            value: 
        """

        """Convert raw heater resistance using calibration data."""
        temperature = min(max(temperature, 200), 400)
        # Get temp measurement for ambient temp.
        if self.ambient_temperature is None:
            prev_gs = self.gas_status
            self.gas_status = 0
            self.ambient_temperature, pres, hum, gas = self.read()
            self.gas_status = prev_gs
            self.ambient_temperature *= 100

        var_1 = ((self.ambient_temperature * self.g_calib.par_g3) / 1000) * 256
        var_2 = (self.g_calib.par_g1 + 784)
        var_2 *= (((((self.g_calib.par_g2 + 154009)
                  * temperature * 5) / 100) + 3276800) / 10)
        var_3 = var_1 + (var_2 / 2)
        var_4 = (var_3 / (self.g_calib.res_heat_range + 4))
        var_5 = (131 * self.g_calib.res_heat_val) + 65536
        heatr_res_x100 = (((var_4 / var_5) - 250) * 34)
        heatr_res = ((heatr_res_x100 + 50) / 100)

        return heatr_res

    def set_heating_time(self, indexes, values):
        """Set gas wait registers.

        Args:
            values: List with the values
            indexes: List with indexes
        """

        for val, i in zip(values, indexes):
            val = self._calc_heater_duration(val)
            self._set_register(self.GAS_WAIT+i, 8, 0, val)

    def _calc_heater_duration(self, duration):
        """Calculate correct value for heater duration setting from 
        milliseconds."""
        if duration < 0xfc0:
            factor = 0

            while duration > 0x3f:
                duration /= 4
                factor += 1

            return int(duration + (factor * 64))

        return 0xff

    def set_heater_off(self, value):
        """Set heater of bit"""

        self._set_register(self.CTRL_GAS_0, self.HEAT_OFF_BITS, 
                           self.HEAT_OFF, value)

    def set_nb_conv(self, value):
        self._set_register(self.CTRL_GAS_1, self.NB_CONV_BITS,
                           self.NB_CONV, value)

    def _get_calibration_pars(self):
        """Get calibrations parameters."""

        # Temperature
        par_t1 = self._get_bytes(self.PAR_T1_l, 16)
        par_t2 = self._get_bytes(self.PAR_T2_l, 16, signed=True)
        par_t3 = self._get_bytes(self.PAR_T3, 8)
        self._t_calib = t_cal(par_t1=par_t1, par_t2=par_t2, par_t3=par_t3)

        # Pressure
        par_p1 = self._get_bytes(self.PAR_P1_l, 16)
        par_p2 = self._get_bytes(self.PAR_P2_l, 16, signed=True)
        par_p3 = self._get_bytes(self.PAR_P3, 8)
        par_p4 = self._get_bytes(self.PAR_P4_l, 16, signed=True)
        par_p5 = self._get_bytes(self.PAR_P5_l, 16, signed=True)
        par_p6 = self._get_bytes(self.PAR_P6, 8)
        par_p7 = self._get_bytes(self.PAR_P7, 8)
        par_p8 = self._get_bytes(self.PAR_P8_l, 16, signed=True)
        par_p9 = self._get_bytes(self.PAR_P9_l, 16, signed=True)
        par_p10 = self._get_bytes(self.PAR_P10, 8)
        self._p_calib = p_cal(par_p1=par_p1, par_p2=par_p2, par_p3=par_p3,
                              par_p4=par_p4, par_p5=par_p5, par_p6=par_p6,
                              par_p7=par_p7, par_p8=par_p8, par_p9=par_p9,
                              par_p10=par_p10)

        # Humidity
        # TODO: Make one call
        par_h1 = self._get_bytes(self.PAR_H1_h, 8) << 4
        par_h1 += self._get_bits(self._get_bytes(self.PAR_H1_l, 8), 4, 4)
        par_h2 = self._get_bytes(self.PAR_H2_h, 8) << 4
        par_h2 += self._get_bits(self._get_bytes(self.PAR_H2_l, 8), 4, 4)
        par_h3 = self._get_bytes(self.PAR_H3, 8, signed=True)
        par_h4 = self._get_bytes(self.PAR_H4, 8, signed=True)
        par_h5 = self._get_bytes(self.PAR_H5, 8, signed=True)
        par_h6 = self._get_bytes(self.PAR_H6, 8)
        par_h7 = self._get_bytes(self.PAR_H7, 8, signed=True)
        self._h_calib = h_cal(par_h1=par_h1, par_h2=par_h2, par_h3=par_h3,
                              par_h4=par_h4, par_h5=par_h5, par_h6=par_h6,
                              par_h7=par_h7)
        
        # Gas
        par_g1 = self._get_bytes(self.PAR_G1, 8, signed=True)
        par_g2 = self._get_bytes(self.PAR_G2_L, 16, signed=True)
        par_g3 = self._get_bytes(self.PAR_G3, 8, signed=True)
        res_heat_range = self._get_bits(self._get_bytes(self.RES_HEAT_RANGE, 8),
                                        2,
                                        4)
        res_heat_val = self._get_bytes(self.RES_HEAT_VAL, 8, signed=True)
        self._g_calib = g_cal(par_g1=par_g1, par_g2=par_g2, par_g3=par_g3,
                              res_heat_range=res_heat_range,
                              res_heat_val=res_heat_val)

    # TODO: Check maybe remove the option to get one byte
    def _get_bytes(self, low_byte_addr, res, signed=False, rev=False):
        """Get lsb and msb and make a number."""

        byte_num = ceil(res / 8)
        data = self.hardware_interfaces[self._i2c].read(self.BME_ADDRESS,
                                                        low_byte_addr,
                                                        byte_num=byte_num)
        # Make it a list if it is one element
        data = data if isinstance(data, list) else [data]
        
        # Reverse it
        if rev:
            data.reverse()

        # Find the bit number of the lsb
        low_res = res % 8
        low_res = low_res if low_res else 8

        # Get only the bits of interest
        data[0] = self._get_bits(data[0], low_res, 8-low_res)

        # Compute the whole number from spare bytes
        num = data[0]
        for (i, d) in enumerate(data[1:], start=1):
            num += d << (i*8 - (8-low_res))

        power = res - 1
        whole = 2**(power+1) - 1
        if signed:
            num = num if num < (2**power - 1) else -((whole ^ num) + 1)

        return num

    def _reset(self):
        """Software reset, is like a power-on reset."""

        self.hardware_interfaces[self._i2c].write(self.BME_ADDRESS,
                                                  self.RESET,
                                                  0xB6)

    def _set_bits(self, register, value, num_bits, shift):
        """Set shift bits from start of register with value.

        Args:
            register:
            value:
            num_bits: Integer indicating how many bits to set.
            shift: Integer indicating the starting bit in the number.
        """

        # Zero target bits
        mask = ((0xFF << (num_bits + shift)) | ((1 << shift) - 1)) & 0xFF
        register &= mask

        return register | (value << shift)

    def _get_bits(self, register, num_bits, shift):
        """Get specific bits from register
        
        Args:
            register:
            num_bits:
            shift:
        """
        
        mask = ((1 << num_bits) - 1) << shift

        return (register & mask) >> shift

    def _get_register(self, register, bits, shift):
        """Get specific bits from register.
        
        Args:
            register:
            bits:
            shift:
        """
        r_val = self.hardware_interfaces[self._i2c].read(self.BME_ADDRESS,
                                                         register)

        return self._get_bits(r_val, bits, shift)

    def _set_register(self, register, bits, shift, value):
        """Write a new value to register.
        
        Args:
            register:
            bits:
            shift:
            value:
        """
        
        r_val = self.hardware_interfaces[self._i2c].read(self.BME_ADDRESS,
                                                         register)
        r_val = self._set_bits(r_val, value, bits, shift)
        self.hardware_interfaces[self._i2c].write(self.BME_ADDRESS,
                                                  register,
                                                  r_val)
