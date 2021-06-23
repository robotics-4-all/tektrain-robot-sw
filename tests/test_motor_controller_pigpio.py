from pidevices import DfrobotMotorControllerPiGPIO
import unittest
import time

class TestPiGPioMotiorDriver(unittest.TestCase):
    def test_init_deinit(self):
        print("Testing initialization/deinitialization.")
        motor_driver = DfrobotMotorControllerPiGPIO(E1=20, E2=21, M1=19, M2=26, resolution=1000, frequency=200)
        
        motor_driver.start()
        motor_driver.start()

        motor_driver.write(0.3, 0.3)
        time.sleep(1)
        motor_driver.stop()

        motor_driver.write(0.3, 0.3)
        time.sleep(1)
        motor_driver.stop()

        motor_driver.write(0.3, 0.3)
        time.sleep(1)
        motor_driver.stop()

    def test_pwm_range(self):
        print("Testing pwm range.")
        motor_driver = DfrobotMotorControllerPiGPIO(E1=20, E2=21, M1=19, M2=26, resolution=1000, frequency=200)

        motor_driver.start()
        
        for i in range(0, 101):
            motor_driver.write(0.01 * i, 0.01 * i)
            time.sleep(0.05)
        
        for i in range(0, 101):
            motor_driver.write(1 - 0.01 * i, 1 - 0.01 * i)
            time.sleep(0.05)

        motor_driver.stop()


    def test_dir(self):
        print("Testing direction of movement")
        motor_driver = DfrobotMotorControllerPiGPIO(E1=20, E2=21, M1=19, M2=26, resolution=1000, frequency=200)
        
        motor_driver.start()

        pwm = 0.4

        motor_driver.write(pwm, pwm)
        time.sleep(3)

        motor_driver.write(pwm, -pwm)
        time.sleep(3)

        motor_driver.write(-pwm, -pwm)
        time.sleep(3)

        motor_driver.write(-pwm, pwm)
        time.sleep(3)
        
        motor_driver.stop()


if __name__ == '__main__':
    unittest.main()