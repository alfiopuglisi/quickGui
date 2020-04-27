# -*- coding: utf-8 -*-

import time
import random
import threading


class Motor():
    '''
    Simple motor class

    A class containing a motor, which can be a real one or
    a simulated one.
    '''

    def __init__(self, qin, qout, motor_class, simul_class):
        self.qin = qin
        self.qout = qout
        self.time_to_die = False
        self.motor_class = motor_class
        self.simul_class = simul_class
        self.status_delay = 0.5
        self.output_lock = threading.Lock()
        self.status_thread = threading.Thread(target=self.status_loop)
        self.status_thread.start()
        self.motor = simul_class()
        self.motor_moving = False

    def run(self):
        while not self.time_to_die:
            cmd, arg = self.qin.get().split(maxsplit=1)
            if cmd == 'QUIT':
                self.time_to_die = True
            elif cmd == 'MOVE':
                self.move(arg)
            elif cmd == 'SIMUL':
                self.simul(bool(int(arg)))

    def simul(self, enable):
        if enable is True:
            self.motor = self.simul_class()
        else:
            self.motor = self.motor_class()
        self.cmd_answer('SIMUL', 'OK')

    def cmd_answer(self, cmd, answ):
        s = '%s %s' % (cmd, answ)
        with self.output_lock:
            self.qout.put(s)

    def move(self, pos):
        if self.motor_moving:
            self.cmd_answer('MOVE', ('Cannot perform MOVE:'
                                    ' another MOVE is already in progress'))
        else:
            self.motor.moveto(float(pos))
            self.motor_moving = True

    def status_loop(self):
        '''Status thread

        Runs forever that refreshes the status
        and sends it over the output queue
        '''
        while not self.time_to_die:

            time.sleep(self.status_delay)
            moving, pos = self.motor.query()
            if not moving and self.motor_moving:
                self.cmd_answer('MOVE', 'OK')

            self.motor_moving = moving
            simulated = (self.motor.__class__ == self.simul_class)

            with self.output_lock:
                self.qout.put('MOVING %s' % int(moving))
                self.qout.put('POS %f' % pos)
                self.qout.put('SIMULATED %d' % int(simulated))


class SimulatedMotor():
    '''
    A simulated motor

    This simulated motor is capable of moving at a certain speed
    towards a target position.
    '''

    def __init__(self):
        self.pos = 0
        self.targetpos = 0
        self.maxspeed = 10
        self.precision = 0.01

    def moveto(self, pos):
        self.targetpos = pos

    def query(self):

        # Force target reached when close
        if abs(self.pos - self.targetpos) < self.precision:
            self.pos = self.targetpos

        if self.pos != self.targetpos:
            moving = True
            step = (self.targetpos - self.pos) / 2
            if step > 0:
                self.pos += min(step, self.maxspeed)
            else:
                self.pos += max(step, -self.maxspeed)
        else:
            moving = False

        pos = self.pos + (random.random() - 0.5) * self.precision / 10
        return moving, pos


class RealMotor():
    '''
    A real motor.

    This one should have methods talking with the hardware.
    moveto() and query() may be called by different threads, so
    a synchronization lock may be needed.
    '''

    def __init__(self):
        pass

    def moveto(self, pos):
        pass

    def query(self):
        return False, 0


def task(qin, qout):
    '''The task visible outside'''
    motor = Motor(qin, qout, RealMotor, SimulatedMotor)
    motor.run()

# ___oOo___
