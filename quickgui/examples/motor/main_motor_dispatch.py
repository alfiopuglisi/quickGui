# -*- coding: utf-8 -*-
'''
A simple main program that binds together
a task and a GUI using multiprocessing
'''
from quickgui.examples.motor.motor_dispatch_task import task
from quickgui.examples.motor.motor_gui import MotorGui

from quickgui.framework import start

start(task=task, gui=MotorGui)
