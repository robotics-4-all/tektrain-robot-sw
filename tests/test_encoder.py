import time
from pidevices.sensors import DfRobotWheelEncoderMcp23017

ENC = "B_5"

encoder = DfRobotWheelEncoderMcp23017(pin=ENC, bus=1, address=0x22)
encoder.start()

for i in range(0,1000):
    time.sleep(0.01)
    val = encoder.read()
   
    print(val, encoder._counter)

encoder.stop()