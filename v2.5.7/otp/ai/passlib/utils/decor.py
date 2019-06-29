from __future__ import absolute_import, division, print_function
import logging
log = logging.getLogger(__name__)
from functools import wraps, update_wrapper
import types
from warnings import warn
from otp.ai.passlib.utils.compat import PY3
__all__ = [
 'classproperty',
 'hybrid_method',
 'memoize_single_value',
 'memoized_property',
 'deprecated_function',
 'deprecated_method']

class classproperty(object):

    def __init__(self, func):
        self.im_func = func

    def __get__(self, obj, cls):
        return self.im_func(cls)

    @property
    def __func__(self):
        return self.im_func


class hybrid_method(object):

    def __init__(self, func):
        self.func = func
        update_wrapper(self, func)

    def __get__(self, obj, cls):
        if obj is None:
            obj = cls
        if PY3:
            return types.MethodType(self.func, obj)
        return types.MethodType(self.func, obj, cls)
        return


def memoize_single_value(func):
    cache = {}

    @wraps(func)
    def wrapper():
        try:
            return cache[True]
        except KeyError:
            pass

        value = cache[True] = func()
        return value

    def clear_cache():
        cache.pop(True, None)
        return

    wrapper.clear_cache = clear_cache
    return wrapper


class memoized_property(object):

    def __init__(self, func):
        self.__func__ = func
        self.__name__ = func.__name__
        self.__doc__ = func.__doc__

    def __get__(self, obj, cls):
        if obj is None:
            return self
        value = self.__func__(obj)
        setattr(obj, self.__name__, value)
        return value

    if not PY3:

        @property
        def im_func(self):
            return self.__func__

    def clear_cache(self, obj):
        obj.__dict__.pop(self.__name__, None)
        return

    def peek_cache(self, obj, default=None):
        return obj.__dict__.get(self.__name__, default)


def deprecated_function(msg=None, deprecated=None, removed=None, updoc=True, replacement=None, _is_method=False, func_module=None):
    if msg is None:
        if _is_method:
            msg = 'the method %(mod)s.%(klass)s.%(name)s() is deprecated'
        else:
            msg = 'the function %(mod)s.%(name)s() is deprecated'
        if deprecated:
            msg += ' as of Passlib %(deprecated)s'
        if removed:
            msg += ', and will be removed in Passlib %(removed)s'
        if replacement:
            msg += ', use %s instead' % replacement
        msg += '.'

    def build(func):
        is_classmethod = _is_method and isinstance(func, classmethod)
        if is_classmethod:
            func = func.__get__(None, type).__func__
        opts = dict(mod=func_module or func.__module__, name=func.__name__, deprecated=deprecated, removed=removed)
        if _is_method:

            def wrapper(*args, **kwds):
                tmp = opts.copy()
                klass = args[0] if is_classmethod else args[0].__class__
                tmp.update(klass=klass.__name__, mod=klass.__module__)
                warn(msg % tmp, DeprecationWarning, stacklevel=2)
                return func(*args, **kwds)

        else:
            text = msg % opts

            def wrapper(*args, **kwds):
                warn(text, DeprecationWarning, stacklevel=2)
                return func(*args, **kwds)

        update_wrapper(wrapper, func)
        if updoc and (deprecated or removed) and wrapper.__doc__ and '.. deprecated::' not in wrapper.__doc__:
            txt = deprecated or ''
            if removed or replacement:
                txt += '\n    '
                if removed:
                    txt += 'and will be removed in version %s' % (removed,)
                if replacement:
                    if removed:
                        txt += ', '
                    txt += 'use %s instead' % replacement
                txt += '.'
            if not wrapper.__doc__.strip(' ').endswith('\n'):
                wrapper.__doc__ += '\n'
            wrapper.__doc__ += '\n.. deprecated:: %s\n' % (txt,)
        if is_classmethod:
            wrapper = classmethod(wrapper)
        return wrapper

    return build


def deprecated_method(msg=None, deprecated=None, removed=None, updoc=True, replacement=None):
    return deprecated_function(msg, deprecated, removed, updoc, replacement, _is_method=True)