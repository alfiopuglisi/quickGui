'''
A simple main program that binds together
a task and a GUI using multiprocessing
'''
from quickgui.examples.minimal.task import task
from quickgui.examples.minimal.example_ui import ui

from quickgui.framework.self_contained_app import self_contained_app

self_contained_app(task, ui)

