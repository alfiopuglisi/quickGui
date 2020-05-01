# -*- coding: utf-8 -*-
import queue
import threading
import functools
import socketserver


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

    def get_qout_copy(self, client_id):
        q = queue.Queue()
        self.qout_clients[client_id] = q
        return q

    def delete_qout_copy(self, client_id):
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
        - the server is shutdown.
        '''
        self._time_to_die = False
        self._p = threading.Thread(target=self.handle_out)
        self._p.start()

        while True:
            print('Input thread looping')
            try:
                msg = self.rfile.readline().strip()
                if not msg:
                    print('Input thread exiting')
                    return   # disconnected
            except Exception:
                print('Input thread exiting - unclean disconnect')
                return
            self.server.qin.put(msg.decode('utf-8'))
        print('Input thread exiting')

    def handle_out(self):
        '''Handler for data going to the client's socket'''
        qout = self.server.get_qout_copy(self.request)
        while not self._time_to_die:
            try:
                msg = qout.get(timeout=1)  # Cycle the loop every now and then
                if msg[-1] != '\n':
                    msg += '\n'
                self.wfile.write(msg.encode('utf-8'))

            except queue.Empty:
                pass
            except Exception:
                print('Output thread exception')
                return
        print('Output thread exiting')

    def finish(self):
        self._time_to_die = True   # Stop the handle_out thread
        self._p.join()
        self.server.delete_qout_copy(self.request)


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
