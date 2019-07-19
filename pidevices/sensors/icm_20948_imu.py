from ..devices import Sensor


class ICM_20948(Sensor):
    """Sparkfun icm-20948 imu."""

    # Registers
    # User Bank 0
    WHO_AM_I = 0x00
    USER_CTRL = 0x03
    LP_CONFIG = 0x05
    PWR_MGMT_1 = 0x06
    PWR_MGMT_2 = 0x07
    INT_PIN_CFG = 0x0F
    INT_ENABLE = 0x10
    INT_ENABLE_1 = 0x11
    INT_ENABLE_2 = 0x12
    INT_ENABLE_3 = 0x13
    I2C_MST_STATUS = 0x17
    INT_STATUS = 0x19
    INT_STATUS_1 = 0x1A
    INT_STATUS_2 = 0x1B
    INT_STATUS_3 = 0x1C
    DELAY_TIME_H = 0x28
    DELAY_TIME_L = 0x29
    ACCEL_XOUT_H = 0x2D
    ACCEL_XOUT_L = 0x2E 
    ACCEL_YOUT_H = 0x2F 
    ACCEL_YOUT_L = 0x30 
    ACCEL_ZOUT_H = 0x31 
    ACCEL_ZOUT_L = 0x32 
    GYRO_XOUT_H = 0x33
    GYRO_XOUT_L = 0x34 
    GYRO_YOUT_H = 0x35 
    GYRO_YOUT_L = 0x36 
    GYRO_ZOUT_H = 0x37 
    GYRO_ZOUT_L = 0x38 
    TEMP_OUT_H = 0x39
    TEMP_OUT_L = 0x3A
    EXT_SLV_SENS_DATA_00 = 0x3B
    EXT_SLV_SENS_DATA_01 = 0x3C 
    EXT_SLV_SENS_DATA_02 = 0x3D
    EXT_SLV_SENS_DATA_03 = 0x3E
    EXT_SLV_SENS_DATA_04 = 0x3F
    EXT_SLV_SENS_DATA_05 = 0x40 
    EXT_SLV_SENS_DATA_06 = 0x41 
    EXT_SLV_SENS_DATA_07 = 0x42 
    EXT_SLV_SENS_DATA_08 = 0x43 
    EXT_SLV_SENS_DATA_09 = 0x44 
    EXT_SLV_SENS_DATA_00 = 0x45 
    EXT_SLV_SENS_DATA_11 = 0x46 
    EXT_SLV_SENS_DATA_12 = 0x47 
    EXT_SLV_SENS_DATA_13 = 0x48 
    EXT_SLV_SENS_DATA_14 = 0x49 
    EXT_SLV_SENS_DATA_15 = 0x4A 
    EXT_SLV_SENS_DATA_16 = 0x4B 
    EXT_SLV_SENS_DATA_17 = 0x4C 
    EXT_SLV_SENS_DATA_18 = 0x4D 
    EXT_SLV_SENS_DATA_19 = 0x4E 
    EXT_SLV_SENS_DATA_20 = 0x4F 
    EXT_SLV_SENS_DATA_21 = 0x50 
    EXT_SLV_SENS_DATA_22 = 0x51 
    EXT_SLV_SENS_DATA_23 = 0x52 
    FIFO_EN_1 = 0x66
    FIFO_EN_2 = 0x67
    FIFO_RST = 0x68
    FIFO_MODE = 0x69
    FIFO_COUNT_H = 0x70
    FIFO_COUNT_L = 0x71
    FIFO_R_W = 0x72
    DATA_RDY_STATUS = 0x74
    FIFO_CFG = 0x76
    REG_BANK_SEL = 0x7F

    # Shifts and bits per register

    # USER_CTRL
    DMP_EN = 7
    DMP_EN_BITS = 1
    FIFO_EN = 6
    FIFO_EN_BITS = 1
    I2C_MST_EN = 5
    I2C_MST_EN_BITS = 1
    I2C_IF_DIS = 4
    I2C_IF_DIS_BITS = 1
    DMP_RST = 3
    DMP_RST_BITS = 1
    SRAM_RST = 2
    SRAM_RST_BITS = 1
    I2C_MST_RST = 1
    I2C_MST_RST_BITS = 1
    
    # LP_CONFIG
    I2C_MST_CYCLE = 6
    I2C_MST_CYCLE_BITS = 1
    ACCEL_CYCLE = 5
    ACCEL_CYCLE_BITS = 1
    GYRO_CYCLE = 4
    GYRO_CYCLE_BITS = 1

    # PWR_MGMT_1
    DEVICE_RESET = 7
    DEVICE_RESET_BITS = 1
    SLEEP = 6
    SLEEP_BITS = 1
    LP_EN = 5
    LP_EN_BITS = 1
    TEMP_DIS = 3
    TEMP_DIS_BITS = 1
    CLKSEL = 0
    CLKSEL_BITS = 3

    # PWR_MGMT_2
    DISABLE_ACCEL = 3
    DISABLE_ACCEL_BITS = 3
    DISABLE_GYRO = 0
    DISABLE_GYRO_BITS = 3

    # INT_PIN_CFG
    INT1_ACTL = 7 
    INT1_ACTL_BITS = 1
    INT1_OPEN = 6
    INT1_OPEN_BITS = 1
    INT1_LATCH_EN = 5
    INT1_LATCH_EN_BITS = 1
    INT1_ANYRD_2CLEAR = 4
    INT1_ANYRD_2CLEAR_BITS = 1
    ACTL_FSYNC = 3
    ACTL_FSYNC_BITS = 1
    FSYNC_INT_MODE_EN = 2
    FSYNC_INT_MODE_EN_BITS = 1
    BYPASS_EN = 1
    BYPASS_EN_BITS = 1

    # INT_ENABLE
    REG_WOF_EN = 7
    REG_WOF_EN_BITS = 1
    WOM_INT_EN = 3
    WOM_INT_EN_BITS = 1
    PLL_RDY_EN = 2
    PLL_RDY_EN_BITS = 1
    DMP_INT1_EN = 1
    DMP_INT1_EN_BITS = 1
    I2C_MST_INT_EN = 0
    I2C_MST_INT_EN_BITS = 1

    # INT_ENABLE_1
    #RAW_DATA_0_RDY_EN = 0
    #RAW_DATA_0_RDY_EN_BITS = 1

    # INT_ENABLE_2
    #FIFO_OVERFLOW_EN = 0
    #FIFO_OVERFLOW_EN_BITS = 5

    # INT_ENABLE_3
    #FIFO_WM_EN = 0
    #FIFO_WM_EN_BITS = 5

    # I2C_MST_STATUS
    PASS_THROUGH = 7
    PASS_THROUGH_BITS = 1
    I2C_SLV4_DONE = 6
    I2C_SLV4_DONE_BITS = 1
    I2C_LOST_ARB = 5
    I2C_LOST_ARB_BITS = 1
    I2C_SLV4_NACK = 4
    I2C_SLV4_NACK_BITS = 1
    I2C_SLV3_NACK = 3
    I2C_SLV3_NACK_BITS = 1
    I2C_SLV2_NACK = 2
    I2C_SLV2_NACK_BITS = 1
    I2C_SLV1_NACK = 1
    I2C_SLV1_NACK_BITS = 1
    I2C_SLV0_NACK = 0
    I2C_SLV0_NACK_BITS = 1
    
    # INT_STATUS
    WOM_INT = 3
    WOM_INT_BITS = 1
    PLL_RDY_INT = 2
    PLL_RDY_INT_BITS = 1
    DMP_INT1 = 1
    DMP_INT1_BITS = 1
    I2C_MST_INT = 0
    I2C_MST_INT_BITS = 1

    # INT_STATUS_1
    #RAW_DATA_0_RDY_INT = 0
    #RAW_DATA_0_RDY_INT_BITS = 1

    # INT_STATUS_2
    #FIFO_OVERFLOW_INT = 0
    #FIFO_OVERFLOW_INT_BITS = 5

    # INT_STATUS_3
    #FIFO_WM_INT = 0
    #FIFO_WM_INT_BITS = 5

    # FIFO_EN_1
    SLV_3_FIFO_EN = 3
    SLV_3_FIFO_EN_BITS = 1
    SLV_2_FIFO_EN = 2
    SLV_2_FIFO_EN_BITS = 1
    SLV_1_FIFO_EN = 1
    SLV_1_FIFO_EN_BITS = 1
    SLV_0_FIFO_EN = 0
    SLV_0_FIFO_EN_BITS = 1

    # FIFO_EN_2
    ACCEL_FIFO_EN = 4
    ACCEL_FIFO_EN_BITS = 1
    GYRO_Z_FIFO_EN = 3
    GYRO_Z_FIFO_EN_BITS = 1
    GYRO_Y_FIFO_EN = 2
    GYRO_Y_FIFO_EN_BITS = 1
    GYRO_X_FIFO_EN = 1
    GYRO_X_FIFO_EN_BITS = 1
    TEMP_FIFO_EN = 0
    TEMP_FIFO_EN_BITS = 1

    # FIFO_RST
    #FIFO_RESET = 0
    #FIFO_RESET_BITS = 5

    # FIFO_MODE
    #FIFO_MODE = 0
    #FIFO_MODE_BITS = 5

    # FIFO_COUNT_H
    #FIFO_CNT = 0
    #FIFO_CNT_H_BITS = 5

    # DATA_RDY_STATUS
    WOF_STATUS = 7
    WOF_STATUS_BITS = 1
    RAW_DATA_RDY = 0
    RAW_DATA_RDY_BITS = 4

    # REG_BANK_SEL
    USER_BANK = 4
    USER_BANK_BITS = 2

    # User bank 1
    SELF_TEST_X_GYRO = 0x02
    SELF_TEST_Y_GYRO = 0x03 
    SELF_TEST_Z_GYRO = 0x04 
    SELF_TEST_X_ACCEL = 0x0E 
    SELF_TEST_Y_ACCEL = 0x0F 
    SELF_TEST_Z_ACCEL = 0x10
    XA_OFFS_H = 0x14 
    XA_OFFS_L = 0x15 
    YA_OFFS_H = 0x17 
    YA_OFFS_L = 0x18 
    ZA_OFFS_H = 0x1A 
    ZA_OFFS_L = 0x1B 
    TIMEBASE_CORRECTION_PLL = 0x28
    REG_BANK_SEL = 0x7F

    # Bits and shifts

    # XA_OFFS_L
    XA_OFFS = 1
    XA_OFFS_BITS = 7

    # YA_OFFS_L
    YA_OFFS = 1
    YA_OFFS_BITS = 7

    # ZA_OFFS_L
    ZA_OFFS = 1
    ZA_OFFS_BITS = 7

    # User bank 2
    GYRO_SMPLRT_DIV = 0x00
    GYRO_CONFIG_1 = 0x01
    GYRO_CONFIG_2 = 0x02
    XG_OFFS_USR_H = 0x03 
    XG_OFFS_USR_L = 0x04 
    YG_OFFS_USR_H = 0x05 
    YG_OFFS_USR_L = 0x06 
    ZG_OFFS_USR_H = 0x07 
    ZG_OFFS_USR_L = 0x08 
    ODR_ALIGN_EN = 0x09
    ACCEL_SMPLRT_DIV_1 = 0x10
    ACCEL_SMPLRT_DIV_2 = 0x11
    ACCEL_INTEL_CTRL = 0x12
    ACCEL_WOM_THR = 0x13
    ACCEL_CONFIG = 0x14
    ACCEL_CONFIG_2 = 0x15
    FSYNC_CONFIG = 0x52
    TEMP_CONFIG = 0x53
    MOD_CTRL_USR = 0x54
    REG_BANK_SEL = 0x7F

    # Bits and shifts
    
    # GYRO_CONFIG_1
    GYRO_DLPFCFG = 3
    GYRO_DLPFCFG_BITS = 3
    GYRO_FS_SEL = 1
    GYRO_FS_SEL_BITS = 2
    GYRO_FCHOICE = 0
    GYRO_FCHOICE_BITS = 1

    # GYRO_CONFIG_2
    XGYRO_CTEN = 5
    XGYRO_CTEN_BITS = 1
    YGYRO_CTEN = 4
    YGYRO_CTEN_BITS = 1
    ZGYRO_CTEN = 3
    ZGYRO_CTEN_BITS = 1
    GYRO_AVGCFG = 0
    GYRO_AVGCFG_BITS = 3

    # ACCEL_INTEL_CTRL
    ACCEL_INTEL_EN = 1
    ACCEL_INTEL_EN_BITS = 1
    ACCEL_INTEL_MODE_INT = 1
    ACCEL_INTEL_MODE_INT_BITS = 1

    # ACCEL_CONFIG
    ACCEL_DLPFCFG = 3
    ACCEL_DLPFCFG_BITS = 3
    ACCEL_FS_SEL = 1
    ACCEL_FS_SEL_BITS = 2
    ACCEL_FCHOICE = 0
    ACCEL_FCHOICE_BITS = 1

    # ACCEL_CONFIG_2
    AX_ST_EN_REG = 4
    AX_ST_EN_REG_BITS = 1
    AY_ST_EN_REG = 3
    AY_ST_EN_REG_BITS = 1
    AZ_ST_EN_REG = 2
    AZ_ST_EN_REG_BITS = 1
    DEC_3_CFG = 0
    DEC_3_CFG_BITS = 2

    # FSYNC_CONFIG
    DELAY_TIME_EN = 7
    DELAY_TIME_EN_BITS = 1
    WOF_DEGLITCH_EN = 5
    WOF_DEGLITCH_EN_BITS = 1
    WOF_EDGE_INT = 4
    WOF_EDGE_INT_BITS = 1
    EXT_SYNC_SET = 0
    EXT_SYNC_SET_BITS = 4

    # User Bank 3
    I2C_MST_ODR_CONFIG = 0x00
    I2C_MST_CTRL = 0x01
    I2C_MST_DELAY_CTRL = 0x02
    I2C_SLV0_ADDR = 0x03
    I2C_SLV0_REG = 0x04
    I2C_SLV0_CTRL = 0x05
    I2C_SLV0_DO = 0x06
    I2C_SLV1_ADDR = 0x07
    I2C_SLV1_REG = 0x08
    I2C_SLV1_CTRL = 0x09
    I2C_SLV1_DO = 0x0A
    I2C_SLV2_ADDR = 0x0B
    I2C_SLV2_REG = 0x0C
    I2C_SLV2_CTRL = 0x0D
    I2C_SLV2_DO = 0x0E
    I2C_SLV3_ADDR = 0x0F
    I2C_SLV3_REG = 0x10
    I2C_SLV3_CTRL = 0x11
    I2C_SLV3_DO = 0x12
    I2C_SLV4_ADDR = 0x13
    I2C_SLV4_REG = 0x14
    I2C_SLV4_CTRL = 0x15
    I2C_SLV4_DO = 0x16
    I2C_SLV4_DI = 0x17
    REG_BANK_SEL = 0x7F

    # Bits and shifts

    # I2C_MST_ODR_CONFIG

    # I2C_MST_CTRL
    MULT_MST_EN = 7
    MULT_MST_EN_BITS = 1
    I2C_MST_P_NSR = 4
    I2C_MST_P_NSR_BITS = 1
    I2C_MST_CLK = 0
    I2C_MST_CLK_BITS = 4

    # I2C_MST_DELAY_CTRL
    DELAY_ES_SHADOW = 7
    DELAY_ES_SHADOW_BITS = 1
    I2C_SLV4_DELAY_EN = 4
    I2C_SLV4_DELAY_EN_BTIS = 1
    I2C_SLV3_DELAY_EN = 3
    I2C_SLV3_DELAY_EN_BTIS = 1
    I2C_SLV2_DELAY_EN = 2
    I2C_SLV2_DELAY_EN_BTIS = 1
    I2C_SLV1_DELAY_EN = 1
    I2C_SLV1_DELAY_EN_BTIS = 1
    I2C_SLV0_DELAY_EN = 0
    I2C_SLV0_DELAY_EN_BTIS = 1

    # I2C_SLV0_ADDR
    I2C_SLV0_RNW = 7
    I2C_SLV0_RNW_BITS = 1
    I2C_ID_0 = 0
    I2C_ID_0_BITS = 7

    # I2C_SLV1_CTRL
    I2C_SLV0_EN = 7
    I2C_SLV0_EN_BITS = 1
    I2C_SLV0_BYTE_SW = 6
    I2C_SLV0_BYTE_SW_BITS = 1
    I2C_SLV0_REG_DIS = 5
    I2C_SLV0_REG_DIS_BITS = 1
    I2C_SLV0_GRP = 4
    I2C_SLV0_GRP_BITS = 1
    I2C_SLV0_LENG = 0
    I2C_SLV0_LENG_BITS = 4

    # I2C_SLV1_ADDR
    I2C_SLV1_RNW = 7
    I2C_SLV1_RNW_BITS = 1
    I2C_ID_1 = 0
    I2C_ID_1_BITS = 7

    # I2C_SLV1_CTRL
    I2C_SLV1_EN = 7
    I2C_SLV1_EN_BITS = 1
    I2C_SLV1_BYTE_SW = 6
    I2C_SLV1_BYTE_SW_BITS = 1
    I2C_SLV1_REG_DIS = 5
    I2C_SLV1_REG_DIS_BITS = 1
    I2C_SLV1_GRP = 4
    I2C_SLV1_GRP_BITS = 1
    I2C_SLV1_LENG = 0
    I2C_SLV1_LENG_BITS = 4

    # I2C_SLV2_ADDR
    I2C_SLV2_RNW = 7
    I2C_SLV2_RNW_BITS = 1
    I2C_ID_2 = 0
    I2C_ID_2_BITS = 7

    # I2C_SLV1_CTRL
    I2C_SLV2_EN = 7
    I2C_SLV2_EN_BITS = 1
    I2C_SLV2_BYTE_SW = 6
    I2C_SLV2_BYTE_SW_BITS = 1
    I2C_SLV2_REG_DIS = 5
    I2C_SLV2_REG_DIS_BITS = 1
    I2C_SLV2_GRP = 4
    I2C_SLV2_GRP_BITS = 1
    I2C_SLV2_LENG = 0
    I2C_SLV2_LENG_BITS = 4

    # I2C_SLV3_ADDR
    I2C_SLV3_RNW = 7
    I2C_SLV3_RNW_BITS = 1
    I2C_ID_3 = 0
    I2C_ID_3_BITS = 7

    # I2C_SLV1_CTRL
    I2C_SLV3_EN = 7
    I2C_SLV3_EN_BITS = 1
    I2C_SLV3_BYTE_SW = 6
    I2C_SLV3_BYTE_SW_BITS = 1
    I2C_SLV3_REG_DIS = 5
    I2C_SLV3_REG_DIS_BITS = 1
    I2C_SLV3_GRP = 4
    I2C_SLV3_GRP_BITS = 1
    I2C_SLV3_LENG = 0
    I2C_SLV3_LENG_BITS = 4

    # I2C_SLV4_ADDR
    I2C_SLV4_RNW = 7
    I2C_SLV4_RNW_BITS = 1
    I2C_ID_4 = 0
    I2C_ID_4_BITS = 7

    # I2C_SLV1_CTRL
    I2C_SLV4_EN = 7
    I2C_SLV4_EN_BITS = 1
    I2C_SLV4_BYTE_SW = 6
    I2C_SLV4_BYTE_SW_BITS = 1
    I2C_SLV4_REG_DIS = 5
    I2C_SLV4_REG_DIS_BITS = 1
    I2C_SLV4_GRP = 4
    I2C_SLV4_GRP_BITS = 1
    I2C_SLV4_LENG = 0
    I2C_SLV4_LENG_BITS = 4

    def __init__(self, name='', max_data_length):
        """Constructor."""

        self.ICM_ADDRESS = 0x68

    def start(self):
        """Initialize hardware and os resources."""
        pass

    def read(self):
        pass

    def stop(self):
        pass

    # Copy the function names from sparkfun c library
    def _get_temp_c(self):
        pass

    def _get_gyr_dps(self, axis):
        pass

    def _get_acc_mg(self, axis):
        pass

    def _get_mag_ut(self, axis):
        pass
    
    # Magenetometer in micro teslas
    def _mag_x(self):
        pass

    def _mag_y(self):
        pass

    def _mag_z(self):
        pass

    # Accel in g's
    def _acc_x(self):
        pass

    def _acc_y(self):
        pass

    def _acc_z(self):
        pass

    # Gyroscope in degrees per second
    def _gyr_x(self):
        pass

    def _gyr_y(self):
        pass

    def _gyr_z(self):
        pass

    # Temperature in degrees of celcius
    def _temp(self):
        pass

    # Set the bank
    def _set_bank(self, bank):
        pass

    def _reset(self):
        """Software reset."""
        pass

    def _sleep(self, on=0):
        """Sleep modoe"""
        pass

    def _low_power(self, on=1):
        """Set the low power mode."""
        pass

    def _set_clock_source(self):
        pass

    def _data_ready(self):
        """Return true if data are ready."""
        pass

    def _set_sample_mode(self, sensor, mode):
        """Set accelerated sample mode for accel, gyro and i2c."""
        pass

    def _set_full_scale(self):
        pass

    def _set_dlpf_cfg(self, value):
        pass

    def _enable_dlpg(self, enable):
        pass

    def _set_sample_rate(self, rate):
        pass

    def _clear_interrupts(self):
        pass

    def _cfg_int_open_drain(self):
        pass

    def _cfg_latch(self):
        pass

    def _cfg_int_any_read_to_clear(self):
        pass

    def _cfg_fsync_active_low(self):
        pass

    def _cfg_fsync_int_mode(self):
        pass

    def _int_enable_i2c(self):
        pass

    def _int_enable_dmo(self):
        pass

    def _int_enable_pll(self):
        pass

    def _int_enbale_wof(self):
        pass

    def _int_enable_raw_data_ready(self):
        pass

    def _int_enable_overflow_fifo(self):
        pass

    def _int_enable_wm_fifo(self):
        pass

    def _i2c_master_passthrough(self):
        pass
    
    def _i2c_master_enable(self):
        pass

    def _i2c_master_config_slave(self):
        pass

    def _i2c_master_slv4_trans(self):
        pass

    def _i2c_master_single_w(self):
        pass

    def _i2c_master_single_r(self):
        pass

    def _startup_def(self):
        pass

    def _start_magne(self):
        pass

    def _get_mang_data(self):
        pass
