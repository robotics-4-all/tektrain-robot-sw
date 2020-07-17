import unittest
import time
from pidevices.sensors.bme680 import BME680


class TestBME680(unittest.TestCase):

    def test_set_bits(self):
        sensor = BME680(1, 0)
        register = 0b11111111
        value = 0
        shift = 3
        bits = 3
        register = sensor._set_bits(register, value, bits, shift)
        #print(bin(register))

    def test_get_bits(self):
        sensor = BME680(1, 0)
        register = 0b00011100
        shift = 4
        bits = 3
        register = sensor._get_bits(register, bits, shift)
        #print(bin(register))

    def test_mode(self):
        pass

    def test_reset(self):
        t_over = 16
        sensor = BME680(1, 0, t_oversample=t_over)
        val = sensor._get_register(sensor.CTRL_MEAS, 
                                   sensor.OSRS_T_BITS,
                                   sensor.OSRS_T)
        sensor._reset()
        val = sensor._get_register(sensor.CTRL_MEAS, 
                                   sensor.OSRS_T_BITS,
                                   sensor.OSRS_T)
        self.assertEqual(val, 0, "Should be zero.")

    def test_init(self):
        t_over = 16
        h_over = 1
        p_over = 0
        iir_coef = 3
        sensor = BME680(1, 0,
                        t_oversample=t_over, 
                        h_oversample=h_over,
                        p_oversample=p_over,
                        iir_coef=iir_coef)
        t_over = sensor.OVERSAMPLING[t_over]
        p_over = sensor.OVERSAMPLING[p_over]
        h_over = sensor.OVERSAMPLING[h_over]
        iir_coef = sensor.IIR[iir_coef]

        ctrl_meas = \
            sensor.hardware_interfaces[sensor._i2c].read(sensor.BME_ADDRESS,
                                                         sensor.CTRL_MEAS)
        ctrl_hum = \
            sensor.hardware_interfaces[sensor._i2c].read(sensor.BME_ADDRESS,
                                                         sensor.CTRL_HUM)
        config = sensor.hardware_interfaces[sensor._i2c].read(sensor.BME_ADDRESS,
                                                              sensor.CONFIG)

        t = sensor._get_bits(ctrl_meas, sensor.OSRS_T_BITS, sensor.OSRS_T)
        p = sensor._get_bits(ctrl_meas, sensor.OSRS_P_BITS, sensor.OSRS_P)
        h = sensor._get_bits(ctrl_hum, sensor.OSRS_H_BITS, sensor.OSRS_H)
        iir = sensor._get_bits(config, sensor.FILTER_BITS, sensor.FILTER)

        self.assertEqual(t, t_over, "Should be {}".format(t_over))
        self.assertEqual(h, h_over, "Should be {}".format(h_over))
        self.assertEqual(p, p_over, "Should be {}".format(p_over))
        self.assertEqual(iir, iir_coef, "Should be {}".format(iir_coef))

    def test_read(self):
        t_over = 8
        h_over = 2
        p_over = 4
        iir_coef = 3
        g_status = 1
        sensor = BME680(1, 0,
                        t_oversample=t_over, 
                        h_oversample=h_over,
                        p_oversample=p_over,
                        iir_coef=iir_coef,
                        gas_status=g_status)
        sensor.set_heating_temp([0], [320])
        sensor.set_heating_time([0], [100])
        sensor.set_nb_conv(0)
        for i in range(10):
            data = sensor.read()
            print("Temp: {}\tPres: {}\tHumi: {}\tGas: {}".format(data.temp,
                                                                 data.pres,
                                                                 data.hum,
                                                                 data.gas))
            time.sleep(1)

        data = sensor.read(hum=False, gas=False, temp=False)
        print("Temp: {}\tPres: {}\tHumi: {}\tGas: {}".format(data.temp,
                                                             data.pres,
                                                             data.hum,
                                                             data.gas))

        data = sensor.read()
        print("Temp: {}\tPres: {}\tHumi: {}\tGas: {}".format(data.temp,
                                                             data.pres,
                                                             data.hum,
                                                             data.gas))

    def test_get_bytes(self):
        sensor = BME680(1, 0)
        sensor._get_bytes(sensor.PAR_T1_l, 2)
        sensor._get_bytes(sensor.PAR_T1_l, 1)


if __name__ == "__main__":
    unittest.main()
