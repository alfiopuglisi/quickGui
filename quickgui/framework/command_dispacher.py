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


class CommandDispatcher:

    def __init__(self):
        self._handlers = {}

    def collect_handlers_from(self, obj):

        for name in dir(obj):
            method = getattr(obj, name)
            info = getattr(method, HIDDEN_ATTR, None)
            if info is not None:
                print('Handler for %s is %s' % (info.cmd, str(method)))
                self._handlers[info.cmd.lower()] = Handler(method,
                                                           info.validator)

    def dispatch(self, cmd, *arg):
        cmd = cmd.lower()
        if cmd not in self._handlers:
            raise DispatchError('No handler for command ' + cmd)

        handler = self._handlers[cmd]
        if len(arg) > 0 and handler.validator is not None:
            try:
                arg = [handler.validator(arg[0])]
            except Exception:
                print('Invalid argument for command %s' % cmd)
                return
        try:
            handler.func(*arg)
        except Exception as e:
            print('Exception handling command %s: %s' % (cmd, str(e)))
