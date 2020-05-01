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
   