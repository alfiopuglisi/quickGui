'''
Arte GUI framework
'''

from PyQt5.QtCore import pyqtSignal, QThread

from quickgui.framework.quick_base import QuickBase, DispatchError


class QuickQtGui(QuickBase):
    '''
    A GUI base class using PyQt to listen to the task queue

    Derived classes must initialize this class with the two
    communication queues and a callback that will be called
    every time something is received on the input queue.

    Also the derived class must provide the event loop using
    QApplication.exec_().
    '''

    def __init__(self, qin, qout):
        super().__init__(qin, qout)

        self._qlistener = self._QueueListener(qin)
        self._qlistener.signal.connect(self._received)
        self._qlistener.start()

    def _received(self, msg):
        try:
            self.dispatch(msg)
        except DispatchError as e:
            print(e)

    class _QueueListener(QThread):

        signal = pyqtSignal(str)

        def __init__(self, qin):
            super().__init__()
            self.qin = qin

        def run(self):
            while 1:
                msg = self.qin.get()
                self.signal.emit(msg)
