# -*- coding: utf-8 -*-
import queue
import threading
import functools
import socketserver


class QueueServer(socketserver.ThreadingTCPServer):
    '''
    Socket server for task queues.

    Each client is served with a dedicated thread. Data coming from all
    clients is put into the task's input queue. Doming
    from the task's output queue is replicated across all clients. If
    a client connection is too slow, some of the output data may be dropped.
    '''
    allow_reuse_address = True
    daemon_threads = True

    def __init__(self, HOST, PORT, handler, qin, qout):
        super().__init__((HOST, PORT), handler)
        self.qin = qin
        self.qout = qout
        self.qout_clients = {}
        self.time_to_die = False
        threading.Thread(target=self.fill_clients).start()

    def get_qout_copy(self, client_id):
        q = queue.Queue()
        self.qout_clients[client_id] = q
        return q

    def delete_qout_copy(self, client_id):
        del self.qout_clients[client_id]

    def fill_clients(self):
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
        self._time_to_die = False
        self._p = threading.Thread(target=self.handle_out)
        self._p.start()

        while not self._time_to_die:
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
        self._time_to_die = True
        self._p.join()
        self.server.delete_qout_copy(self.request)


def _start_server(host, port, qin, qout):

    with QueueServer(host, port, QueueHandler, qin, qout) as server:
        print("started server on port %d" % port)
        server.serve_forever()
        print('start_server exiting')

def get_server(host, port):
    return functools.partial(_start_server, host, port)
