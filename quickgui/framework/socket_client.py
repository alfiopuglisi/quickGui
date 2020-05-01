# -*- coding: utf-8 -*-

import time
import queue
import socket
import select
import functools


class DisconnectedException(Exception):
    '''Socket was disconnected'''

    pass


class QueueClient():
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

    def __init__(self, host, port, qin, qout):
        self.qin = qin
        self.qout = qout
        self.host = host
        self.port = port
        self.time_to_die = False

    def run(self):

        while not self.time_to_die:
            self.connect()
            while not self.time_to_die:
                try:
                    r, _, _ = select.select([self.sock, self.qout], [], [])
                    if self.sock in r:
                        self.read()
                    if self.qout in r:
                        self.write()
                except DisconnectedException:
                    self.disconnect()
                    break

    def read(self):
        msg = None
        try:
            msg = self.sfile.readline()
            if msg:
                self.qin.put(msg, block=False)
            else:
                print('recv giving up')
                raise DisconnectedException
        except queue.Full:
            return
        except OSError as e:
            print('Exception: ', e)
            raise DisconnectedException

    def write(self):
        try:
            msg = self.qout.get(block=False)

            # Do not propagate quit messages, it's our GUI shutting down
            if msg.lower() == 'quit':
                self.time_to_die = True
                raise DisconnectedException

            self.sfile.write(msg + '\n')
            self.sfile.flush()
        except queue.Empty:
            return
        except OSError as e:
            print('Send failed', e)
            raise DisconnectedException

    def connect(self):
        while not self.time_to_die:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                print('connecting to ', self.host, self.port)
                self.sock.connect((self.host, self.port))
                self.sfile = self.sock.makefile('rw')
                print('Connected!')
                break
            except Exception as e:
                print(e)
            time.sleep(1)

    def disconnect(self):
        try:
            self.sock.shutdown()
            self.sock.close()
        except Exception:
            pass


def _start_client(host, port, qin, qout):

    client = QueueClient(host, port, qin, qout)
    client.run()


def get_client(host, port):
    '''Get a TCP client adapter

    Returns a callable that, when called, produces a TCP client that will
    connect to `host`:`port`, and can be used to connect a GUI's or
    another client's input/output queues to a TCP socket.

    The callable will have two arguments: `qin` and `qout`, that must be
    the same queues used in the GUI instantiation.
    '''
    return functools.partial(_start_client, host, port)
