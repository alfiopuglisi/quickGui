# -*- coding: utf-8 -*-

import time
import queue
import socket
import select
import functools

from quickgui.framework.quick_base import time_to_die

def socket_client(host, port, qin, qout):
    '''
    TCP client for queue-based communication.

    Runs an infinite loop where it will connect to the specified host
    and port, send whatever data comes from qout to the socket, and puts
    any incoming data from the socket into qin.

    qin and qout are seen from the perspective of the client, so qin is data
    going to the client, and qout is data going to the task.

    If the server connection is lost, this client will automatically try
    to reconnect in an infinite loop instead of shutting down.
    '''
    while not time_to_die():
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                print('connecting to ', host, port)
                sock.connect((host, port))

                while not time_to_die():
                    r, _, _ = select.select([sock, qout], [], [])

                    if qout in r:
                        msg = qout.get()
                        sock.sendall(msg.encode('utf-8'))

                    if sock in r:
                        msg = sock.recv(128)   # NewLineQueue will take care
                        if msg:                # of message boundaries.
                            try:
                                qin.put(msg.decode('utf-8'), block=False)
                            except queue.Full:
                                pass
                        else:
                            raise OSError('client disconnected')

            except OSError as e:
                print(e)
                time.sleep(1)


def get_client(host, port):
    '''Get a TCP client adapter

    Returns a callable that, when called, produces a TCP client that will
    connect to `host`:`port`, and can be used to connect a GUI's or
    another client's input/output queues to a TCP socket.

    The callable will have two arguments: `qin` and `qout`, that must be
    the same queues used in the GUI instantiation.
    '''
    return functools.partial(socket_client, host, port)
