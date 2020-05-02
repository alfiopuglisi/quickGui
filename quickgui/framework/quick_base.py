# -*- coding: utf-8 -*-

from collections import namedtuple

HIDDEN_ATTR = '__handle_func'

Info = namedtuple('Info', 'cmd validator')
Handler = namedtuple('Handler', 'func validator')


def handler(cmd, validator=None):
    '''Decorator for command handlers'''
    def decorator(f):
        setattr(f, HIDDEN_ATTR, Info(cmd, validator))
        return f
    return decorator


class DispatchError(Exception):
    pass


def handler_int(cmd):
    return handler(cmd, validator=int)


def handler_float(cmd):
    return handler(cmd, validator=float)


def handler_str(cmd):
    return handler(cmd, validator=str)


its_time_to_die = False


def time_to_die():
    return its_time_to_die


def set_time_to_die(value):
    global its_time_to_die
    its_time_to_die = value


class QuickBase():

    def __init__(self, qin, qout):
        self.qin = qin
        self.qout = qout
        self._handlers = {}

        for name in dir(self):
            method = getattr(self, name)
            info = getattr(method, HIDDEN_ATTR, None)
            if info is not None:
                print('Handler for %s is %s' % (info.cmd, str(method)))
                self._handlers[info.cmd.lower()] = Handler(method,
                                                           info.validator)

    def dispatch(self, msg):
        try:
            cmd, *arg = msg.split(maxsplit=1)
        except ValueError:  # if the split does not work
            raise DispatchError('Malformed message')

        cmd = cmd.lower()
        if cmd not in self._handlers:
            raise DispatchError('No handler for command ' + cmd)

        handler = self._handlers[cmd]
        if len(arg) > 0 and handler.validator is not None:
            try:
                arg = [handler.validator(arg[0])]
            except Exception:
                raise DispatchError('Invalid argument for command %s' % cmd)

        try:
            handler.func(*arg)
        except Exception as e:
            raise DispatchError('Exception handling command %s: %s' % (cmd, str(e)))

    def send(self, cmd):
        if cmd[-1] != '\n':
            cmd += '\n'
        self.qout.put(cmd)

    def send_to_myself(self, cmd):
        if cmd[-1] != '\n':
            cmd += '\n'
        self.qin.put(cmd)
