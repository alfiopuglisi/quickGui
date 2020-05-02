'''
A simple application that binds together a task and a GUI.

Both task and GUI must be callables and accept
two arguments in order to receive the
communication queues.

'''

import queue
import select
import threading
from collections.abc import Iterable

from quickgui.framework.queues import NewLineQueue
from quickgui.framework.quick_base import time_to_die, set_time_to_die


class Exchange():
    '''
    Central exchange for queues.

    Incoming messages from any queue are replicated to all output queues,
    except for the ones in the same category.
    '''

    def __init__(self):
        self.qins = []
        self.qouts = []

    def get(self, category=''):
        qin = NewLineQueue()
        qout = NewLineQueue()
        qin.category = category
        qout.category = category
        self.qins.append(qin)
        self.qouts.append(qout)
        return qin, qout

    def run(self):
        while not time_to_die():
            r, _, _ = select.select(self.qouts, [], [])
            for qout in r:
                data = qout.get(block=False)
                for qin in self.qins:
                    if qin.category != qout.category:
                        try:
                            qin.put(data, block=False)
                        except queue.Full:
                            pass


def start(task=None, gui=None, task_servers=None, gui_client=None):
    '''
    App launcher

    task = task running in background
    gui: GUI running in foreground
    task_servers: optional server(s) for task, for remote connections
    gui_client: optional client for GUI, for remote connections

    This launcher uses the class Exchange above to simplify
    the queue plumbing.
    However the exchange causes rapid message inflation for anything but
    the simplest topologies.
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
    exchange = Exchange()

    for i, server in enumerate(task_servers):
        qin, qout = exchange.get('task_server')
        t = threading.Thread(target=server, args=(qout, qin))
        t.start()
        joinables.append(t)

    if task:
        qin, qout = exchange.get('task')
        t = threading.Thread(target=task, args=(qin, qout))
        t.start()
        joinables.append(t)

    if gui_client:
        qin, qout = exchange.get('gui_client')
        t = threading.Thread(target=gui_client, args=(qout, qin))
        t.start()
        joinables.append(t)

    # Start GUI in foreground
    # This call will block until the gui quits.
    if gui:
        qin, qout = exchange.get('gui')

    threading.Thread(target=exchange.run).start()

    if gui:
        gui(qin, qout)

    set_time_to_die(True)

    for joinable in joinables:
        joinable.join()


def self_contained_app(task, gui):

    q1 = NewLineQueue()
    q2 = NewLineQueue()

    # Spawn task

    t = threading.Thread(target=task, args=(q1, q2))
    t.start()

    # Start GUI (with reversed queues)
    gui(q2, q1)

    # Shutdown task
    q1.put('quit')
    t.join()
