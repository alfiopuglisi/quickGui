# -*- coding: utf-8 -*-

HIDDEN_ATTR = '__handle_for'


def handler(cmd):
    '''Decorator for command functions'''
    def decorator(f):

        setattr(f, HIDDEN_ATTR, cmd)
        return f

    return decorator


class DispatchingTask():
    '''
    '''

    def __init__(self, qin, qout):
        self.qin = qin
        self.qout = qout
        self.time_to_die = False
        self._handlers = {}

        for name in dir(self):
            method = getattr(self, name)
            cmd = getattr(method, HIDDEN_ATTR, None)
            if cmd is not None:
                print('Handler for %s is %s' % (cmd, str(method)))
                self._handlers[cmd] = method

    def run(self):
        while not self.time_to_die:
            cmd, arg = self.qin.get().split(maxsplit=1)
            reply = None
            if cmd not in self._handlers:
                print('No handler for command ' + cmd)
                reply = 'Unknown command'
            else:
                try:
                    reply = self._handlers[cmd](arg)
                except Exception as e:
                    reply = str(e)
            if reply is not None:
                self.cmd_reply(cmd, reply)

    def cmd_reply(self, cmd, reply):
        self.qout.put('%s %s' % (cmd, reply))

    @handler('QUIT')
    def quit_handler(self, enable):
        self.time_to_die = True

# ___oOo___
