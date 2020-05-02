# -*- coding: utf-8 -*-

import os
import queue
import socket


class PollableQueue(queue.Queue):
    '''Pollable queue from Python Cookbook, 3rd Edition

    Python Cookbook, 3rd Edition
    Recipes for Mastering Python 3
    By Brian Jones, David Beazley

    "writing a program that uses several chunks of code from this
    book does not require permission."

    This queue can be used in the first argument (readable sockets)
    of a select() call. When something is in the queue, select() returns
    that the queue is readable.

    The trick is a small loopback socket that keeps in sync with the
    queue's contents.

    apuglisi 2020-04-30  modified get() and put() methods
                         to accept the same parameter as queue.Queue.
    '''

    def __init__(self):
        super().__init__()
        # Create a pair of connected sockets
        if os.name == 'posix':
            self._putsocket, self._getsocket = socket.socketpair()
        else:
            # Compatibility on non-POSIX systems
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.bind(('127.0.0.1', 0))
            server.listen(1)
            self._putsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._putsocket.connect(server.getsockname())
            self._getsocket, _ = server.accept()
            server.close()

    def fileno(self):
        return self._getsocket.fileno()

    def put(self, item, block=True, timeout=None):
        super().put(item, block, timeout)
        self._putsocket.send(b'x')

    def get(self, block=True, timeout=None):
        item = super().get(block, timeout)
        # perform recv() only if get() is successful
        self._getsocket.recv(1)
        return item


class NewLineQueue(PollableQueue):
    '''Queue that forces messages to be terminated with newlines'''

    def __init__(self):
        super().__init__()
        self._outbuf = ''

    def put(self, s, block=True, timeout=None):
        if not isinstance(s, str):
            raise TypeError('A NewLineQueue only accepts strings')

        *lines, last_line = (self._outbuf + s).splitlines(keepends=True)

        for line in lines:
            super().put(line, block, timeout)

        if last_line.endswith('\n'):
            super().put(last_line, block, timeout)
            self._outbuf = ''
        else:
            self._outbuf = last_line


class MultiQueue():
    '''
    Queue fan-out.

    Builds N queues and replicates the put method across all of them.
    Sub-queues can be accessed with operator[].

    The queue type is passed in the constructor as `klass`. Anything
    that implements a `put` method is OK.
    '''

    def __init__(self, n, klass):
        self.qlist = [klass() for i in range(n)]

    def __getitem__(self, idx):
        return self.qlist[idx]

    def put(self, *args, **kwargs):
        for q in self.qlist:
            q.put(*args, **kwargs)
