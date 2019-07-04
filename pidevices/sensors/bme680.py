import time
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
g_cal = namedtuple('g_cal', ['par_g1', 'par_g2', 'par_g3'])


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
    IIR = {0: 0, 1: 1, 3: 2, 7: 3, 15: 4, 31: 5, 63:6, 127:7}

    def __init__(self, bus,
                 slave, t_oversample=1, 
                 p_oversample=0, h_oversample=0,
                 iir_coef=0, gas_status=0,
                 name="", max_data_length=1):
        """Constructor

        Args:
            bus: The i2c bus.
            slave: The slave address. Should be 0 or 1
        """

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

    def start(self):
        """Initialize hardware and os resources."""
        
        self._i2c = self.init_interface("i2c", bus=self._bus)

    def read(self):
        """Get a measurment.
        
        Args:
            meas: String that could be temperature, humidity, pressure or gas.
        """

        self._set_register(self.CTRL_MEAS, self.MODE_BITS,
                           self.MODE, self.MODES['forced'])

        # Wait for measurements to finish
        while self._get_register(self.MEAS_STATUS_0, self.MEASURING_BITS,
                self.MEASURING):
            time.sleep(0.01)

        # Read results
        try:
            temp = self._read_temp_hum(self.TEMP_MSB, self.t_oversample,
                                       self.TEMP_XLSB_7_4_BITS, self.TEMP_XLSB_7_4,
                                       self._calc_temp)
        except TypeError:
            temp = 0

        try:
            pres = self._read_temp_hum(self.PRESS_MSB, self.p_oversample,
                                       self.PRESS_XLSB_7_4_BITS, self.PRESS_XLSB_7_4,
                                       self._calc_pres)
        except TypeError:
            pres = 0

        try:
            humi = self._read_humi()
        except TypeError:
            humi = 0

        return temp/100, pres/100, humi/1000

    def _read_humi(self):
        """Read humidity measurment."""

        if not self.h_oversample:
            return None

        adc = self._get_bytes(self.HUM_MSB, 2, rev=True)

        return self._calc_humi(adc)

    def _read_temp_pre(self, register, oversample, bits, shift, calculator):
        """Read pressure or temperature measurement.
        
        Args:
            register: The result msb
            calculator the function for computing the result from adc
        """
        
        data = self.hardware_interfaces[self._i2c].read(self.BME_ADDRESS,
                                                        register,
                                                        byte_num=3)

        # If iir is enable then the result resolution is 20 bits
        if self.iir_coef and oversample:
            last_byte = 4
        # if iir is not enabled the resultion is 16 + (osrt_f - 1)
        elif not self.iir_coef and oversample:
            last_byte = self.OVERSAMPLING[oversample] - 1
        # If oversample is 0 the measurment is skipped
        else:
            return None
        resolution = 16 + last_byte

        # Keep bits of interest from the lsb
        data[2] = self._get_bits(data[2], last_byte, bits - last_byte + shift)
        
        # Calculate whole adc reading
        adc = (data[0] << (resolution-8)) | (data[1] << last_byte) | data[2]

        return calculator(adc)

    def _calc_temp(self, temp_adc, INT=True):
        """Calculate temperature from adc value."""
        var_1 = (temp_adc >> 3) - (self.t_calib.par_t1 << 1)
        var_2 = (var_1*self.t_calib.par_t2) >> 11
        var_3 = ((var_1 >> 1) * (var_1 >> 1)) >> 12
        var_3 = ((var_3) * (self.t_calib.par_t3 << 4)) >> 14
        self._t_fine = var_2 + var_3

        return ((self.t_fine * 5) + 128) >> 8

    def _calc_pres(self, pres_adc, INT=True):
        """Convert the raw pressure using calibration data."""

        var_1 = ((self.t_fine) >> 1) - 64000
        var_2 = ((((var_1 >> 2) * (var_1 >> 2)) >> 11) *
                self.p_calib.par_p6) >> 2
        var_2 = var_2 + ((var_1 * self.p_calib.par_p5) << 1)
        var_2 = (var_2 >> 2) + (self.p_calib.par_p4 << 16)
        var_1 = (((((var_1 >> 2) * (var_1 >> 2)) >> 13) *
                ((self.p_calib.par_p3 << 5)) >> 3) +
                ((self.p_calib.par_p2 * var_1) >> 1))
        var_1 = var_1 >> 18

        var_1 = ((32768 + var_1) * self.p_calib.par_p1) >> 15
        calc_pressure = 1048576 - pres_adc
        calc_pressure = ((calc_pressure - (var_2 >> 12)) * (3125))

        if calc_pressure >= (1 << 31):
            calc_pressure = ((calc_pressure // var_1) << 1)
        else:
            calc_pressure = ((calc_pressure << 1) // var_1)

        var_1 = (self.p_calib.par_p9 * (((calc_pressure >> 3) *
                (calc_pressure >> 3)) >> 13)) >> 12
        var_2 = ((calc_pressure >> 2) *
                self.p_calib.par_p8) >> 13
        var_3 = ((calc_pressure >> 8) * (calc_pressure >> 8) *
                (calc_pressure >> 8) *
                self.p_calib.par_p10) >> 17

        calc_pressure = (calc_pressure) + ((var_1 + var_2 + var_3 +
                                           (self.p_calib.par_p7 << 7)) >> 4)

        return calc_pressure

    def _calc_humi(self, humidity_adc, INT=True):
        """Convert the raw humidity using calibration data."""
        temp_scaled = ((self.t_fine * 5) + 128) >> 8
        var_1 = (humidity_adc - ((self.h_calib.par_h1 * 16))) -\
               (((temp_scaled * self.h_calib.par_h3) // (100)) >> 1)
        var_2 = (self.h_calib.par_h2 *
                (((temp_scaled * self.h_calib.par_h4) // (100)) +
                 (((temp_scaled * ((temp_scaled * self.h_calib.par_h5)\
                    // (100))) >> 6)\
                    // (100)) + (1 * 16384))) >> 10
        var_3 = var_1 * var_2
        var_4 = self.h_calib.par_h6 << 7
        var_4 = ((var_4) + ((temp_scaled * self.h_calib.par_h7) // (100))) >> 4
        var_5 = ((var_3 >> 14) * (var_3 >> 14)) >> 10
        var_6 = (var_4 * var_5) >> 1
        calc_hum = (((var_3 + var_6) >> 10) * (1000)) >> 12

        return min(max(calc_hum, 0), 100000)

    def stop(self):
        pass
    
    def set_idac_heat(self, indexes, values):
        """Set idac_heat_x registers.
        
        Args:
            values: List with the values
            indexes: List with indexes
        """

        for val, i in zip(values, indexes):
            self._set_register(self.IDAC_HEAT+i, 0, 0, val)

    def set_res_heat(self, indexes, values):
        """Set idac_heat_x registers.
        
        Args:
            values: List with the values
            indexes: List with indexes
        """

        for val, i in zip(values, indexes):
            self._set_register(self.RES_HEAT+i, 0, 0, val)

    # TODO: dont calculate if the temperature isn't set
    def _calc_res_heat(self, temperature):
        """Calculate resistance heat
        
        Args:
            value: 
        """

        """Convert raw heater resistance using calibration data."""
        temperature = min(max(temperature, 200), 400)
        ambient_temperature, _ = self.read()
        ambient_temperature *= 100

        var1 = ((self.ambient_temperature * self.calibration_data.par_gh3) / 1000) * 256
        var2 = (self.calibration_data.par_gh1 + 784)\
               * (((((self.calibration_data.par_gh2 + 154009)\
                      * temperature * 5) / 100) + 3276800) / 10)
        var3 = var1 + (var2 / 2)
        var4 = (var3 / (self.calibration_data.res_heat_range + 4))
        var5 = (131 * self.calibration_data.res_heat_val) + 65536
        heatr_res_x100 = (((var4 / var5) - 250) * 34)
        heatr_res = ((heatr_res_x100 + 50) / 100)

        return heatr_res

    def set_gas_wait(self, indexes, values, multis):
        """Set gas wait registers.

        Args:
            indexes:
            values,:
            multis:
        """

        for val, mul, i in zip(values, multis, indexes):
            self._set_register(self.GAS_WAIT+i, 6, 0, val)
            self._set_register(self.GAS_WAIT+i, 2, 6, mul)

    def set_heater_off(self, value):
        """Set heater of bit

        """

        self._set_register(self.CTRL_GAS_0, self.HEAT_OFF_BITS, 
                           self.HEAT_OFF, value)

    def set_nb_conv(self, value):
        self._set_register(self.CTRL_GAS_1, self.NB_CONV_BITS,
                           self.NB_CONV, value)

    def _get_calibration_pars(self):
        """Get calibrations parameters."""

        # Temperature
        par_t1 = self._get_bytes(self.PAR_T1_l, 2)
        par_t2 = self._get_bytes(self.PAR_T2_l, 2, signed=True)
        par_t3 = self._get_bytes(self.PAR_T3, 1)
        self._t_calib = t_cal(par_t1=par_t1, par_t2=par_t2, par_t3=par_t3)

        # Pressure
        par_p1 = self._get_bytes(self.PAR_P1_l, 2)
        par_p2 = self._get_bytes(self.PAR_P2_l, 2, signed=True)
        par_p3 = self._get_bytes(self.PAR_P3, 1)
        par_p4 = self._get_bytes(self.PAR_P4_l, 2, signed=True)
        par_p5 = self._get_bytes(self.PAR_P5_l, 2, signed=True)
        par_p6 = self._get_bytes(self.PAR_P6, 1)
        par_p7 = self._get_bytes(self.PAR_P7, 1)
        par_p8 = self._get_bytes(self.PAR_P8_l, 2, signed=True)
        par_p9 = self._get_bytes(self.PAR_P9_l, 2, signed=True)
        par_p10 = self._get_bytes(self.PAR_P10, 1)
        self._p_calib = p_cal(par_p1=par_p1, par_p2=par_p2, par_p3=par_p3,
                              par_p4=par_p4, par_p5=par_p5, par_p6=par_p6,
                              par_p7=par_p7, par_p8=par_p8, par_p9=par_p9,
                              par_p10=par_p10)

        # Humidity
        par_h1 = self._get_bytes(self.PAR_H1_h, 1) << 4
        par_h1 += self._get_bits(self._get_bytes(self.PAR_H1_l, 1), 4, 4)
        par_h2 = self._get_bytes(self.PAR_H2_h, 1) << 4
        par_h2 += self._get_bits(self._get_bytes(self.PAR_H2_l, 1), 4, 4)
        par_h3 = self._get_bytes(self.PAR_H3, 1, signed=True)
        par_h4 = self._get_bytes(self.PAR_H4, 1, signed=True)
        par_h5 = self._get_bytes(self.PAR_H5, 1, signed=True)
        par_h6 = self._get_bytes(self.PAR_H6, 1)
        par_h7 = self._get_bytes(self.PAR_H7, 1, signed=True)
        self._h_calib = h_cal(par_h1=par_h1, par_h2=par_h2, par_h3=par_h3,
                              par_h4=par_h4, par_h5=par_h5, par_h6=par_h6,
                              par_h7=par_h7)
        
        # Gas
        par_g1 = self._get_bytes(self.PAR_G1, 1)
        par_g2 = self._get_bytes(self.PAR_G2_L, 2, signed=True)
        par_g3 = self._get_bytes(self.PAR_G3, 1)
        self._g_calib = g_cal(par_g1=par_g1, par_g2=par_g2, par_g3=par_g3)
        self._res_heat_range = self._get_bits(self._get_bytes(self.RES_HEAT_RANGE, 1), 2, 4)

    # TODO: Check maybe remove the option to get one byte
    def _get_bytes(self, low_byte_addr, byte_num, signed=False, rev=False):
        """Get lsb and msb and make a number."""

        data = self.hardware_interfaces[self._i2c].read(self.BME_ADDRESS,
                                                        low_byte_addr,
                                                        byte_num=byte_num)
        # Make it a list if it is one element
        data = data if isinstance(data, list) else [data]
        
        # Reverse it
        if rev:
            data.reverse()

        res = 0
        for (i, d) in enumerate(data):
            res += d << (i*8)

        power = byte_num*8 - 1
        whole = 2**(power+1) - 1
        if signed:
            res = res if res < (2**power - 1) else -((whole ^ res) + 1)

        return res

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

    @property
    def t_oversample(self):
        return self._t_oversample

    @t_oversample.setter
    def t_oversample(self, value):
        self._t_oversample = value

        # Set osrs_t
        self._set_register(self.CTRL_MEAS, self.OSRS_T_BITS,
                           self.OSRS_T, self.OVERSAMPLING[value])

    @property
    def p_oversample(self):
        return self._p_oversample

    @p_oversample.setter
    def p_oversample(self, value):
        self._p_oversample = value

        # Set osrs_p
        self._set_register(self.CTRL_MEAS, self.OSRS_P_BITS,
                           self.OSRS_P, self.OVERSAMPLING[value])

    @property
    def h_oversample(self):
        return self._h_oversample

    @h_oversample.setter
    def h_oversample(self, value):
        self._h_oversample = value

        # Set osrs_h
        self._set_register(self.CTRL_HUM, self.OSRS_H_BITS,
                           self.OSRS_H, self.OVERSAMPLING[value])

    @property
    def iir_coef(self):
        return self._iir_coef

    @iir_coef.setter
    def iir_coef(self, value):
        self._iir_coef = value

        # Set osrs_t
        self._set_register(self.CONFIG, self.FILTER_BITS,
                           self.FILTER, self.IIR[value])

    @property
    def gas_status(self):
        return self._gas_status

    @gas_status.setter
    def gas_status(self, value):
        self._gas_status = value

        # Set register
        self._set_register(self.CTRL_GAS_1, self.RUN_GUS_BITS,
                           self.RUN_GUS, value)

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
    def t_fine(self):
        return self._t_fine

    @property
    def res_heat_range(self):
        return self._res_heat_range
