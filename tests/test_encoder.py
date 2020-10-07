import time
from pidevices.sensors import DfRobotWheelEncoderRpiGPIO


encoder = DfRobotWheelEncoderRpiGPIO(pin=23, name="ENC_LEFT")
encoder.stop()
encoder.start()

for i in range(0,100):
    
    rpm = encoder.read_rpm()
    time.sleep(0.1)
    print("Rpm is:", rpm)

encoder.stop()