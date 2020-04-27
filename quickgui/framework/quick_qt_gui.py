'''
Arte GUI framework
'''

from PyQt5.QtCore import pyqtSignal, QThread

class QuickQtGui():
   '''
   A GUI base class using PyQt to listen to the task queue

   Derived classes must initialize this class with the two
   communication queues and a callback that will be called
   every time something is received on the input queue.

   Also the derived class must provide the event loop using
   QApplication.exec_().
   '''

   def __init__(self, qin, qout, data_callback):
       self.qin = qin
       self.qout = qout
       self._qlistener = self.QueueListener(qin)
       self._qlistener.signal.connect(self._received)
       self._qlistener.start()
       self._data_callback = data_callback

   def send(self, data):
       self.qout.put(data)

   def _received(self, i):
       value = self._qlistener.get(i)
       self._data_callback(value)

   class QueueListener(QThread):

       signal = pyqtSignal(int)

       def __init__(self, qin):
           super().__init__()
           self.qin = qin
           self.results = {}
           self.counter=0

       def run(self):
           while 1:
               data = self.qin.get()
               self.results[self.counter] = data
               self.signal.emit(self.counter)
               self.counter += 1

       def get(self, i):
           value = self.results[i]
           del self.results[i]
           return value

