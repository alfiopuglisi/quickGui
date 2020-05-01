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
import threading

from quickgui.framework.command_dispacher import CommandDispatcher, handler, \
                                                 DispatchError


def periodic(f):
    '''Decorator for periodic handler'''
    return handler('periodic')(f)


class QuickTask():
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
        self.qin = qin
        self.qout = qout
        self.time_to_die = False
        self.period = 1
        self.dispatcher = CommandDispatcher()
        self.dispatcher.collect_handlers_from(self)

    def run(self):
        threading.Thread(target=self._periodic_loop).start()

        while not self.time_to_die:
            try:
                cmd, *arg = self.qin.get().split(maxsplit=1)
            except ValueError:  # if the split does not work
                continue
            try:
                self.dispatcher.dispatch(cmd, *arg)
            except DispatchError as e:
                print(e)

    def send(self, cmd):
        if cmd[-1] != '\n':
            cmd += '\n'
        self.qout.put(cmd)
   
    @handler('quit')
    def quit_handler(self):
        self.send('quit')     # Tell clients that we are quitting
        self.time_to_die = True

    @handler('periodic')
    def _periodic(self):
        pass

    def _periodic_loop(self):
        while not self.time_to_die:
            time.sleep(self.period)
            self.qin.put('periodic')

# ___oOo___
