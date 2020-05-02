# -*- coding: utf-8 -*-
import queue
import select
import socket
import functools


def serve_forever(host, port, qin, qout):
    '''
    Socket server for task queues.

    Loops forever, accepting new connections, sending any data
    received from the task to all clients, and forwarding any data
    received from client to the task.

    qint and qout are seen from the task's perspective, so qin is data
    going to the task, and qout is data going to the clients.

    Exits if the 'quit' message is seen passing from the task to the clients.
    '''
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serversocket.bind((host, port))
    serversocket.listen(5)
    print("started server on port %d" % port)

    sockets = []

    while True:
        r, _, _ = select.select([serversocket, qout] + sockets, [], [])
        _, w, _ = select.select([], sockets, [], 0)

        if serversocket in r:
            sock, address = serversocket.accept()
            sockets.append(sock)
            print('Accepted new connection from ', address)

        try:
            msg = qout.get(block=False)
        except queue.Empty:
            msg = ''

        if msg.strip().lower().startswith('quit'):  # Task has quit
            print('task has quit, shutting down')
            return

        for sock in sockets:
            try:
                if msg and (sock in w):
                    sock.sendall(msg.encode('utf-8'))
                if sock in r:
                    data = sock.recv(128)  # NewLineQueue will take care
                                           # of message boundaries.
                    if data:
                        qin.put(data.decode('utf-8'))
                    else:
                        raise Exception('Disconnected')
            except Exception as e:
                print('Removing client socket %s: %s' % (sock.getpeername(), e))
                sockets.remove(sock)


def get_server(host, port):
    '''Get a TCP server adapter

    Returns a callable that, when called, produces a TCP server
    running on `host`:`port`, and can be used to connect the task
    input/output queues to a TCP socket.

    The callable will have two arguments: `qin` and `qout`, that must be
    the same queues used in the task's instantiation.
    '''
    return functools.partial(serve_forever, host, port)
