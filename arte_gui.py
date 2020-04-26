'''
Arte GUI framework
'''

import abc

class ArteGui():
   '''
   The abstract GUI class.

   Derived classes must implement the
   `send` and `receive` methods using the two queues.
   '''

   def __init__(self, qin, qout):
       self.qin = qin
       self.qout = qout

   @abc.abstractmethod
   def send(self, data):
       pass

   @abc.abstractmethod
   def receive(self, idx):
       pass


