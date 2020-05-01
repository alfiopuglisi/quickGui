'''
A simple main program that binds together
a task and a GUI using multiprocessing
'''
from task_dispatch import task_dispatch
from example_dispatch import ExampleDispatch

from launcher import self_contained_app

self_contained_app(task_dispatch, ExampleDispatch)

