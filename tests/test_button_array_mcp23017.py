import unittest
import time
from pidevices.sensors.button_array import ButtonArrayMcp23017


class TestButtonArrayMcp23017(unittest.TestCase):
    
    # def test_read(self):
    #     array = ButtonArrayMcp23017(["B_0", "B_1", "B_2", "B_3", "B_4", "B_5",
    #                                  "A_1", "A_6", "A_5", "A_2", "A_3", "A_4"],
    #                                 direction="down", bounce=200)

    #     pin = 0
    #     print("Read button {} for 5s".format(pin))
    #     t_s = time.time()
    #     while time.time() - t_s < 5:
    #         print(array.read(pin))
    #         time.sleep(0.5)

    #     pin = 1
    #     print("Read button {} for 5s".format(pin))
    #     t_s = time.time()
    #     while time.time() - t_s < 5:
    #         print(array.read(pin))
    #         time.sleep(0.5)

    #     pin = 2
    #     print("Read button {} for 5s".format(pin))
    #     t_s = time.time()
    #     while time.time() - t_s < 5:
    #         print(array.read(pin))
    #         time.sleep(0.5)

    #     pin = 3
    #     print("Read button {} for 5s".format(pin))
    #     t_s = time.time()
    #     while time.time() - t_s < 5:
    #         print(array.read(pin))
    #         time.sleep(0.5)

    #     pin = 4
    #     print("Read button {} for 5s".format(pin))
    #     t_s = time.time()
    #     while time.time() - t_s < 5:
    #         print(array.read(pin))
    #         time.sleep(0.5)

    #     pin = 5
    #     print("Read button {} for 5s".format(pin))
    #     t_s = time.time()
    #     while time.time() - t_s < 5:
    #         print(array.read(pin))
    #         time.sleep(0.5)

    #     pin = 6
    #     print("Read button {} for 5s".format(pin))
    #     t_s = time.time()
    #     while time.time() - t_s < 5:
    #         print(array.read(pin))
    #         time.sleep(0.5)

    #     pin = 7
    #     print("Read button {} for 5s".format(pin))
    #     t_s = time.time()
    #     while time.time() - t_s < 5:
    #         print(array.read(pin))
    #         time.sleep(0.5)

    #     pin = 8
    #     print("Read button {} for 5s".format(pin))
    #     t_s = time.time()
    #     while time.time() - t_s < 5:
    #         print(array.read(pin))
    #         time.sleep(0.5)

    #     pin = 9
    #     print("Read button {} for 5s".format(pin))
    #     t_s = time.time()
    #     while time.time() - t_s < 5:
    #         print(array.read(pin))
    #         time.sleep(0.5)

    #     pin = 10 
    #     print("Read button {} for 5s".format(pin))
    #     t_s = time.time()
    #     while time.time() - t_s < 5:
    #         print(array.read(pin))
    #         time.sleep(0.5)

    #     pin = 11
    #     print("Read button {} for 5s".format(pin))
    #     t_s = time.time()
    #     while time.time() - t_s < 5:
    #         print(array.read(pin))
    #         time.sleep(0.5)
    
    # def test_wait(self):
    #     array = ButtonArrayMcp23017(["B_0", "B_1", "B_2", "B_3", "B_4", "B_5",
    #                                  "A_1", "A_6", "A_5", "A_2", "A_3", "A_4"],
    #                                 direction="down", bounce=200)
    #     button = 0
    #     array.wait_for_press(button)
    #     print("Pressed {}".format(button))

    #     button = 1
    #     array.wait_for_press(button)
    #     print("Pressed {}".format(button))

    #     button = 2
    #     array.wait_for_press(button)
    #     print("Pressed {}".format(button))

    #     button = 3
    #     array.wait_for_press(button)
    #     print("Pressed {}".format(button))

    #     button = 4
    #     array.wait_for_press(button)
    #     print("Pressed {}".format(button))

    #     button = 5
    #     array.wait_for_press(button)
    #     print("Pressed {}".format(button))

    #     button = 6
    #     array.wait_for_press(button)
    #     print("Pressed {}".format(button))

    #     button = 7
    #     array.wait_for_press(button)
    #     print("Pressed {}".format(button))

    #     button = 8
    #     array.wait_for_press(button)
    #     print("Pressed {}".format(button))

    #     button = 9
    #     array.wait_for_press(button)
    #     print("Pressed {}".format(button))

    #     button = 10
    #     array.wait_for_press(button)
    #     print("Pressed {}".format(button))

    #     button = 11
    #     array.wait_for_press(button)
    #     print("Pressed {}".format(button))
    
    def test_when_pressed(self):
        array = ButtonArrayMcp23017(["B_0", "B_1", "B_2", "B_3", "B_4", "B_5",
                                     "A_1", "A_6", "A_5", "A_2", "A_3", "A_4"],
                                    direction="down", bounce=200)

        # def f_0(pin):
        #     print("{} Interrupt on button {}".format(f_0.c, pin))
        #     f_0.c += 1
        # f_0.c = 0
        # pin = 0
        # array.when_pressed(pin, f_0, pin)

        # def f_1(pin):
        #     print("{} Interrupt on button {}".format(f_1.c, pin))
        #     f_1.c += 1
        # f_1.c = 0
        # pin = 1
        # array.when_pressed(pin, f_1, pin)

        # def f_2(pin):
        #     print("{} Interrupt on button {}".format(f_2.c, pin))
        #     f_2.c += 1
        # f_2.c = 0
        # pin = 2
        # array.when_pressed(pin, f_2, pin)

        # def f_3(pin):
        #     print("{} Interrupt on button {}".format(f_3.c, pin))
        #     f_3.c += 1
        # f_3.c = 0
        # pin = 3
        # array.when_pressed(pin, f_3, pin)

        # def f_4(pin):
        #     print("{} Interrupt on button {}".format(f_4.c, pin))
        #     f_4.c += 1
        # f_4.c = 0
        # pin = 4
        # array.when_pressed(pin, f_4, pin)

        # def f_5(pin):
        #     print("{} Interrupt on button {}".format(f_5.c, pin))
        #     f_5.c += 1
        # f_5.c = 0
        # pin = 5
        # array.when_pressed(pin, f_5, pin)

        # def f_6(pin):
        #     print("{} Interrupt on button {}".format(f_6.c, pin))
        #     f_6.c += 1
        # f_6.c = 0
        # pin = 6
        # array.when_pressed(pin, f_6, pin)

        # def f_7(pin):
        #     print("{} Interrupt on button {}".format(f_7.c, pin))
        #     f_7.c += 1
        # f_7.c = 0
        # pin = 7
        # array.when_pressed(pin, f_7, pin)

        # def f_8(pin):
        #     print("{} Interrupt on button {}".format(f_8.c, pin))
        #     f_8.c += 1
        # f_8.c = 0
        # pin = 8
        # array.when_pressed(pin, f_8, pin)

        # def f_9(pin):
        #     print("{} Interrupt on button {}".format(f_9.c, pin))
        #     f_9.c += 1
        # f_9.c = 0
        # pin = 9
        # array.when_pressed(pin, f_9, pin)

        # def f_10(pin):
        #     print("{} Interrupt on button {}".format(f_10.c, pin))
        #     f_10.c += 1
        # f_10.c = 0
        # pin = 10
        # array.when_pressed(pin, f_10, pin)

        # def f_11(pin):
        #     print("{} Interrupt on button {}".format(f_11.c, pin))
        #     f_11.c += 1
        # f_11.c = 0
        # pin = 11
        # array.when_pressed(pin, f_11, pin)

        def f(pin):
            print("{} Interrupt on button {}".format(counters[pin], pin))
            counters[pin] += 1
        counters = [0] * 12
        
        for i in range(12):
            array.when_pressed(i, f, i)
        
        buttons = [i for i in range(12)]
        array.enable_pressed(buttons)

        pin = 11
        print("Read button {} for 5s".format(pin))
        t_s = time.time()
        while time.time() - t_s < 10:
            #if array.read(pin):
            print("Pressed")
            time.sleep(0.5)

        print("Asynch mode")

        time.sleep(20)
        array.stop()
        

if __name__ == "__main__":
    unittest.main()
