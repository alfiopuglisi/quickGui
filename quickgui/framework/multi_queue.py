# -*- coding: utf-8 -*-

from quickgui.framework.pollable_queue import PollableQueue

class MultiQueue():
    '''
    Queue fan-out.

    Builds N queues and replicates the put method across all of them.
    Sub-queues can be accessed with operator[].
    '''

    def __init__(self, n):
        self.qlist = [PollableQueue() for i in range(n)]

    def __getitem__(self, idx):
        return self.qlist[idx]

    def put(self, *args, **kwargs):
        for q in self.qlist:
            q.put(*args, **kwargs)
