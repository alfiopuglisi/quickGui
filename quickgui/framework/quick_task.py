# -*- coding: utf-8 -*-
'''
TODO: handlers with type checking:
@handler_int('CMD')
...

a caching "send" method that only calls qout.put when the value
is different from the last one, to reduce traffic.

a keepalive mechanism so that every X seconds a value is sent out
even if the task does not do anything.
'''

import time
import queue
import threading

from quickgui.framework.quick_base import QuickBase, handler, DispatchError
from quickgui.framework.quick_base import time_to_die


def periodic(f):
    '''Decorator for periodic handler'''
    return handler('periodic')(f)


class QuickTask(QuickBase):
    '''
    A task that dispatches commands to handler functions

    When the command 'CMD' is received, the method decorated with
    @handler('CMD') is called, together with an optional argument.
    In addition, a 'PERIODIC' command is inserted
    at regular intervals in the queue.

    Even if this class uses threads internally, handlers are not
    multi-threaded. All handlers run sequentially in the same thread.
    '''

    def __init__(self, qin, qout):
        super().__init__(qin, qout)
        self.period = 1

    def run(self):
        threading.Thread(target=self._periodic_loop).start()

        while not time_to_die():

            # Execute the while loop every now and then
            try:
                msg = self.qin.get(timeout=1)
            except queue.Empty:
                continue

            try:
                self.dispatch(msg)
            except DispatchError as e:
                print(e)

    @handler('periodic')
    def _periodic(self):
        pass

    def _periodic_loop(self):
        while not time_to_die():
            time.sleep(self.period)
            self.send_to_myself('periodic')

# ___oOo___
