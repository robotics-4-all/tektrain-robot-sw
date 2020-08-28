from pidevices import PCA9685 






controller = PCA9685(bus=1, frequency=50)
controller.stop()
