import logging
log = logging.getLogger(__name__)
import sys
from otp.ai.passlib.utils.decor import deprecated_method
__all__ = [
 'PasswordHash']

def recreate_with_metaclass(meta):

    def builder(cls):
        if meta is type(cls):
            return cls
        return meta(cls.__name__, cls.__bases__, cls.__dict__.copy())

    return builder


from abc import ABCMeta, abstractmethod, abstractproperty

@recreate_with_metaclass(ABCMeta)
class PasswordHash(object):
    is_disabled = False
    truncate_size = None
    truncate_error = True
    truncate_verify_reject = True

    @classmethod
    @abstractmethod
    def hash(cls, secret, **setting_and_context_kwds):
        raise NotImplementedError('must be implemented by subclass')

    @deprecated_method(deprecated='1.7', removed='2.0', replacement='.hash()')
    @classmethod
    def encrypt(cls, *args, **kwds):
        return cls.hash(*args, **kwds)

    @classmethod
    @abstractmethod
    def verify(cls, secret, hash, **context_kwds):
        raise NotImplementedError('must be implemented by subclass')

    @classmethod
    @abstractmethod
    def using(cls, relaxed=False, **kwds):
        raise NotImplementedError('must be implemented by subclass')

    @classmethod
    def needs_update(cls, hash, secret=None):
        return False

    @classmethod
    @abstractmethod
    def identify(cls, hash):
        raise NotImplementedError('must be implemented by subclass')

    @deprecated_method(deprecated='1.7', removed='2.0')
    @classmethod
    def genconfig(cls, **setting_kwds):
        if cls.context_kwds:
            raise NotImplementedError('must be implemented by subclass')
        return cls.using(**setting_kwds).hash('')

    @deprecated_method(deprecated='1.7', removed='2.0')
    @classmethod
    def genhash(cls, secret, config, **context):
        raise NotImplementedError('must be implemented by subclass')

    deprecated = False


class DisabledHash(PasswordHash):
    is_disabled = True

    @classmethod
    def disable(cls, hash=None):
        return cls.hash('')

    @classmethod
    def enable(cls, hash):
        raise ValueError('cannot restore original hash')