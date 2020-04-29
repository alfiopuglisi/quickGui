# -*- coding: utf-8 -*-

import queue
import threading


def queue_tee(q, n=2, loop_time=1):
    '''
    Returns N queues that are tied to the input one `q`.

    Data will be replicated over the N queues automatically using a
    background thread.
    If the message 'quit' is seen passing through the queue, the thread
    terminates after forwarding the message
    '''
    qlist = [queue.Queue() for i in range(n)]

    def loop():
        while True:
            try:
                data = q.get(timeout=loop_time)
            except queue.Empty:
                continue

            for q2 in qlist:
                try:
                    q2.put(data, block=False)
                except queue.Full:
                    pass

            if isinstance(data, bytes):
                data = data.decode('utf-8')
            if isinstance(data, str) and data.strip().lower() == 'quit':
                return

    threading.Thread(target=loop).start()
    return qlist
