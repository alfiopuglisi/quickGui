'''
A simple application that binds together a task and a GUI.

Both task and GUI must be callables and accept
two arguments in order to receive the
communication queues.

'''

import queue
import threading

from quickgui.framework.task_combiner import queue_tee

def start_app(task=None, gui=None, task_server=None, gui_client=None):
    '''
    task = task running in background
    gui: GUI running in foreground
    task_server: optional server(s) for task, for remote connections
    gui_client: optional client for GUI, for remote connections
    '''
    q1 = queue.Queue()
    q2 = queue.Queue()
    joinables = []

    if task:
        t = threading.Thread(target=task, args=(q1, q2))
        t.start()
        joinables.append(t)

    if task_server:
        q2, q2_server = queue_tee(q2)
        t2 = threading.Thread(target=task_server, args=(q1, q2_server))
        t2.start()
        joinables.append(t2)

    if gui_client:
        g2 = threading.Thread(target=gui_client, args=(q1, q2))
        g2.start()
        joinables.append(g2)

    # Start GUI (with reversed queues)
    # This call will block until the gui quits.
    if gui:
        gui(q2, q1)

        if task:
            # Shutdown task when GUI exits
            q1.put('QUIT')

    for joinable in joinables:
        joinable.join()


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



        
    
    
    
    