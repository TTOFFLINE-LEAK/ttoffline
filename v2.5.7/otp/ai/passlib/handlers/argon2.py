from __future__ import with_statement, absolute_import
import logging
log = logging.getLogger(__name__)
import re, types
from warnings import warn
_argon2_cffi = None
_argon2pure = None
from otp.ai.passlib import exc
from otp.ai.passlib.crypto.digest import MAX_UINT32
from otp.ai.passlib.utils import to_bytes
from otp.ai.passlib.utils.binary import b64s_encode, b64s_decode
from otp.ai.passlib.utils.compat import u, unicode, bascii_to_str
import otp.ai.passlib.utils.handlers as uh
__all__ = [
 'argon2']
try:
    import argon2 as _argon2_cffi
except ImportError:
    _argon2_cffi = None

_PasswordHasher = getattr(_argon2_cffi, 'PasswordHasher', None)
if _PasswordHasher:
    _default_settings = _PasswordHasher()
    _default_version = _argon2_cffi.low_level.ARGON2_VERSION
else:

    class _default_settings():
        time_cost = 2
        memory_cost = 512
        parallelism = 2
        salt_len = 16
        hash_len = 16


    _default_version = 19

class _Argon2Common(uh.SubclassBackendMixin, uh.ParallelismMixin, uh.HasRounds, uh.HasRawSalt, uh.HasRawChecksum, uh.GenericHandler):
    name = 'argon2'
    setting_kwds = ('salt', 'salt_size', 'salt_len', 'rounds', 'time_cost', 'memory_cost',
                    'parallelism', 'digest_size', 'hash_len')
    ident = u('$argon2i')
    checksum_size = _default_settings.hash_len
    ident_values = (
     u('$argon2i$'), u('$argon2d$'))
    default_salt_size = _default_settings.salt_len
    min_salt_size = 8
    max_salt_size = MAX_UINT32
    default_rounds = _default_settings.time_cost
    min_rounds = 1
    max_rounds = MAX_UINT32
    rounds_cost = 'linear'
    max_parallelism = 16777215
    max_version = _default_version
    min_desired_version = None
    min_memory_cost = 8
    max_threads = -1
    pure_use_threads = False
    parallelism = _default_settings.parallelism
    version = _default_version
    memory_cost = _default_settings.memory_cost
    type_d = False
    data = None

    @classmethod
    def using(cls, memory_cost=None, salt_len=None, time_cost=None, digest_size=None, checksum_size=None, hash_len=None, max_threads=None, **kwds):
        if time_cost is not None:
            if 'rounds' in kwds:
                raise TypeError("'time_cost' and 'rounds' are mutually exclusive")
            kwds['rounds'] = time_cost
        if salt_len is not None:
            if 'salt_size' in kwds:
                raise TypeError("'salt_len' and 'salt_size' are mutually exclusive")
            kwds['salt_size'] = salt_len
        if hash_len is not None:
            if digest_size is not None:
                raise TypeError("'hash_len' and 'digest_size' are mutually exclusive")
            digest_size = hash_len
        if checksum_size is not None:
            if digest_size is not None:
                raise TypeError("'checksum_size' and 'digest_size' are mutually exclusive")
            digest_size = checksum_size
        subcls = super(_Argon2Common, cls).using(**kwds)
        relaxed = kwds.get('relaxed')
        if digest_size is not None:
            if isinstance(digest_size, uh.native_string_types):
                digest_size = int(digest_size)
            subcls.checksum_size = uh.norm_integer(subcls, digest_size, min=16, max=MAX_UINT32, param='digest_size', relaxed=relaxed)
        if memory_cost is not None:
            if isinstance(memory_cost, uh.native_string_types):
                memory_cost = int(memory_cost)
            subcls.memory_cost = subcls._norm_memory_cost(memory_cost, relaxed=relaxed)
        subcls._validate_constraints(subcls.memory_cost, subcls.parallelism)
        if max_threads is not None:
            if isinstance(max_threads, uh.native_string_types):
                max_threads = int(max_threads)
            if max_threads < 1 and max_threads != -1:
                raise ValueError('max_threads (%d) must be -1 (unlimited), or at least 1.' % (
                 max_threads,))
            subcls.max_threads = max_threads
        return subcls

    @classmethod
    def _validate_constraints(cls, memory_cost, parallelism):
        min_memory_cost = 8 * parallelism
        if memory_cost < min_memory_cost:
            raise ValueError('%s: memory_cost (%d) is too low, must be at least 8 * parallelism (8 * %d = %d)' % (
             cls.name, memory_cost,
             parallelism, min_memory_cost))

    @classmethod
    def identify(cls, hash):
        hash = uh.to_unicode_for_identify(hash)
        return hash.startswith(cls.ident_values)

    _hash_regex = re.compile('\n        ^\n        \\$argon2(?P<type>[id])\\$\n        (?:\n            v=(?P<version>\\d+)\n            \\$\n        )?\n        m=(?P<memory_cost>\\d+)\n        ,\n        t=(?P<time_cost>\\d+)\n        ,\n        p=(?P<parallelism>\\d+)\n        (?:\n            ,keyid=(?P<keyid>[^,$]+)\n        )?\n        (?:\n            ,data=(?P<data>[^,$]+)\n        )?\n        (?:\n            \\$\n            (?P<salt>[^$]+)\n            (?:\n                \\$\n                (?P<digest>.+)\n            )?\n        )?\n        $\n    ', re.X)

    @classmethod
    def from_string(cls, hash):
        if isinstance(hash, unicode):
            hash = hash.encode('utf-8')
        if not isinstance(hash, bytes):
            raise exc.ExpectedStringError(hash, 'hash')
        m = cls._hash_regex.match(hash)
        if not m:
            raise exc.MalformedHashError(cls)
        type, version, memory_cost, time_cost, parallelism, keyid, data, salt, digest = m.group('type', 'version', 'memory_cost', 'time_cost', 'parallelism', 'keyid', 'data', 'salt', 'digest')
        if keyid:
            raise NotImplementedError("argon2 'keyid' parameter not supported")
        return cls(type_d=type == 'd', version=int(version) if version else 16, memory_cost=int(memory_cost), rounds=int(time_cost), parallelism=int(parallelism), salt=b64s_decode(salt) if salt else None, data=b64s_decode(data) if data else None, checksum=b64s_decode(digest) if digest else None)

    def to_string(self):
        ident = str(self.ident_values[self.type_d])
        version = self.version
        if version == 16:
            vstr = ''
        else:
            vstr = 'v=%d$' % version
        data = self.data
        if data:
            kdstr = ',data=' + bascii_to_str(b64s_encode(self.data))
        else:
            kdstr = ''
        return '%s%sm=%d,t=%d,p=%d%s$%s$%s' % (ident, vstr, self.memory_cost,
         self.rounds, self.parallelism,
         kdstr,
         bascii_to_str(b64s_encode(self.salt)),
         bascii_to_str(b64s_encode(self.checksum)))

    def __init__(self, type_d=False, version=None, memory_cost=None, data=None, **kwds):
        checksum = kwds.get('checksum')
        if checksum is not None:
            self.checksum_size = len(checksum)
        super(_Argon2Common, self).__init__(**kwds)
        self.type_d = type_d
        if version is None:
            pass
        else:
            self.version = self._norm_version(version)
        if memory_cost is None:
            pass
        else:
            self.memory_cost = self._norm_memory_cost(memory_cost)
        if data is None:
            pass
        else:
            if not isinstance(data, bytes):
                raise uh.exc.ExpectedTypeError(data, 'bytes', 'data')
            self.data = data
        return

    @classmethod
    def _norm_version(cls, version):
        if not isinstance(version, uh.int_types):
            raise uh.exc.ExpectedTypeError(version, 'integer', 'version')
        if version < 19 and version != 16:
            raise ValueError('invalid argon2 hash version: %d' % (version,))
        backend = cls.get_backend()
        if version > cls.max_version:
            raise ValueError('%s: hash version 0x%X not supported by %r backend (max version is 0x%X); try updating or switching backends' % (
             cls.name, version, backend, cls.max_version))
        return version

    @classmethod
    def _norm_memory_cost(cls, memory_cost, relaxed=False):
        return uh.norm_integer(cls, memory_cost, min=cls.min_memory_cost, param='memory_cost', relaxed=relaxed)

    def _calc_needs_update(self, **kwds):
        cls = type(self)
        if self.type_d:
            return True
        minver = cls.min_desired_version
        if minver is None or minver > cls.max_version:
            minver = cls.max_version
        if self.version < minver:
            return True
        if self.memory_cost != cls.memory_cost:
            return True
        if self.checksum_size != cls.checksum_size:
            return True
        return super(_Argon2Common, self)._calc_needs_update(**kwds)

    _no_backend_suggestion = " -- recommend you install one (e.g. 'pip install argon2_cffi')"

    @classmethod
    def _finalize_backend_mixin(mixin_cls, name, dryrun):
        max_version = mixin_cls.max_version
        if max_version < 19:
            warn("%r doesn't support argon2 v1.3, and should be upgraded" % name, uh.exc.PasslibSecurityWarning)
        return True

    @classmethod
    def _adapt_backend_error(cls, err, hash=None, self=None):
        backend = cls.get_backend()
        if self is None and hash is not None:
            self = cls.from_string(hash)
        if self is not None:
            self._validate_constraints(self.memory_cost, self.parallelism)
            if backend == 'argon2_cffi' and self.data is not None:
                raise NotImplementedError("argon2_cffi backend doesn't support the 'data' parameter")
        text = str(err)
        if text not in ('Decoding failed', ):
            reason = '%s reported: %s: hash=%r' % (backend, text, hash)
        else:
            reason = repr(hash)
        raise exc.MalformedHashError(cls, reason=reason)
        return


class _NoBackend(_Argon2Common):

    @classmethod
    def hash(cls, secret):
        cls._stub_requires_backend()
        return cls.hash(secret)

    @classmethod
    def verify(cls, secret, hash):
        cls._stub_requires_backend()
        return cls.verify(secret, hash)

    @uh.deprecated_method(deprecated='1.7', removed='2.0')
    @classmethod
    def genhash(cls, secret, config):
        cls._stub_requires_backend()
        return cls.genhash(secret, config)

    def _calc_checksum(self, secret):
        self._stub_requires_backend()
        return super(argon2, self)._calc_checksum(secret)


class _CffiBackend(_Argon2Common):

    @classmethod
    def _load_backend_mixin(mixin_cls, name, dryrun):
        if _argon2_cffi is None:
            return False
        max_version = _argon2_cffi.low_level.ARGON2_VERSION
        log.debug("detected 'argon2_cffi' backend, version %r, with support for 0x%x argon2 hashes", _argon2_cffi.__version__, max_version)
        mixin_cls.version = mixin_cls.max_version = max_version
        return mixin_cls._finalize_backend_mixin(name, dryrun)

    @classmethod
    def hash(cls, secret):
        uh.validate_secret(secret)
        secret = to_bytes(secret, 'utf-8')
        try:
            return bascii_to_str(_argon2_cffi.low_level.hash_secret(type=_argon2_cffi.low_level.Type.I, memory_cost=cls.memory_cost, time_cost=cls.default_rounds, parallelism=cls.parallelism, salt=to_bytes(cls._generate_salt()), hash_len=cls.checksum_size, secret=secret))
        except _argon2_cffi.exceptions.HashingError as err:
            raise cls._adapt_backend_error(err)

    @classmethod
    def verify(cls, secret, hash):
        uh.validate_secret(secret)
        secret = to_bytes(secret, 'utf-8')
        hash = to_bytes(hash, 'ascii')
        if hash.startswith('$argon2d$'):
            type = _argon2_cffi.low_level.Type.D
        else:
            type = _argon2_cffi.low_level.Type.I
        try:
            result = _argon2_cffi.low_level.verify_secret(hash, secret, type)
            return True
        except _argon2_cffi.exceptions.VerifyMismatchError:
            return False
        except _argon2_cffi.exceptions.VerificationError as err:
            raise cls._adapt_backend_error(err, hash=hash)

    @classmethod
    def genhash(cls, secret, config):
        uh.validate_secret(secret)
        secret = to_bytes(secret, 'utf-8')
        self = cls.from_string(config)
        if self.type_d:
            type = _argon2_cffi.low_level.Type.D
        else:
            type = _argon2_cffi.low_level.Type.I
        try:
            result = bascii_to_str(_argon2_cffi.low_level.hash_secret(type=type, memory_cost=self.memory_cost, time_cost=self.rounds, parallelism=self.parallelism, salt=to_bytes(self.salt), hash_len=self.checksum_size, secret=secret, version=self.version))
        except _argon2_cffi.exceptions.HashingError as err:
            raise cls._adapt_backend_error(err, hash=config)

        if self.version == 16:
            result = result.replace('$v=16$', '$')
        return result

    def _calc_checksum(self, secret):
        raise AssertionError("shouldn't be called under argon2_cffi backend")


class _PureBackend(_Argon2Common):

    @classmethod
    def _load_backend_mixin(mixin_cls, name, dryrun):
        global _argon2pure
        try:
            import argon2pure as _argon2pure
        except ImportError:
            return False
        else:
            try:
                from argon2pure import ARGON2_DEFAULT_VERSION as max_version
            except ImportError:
                log.warning("detected 'argon2pure' backend, but package is too old (passlib requires argon2pure >= 1.2.3)")
                return False

        log.debug("detected 'argon2pure' backend, with support for 0x%x argon2 hashes", max_version)
        if not dryrun:
            warn("Using argon2pure backend, which is 100x+ slower than is required for adequate security. Installing argon2_cffi (via 'pip install argon2_cffi') is strongly recommended", exc.PasslibSecurityWarning)
        mixin_cls.version = mixin_cls.max_version = max_version
        return mixin_cls._finalize_backend_mixin(name, dryrun)

    def _calc_checksum(self, secret):
        uh.validate_secret(secret)
        secret = to_bytes(secret, 'utf-8')
        if self.type_d:
            type = _argon2pure.ARGON2D
        else:
            type = _argon2pure.ARGON2I
        kwds = dict(password=secret, salt=self.salt, time_cost=self.rounds, memory_cost=self.memory_cost, parallelism=self.parallelism, tag_length=self.checksum_size, type_code=type, version=self.version)
        if self.max_threads > 0:
            kwds['threads'] = self.max_threads
        if self.pure_use_threads:
            kwds['use_threads'] = True
        if self.data:
            kwds['associated_data'] = self.data
        try:
            return _argon2pure.argon2(**kwds)
        except _argon2pure.Argon2Error as err:
            raise self._adapt_backend_error(err, self=self)


class argon2(_NoBackend, _Argon2Common):
    backends = ('argon2_cffi', 'argon2pure')
    _backend_mixin_target = True
    _backend_mixin_map = {None: _NoBackend, 
       'argon2_cffi': _CffiBackend, 
       'argon2pure': _PureBackend}