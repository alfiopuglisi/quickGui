'''
A simple main program that binds together
a task and a GUI using multiprocessing
'''
from quickgui.examples.qt.task import task
from quickgui.examples.qt.example_gui import ExampleGui

from quickgui.framework.self_contained_app import self_contained_app

self_contained_app(task, ExampleGui)

