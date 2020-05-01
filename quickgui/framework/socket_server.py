# -*- coding: utf-8 -*-
import queue
import threading
import functools
import socketserver

from contextlib import contextmanager

class QueueServer(socketserver.ThreadingTCPServer):
    '''
    Socket server for task queues.

    Each client is served with a dedicated thread. Data coming from all
    clients is put into the task's input queue. Data coming
    from the task's output queue is replicated across all clients. If
    a client connection is too slow, some of the output data may be dropped.

    qint and qout are seen from the task's perspective, so qin is data
    going to the task, and qout is data going to the clients.

    This server uses daemonic threads in order to be able to shutdown
    even while handler threads are performing blocking I/O like readline().
    Shutdown is initiated automatically if the 'quit' message is seen
    passing from the task to the clients.
    '''

    allow_reuse_address = True
    daemon_threads = True   # Allow shutdown without waiting for threads

    def __init__(self, HOST, PORT, handler, qin, qout):
        super().__init__((HOST, PORT), handler)
        self.qin = qin
        self.qout = qout
        self.qout_clients = {}
        threading.Thread(target=self.fill_clients).start()

    @contextmanager
    def qout_copy(self, client_id):
        q = queue.Queue()
        self.qout_clients[client_id] = q
        try:
            yield q
        except Exception:
            pass
        finally:
            del self.qout_clients[client_id]
        
    def fill_clients(self):
        '''
        Get data from the qout queue and send it to all client threads.

        Stop when the command 'quit' has seen passing through the queue.
        '''
        while True:
            data = self.qout.get()
            for k, q in self.qout_clients.items():
                try:
                    q.put(data, block=False)
                except queue.Full:
                    # Slow clients will drop messages and
                    # should not block the rest.
                    pass
            if data.strip().lower() == 'quit':  # Task has quit
                print('task has quit, shutting down')
                self.shutdown()
                return


class QueueHandler(socketserver.StreamRequestHandler):
    '''
    Handler for a client connection

    Writes all incoming data into the task input queue, and sends
    all the task's output into the socket. The two queues are managed
    by separate threads in order to simplify the blocking calls management.
    '''

    def handle(self):
        '''Handler for data coming from the client's socket.

        Loops forever until:
        - the client disconnects, or
        - the server is shutdown
        '''
        threading.Thread(target=self.handle_out).start()

        try:
            for msg in iter(self.rfile.readline, b''):
                self.server.qin.put(msg.decode('utf-8'))
        except Exception as e:
            print('Exception in input thread:', e)

    def handle_out(self):
        '''Handler for data going to the client's socket'''
        
        with self.server.qout_copy(self.request) as qout:

            for msg in iter(qout.get, None):
                self.wfile.write(msg.encode('utf-8'))

        print('Output thread exiting')

def _start_server(host, port, qin, qout):

    with QueueServer(host, port, QueueHandler, qin, qout) as server:
        print("started server on port %d" % port)
        server.serve_forever()
        print('start_server exiting')


def get_server(host, port):
    '''Get a TCP server adapter

    Returns a callable that, when called, produces a TCP server
    running on `host`:`port`, and can be used to connect the task
    input/output queues to a TCP socket.

    The callable will have two arguments: `qin` and `qout`, that must be
    the same queues used in the task's instantiation.
    '''
    return functools.partial(_start_server, host, port)
