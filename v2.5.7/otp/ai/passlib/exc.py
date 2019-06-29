

class UnknownBackendError(ValueError):

    def __init__(self, hasher, backend):
        self.hasher = hasher
        self.backend = backend
        message = '%s: unknown backend: %r' % (hasher.name, backend)
        ValueError.__init__(self, message)


class MissingBackendError(RuntimeError):
    pass


class PasswordSizeError(ValueError):
    max_size = None

    def __init__(self, max_size, msg=None):
        self.max_size = max_size
        if msg is None:
            msg = 'password exceeds maximum allowed size'
        ValueError.__init__(self, msg)
        return


class PasswordTruncateError(PasswordSizeError):

    def __init__(self, cls, msg=None):
        if msg is None:
            msg = 'Password too long (%s truncates to %d characters)' % (
             cls.name, cls.truncate_size)
        PasswordSizeError.__init__(self, cls.truncate_size, msg)
        return


class PasslibSecurityError(RuntimeError):
    pass


class TokenError(ValueError):
    _default_message = 'Token not acceptable'

    def __init__(self, msg=None, *args, **kwds):
        if msg is None:
            msg = self._default_message
        ValueError.__init__(self, msg, *args, **kwds)
        return


class MalformedTokenError(TokenError):
    _default_message = 'Unrecognized token'


class InvalidTokenError(TokenError):
    _default_message = 'Token did not match'


class UsedTokenError(TokenError):
    _default_message = 'Token has already been used, please wait for another.'
    expire_time = None

    def __init__(self, *args, **kwds):
        self.expire_time = kwds.pop('expire_time', None)
        TokenError.__init__(self, *args, **kwds)
        return


class UnknownHashError(ValueError):

    def __init__(self, name):
        self.name = name
        ValueError.__init__(self, 'unknown hash algorithm: %r' % name)


class PasslibWarning(UserWarning):
    pass


class PasslibConfigWarning(PasslibWarning):
    pass


class PasslibHashWarning(PasslibWarning):
    pass


class PasslibRuntimeWarning(PasslibWarning):
    pass


class PasslibSecurityWarning(PasslibWarning):
    pass


def _get_name(handler):
    if handler:
        return handler.name
    return '<unnamed>'


def type_name(value):
    cls = value.__class__
    if cls.__module__ and cls.__module__ not in ('__builtin__', 'builtins'):
        return '%s.%s' % (cls.__module__, cls.__name__)
    if value is None:
        return 'None'
    return cls.__name__
    return


def ExpectedTypeError(value, expected, param):
    name = type_name(value)
    return TypeError('%s must be %s, not %s' % (param, expected, name))


def ExpectedStringError(value, param):
    return ExpectedTypeError(value, 'unicode or bytes', param)


def MissingDigestError(handler=None):
    name = _get_name(handler)
    return ValueError('expected %s hash, got %s config string instead' % (
     name, name))


def NullPasswordError(handler=None):
    name = _get_name(handler)
    return ValueError('%s does not allow NULL bytes in password' % name)


def InvalidHashError(handler=None):
    return ValueError('not a valid %s hash' % _get_name(handler))


def MalformedHashError(handler=None, reason=None):
    text = 'malformed %s hash' % _get_name(handler)
    if reason:
        text = '%s (%s)' % (text, reason)
    return ValueError(text)


def ZeroPaddedRoundsError(handler=None):
    return MalformedHashError(handler, 'zero-padded rounds')


def ChecksumSizeError(handler, raw=False):
    checksum_size = handler.checksum_size
    unit = 'bytes' if raw else 'chars'
    reason = 'checksum must be exactly %d %s' % (checksum_size, unit)
    return MalformedHashError(handler, reason)