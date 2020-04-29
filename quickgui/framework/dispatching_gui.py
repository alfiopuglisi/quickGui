'''
Arte GUI framework
'''

from quickgui.framework.quick_qt_gui import QuickQtGui

HIDDEN_ATTR = '__handle_for'


class DispatchingQtGui(QuickQtGui):
    '''
    '''

    def __init__(self, qin, qout):
        super().__init__(qin, qout, None)
        self._handlers = {}

        for name in dir(self):
            method = getattr(self, name)
            cmd = getattr(method, HIDDEN_ATTR, None)
            if cmd is not None:
                print('Handler for %s is %s' % (cmd, str(method)))
                self._handlers[cmd.upper()] = method

    def _received(self, i):
        value = self._qlistener.get(i)
        cmd, value = value.split(maxsplit=1)
        try:
            self._handlers[cmd.upper()](value)
        except KeyError:
            print('No handler for command ' + cmd)


def handler(cmd):
    '''Decorator for handler functions'''
    def decorator(f):

        setattr(f, HIDDEN_ATTR, cmd)
        return f

    return decorator
