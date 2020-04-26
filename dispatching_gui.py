'''
Arte GUI framework
'''

from PyQt5.QtCore import pyqtSignal, QThread

from arte_qt_gui import ArteQtGui

HIDDEN_ATTR = '__handle_for'

class DispatchingGui(ArteQtGui):
   '''
   '''

   def __init__(self, qin, qout):
       super().__init__(qin, qout, None)
       self._handlers = {}

       for name in dir(self):
           method = getattr(self, name)
           cmd = getattr(method, HIDDEN_ATTR, None)
           if cmd is not None:
               self._handlers[cmd] = method
               break

   def _received(self, i):
       value = self._qlistener.get(i)
       cmd, value = value.split(maxsplit=1)
       try:
           self._handlers[cmd](value)
       except KeyError:
           print('No handler for command '+cmd)


def cmd(cmd):

    def decorator(f):

        setattr(f, HIDDEN_ATTR, cmd)
        return f

    return decorator
