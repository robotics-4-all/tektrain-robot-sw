from pidevices.actuators import DfrobotMotorControllerPiGPIO
from pidevices import CytronLfLSS05Mcp23017
import time
import threading
import numpy as np



class PID:
    def __init__(self, sample_rate, kp, ki, kd):
        self._sample_period = float(1 / sample_rate)

        self._current_time = time.time()
        self._prev_time = self._current_time
        
        self._prev_error = 0.0

        self._windup = 20.0

        self._kp = kp
        self._ki = ki
        self._kd = kd 

        self._Pterm = 0.0
        self._Iterm = 0.0
        self._Dterm = 0.0

        self._low_pass = [0, 0, 0]
        self._filter_size = 4

    @property
    def sample_rate(self):
        return 1 / self._sample_period

    @sample_rate.setter
    def sample_rate(self, rate):
        if rate > 0:
            self._sample_period = float(1 / rate)
    
    @property
    def windup(self):
        return self._windup

    @windup.setter
    def windup(self, windup):
        if rate > 0:
            self._windup = windup

    @property
    def kp(self):
        return self._kp
    
    @kp.setter
    def kp(self, kp_gain):
        if kp_gain >= 0:
            self._kp = kp_gain

    @property
    def ki(self):
        return self._ki

    @ki.setter
    def ki(self, ki_gain):
        if ki_gain >= 0:
            self._ki = ki_gain

    @property
    def kd(self):
        return self._kd

    @kd.setter
    def kd(self, kd_gain):
        if kd_gain >= 0:
            self._kd = kd_gain


    def calcPID(self, error):
        self._current_time = time.time()

        delta_time = self._current_time - self._prev_time
        delta_error = error - self._prev_error
        
        pid_val = 0.0

        if delta_time > self._sample_period:
            #to add windup for integral component
            self._Pterm = error
            if self._Iterm > self._windup:
                self._Iterm = 0.9 * self._windup
            elif self._Iterm < -self._windup:
                self._Iterm = -0.9 * self._windup
            else:
                self._Iterm += error * delta_time
            
            self._Dterm = (delta_error / delta_time) if delta_time > 0 else 0.0
            self._low_pass.append(self._Dterm)
            if len(self._low_pass) > self._filter_size:
                self._low_pass.pop()
            


            pid_val = (self._kp * self._Pterm) + (self._ki * self._Iterm) + (self._kd * sum(self._low_pass) / self._filter_size)

            # update state
            self._prev_time = self._current_time
            self._prev_error = error
            
            
        return pid_val
            



class LineFollower(PID):
    def __init__(self, sample_rate, kp, ki, kd):
        # initialize classes
        super(LineFollower, self).__init__(sample_rate, kp, ki, kd)
        self.motor_driver = DfrobotMotorControllerPiGPIO(E1=20, E2=12, M1=21, M2=16, range=1.0)
        self.lf = CytronLfLSS05Mcp23017('A_2', 'A_3', 'A_4', 'A_5', 'A_6', cal='A_7', bus=1, address=0x22)


        # setup constants 
        self.pid_gains = np.array([kp, ki, kd])
        self.weights =  np.array([-4.5, -2.5, 0.0, 2.5, 4.5])    

        # other members
        self._speed = 0.3

        self.thread = None
        self._alive = True

        self._stop_timer = 0.0
        self._stop_state = False

        self.measurements = np.array([0, 0, 0, 0, 0])


    def start(self):
        print("Calibrating sensor")
        self.lf.calibrate()
        self.motor_driver.start()

        time.sleep(5)
        print("Starting")
        self.thread = threading.Thread(target=self._run, args=(), daemon = True)
        self.thread.start()
        

    def _run(self):
        while self._alive:
            # aquire new measurement
            self._read()
            # find error
            curr_error = self._error()
            # calculate pid value
            pid = self.calcPID(curr_error)
            # command motors
            self._move(pid)
            time.sleep(0.051)


    def _read(self):
        self.measurements = np.array(list(self.lf.read()))

        # stopping condition - out of the line for 2 seconds
        if np.sum(self.measurements) == 0.0:
            if not self._stop_state:
                print("Timer started")
                self._stop_timer = time.time()
                self._stop_state = True
            else:
                print("Checking if should terminated!")
                if (time.time() - self._stop_timer) > 0.8:
                    self.stop()
        else:
            self._stop_timer = time.time()
            self._stop_state  = False

    @property
    def speed(self):
        return self._speed

    @speed.setter
    def speed(self, val):
        if 0 <= val and val <= 1.0:
            self._speed = val

    

    def _error(self):
        if np.count_nonzero(self.measurements != 0):
            error = np.dot(self.measurements, self.weights) / np.count_nonzero(self.measurements != 0)
        else:
            error = 0.0

        return error

    def _move(self, pid_val):
        self.motor_driver.move_linear_side(self._speed + pid_val, 1)
        self.motor_driver.move_linear_side(self._speed - pid_val, 0)


    def stop(self):
        self.motor_driver.stop()
        self.lf.stop()
        self._alive = False
        print("Line follower terminated")


# 1 - left
# 2 - right

# + on left
# - on right

if __name__ == "__main__":
    lf = LineFollower(20, 0.09, 0.005, 0.0005)

    lf.start()
    
    running = True
    while running:
        x = float(input())
        if x == 0.0:
            running = False
        elif x > 0.0:
            lf.speed = x

    lf.stop()
