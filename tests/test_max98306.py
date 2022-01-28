import unittest
import traceback
import time
from pidevices import Max98306, Max98306Error


class TestMAX98306(unittest.TestCase):
    def test_correct_input(self):
        try:
            amp = Max98306(shutdown_pin=4)
            
            amp.enable()
            time.sleep(1)
            amp.disable()
            
            amp.stop()
        except:
            traceback.print_exc(file=sys.stdout)
            self.assertTrue(False)

    def test_invalid_input_pin(self):
        try:
            should_fail = False
            
            try:
                amp = Max98306(shutdown_pin="invalid_pin")
            except Max98306Error as e:
                should_fail = True

                print("Caught error as i should with msg: {}".format(e))

            self.assertTrue(should_fail)
        except:
            traceback.print_exc(file=sys.stdout)
            self.assertTrue(False)

if __name__ == "__main__":
    unittest.main()