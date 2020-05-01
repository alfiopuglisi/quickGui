# -*- coding: utf-8 -*-

HIDDEN_ATTR = '__handle_for'


def handler(cmd):
    '''Decorator for command handlers'''
    def decorator(f):
        setattr(f, HIDDEN_ATTR, cmd)
        return f
    return decorator


class DispatchError(Exception):
    pass


class CommandDispatcher:

    def __init__(self):
        self._handlers = {}

    def collect_handlers_from(self, obj):

        for name in dir(obj):
            method = getattr(obj, name)
            cmd = getattr(method, HIDDEN_ATTR, None)
            if cmd is not None:
                print('Handler for %s is %s' % (cmd, str(method)))
                self._handlers[cmd.lower()] = method

    def dispatch(self, cmd, *arg):
        if cmd.lower() not in self._handlers:
            raise DispatchError('No handler for command ' + cmd)
        else:
            try:
                self._handlers[cmd.lower()](*arg)
            except Exception as e:
                print('Exception handling command %s: %s' % (cmd, str(e)))
