#!/usr/bin/env python
from pidevices.sensors.cv2_camera import VirtualCamera
import time
import cv2
import sys
import numpy as np
 
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Wrong number of arguments... expected <device>")
        sys.exit(-1)

    device = int(sys.argv[1])
    camera = VirtualCamera(vdevice=device, framerate = 20)

    image = camera.read()

    camera.read_continuous()

    try:
        while True:
            cv2.imwrite("imtest.jpg", camera.get_frame().frame)

            time.sleep(1)
    except KeyboardInterrupt as e:
        camera.stop_continuous()

    camera.stop()