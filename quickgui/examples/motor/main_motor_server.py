# -*- coding: utf-8 -*-
'''
A simple main program that binds together
a task and a GUI using multiprocessing.
In addition the motor has a TCP server interface
'''
from quickgui.examples.motor.motor_task import task

from quickgui.framework import get_server, start

host = ''
port = 3333

start(task=task, task_servers = get_server(host, port))
