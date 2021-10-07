#!/usr/bin/env python
from pidevices.sensors.cv2_camera import VirtualCamera, Dims
import time
import cv2
import sys
import base64
import numpy as np
 
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Wrong number of arguments... expected <device>")
        sys.exit(-1)

    device = int(sys.argv[1])
    camera = VirtualCamera(vdevice=device, framerate = 20)
    
    image = camera.read()

    camera.read_continuous(image_dims=Dims(width=640, height=480))

    try:
        while True:
            data = camera.get_frame().data

            data = base64.b64encode(data).decode("ascii")
            frame = base64.b64decode(data.encode("ascii"))

            image_array = np.frombuffer(frame, dtype = "uint8")
            image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

            cv2.imwrite("imtest.bmp", image)

            time.sleep(1)
    except KeyboardInterrupt as e:
        camera.stop_continuous()

    camera.stop()