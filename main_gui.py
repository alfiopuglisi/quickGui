'''
A simple main program that binds together
a task and a GUI using multiprocessing
'''
from task import task
from example_gui import ExampleGui

from self_contained_app import self_contained_app

self_contained_app(task, ExampleGui)

