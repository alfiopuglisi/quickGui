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

HIDDEN_ATTR = '__handle_for'


def handler(cmd):
    '''Decorator for command handlers'''
    def decorator(f):
        setattr(f, HIDDEN_ATTR, cmd)
        return f
    return decorator


def periodic(f):
    '''Decorator for periodic handler'''
    return handler('periodic')(f)


class DispatchingTask():
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
        self._handlers = {}
        self.period = 1

        for name in dir(self):
            method = getattr(self, name)
            cmd = getattr(method, HIDDEN_ATTR, None)
            if cmd is not None:
                print('Handler for %s is %s' % (cmd, str(method)))
                self._handlers[cmd.lower()] = method

    def run(self):
        threading.Thread(target=self._periodic_loop).start()

        while not self.time_to_die:
            try:
                cmd, *arg = self.qin.get().split(maxsplit=1)
            except ValueError:  # if the split does not work
                continue
            print('CMD: ',cmd)
            if cmd.lower() not in self._handlers:
                print('No handler for command ' + cmd)
            else:
                try:
                    self._handlers[cmd.lower()](*arg)
                except Exception as e:
                    print('Exception handling command %s: %s' % (cmd, str(e)))

    @handler('quit')
    def quit_handler(self):
        self.qout.put('quit')  # Tell clients that we are quitting
        self.time_to_die = True

    @handler('periodic')
    def _periodic(self):
        pass

    def _periodic_loop(self):
        while not self.time_to_die:
            time.sleep(self.period)
            self.qin.put('periodic')

# ___oOo___
