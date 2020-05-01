'''
A simple application that binds together a task and a GUI.

Both task and GUI must be callables and accept
two arguments in order to receive the
communication queues.

'''

import queue
import threading
from collections.abc import Iterable

from quickgui.framework.multi_queue import MultiQueue
from quickgui.framework.pollable_queue import PollableQueue


def start(task=None, gui=None, task_servers=None, gui_client=None):
    '''
    App launcher

    task = task running in background
    gui: GUI running in foreground
    task_servers: optional server(s) for task, for remote connections
    gui_client: optional client for GUI, for remote connections
    '''

    if task_servers is None:
        task_servers = []
    elif not isinstance(task_servers, Iterable):
        task_servers = [task_servers]

    if task_servers and not task:
        raise Exception('Task servers can only be started together with tasks')
    if gui_client and task:
        raise Exception('GUI client can be started with GUIs only')

    joinables = []

    if task:
        n_out_queues = len(task_servers)
        if gui:
            n_out_queues += 1

        qin = queue.Queue()
        qout = MultiQueue(n_out_queues)
        qout_gui = qout[-1]

        for i, server in enumerate(task_servers):
            t = threading.Thread(target=server, args=(qin, qout[i]))
            t.start()
            joinables.append(t)

        t = threading.Thread(target=task, args=(qin, qout))
        t.start()
        joinables.append(t)

    if gui_client:
        qin = PollableQueue()
        qout_gui = queue.Queue()
        t = threading.Thread(target=gui_client, args=(qin, qout_gui))
        t.start()
        joinables.append(t)

    # Start GUI (with reversed queues)
    # This call will block until the gui quits.
    if gui:
        gui(qout_gui, qin)

        if task or gui_client:
            # Shutdown task when GUI exits
            print('start_app(): stopping task')
            qin.put('QUIT')

    for joinable in joinables:
        joinable.join()


def self_contained_app(task, gui):

    q1 = queue.Queue()
    q2 = queue.Queue()

    # Spawn task

    t = threading.Thread(target=task, args=(q1, q2))
    t.start()

    # Start GUI (with reversed queues)
    gui(q2, q1)

    # Shutdown task
    q1.put('quit')
    t.join()
