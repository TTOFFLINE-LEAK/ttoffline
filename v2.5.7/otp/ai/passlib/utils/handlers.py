from __future__ import with_statement
import inspect, logging
log = logging.getLogger(__name__)
import math, threading
from warnings import warn
import otp.ai.passlib.exc as exc, otp.ai.passlib.ifc as ifc
from otp.ai.passlib.exc import MissingBackendError, PasslibConfigWarning, PasslibHashWarning
from otp.ai.passlib.ifc import PasswordHash
from otp.ai.passlib.registry import get_crypt_handler
from otp.ai.passlib.utils import consteq, getrandstr, getrandbytes, rng, to_native_str, is_crypt_handler, to_unicode, MAX_PASSWORD_SIZE, accepts_keyword, as_bool, update_mixin_classes
from otp.ai.passlib.utils.binary import BASE64_CHARS, HASH64_CHARS, PADDED_BASE64_CHARS, HEX_CHARS, UPPER_HEX_CHARS, LOWER_HEX_CHARS, ALL_BYTE_VALUES
from otp.ai.passlib.utils.compat import join_byte_values, irange, u, native_string_types, uascii_to_str, join_unicode, unicode, str_to_uascii, join_unicode, unicode_or_bytes_types, PY2, int_types
from otp.ai.passlib.utils.decor import classproperty, deprecated_method
__all__ = [
 'parse_mc2',
 'parse_mc3',
 'render_mc2',
 'render_mc3',
 'GenericHandler',
 'StaticHandler',
 'HasUserContext',
 'HasRawChecksum',
 'HasManyIdents',
 'HasSalt',
 'HasRawSalt',
 'HasRounds',
 'HasManyBackends',
 'PrefixWrapper']
H64_CHARS = HASH64_CHARS
B64_CHARS = BASE64_CHARS
PADDED_B64_CHARS = PADDED_BASE64_CHARS
UC_HEX_CHARS = UPPER_HEX_CHARS
LC_HEX_CHARS = LOWER_HEX_CHARS

def _bitsize(count, chars):
    if chars and count:
        import math
        return int(count * math.log(len(chars), 2))
    return 0


def guess_app_stacklevel(start=1):
    frame = inspect.currentframe()
    count = -start
    try:
        while frame:
            name = frame.f_globals.get('__name__', '')
            if name.startswith('passlib.tests.') or not name.startswith('passlib.'):
                return max(1, count)
            count += 1
            frame = frame.f_back

        return start
    finally:
        del frame


def warn_hash_settings_deprecation(handler, kwds):
    warn("passing settings to %(handler)s.hash() is deprecated, and won't be supported in Passlib 2.0; use '%(handler)s.using(**settings).hash(secret)' instead" % dict(handler=handler.name), DeprecationWarning, stacklevel=guess_app_stacklevel(2))


def extract_settings_kwds(handler, kwds):
    context_keys = set(handler.context_kwds)
    return dict((key not in context_keys and key, kwds.pop(key)) for key in list(kwds))


_UDOLLAR = u('$')
_UZERO = u('0')

def validate_secret(secret):
    if not isinstance(secret, unicode_or_bytes_types):
        raise exc.ExpectedStringError(secret, 'secret')
    if len(secret) > MAX_PASSWORD_SIZE:
        raise exc.PasswordSizeError(MAX_PASSWORD_SIZE)


def to_unicode_for_identify(hash):
    if isinstance(hash, unicode):
        return hash
    if isinstance(hash, bytes):
        try:
            return hash.decode('utf-8')
        except UnicodeDecodeError:
            return hash.decode('latin-1')

    else:
        raise exc.ExpectedStringError(hash, 'hash')


def parse_mc2(hash, prefix, sep=_UDOLLAR, handler=None):
    hash = to_unicode(hash, 'ascii', 'hash')
    if not hash.startswith(prefix):
        raise exc.InvalidHashError(handler)
    parts = hash[len(prefix):].split(sep)
    if len(parts) == 2:
        salt, chk = parts
        return (
         salt, chk or None)
    if len(parts) == 1:
        return (parts[0], None)
    raise exc.MalformedHashError(handler)
    return


def parse_mc3(hash, prefix, sep=_UDOLLAR, rounds_base=10, default_rounds=None, handler=None):
    hash = to_unicode(hash, 'ascii', 'hash')
    if not hash.startswith(prefix):
        raise exc.InvalidHashError(handler)
    parts = hash[len(prefix):].split(sep)
    if len(parts) == 3:
        rounds, salt, chk = parts
    else:
        if len(parts) == 2:
            rounds, salt = parts
            chk = None
        else:
            raise exc.MalformedHashError(handler)
    if rounds.startswith(_UZERO) and rounds != _UZERO:
        raise exc.ZeroPaddedRoundsError(handler)
    else:
        if rounds:
            rounds = int(rounds, rounds_base)
        else:
            if default_rounds is None:
                raise exc.MalformedHashError(handler, 'empty rounds field')
            else:
                rounds = default_rounds
    return (rounds, salt, chk or None)


def parse_int(source, base=10, default=None, param='value', handler=None):
    if source.startswith(_UZERO) and source != _UZERO:
        raise exc.MalformedHashError(handler, 'zero-padded %s field' % param)
    else:
        if source:
            return int(source, base)
        if default is None:
            raise exc.MalformedHashError(handler, 'empty %s field' % param)
        else:
            return default
    return


def render_mc2(ident, salt, checksum, sep=u('$')):
    if checksum:
        parts = [
         ident, salt, sep, checksum]
    else:
        parts = [
         ident, salt]
    return uascii_to_str(join_unicode(parts))


def render_mc3(ident, rounds, salt, checksum, sep=u('$'), rounds_base=10):
    if rounds is None:
        rounds = u('')
    else:
        if rounds_base == 16:
            rounds = u('%x') % rounds
        else:
            rounds = unicode(rounds)
    if checksum:
        parts = [
         ident, rounds, sep, salt, sep, checksum]
    else:
        parts = [
         ident, rounds, sep, salt]
    return uascii_to_str(join_unicode(parts))


def validate_default_value(handler, default, norm, param='value'):
    return True


def norm_integer(handler, value, min=1, max=None, param='value', relaxed=False):
    if not isinstance(value, int_types):
        raise exc.ExpectedTypeError(value, 'integer', param)
    if value < min:
        msg = '%s: %s (%d) is too low, must be at least %d' % (handler.name, param, value, min)
        if relaxed:
            warn(msg, exc.PasslibHashWarning)
            value = min
        else:
            raise ValueError(msg)
    if max and value > max:
        msg = '%s: %s (%d) is too large, cannot be more than %d' % (handler.name, param, value, max)
        if relaxed:
            warn(msg, exc.PasslibHashWarning)
            value = max
        else:
            raise ValueError(msg)
    return value


class MinimalHandler(PasswordHash):
    _configured = False

    @classmethod
    def using(cls, relaxed=False):
        name = cls.__name__
        if not cls._configured:
            name = '<customized %s hasher>' % name
        return type(name, (cls,), dict(__module__=cls.__module__, _configured=True))


class TruncateMixin(MinimalHandler):
    truncate_error = False
    truncate_verify_reject = False

    @classmethod
    def using(cls, truncate_error=None, **kwds):
        subcls = super(TruncateMixin, cls).using(**kwds)
        if truncate_error is not None:
            truncate_error = as_bool(truncate_error, param='truncate_error')
            if truncate_error is not None:
                subcls.truncate_error = truncate_error
        return subcls

    @classmethod
    def _check_truncate_policy(cls, secret):
        if cls.truncate_error and len(secret) > cls.truncate_size:
            raise exc.PasswordTruncateError(cls)


class GenericHandler(MinimalHandler):
    setting_kwds = None
    context_kwds = ()
    ident = None
    _hash_regex = None
    checksum_size = None
    checksum_chars = None
    _checksum_is_bytes = False
    checksum = None

    def __init__(self, checksum=None, use_defaults=False, **kwds):
        self.use_defaults = use_defaults
        super(GenericHandler, self).__init__(**kwds)
        if checksum is not None:
            self.checksum = self._norm_checksum(checksum)
        return

    def _norm_checksum(self, checksum, relaxed=False):
        raw = self._checksum_is_bytes
        if raw:
            if not isinstance(checksum, bytes):
                raise exc.ExpectedTypeError(checksum, 'bytes', 'checksum')
        else:
            if not isinstance(checksum, unicode):
                if isinstance(checksum, bytes) and relaxed:
                    warn('checksum should be unicode, not bytes', PasslibHashWarning)
                    checksum = checksum.decode('ascii')
                else:
                    raise exc.ExpectedTypeError(checksum, 'unicode', 'checksum')
        cc = self.checksum_size
        if cc and len(checksum) != cc:
            raise exc.ChecksumSizeError(self, raw=raw)
        if not raw:
            cs = self.checksum_chars
            if cs and any(c not in cs for c in checksum):
                raise ValueError('invalid characters in %s checksum' % (self.name,))
        return checksum

    @classmethod
    def identify(cls, hash):
        hash = to_unicode_for_identify(hash)
        if not hash:
            return False
        ident = cls.ident
        if ident is not None:
            return hash.startswith(ident)
        pat = cls._hash_regex
        if pat is not None:
            return pat.match(hash) is not None
        try:
            cls.from_string(hash)
            return True
        except ValueError:
            return False

        return

    @classmethod
    def from_string(cls, hash, **context):
        raise NotImplementedError('%s must implement from_string()' % (cls,))

    def to_string(self):
        raise NotImplementedError('%s must implement from_string()' % (self.__class__,))

    @property
    def _stub_checksum(self):
        if self.checksum_size:
            if self._checksum_is_bytes:
                return '\x00' * self.checksum_size
            if self.checksum_chars:
                return self.checksum_chars[0] * self.checksum_size
        if isinstance(self, HasRounds):
            orig = self.rounds
            self.rounds = self.min_rounds or 1
            try:
                return self._calc_checksum('')
            finally:
                self.rounds = orig

        return self._calc_checksum('')

    def _calc_checksum(self, secret):
        raise NotImplementedError('%s must implement _calc_checksum()' % (
         self.__class__,))

    @classmethod
    def hash(cls, secret, **kwds):
        if kwds:
            settings = extract_settings_kwds(cls, kwds)
            if settings:
                warn_hash_settings_deprecation(cls, settings)
                return cls.using(**settings).hash(secret, **kwds)
        validate_secret(secret)
        self = cls(use_defaults=True, **kwds)
        self.checksum = self._calc_checksum(secret)
        return self.to_string()

    @classmethod
    def verify(cls, secret, hash, **context):
        validate_secret(secret)
        self = cls.from_string(hash, **context)
        chk = self.checksum
        if chk is None:
            raise exc.MissingDigestError(cls)
        return consteq(self._calc_checksum(secret), chk)

    @deprecated_method(deprecated='1.7', removed='2.0')
    @classmethod
    def genconfig(cls, **kwds):
        settings = extract_settings_kwds(cls, kwds)
        if settings:
            return cls.using(**settings).genconfig(**kwds)
        self = cls(use_defaults=True, **kwds)
        self.checksum = self._stub_checksum
        return self.to_string()

    @deprecated_method(deprecated='1.7', removed='2.0')
    @classmethod
    def genhash(cls, secret, config, **context):
        if config is None:
            raise TypeError('config must be string')
        validate_secret(secret)
        self = cls.from_string(config, **context)
        self.checksum = self._calc_checksum(secret)
        return self.to_string()

    @classmethod
    def needs_update(cls, hash, secret=None, **kwds):
        self = cls.from_string(hash)
        return self._calc_needs_update(secret=secret, **kwds)

    def _calc_needs_update(self, secret=None):
        return False

    _unparsed_settings = ('salt_size', 'relaxed')
    _unsafe_settings = ('salt', 'checksum')

    @classproperty
    def _parsed_settings(cls):
        return (key for key in cls.setting_kwds if key not in cls._unparsed_settings)

    @staticmethod
    def _sanitize(value, char=u('*')):
        if value is None:
            return
        if isinstance(value, bytes):
            from otp.ai.passlib.utils.binary import ab64_encode
            value = ab64_encode(value).decode('ascii')
        else:
            if not isinstance(value, unicode):
                value = unicode(value)
        size = len(value)
        clip = min(4, size // 8)
        return value[:clip] + char * (size - clip)

    @classmethod
    def parsehash(cls, hash, checksum=True, sanitize=False):
        self = cls.from_string(hash)
        UNSET = object()
        kwds = dict((
         getattr(self, key) != getattr(cls, key, UNSET) and key, getattr(self, key)) for key in self._parsed_settings)
        if checksum and self.checksum is not None:
            kwds['checksum'] = self.checksum
        if sanitize:
            if sanitize is True:
                sanitize = cls._sanitize
            for key in cls._unsafe_settings:
                if key in kwds:
                    kwds[key] = sanitize(kwds[key])

        return kwds

    @classmethod
    def bitsize(cls, **kwds):
        try:
            info = super(GenericHandler, cls).bitsize(**kwds)
        except AttributeError:
            info = {}

        cc = ALL_BYTE_VALUES if cls._checksum_is_bytes else cls.checksum_chars
        if cls.checksum_size and cc:
            info['checksum'] = _bitsize(cls.checksum_size, cc)
        return info


class StaticHandler(GenericHandler):
    setting_kwds = ()
    _hash_prefix = u('')

    @classmethod
    def from_string(cls, hash, **context):
        hash = to_unicode(hash, 'ascii', 'hash')
        hash = cls._norm_hash(hash)
        prefix = cls._hash_prefix
        if prefix:
            if hash.startswith(prefix):
                hash = hash[len(prefix):]
            else:
                raise exc.InvalidHashError(cls)
        return cls(checksum=hash, **context)

    @classmethod
    def _norm_hash(cls, hash):
        return hash

    def to_string(self):
        return uascii_to_str(self._hash_prefix + self.checksum)

    __cc_compat_hack = None

    def _calc_checksum(self, secret):
        cls = self.__class__
        wrapper_cls = cls.__cc_compat_hack
        if wrapper_cls is None:

            def inner(self, secret):
                raise NotImplementedError('%s must implement _calc_checksum()' % (
                 cls,))

            wrapper_cls = cls.__cc_compat_hack = type(cls.__name__ + '_wrapper', (
             cls,), dict(_calc_checksum=inner, __module__=cls.__module__))
        context = dict((k, getattr(self, k)) for k in self.context_kwds)
        try:
            hash = wrapper_cls.genhash(secret, None, **context)
        except TypeError as err:
            if str(err) == 'config must be string':
                raise NotImplementedError('%s must implement _calc_checksum()' % (
                 cls,))
            else:
                raise

        warn('%r should be updated to implement StaticHandler._calc_checksum() instead of StaticHandler.genhash(), support for the latter style will be removed in Passlib 1.8' % cls, DeprecationWarning)
        return str_to_uascii(hash)


class HasEncodingContext(GenericHandler):
    context_kwds = ('encoding', )
    default_encoding = 'utf-8'

    def __init__(self, encoding=None, **kwds):
        super(HasEncodingContext, self).__init__(**kwds)
        self.encoding = encoding or self.default_encoding


class HasUserContext(GenericHandler):
    context_kwds = ('user', )

    def __init__(self, user=None, **kwds):
        super(HasUserContext, self).__init__(**kwds)
        self.user = user

    @classmethod
    def hash(cls, secret, user=None, **context):
        return super(HasUserContext, cls).hash(secret, user=user, **context)

    @classmethod
    def verify(cls, secret, hash, user=None, **context):
        return super(HasUserContext, cls).verify(secret, hash, user=user, **context)

    @deprecated_method(deprecated='1.7', removed='2.0')
    @classmethod
    def genhash(cls, secret, config, user=None, **context):
        return super(HasUserContext, cls).genhash(secret, config, user=user, **context)


class HasRawChecksum(GenericHandler):
    _checksum_is_bytes = True


class HasManyIdents(GenericHandler):
    default_ident = None
    ident_values = None
    ident_aliases = None
    ident = None

    @classmethod
    def using(cls, default_ident=None, ident=None, **kwds):
        if ident is not None:
            if default_ident is not None:
                raise TypeError("'default_ident' and 'ident' are mutually exclusive")
            default_ident = ident
        subcls = super(HasManyIdents, cls).using(**kwds)
        if default_ident is not None:
            subcls.default_ident = cls(ident=default_ident, use_defaults=True).ident
        return subcls

    def __init__(self, ident=None, **kwds):
        super(HasManyIdents, self).__init__(**kwds)
        if ident is not None:
            ident = self._norm_ident(ident)
        else:
            if self.use_defaults:
                ident = self.default_ident
            else:
                raise TypeError('no ident specified')
        self.ident = ident
        return

    @classmethod
    def _norm_ident(cls, ident):
        if isinstance(ident, bytes):
            ident = ident.decode('ascii')
        iv = cls.ident_values
        if ident in iv:
            return ident
        ia = cls.ident_aliases
        if ia:
            try:
                value = ia[ident]
            except KeyError:
                pass
            else:
                if value in iv:
                    return value

        raise ValueError('invalid ident: %r' % (ident,))

    @classmethod
    def identify(cls, hash):
        hash = to_unicode_for_identify(hash)
        return hash.startswith(cls.ident_values)

    @classmethod
    def _parse_ident(cls, hash):
        hash = to_unicode(hash, 'ascii', 'hash')
        for ident in cls.ident_values:
            if hash.startswith(ident):
                return (ident, hash[len(ident):])

        raise exc.InvalidHashError(cls)


class HasSalt(GenericHandler):
    min_salt_size = 0
    max_salt_size = None
    salt_chars = None

    @classproperty
    def default_salt_size(cls):
        return cls.max_salt_size

    @classproperty
    def default_salt_chars(cls):
        return cls.salt_chars

    _salt_is_bytes = False
    _salt_unit = 'chars'
    salt = None

    @classmethod
    def using(cls, default_salt_size=None, salt_size=None, salt=None, **kwds):
        if salt_size is not None:
            if default_salt_size is not None:
                raise TypeError("'salt_size' and 'default_salt_size' aliases are mutually exclusive")
            default_salt_size = salt_size
        subcls = super(HasSalt, cls).using(**kwds)
        relaxed = kwds.get('relaxed')
        if default_salt_size is not None:
            if isinstance(default_salt_size, native_string_types):
                default_salt_size = int(default_salt_size)
            subcls.default_salt_size = subcls._clip_to_valid_salt_size(default_salt_size, param='salt_size', relaxed=relaxed)
        if salt is not None:
            salt = subcls._norm_salt(salt, relaxed=relaxed)
            subcls._generate_salt = staticmethod(lambda : salt)
        return subcls

    @classmethod
    def _clip_to_valid_salt_size(cls, salt_size, param='salt_size', relaxed=True):
        mn = cls.min_salt_size
        mx = cls.max_salt_size
        if mn == mx:
            if salt_size != mn:
                msg = '%s: %s (%d) must be exactly %d' % (cls.name, param, salt_size, mn)
                if relaxed:
                    warn(msg, PasslibHashWarning)
                else:
                    raise ValueError(msg)
            return mn
        if salt_size < mn:
            msg = '%s: %s (%r) below min_salt_size (%d)' % (cls.name, param, salt_size, mn)
            if relaxed:
                warn(msg, PasslibHashWarning)
                salt_size = mn
            else:
                raise ValueError(msg)
        if mx and salt_size > mx:
            msg = '%s: %s (%r) above max_salt_size (%d)' % (cls.name, param, salt_size, mx)
            if relaxed:
                warn(msg, PasslibHashWarning)
                salt_size = mx
            else:
                raise ValueError(msg)
        return salt_size

    def __init__(self, salt=None, **kwds):
        super(HasSalt, self).__init__(**kwds)
        if salt is not None:
            salt = self._parse_salt(salt)
        else:
            if self.use_defaults:
                salt = self._generate_salt()
            else:
                raise TypeError('no salt specified')
        self.salt = salt
        return

    def _parse_salt(self, salt):
        return self._norm_salt(salt)

    @classmethod
    def _norm_salt(cls, salt, relaxed=False):
        if cls._salt_is_bytes:
            if not isinstance(salt, bytes):
                raise exc.ExpectedTypeError(salt, 'bytes', 'salt')
        else:
            if not isinstance(salt, unicode):
                if isinstance(salt, bytes) and (PY2 or relaxed):
                    salt = salt.decode('ascii')
                else:
                    raise exc.ExpectedTypeError(salt, 'unicode', 'salt')
            sc = cls.salt_chars
            if sc is not None and any(c not in sc for c in salt):
                raise ValueError('invalid characters in %s salt' % cls.name)
        mn = cls.min_salt_size
        if mn and len(salt) < mn:
            msg = 'salt too small (%s requires %s %d %s)' % (cls.name,
             'exactly' if mn == cls.max_salt_size else '>=', mn, cls._salt_unit)
            raise ValueError(msg)
        mx = cls.max_salt_size
        if mx and len(salt) > mx:
            msg = 'salt too large (%s requires %s %d %s)' % (cls.name,
             'exactly' if mx == mn else '<=', mx, cls._salt_unit)
            if relaxed:
                warn(msg, PasslibHashWarning)
                salt = cls._truncate_salt(salt, mx)
            else:
                raise ValueError(msg)
        return salt

    @staticmethod
    def _truncate_salt(salt, mx):
        return salt[:mx]

    @classmethod
    def _generate_salt(cls):
        return getrandstr(rng, cls.default_salt_chars, cls.default_salt_size)

    @classmethod
    def bitsize(cls, salt_size=None, **kwds):
        info = super(HasSalt, cls).bitsize(**kwds)
        if salt_size is None:
            salt_size = cls.default_salt_size
        info['salt'] = _bitsize(salt_size, cls.default_salt_chars)
        return info


class HasRawSalt(HasSalt):
    salt_chars = ALL_BYTE_VALUES
    _salt_is_bytes = True
    _salt_unit = 'bytes'

    @classmethod
    def _generate_salt(cls):
        return getrandbytes(rng, cls.default_salt_size)


class HasRounds(GenericHandler):
    min_rounds = 0
    max_rounds = None
    rounds_cost = 'linear'
    using_rounds_kwds = ('min_desired_rounds', 'max_desired_rounds', 'min_rounds',
                         'max_rounds', 'default_rounds', 'vary_rounds')
    min_desired_rounds = None
    max_desired_rounds = None
    default_rounds = None
    vary_rounds = None
    rounds = None

    @classmethod
    def using(cls, min_desired_rounds=None, max_desired_rounds=None, default_rounds=None, vary_rounds=None, min_rounds=None, max_rounds=None, rounds=None, **kwds):
        if min_rounds is not None:
            if min_desired_rounds is not None:
                raise TypeError("'min_rounds' and 'min_desired_rounds' aliases are mutually exclusive")
            min_desired_rounds = min_rounds
        if max_rounds is not None:
            if max_desired_rounds is not None:
                raise TypeError("'max_rounds' and 'max_desired_rounds' aliases are mutually exclusive")
            max_desired_rounds = max_rounds
        if rounds is not None:
            if min_desired_rounds is None:
                min_desired_rounds = rounds
            if max_desired_rounds is None:
                max_desired_rounds = rounds
            if default_rounds is None:
                default_rounds = rounds
        subcls = super(HasRounds, cls).using(**kwds)
        relaxed = kwds.get('relaxed')
        if min_desired_rounds is None:
            explicit_min_rounds = False
            min_desired_rounds = cls.min_desired_rounds
        else:
            explicit_min_rounds = True
            if isinstance(min_desired_rounds, native_string_types):
                min_desired_rounds = int(min_desired_rounds)
            subcls.min_desired_rounds = subcls._norm_rounds(min_desired_rounds, param='min_desired_rounds', relaxed=relaxed)
        if max_desired_rounds is None:
            max_desired_rounds = cls.max_desired_rounds
        else:
            if isinstance(max_desired_rounds, native_string_types):
                max_desired_rounds = int(max_desired_rounds)
            if min_desired_rounds and max_desired_rounds < min_desired_rounds:
                msg = '%s: max_desired_rounds (%r) below min_desired_rounds (%r)' % (
                 subcls.name, max_desired_rounds, min_desired_rounds)
                if explicit_min_rounds:
                    raise ValueError(msg)
                else:
                    warn(msg, PasslibConfigWarning)
                    max_desired_rounds = min_desired_rounds
            subcls.max_desired_rounds = subcls._norm_rounds(max_desired_rounds, param='max_desired_rounds', relaxed=relaxed)
        if default_rounds is not None:
            if isinstance(default_rounds, native_string_types):
                default_rounds = int(default_rounds)
            if min_desired_rounds and default_rounds < min_desired_rounds:
                raise ValueError('%s: default_rounds (%r) below min_desired_rounds (%r)' % (
                 subcls.name, default_rounds, min_desired_rounds))
            else:
                if max_desired_rounds and default_rounds > max_desired_rounds:
                    raise ValueError('%s: default_rounds (%r) above max_desired_rounds (%r)' % (
                     subcls.name, default_rounds, max_desired_rounds))
            subcls.default_rounds = subcls._norm_rounds(default_rounds, param='default_rounds', relaxed=relaxed)
        if subcls.default_rounds is not None:
            subcls.default_rounds = subcls._clip_to_desired_rounds(subcls.default_rounds)
        if vary_rounds is not None:
            if isinstance(vary_rounds, native_string_types):
                if vary_rounds.endswith('%'):
                    vary_rounds = float(vary_rounds[:-1]) * 0.01
                elif '.' in vary_rounds:
                    vary_rounds = float(vary_rounds)
                else:
                    vary_rounds = int(vary_rounds)
            if vary_rounds < 0:
                raise ValueError('%s: vary_rounds (%r) below 0' % (
                 subcls.name, vary_rounds))
            else:
                if isinstance(vary_rounds, float):
                    if vary_rounds > 1:
                        raise ValueError('%s: vary_rounds (%r) above 1.0' % (
                         subcls.name, vary_rounds))
                else:
                    if not isinstance(vary_rounds, int):
                        raise TypeError('vary_rounds must be int or float')
            if vary_rounds:
                warn("The 'vary_rounds' option is deprecated as of Passlib 1.7, and will be removed in Passlib 2.0", PasslibConfigWarning)
            subcls.vary_rounds = vary_rounds
        return subcls

    @classmethod
    def _clip_to_desired_rounds(cls, rounds):
        mnd = cls.min_desired_rounds or 0
        if rounds < mnd:
            return mnd
        mxd = cls.max_desired_rounds
        if mxd and rounds > mxd:
            return mxd
        return rounds

    @classmethod
    def _calc_vary_rounds_range(cls, default_rounds):
        vary_rounds = cls.vary_rounds

        def linear_to_native(value, upper):
            return value

        if isinstance(vary_rounds, float):
            if cls.rounds_cost == 'log2':
                default_rounds = 1 << default_rounds

                def linear_to_native(value, upper):
                    if value <= 0:
                        return 0
                    if upper:
                        return int(math.log(value, 2))
                    return int(math.ceil(math.log(value, 2)))

            vary_rounds = int(default_rounds * vary_rounds)
        lower = linear_to_native(default_rounds - vary_rounds, False)
        upper = linear_to_native(default_rounds + vary_rounds, True)
        return (
         cls._clip_to_desired_rounds(lower), cls._clip_to_desired_rounds(upper))

    def __init__(self, rounds=None, **kwds):
        super(HasRounds, self).__init__(**kwds)
        if rounds is not None:
            rounds = self._parse_rounds(rounds)
        else:
            if self.use_defaults:
                rounds = self._generate_rounds()
            else:
                raise TypeError('no rounds specified')
        self.rounds = rounds
        return

    def _parse_rounds(self, rounds):
        return self._norm_rounds(rounds)

    @classmethod
    def _norm_rounds(cls, rounds, relaxed=False, param='rounds'):
        return norm_integer(cls, rounds, cls.min_rounds, cls.max_rounds, param=param, relaxed=relaxed)

    @classmethod
    def _generate_rounds(cls):
        rounds = cls.default_rounds
        if rounds is None:
            raise TypeError('%s rounds value must be specified explicitly' % (cls.name,))
        if cls.vary_rounds:
            lower, upper = cls._calc_vary_rounds_range(rounds)
            if lower < upper:
                rounds = rng.randint(lower, upper)
        return rounds

    def _calc_needs_update(self, **kwds):
        min_desired_rounds = self.min_desired_rounds
        if min_desired_rounds and self.rounds < min_desired_rounds:
            return True
        max_desired_rounds = self.max_desired_rounds
        if max_desired_rounds and self.rounds > max_desired_rounds:
            return True
        return super(HasRounds, self)._calc_needs_update(**kwds)

    @classmethod
    def bitsize(cls, rounds=None, vary_rounds=0.1, **kwds):
        info = super(HasRounds, cls).bitsize(**kwds)
        if cls.rounds_cost != 'log2':
            import math
            if rounds is None:
                rounds = cls.default_rounds
            info['rounds'] = max(0, int(1 + math.log(rounds * vary_rounds, 2)))
        return info


class ParallelismMixin(GenericHandler):
    parallelism = 1

    @classmethod
    def using(cls, parallelism=None, **kwds):
        subcls = super(ParallelismMixin, cls).using(**kwds)
        if parallelism is not None:
            if isinstance(parallelism, native_string_types):
                parallelism = int(parallelism)
            subcls.parallelism = subcls._norm_parallelism(parallelism, relaxed=kwds.get('relaxed'))
        return subcls

    def __init__(self, parallelism=None, **kwds):
        super(ParallelismMixin, self).__init__(**kwds)
        if parallelism is None:
            pass
        else:
            self.parallelism = self._norm_parallelism(parallelism)
        return

    @classmethod
    def _norm_parallelism(cls, parallelism, relaxed=False):
        return norm_integer(cls, parallelism, min=1, param='parallelism', relaxed=relaxed)

    def _calc_needs_update(self, **kwds):
        if self.parallelism != type(self).parallelism:
            return True
        return super(ParallelismMixin, self)._calc_needs_update(**kwds)


_backend_lock = threading.RLock()

class BackendMixin(PasswordHash):
    backends = None
    __backend = None
    _no_backend_suggestion = None
    _pending_backend = None
    _pending_dry_run = False

    @classmethod
    def get_backend(cls):
        if not cls.__backend:
            cls.set_backend()
        return cls.__backend

    @classmethod
    def has_backend(cls, name='any'):
        try:
            cls.set_backend(name, dryrun=True)
            return True
        except (exc.MissingBackendError, exc.PasslibSecurityError):
            return False

    @classmethod
    def set_backend(cls, name='any', dryrun=False):
        if name == 'any' and cls.__backend or name and name == cls.__backend:
            return cls.__backend
        owner = cls._get_backend_owner()
        if owner is not cls:
            return owner.set_backend(name, dryrun=dryrun)
        if name == 'any' or name == 'default':
            default_error = None
            for name in cls.backends:
                try:
                    return cls.set_backend(name, dryrun=dryrun)
                except exc.MissingBackendError:
                    continue
                except exc.PasslibSecurityError as err:
                    if default_error is None:
                        default_error = err
                    continue

            if default_error is None:
                msg = '%s: no backends available' % cls.name
                if cls._no_backend_suggestion:
                    msg += cls._no_backend_suggestion
                default_error = exc.MissingBackendError(msg)
            raise default_error
        if name not in cls.backends:
            raise exc.UnknownBackendError(cls, name)
        with _backend_lock:
            orig = (
             cls._pending_backend, cls._pending_dry_run)
            try:
                cls._pending_backend = name
                cls._pending_dry_run = dryrun
                cls._set_backend(name, dryrun)
            finally:
                cls._pending_backend, cls._pending_dry_run = orig

            if not dryrun:
                cls.__backend = name
            return name
        return

    @classmethod
    def _get_backend_owner(cls):
        return cls

    @classmethod
    def _set_backend(cls, name, dryrun):
        loader = cls._get_backend_loader(name)
        kwds = {}
        if accepts_keyword(loader, 'name'):
            kwds['name'] = name
        if accepts_keyword(loader, 'dryrun'):
            kwds['dryrun'] = dryrun
        ok = loader(**kwds)
        if ok is False:
            raise exc.MissingBackendError('%s: backend not available: %s' % (
             cls.name, name))
        else:
            if ok is not True:
                raise AssertionError('backend loaders must return True or False: %r' % (
                 ok,))

    @classmethod
    def _get_backend_loader(cls, name):
        raise NotImplementedError('implement in subclass')

    @classmethod
    def _stub_requires_backend(cls):
        if cls.__backend:
            raise AssertionError('%s: _finalize_backend(%r) failed to replace lazy loader' % (
             cls.name, cls.__backend))
        cls.set_backend()
        if not cls.__backend:
            raise AssertionError('%s: set_backend() failed to load a default backend' % cls.name)


class SubclassBackendMixin(BackendMixin):
    _backend_mixin_target = False
    _backend_mixin_map = None

    @classmethod
    def _get_backend_owner(cls):
        if not cls._backend_mixin_target:
            raise AssertionError('_backend_mixin_target not set')
        for base in cls.__mro__:
            if base.__dict__.get('_backend_mixin_target'):
                return base

        raise AssertionError("expected to find class w/ '_backend_mixin_target' set")

    @classmethod
    def _set_backend(cls, name, dryrun):
        super(SubclassBackendMixin, cls)._set_backend(name, dryrun)
        mixin_map = cls._backend_mixin_map
        mixin_cls = mixin_map[name]
        update_mixin_classes(cls, add=mixin_cls, remove=mixin_map.values(), append=True, before=SubclassBackendMixin, dryrun=dryrun)

    @classmethod
    def _get_backend_loader(cls, name):
        return cls._backend_mixin_map[name]._load_backend_mixin


class HasManyBackends(BackendMixin, GenericHandler):

    def _calc_checksum(self, secret):
        return self._calc_checksum_backend(secret)

    def _calc_checksum_backend(self, secret):
        self._stub_requires_backend()
        return self._calc_checksum_backend(secret)

    @classmethod
    def _get_backend_loader(cls, name):
        loader = getattr(cls, '_load_backend_' + name, None)
        if loader is None:

            def loader():
                return cls.__load_legacy_backend(name)

        return loader

    @classmethod
    def __load_legacy_backend(cls, name):
        value = getattr(cls, '_has_backend_' + name)
        warn('%s: support for ._has_backend_%s is deprecated as of Passlib 1.7, and will be removed in Passlib 1.9/2.0, please implement ._load_backend_%s() instead' % (
         cls.name, name, name), DeprecationWarning)
        if value:
            func = getattr(cls, '_calc_checksum_' + name)
            cls._set_calc_checksum_backend(func)
            return True
        return False

    @classmethod
    def _set_calc_checksum_backend(cls, func):
        backend = cls._pending_backend
        if not callable(func):
            raise RuntimeError('%s: backend %r returned invalid callable: %r' % (
             cls.name, backend, func))
        if not cls._pending_dry_run:
            cls._calc_checksum_backend = func


class PrefixWrapper(object):
    _using_clone_attrs = ()

    def __init__(self, name, wrapped, prefix=u(''), orig_prefix=u(''), lazy=False, doc=None, ident=None):
        self.name = name
        if isinstance(prefix, bytes):
            prefix = prefix.decode('ascii')
        self.prefix = prefix
        if isinstance(orig_prefix, bytes):
            orig_prefix = orig_prefix.decode('ascii')
        self.orig_prefix = orig_prefix
        if doc:
            self.__doc__ = doc
        if hasattr(wrapped, 'name'):
            self._set_wrapped(wrapped)
        else:
            self._wrapped_name = wrapped
            if not lazy:
                self._get_wrapped()
        if ident is not None:
            if ident is True:
                if prefix:
                    ident = prefix
                else:
                    raise ValueError('no prefix specified')
            if isinstance(ident, bytes):
                ident = ident.decode('ascii')
            if ident[:len(prefix)] != prefix[:len(ident)]:
                raise ValueError('ident must agree with prefix')
            self._ident = ident
        return

    _wrapped_name = None
    _wrapped_handler = None

    def _set_wrapped(self, handler):
        if 'ident' in handler.setting_kwds and self.orig_prefix:
            warn("PrefixWrapper: 'orig_prefix' option may not work correctly for handlers which have multiple identifiers: %r" % (
             handler.name,), exc.PasslibRuntimeWarning)
        self._wrapped_handler = handler

    def _get_wrapped(self):
        handler = self._wrapped_handler
        if handler is None:
            handler = get_crypt_handler(self._wrapped_name)
            self._set_wrapped(handler)
        return handler

    wrapped = property(_get_wrapped)
    _ident = False

    @property
    def ident(self):
        value = self._ident
        if value is False:
            value = None
            if not self.orig_prefix:
                wrapped = self.wrapped
                ident = getattr(wrapped, 'ident', None)
                if ident is not None:
                    value = self._wrap_hash(ident)
            self._ident = value
        return value

    _ident_values = False

    @property
    def ident_values(self):
        value = self._ident_values
        if value is False:
            value = None
            if not self.orig_prefix:
                wrapped = self.wrapped
                idents = getattr(wrapped, 'ident_values', None)
                if idents:
                    value = tuple(self._wrap_hash(ident) for ident in idents)
            self._ident_values = value
        return value

    _proxy_attrs = ('setting_kwds', 'context_kwds', 'default_rounds', 'min_rounds',
                    'max_rounds', 'rounds_cost', 'min_desired_rounds', 'max_desired_rounds',
                    'vary_rounds', 'default_salt_size', 'min_salt_size', 'max_salt_size',
                    'salt_chars', 'default_salt_chars', 'backends', 'has_backend',
                    'get_backend', 'set_backend', 'is_disabled', 'truncate_size',
                    'truncate_error', 'truncate_verify_reject', '_salt_is_bytes')

    def __repr__(self):
        args = [
         repr(self._wrapped_name or self._wrapped_handler)]
        if self.prefix:
            args.append('prefix=%r' % self.prefix)
        if self.orig_prefix:
            args.append('orig_prefix=%r' % self.orig_prefix)
        args = (', ').join(args)
        return 'PrefixWrapper(%r, %s)' % (self.name, args)

    def __dir__(self):
        attrs = set(dir(self.__class__))
        attrs.update(self.__dict__)
        wrapped = self.wrapped
        attrs.update(attr for attr in self._proxy_attrs if hasattr(wrapped, attr))
        return list(attrs)

    def __getattr__(self, attr):
        if attr in self._proxy_attrs:
            return getattr(self.wrapped, attr)
        raise AttributeError('missing attribute: %r' % (attr,))

    def __setattr__(self, attr, value):
        if attr in self._proxy_attrs and self._derived_from:
            wrapped = self.wrapped
            if hasattr(wrapped, attr):
                setattr(wrapped, attr, value)
                return
        return object.__setattr__(self, attr, value)

    def _unwrap_hash(self, hash):
        prefix = self.prefix
        if not hash.startswith(prefix):
            raise exc.InvalidHashError(self)
        return self.orig_prefix + hash[len(prefix):]

    def _wrap_hash(self, hash):
        if isinstance(hash, bytes):
            hash = hash.decode('ascii')
        orig_prefix = self.orig_prefix
        if not hash.startswith(orig_prefix):
            raise exc.InvalidHashError(self.wrapped)
        wrapped = self.prefix + hash[len(orig_prefix):]
        return uascii_to_str(wrapped)

    _derived_from = None

    def using(self, **kwds):
        subcls = self.wrapped.using(**kwds)
        wrapper = PrefixWrapper(self.name, subcls, prefix=self.prefix, orig_prefix=self.orig_prefix)
        wrapper._derived_from = self
        for attr in self._using_clone_attrs:
            setattr(wrapper, attr, getattr(self, attr))

        return wrapper

    def needs_update(self, hash, **kwds):
        hash = self._unwrap_hash(hash)
        return self.wrapped.needs_update(hash, **kwds)

    def identify(self, hash):
        hash = to_unicode_for_identify(hash)
        if not hash.startswith(self.prefix):
            return False
        hash = self._unwrap_hash(hash)
        return self.wrapped.identify(hash)

    @deprecated_method(deprecated='1.7', removed='2.0')
    def genconfig(self, **kwds):
        config = self.wrapped.genconfig(**kwds)
        if config is None:
            raise RuntimeError('.genconfig() must return a string, not None')
        return self._wrap_hash(config)

    @deprecated_method(deprecated='1.7', removed='2.0')
    def genhash(self, secret, config, **kwds):
        if config is not None:
            config = to_unicode(config, 'ascii', 'config/hash')
            config = self._unwrap_hash(config)
        return self._wrap_hash(self.wrapped.genhash(secret, config, **kwds))

    @deprecated_method(deprecated='1.7', removed='2.0', replacement='.hash()')
    def encrypt(self, secret, **kwds):
        return self.hash(secret, **kwds)

    def hash(self, secret, **kwds):
        return self._wrap_hash(self.wrapped.hash(secret, **kwds))

    def verify(self, secret, hash, **kwds):
        hash = to_unicode(hash, 'ascii', 'hash')
        hash = self._unwrap_hash(hash)
        return self.wrapped.verify(secret, hash, **kwds)