from pidevices.sensors.df_robot_wheel_encoders import DfRobotWheelEncoderPiGPIO
from pidevices import DfrobotMotorControllerPiGPIO
import threading
import unittest
import time

is_alive = True

def threadCall(enc):
   global is_alive
   enc.start()

   while is_alive:
      val = enc.read()["rps"]
      print(f"Thread {threading.get_ident()} record: {val}")
      time.sleep(0.1)

   print(f"Thread {threading.get_ident()} Terminated")

class TestDfRobotEncodersPigpio(unittest.TestCase):
   def test_encoders(self):
      global is_alive

      motor_driver = DfrobotMotorControllerPiGPIO(E1=20, E2=21, M1=19, M2=26, resolution=1000, frequency=200)
      motor_driver.start()

      enc1 = DfRobotWheelEncoderPiGPIO(pin=23, resolution=10)
      enc2 = DfRobotWheelEncoderPiGPIO(pin=24, resolution=10)

      t1 = threading.Thread(target=threadCall, args=(enc1,), daemon=True)
      t2 = threading.Thread(target=threadCall, args=(enc2,), daemon=True)

      motor_driver.write(0.3, 0.3)

      t1.start()
      t2.start()

      time.sleep(5)

      is_alive = False
      
      time.sleep(0.5)

      motor_driver.stop()

if __name__ == "__main__":
   unittest.main()