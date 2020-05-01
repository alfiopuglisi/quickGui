# -*- coding: utf-8 -*-

import random

from quickgui.framework import DispatchingTask, periodic, \
                               handler_int, handler_float

class Motor(DispatchingTask):
    '''A class containing a motor, which can be real or simulated.'''

    def __init__(self, qin, qout, motor_class, simul_class):
        super().__init__(qin, qout)
        self.time_to_die = False
        self.motor_class = motor_class
        self.simul_class = simul_class
        self.period = 0.5
        self.motor = simul_class()

    def is_simulated(self):
        return self.motor.__class__ == self.simul_class

    @handler_int('SIMUL')
    def simul(self, enable):
        if enable != 0 and not self.is_simulated():
            self.motor = self.simul_class()
        elif enable == 0 and self.is_simulated():
            self.motor = self.motor_class()

    @handler_float('MOVE')
    def move(self, pos):
        self.motor.moveto(pos)

    @periodic
    def refresh_status(self):
        '''Refreshes the status and sends it over the output queue'''
        moving, pos = self.motor.query()
        simulated = (self.motor.__class__ == self.simul_class)

        self.qout.put('MOVING %s' % int(moving))
        self.qout.put('POS %f' % pos)
        self.qout.put('SIMULATED %d' % int(simulated))


class SimulatedMotor():
    '''
    A simulated motor

    This simulated motor is capable of moving at a certain speed
    towards a target position. Target position can be changed at any time.
    '''

    def __init__(self):
        self.pos = 0
        self.targetpos = 0
        self.maxspeed = 10
        self.precision = 0.01

    def moveto(self, pos):
        self.targetpos = pos

    def query(self):

        if self.pos != self.targetpos:
            moving = True
            step = (self.targetpos - self.pos) / 2

            if abs(step) < self.precision:
                self.pos = self.targetpos
            elif step > 0:
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
