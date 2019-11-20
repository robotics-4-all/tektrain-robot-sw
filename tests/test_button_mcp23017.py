import unittest
import time
from pidevices.sensors.button import ButtonMcp23017


class TestButtonMcp23017(unittest.TestCase):

    def test_read(self):
        button = ButtonMcp23017("A_0", direction="down", bus=5, address=0x20)

        t_start = time.time()
        while time.time() - t_start < 10:
            print(button.read())
            time.sleep(0.2)

        button.stop()

    def test_wait(self):
        button = ButtonMcp23017("A_0", direction="down", bus=5, address=0x20)
        button.wait_for_press()
        print("Pressed")
        #button.stop()

    def test_when_pressed(self):
        def test(a1, a2):
            print("{} args {} {}".format(test.c, a1, a2))
            test.c += 1
        test.c = 0 
        button = ButtonMcp23017("A_0", direction="down", edge="rising",
                                bounce=70, bus=5, address=0x20)
        button.when_pressed(test, 1, 2)
        t_start = time.time()
        while time.time() - t_start < 10:
            time.sleep(1)
        button.stop()


if __name__ == "__main__":
    unittest.main()
