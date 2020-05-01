'''
Arte GUI framework
'''

from quickgui.framework.quick_qt_gui import QuickQtGui
from quickgui.framework.command_dispacher import CommandDispatcher, \
                                                 DispatchError


class DispatchingQtGui(QuickQtGui):
    '''
    '''

    def __init__(self, qin, qout):
        super().__init__(qin, qout, None)
        self.dispatcher = CommandDispatcher()
        self.dispatcher.collect_handlers_from(self)

    def _received(self, i):
        msg = self._qlistener.get(i)
        try:
            cmd, *arg = msg.split(maxsplit=1)
        except ValueError:  # if the split does not work
            return

        try:
            self.dispatcher.dispatch(cmd, *arg)
        except DispatchError as e:
            print(e)
