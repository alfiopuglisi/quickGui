'''
A simple application that binds together
a task and a GUI using multiprocessing.

Both task and GUI must be callables and accept
two arguments in order to receive the 
communication queues.
'''

import multiprocessing as mp

def self_contained_app(task, gui):

   q1 = mp.Queue()
   q2 = mp.Queue()

   # Spawn task

   p = mp.Process(target = task, args=(q1, q2))
   p.start()

   # Start GUI (with reversed queues)
   gui(q2, q1)

   # Shutdown task
   q1.put(None)
   p.join()
