# -*- coding: utf-8 -*-

# -*- coding: utf-8 -*-
'''
A simple main program that binds together
a task and a GUI using multiprocessing.
In addition the motor has a TCP server interface
'''
from quickgui.examples.motor.motor_gui import MotorGui
from quickgui.framework.socket_client import get_client
from quickgui.framework.self_contained_app import start

host = 'localhost'
port = 3333

start(gui=MotorGui, gui_client = get_client(host, port))
