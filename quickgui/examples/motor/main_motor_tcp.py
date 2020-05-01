# -*- coding: utf-8 -*-
'''
A simple main program that binds together
a task and a GUI using multiprocessing.
In addition the motor has a TCP server interface
'''
from quickgui.examples.motor.motor_dispatch_task import task
from quickgui.examples.motor.motor_gui import MotorGui
from quickgui.framework.socket_server import get_server
from quickgui.framework.self_contained_app import start

host = ''
port = 3333


start(task=task, gui=MotorGui, task_servers = get_server(host, port))