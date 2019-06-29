import sys, logging
log = logging.getLogger(__name__)
from warnings import warn
from otp.ai.passlib.utils import to_native_str, str_consteq
from otp.ai.passlib.utils.compat import unicode, u, unicode_or_bytes_types
import otp.ai.passlib.utils.handlers as uh
__all__ = [
 'unix_disabled',
 'unix_fallback',
 'plaintext']

class unix_fallback(uh.ifc.DisabledHash, uh.StaticHandler):
    name = 'unix_fallback'
    context_kwds = ('enable_wildcard', )

    @classmethod
    def identify(cls, hash):
        if isinstance(hash, unicode_or_bytes_types):
            return True
        raise uh.exc.ExpectedStringError(hash, 'hash')

    def __init__(self, enable_wildcard=False, **kwds):
        warn("'unix_fallback' is deprecated, and will be removed in Passlib 1.8; please use 'unix_disabled' instead.", DeprecationWarning)
        super(unix_fallback, self).__init__(**kwds)
        self.enable_wildcard = enable_wildcard

    def _calc_checksum(self, secret):
        if self.checksum:
            return self.checksum
        return u('!')

    @classmethod
    def verify(cls, secret, hash, enable_wildcard=False):
        uh.validate_secret(secret)
        if not isinstance(hash, unicode_or_bytes_types):
            raise uh.exc.ExpectedStringError(hash, 'hash')
        else:
            if hash:
                return False
            return enable_wildcard


_MARKER_CHARS = u('*!')
_MARKER_BYTES = '*!'

class unix_disabled(uh.ifc.DisabledHash, uh.MinimalHandler):
    name = 'unix_disabled'
    setting_kwds = ('marker', )
    context_kwds = ()
    _disable_prefixes = tuple(str(_MARKER_CHARS))
    if 'bsd' in sys.platform:
        default_marker = u('*')
    else:
        default_marker = u('!')

    @classmethod
    def using(cls, marker=None, **kwds):
        subcls = super(unix_disabled, cls).using(**kwds)
        if marker is not None:
            if not cls.identify(marker):
                raise ValueError('invalid marker: %r' % marker)
            subcls.default_marker = marker
        return subcls

    @classmethod
    def identify(cls, hash):
        if isinstance(hash, unicode):
            start = _MARKER_CHARS
        else:
            if isinstance(hash, bytes):
                start = _MARKER_BYTES
            else:
                raise uh.exc.ExpectedStringError(hash, 'hash')
        return not hash or hash[0] in start

    @classmethod
    def verify(cls, secret, hash):
        uh.validate_secret(secret)
        if not cls.identify(hash):
            raise uh.exc.InvalidHashError(cls)
        return False

    @classmethod
    def hash(cls, secret, **kwds):
        if kwds:
            uh.warn_hash_settings_deprecation(cls, kwds)
            return cls.using(**kwds).hash(secret)
        uh.validate_secret(secret)
        marker = cls.default_marker
        return to_native_str(marker, param='marker')

    @uh.deprecated_method(deprecated='1.7', removed='2.0')
    @classmethod
    def genhash(cls, secret, config, marker=None):
        if not cls.identify(config):
            raise uh.exc.InvalidHashError(cls)
        else:
            if config:
                uh.validate_secret(secret)
                return to_native_str(config, param='config')
            if marker is not None:
                cls = cls.using(marker=marker)
            return cls.hash(secret)
        return

    @classmethod
    def disable(cls, hash=None):
        out = cls.hash('')
        if hash is not None:
            hash = to_native_str(hash, param='hash')
            if cls.identify(hash):
                hash = cls.enable(hash)
            if hash:
                out += hash
        return out

    @classmethod
    def enable(cls, hash):
        hash = to_native_str(hash, param='hash')
        for prefix in cls._disable_prefixes:
            if hash.startswith(prefix):
                orig = hash[len(prefix):]
                if orig:
                    return orig
                raise ValueError('cannot restore original hash')

        raise uh.exc.InvalidHashError(cls)


class plaintext(uh.MinimalHandler):
    name = 'plaintext'
    setting_kwds = ()
    context_kwds = ('encoding', )
    default_encoding = 'utf-8'

    @classmethod
    def identify(cls, hash):
        if isinstance(hash, unicode_or_bytes_types):
            return True
        raise uh.exc.ExpectedStringError(hash, 'hash')

    @classmethod
    def hash(cls, secret, encoding=None):
        uh.validate_secret(secret)
        if not encoding:
            encoding = cls.default_encoding
        return to_native_str(secret, encoding, 'secret')

    @classmethod
    def verify(cls, secret, hash, encoding=None):
        if not encoding:
            encoding = cls.default_encoding
        hash = to_native_str(hash, encoding, 'hash')
        if not cls.identify(hash):
            raise uh.exc.InvalidHashError(cls)
        return str_consteq(cls.hash(secret, encoding), hash)

    @uh.deprecated_method(deprecated='1.7', removed='2.0')
    @classmethod
    def genconfig(cls):
        return cls.hash('')

    @uh.deprecated_method(deprecated='1.7', removed='2.0')
    @classmethod
    def genhash(cls, secret, config, encoding=None):
        if not cls.identify(config):
            raise uh.exc.InvalidHashError(cls)
        return cls.hash(secret, encoding=encoding)