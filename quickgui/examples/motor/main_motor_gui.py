# -*- coding: utf-8 -*-

# -*- coding: utf-8 -*-
'''
A simple main program that binds together
a task and a GUI using multiprocessing.
In addition the motor has a TCP server interface
'''
from quickgui.examples.motor.motor_gui import MotorGui

from quickgui.framework import get_client, start

host = 'localhost'
port = 3333

start(gui=MotorGui, gui_client = get_client(host, port))
