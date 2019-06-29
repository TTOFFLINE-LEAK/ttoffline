from __future__ import with_statement, absolute_import
from base64 import b64encode
from hashlib import sha256
import os, re, logging
log = logging.getLogger(__name__)
from warnings import warn
_bcrypt = None
_pybcrypt = None
_bcryptor = None
_builtin_bcrypt = None
from otp.ai.passlib.exc import PasslibHashWarning, PasslibSecurityWarning, PasslibSecurityError
from otp.ai.passlib.utils import safe_crypt, repeat_string, to_bytes, parse_version, rng, getrandstr, test_crypt, to_unicode
from otp.ai.passlib.utils.binary import bcrypt64
from otp.ai.passlib.utils.compat import u, uascii_to_str, unicode, str_to_uascii
import otp.ai.passlib.utils.handlers as uh
__all__ = [
 'bcrypt']
IDENT_2 = u('$2$')
IDENT_2A = u('$2a$')
IDENT_2X = u('$2x$')
IDENT_2Y = u('$2y$')
IDENT_2B = u('$2b$')
_BNULL = '\x00'
TEST_HASH_2A = '$2a$04$5BJqKfqMQvV7nS.yUguNcueVirQqDBGaLXSqj.rs.pZPlNR0UX/HK'

def _detect_pybcrypt():
    try:
        import bcrypt
    except ImportError:
        return
    else:
        try:
            from bcrypt._bcrypt import __version__
        except ImportError:
            return False

    return True


class _BcryptCommon(uh.SubclassBackendMixin, uh.TruncateMixin, uh.HasManyIdents, uh.HasRounds, uh.HasSalt, uh.GenericHandler):
    name = 'bcrypt'
    setting_kwds = ('salt', 'rounds', 'ident', 'truncate_error')
    checksum_size = 31
    checksum_chars = bcrypt64.charmap
    default_ident = IDENT_2B
    ident_values = (IDENT_2, IDENT_2A, IDENT_2X, IDENT_2Y, IDENT_2B)
    ident_aliases = {u('2'): IDENT_2, u('2a'): IDENT_2A, u('2y'): IDENT_2Y, u('2b'): IDENT_2B}
    min_salt_size = max_salt_size = 22
    salt_chars = bcrypt64.charmap
    default_rounds = 12
    min_rounds = 4
    max_rounds = 31
    rounds_cost = 'log2'
    truncate_size = 72
    _workrounds_initialized = False
    _has_2a_wraparound_bug = False
    _lacks_20_support = False
    _lacks_2y_support = False
    _lacks_2b_support = False
    _fallback_ident = IDENT_2A

    @classmethod
    def from_string(cls, hash):
        ident, tail = cls._parse_ident(hash)
        if ident == IDENT_2X:
            raise ValueError("crypt_blowfish's buggy '2x' hashes are not currently supported")
        rounds_str, data = tail.split(u('$'))
        rounds = int(rounds_str)
        if rounds_str != u('%02d') % (rounds,):
            raise uh.exc.MalformedHashError(cls, 'malformed cost field')
        salt, chk = data[:22], data[22:]
        return cls(rounds=rounds, salt=salt, checksum=chk or None, ident=ident)

    def to_string(self):
        hash = u('%s%02d$%s%s') % (self.ident, self.rounds, self.salt, self.checksum)
        return uascii_to_str(hash)

    def _get_config(self, ident):
        config = u('%s%02d$%s') % (ident, self.rounds, self.salt)
        return uascii_to_str(config)

    @classmethod
    def needs_update(cls, hash, **kwds):
        if isinstance(hash, bytes):
            hash = hash.decode('ascii')
        if hash.startswith(IDENT_2A) and hash[28] not in bcrypt64._padinfo2[1]:
            return True
        return super(_BcryptCommon, cls).needs_update(hash, **kwds)

    @classmethod
    def normhash(cls, hash):
        if cls.identify(hash):
            return cls.from_string(hash).to_string()
        return hash

    @classmethod
    def _generate_salt(cls):
        salt = super(_BcryptCommon, cls)._generate_salt()
        return bcrypt64.repair_unused(salt)

    @classmethod
    def _norm_salt(cls, salt, **kwds):
        salt = super(_BcryptCommon, cls)._norm_salt(salt, **kwds)
        changed, salt = bcrypt64.check_repair_unused(salt)
        if changed:
            warn('encountered a bcrypt salt with incorrectly set padding bits; you may want to use bcrypt.normhash() to fix this; this will be an error under Passlib 2.0', PasslibHashWarning)
        return salt

    def _norm_checksum(self, checksum, relaxed=False):
        checksum = super(_BcryptCommon, self)._norm_checksum(checksum, relaxed=relaxed)
        changed, checksum = bcrypt64.check_repair_unused(checksum)
        if changed:
            warn('encountered a bcrypt hash with incorrectly set padding bits; you may want to use bcrypt.normhash() to fix this; this will be an error under Passlib 2.0', PasslibHashWarning)
        return checksum

    _no_backend_suggestion = " -- recommend you install one (e.g. 'pip install bcrypt')"

    @classmethod
    def _finalize_backend_mixin(mixin_cls, backend, dryrun):
        global _bcryptor
        if mixin_cls._workrounds_initialized:
            return True
        verify = mixin_cls.verify
        err_types = (
         ValueError,)
        if _bcryptor:
            err_types += (_bcryptor.engine.SaltError,)

        def safe_verify(secret, hash):
            try:
                return verify(secret, hash)
            except err_types:
                return NotImplemented
            except AssertionError as err:
                log.debug('trapped unexpected response from %r backend: verify(%r, %r):', backend, secret, hash, exc_info=True)
                return NotImplemented

        def assert_lacks_8bit_bug(ident):
            secret = '\xa3'
            bug_hash = ident.encode('ascii') + '05$/OK.fbVrR/bpIqNJ5ianF.CE5elHaaO4EbggVDjb8P19RukzXSM3e'
            if verify(secret, bug_hash):
                raise PasslibSecurityError('passlib.hash.bcrypt: Your installation of the %r backend is vulnerable to the crypt_blowfish 8-bit bug (CVE-2011-2483), and should be upgraded or replaced with another backend.' % backend)
            correct_hash = ident.encode('ascii') + '05$/OK.fbVrR/bpIqNJ5ianF.Sa7shbm4.OzKpvFnX1pQLmQW96oUlCq'
            if not verify(secret, correct_hash):
                raise RuntimeError('%s backend failed to verify %s 8bit hash' % (backend, ident))

        def detect_wrap_bug(ident):
            secret = ('0123456789' * 26)[:255]
            bug_hash = ident.encode('ascii') + '04$R1lJ2gkNaoPGdafE.H.16.nVyh2niHsGJhayOHLMiXlI45o8/DU.6'
            if verify(secret, bug_hash):
                return True
            correct_hash = ident.encode('ascii') + '04$R1lJ2gkNaoPGdafE.H.16.1MKHPvmKwryeulRe225LKProWYwt9Oi'
            if not verify(secret, correct_hash):
                raise RuntimeError('%s backend failed to verify %s wraparound hash' % (backend, ident))
            return False

        def assert_lacks_wrap_bug(ident):
            if not detect_wrap_bug(ident):
                return
            raise RuntimeError('%s backend unexpectedly has wraparound bug for %s' % (backend, ident))

        test_hash_20 = '$2$04$5BJqKfqMQvV7nS.yUguNcuRfMMOXK0xPWavM7pOzjEi5ze5T1k8/S'
        result = safe_verify('test', test_hash_20)
        if not result:
            raise RuntimeError('%s incorrectly rejected $2$ hash' % backend)
        else:
            if result is NotImplemented:
                mixin_cls._lacks_20_support = True
                log.debug('%r backend lacks $2$ support, enabling workaround', backend)
        result = safe_verify('test', TEST_HASH_2A)
        if not result:
            raise RuntimeError('%s incorrectly rejected $2a$ hash' % backend)
        else:
            if result is NotImplemented:
                raise RuntimeError('%s lacks support for $2a$ hashes' % backend)
            else:
                assert_lacks_8bit_bug(IDENT_2A)
                if detect_wrap_bug(IDENT_2A):
                    warn('passlib.hash.bcrypt: Your installation of the %r backend is vulnerable to the bsd wraparound bug, and should be upgraded or replaced with another backend (enabling workaround for now).' % backend, uh.exc.PasslibSecurityWarning)
                    mixin_cls._has_2a_wraparound_bug = True
        test_hash_2y = TEST_HASH_2A.replace('2a', '2y')
        result = safe_verify('test', test_hash_2y)
        if not result:
            raise RuntimeError('%s incorrectly rejected $2y$ hash' % backend)
        else:
            if result is NotImplemented:
                mixin_cls._lacks_2y_support = True
                log.debug('%r backend lacks $2y$ support, enabling workaround', backend)
            else:
                assert_lacks_8bit_bug(IDENT_2Y)
                assert_lacks_wrap_bug(IDENT_2Y)
        test_hash_2b = TEST_HASH_2A.replace('2a', '2b')
        result = safe_verify('test', test_hash_2b)
        if not result:
            raise RuntimeError('%s incorrectly rejected $2b$ hash' % backend)
        else:
            if result is NotImplemented:
                mixin_cls._lacks_2b_support = True
                log.debug('%r backend lacks $2b$ support, enabling workaround', backend)
            else:
                mixin_cls._fallback_ident = IDENT_2B
                assert_lacks_8bit_bug(IDENT_2B)
                assert_lacks_wrap_bug(IDENT_2B)
        mixin_cls._workrounds_initialized = True
        return True

    def _prepare_digest_args(self, secret):
        return self._norm_digest_args(secret, self.ident, new=self.use_defaults)

    @classmethod
    def _norm_digest_args(cls, secret, ident, new=False):
        if isinstance(secret, unicode):
            secret = secret.encode('utf-8')
        uh.validate_secret(secret)
        if new:
            cls._check_truncate_policy(secret)
        if _BNULL in secret:
            raise uh.exc.NullPasswordError(cls)
        if cls._has_2a_wraparound_bug and len(secret) >= 255:
            secret = secret[:72]
        if ident == IDENT_2A:
            pass
        else:
            if ident == IDENT_2B:
                if cls._lacks_2b_support:
                    ident = cls._fallback_ident
            else:
                if ident == IDENT_2Y:
                    if cls._lacks_2y_support:
                        ident = cls._fallback_ident
                else:
                    if ident == IDENT_2:
                        if cls._lacks_20_support:
                            if secret:
                                secret = repeat_string(secret, 72)
                            ident = cls._fallback_ident
                    else:
                        if ident == IDENT_2X:
                            raise RuntimeError('$2x$ hashes not currently supported by passlib')
                        else:
                            raise AssertionError('unexpected ident value: %r' % ident)
        return (
         secret, ident)


class _NoBackend(_BcryptCommon):

    def _calc_checksum(self, secret):
        self._stub_requires_backend()
        return super(bcrypt, self)._calc_checksum(secret)


class _BcryptBackend(_BcryptCommon):

    @classmethod
    def _load_backend_mixin(mixin_cls, name, dryrun):
        global _bcrypt
        if _detect_pybcrypt():
            return False
        try:
            import bcrypt as _bcrypt
        except ImportError:
            return False
        else:
            try:
                version = _bcrypt.__about__.__version__
            except:
                log.warning('(trapped) error reading bcrypt version', exc_info=True)
                version = '<unknown>'

        log.debug("detected 'bcrypt' backend, version %r", version)
        return mixin_cls._finalize_backend_mixin(name, dryrun)

    def _calc_checksum(self, secret):
        secret, ident = self._prepare_digest_args(secret)
        config = self._get_config(ident)
        if isinstance(config, unicode):
            config = config.encode('ascii')
        hash = _bcrypt.hashpw(secret, config)
        return hash[-31:].decode('ascii')


class _BcryptorBackend(_BcryptCommon):

    @classmethod
    def _load_backend_mixin(mixin_cls, name, dryrun):
        global _bcryptor
        try:
            import bcryptor as _bcryptor
        except ImportError:
            return False

        return mixin_cls._finalize_backend_mixin(name, dryrun)

    def _calc_checksum(self, secret):
        secret, ident = self._prepare_digest_args(secret)
        config = self._get_config(ident)
        hash = _bcryptor.engine.Engine(False).hash_key(secret, config)
        return str_to_uascii(hash[-31:])


class _PyBcryptBackend(_BcryptCommon):
    _calc_lock = None

    @classmethod
    def _load_backend_mixin(mixin_cls, name, dryrun):
        global _pybcrypt
        if not _detect_pybcrypt():
            return False
        try:
            import bcrypt as _pybcrypt
        except ImportError:
            return False
        else:
            try:
                version = _pybcrypt._bcrypt.__version__
            except:
                log.warning('(trapped) error reading pybcrypt version', exc_info=True)
                version = '<unknown>'

        log.debug("detected 'pybcrypt' backend, version %r", version)
        vinfo = parse_version(version) or (0, 0)
        if vinfo < (0, 3):
            warn('py-bcrypt %s has a major security vulnerability, you should upgrade to py-bcrypt 0.3 immediately.' % version, uh.exc.PasslibSecurityWarning)
            if mixin_cls._calc_lock is None:
                import threading
                mixin_cls._calc_lock = threading.Lock()
            mixin_cls._calc_checksum = mixin_cls._calc_checksum_threadsafe.__func__
        return mixin_cls._finalize_backend_mixin(name, dryrun)

    def _calc_checksum_threadsafe(self, secret):
        with self._calc_lock:
            return self._calc_checksum_raw(secret)

    def _calc_checksum_raw(self, secret):
        secret, ident = self._prepare_digest_args(secret)
        config = self._get_config(ident)
        hash = _pybcrypt.hashpw(secret, config)
        return str_to_uascii(hash[-31:])

    _calc_checksum = _calc_checksum_raw


class _OsCryptBackend(_BcryptCommon):

    @classmethod
    def _load_backend_mixin(mixin_cls, name, dryrun):
        if not test_crypt('test', TEST_HASH_2A):
            return False
        return mixin_cls._finalize_backend_mixin(name, dryrun)

    def _calc_checksum(self, secret):
        secret, ident = self._prepare_digest_args(secret)
        config = self._get_config(ident)
        hash = safe_crypt(secret, config)
        if hash:
            return hash[-31:]
        raise uh.exc.MissingBackendError("non-utf8 encoded passwords can't be handled by crypt.crypt() under python3, recommend running `pip install bcrypt`.")


class _BuiltinBackend(_BcryptCommon):

    @classmethod
    def _load_backend_mixin(mixin_cls, name, dryrun):
        global _builtin_bcrypt
        from otp.ai.passlib.utils import as_bool
        if not as_bool(os.environ.get('PASSLIB_BUILTIN_BCRYPT')):
            log.debug("bcrypt 'builtin' backend not enabled via $PASSLIB_BUILTIN_BCRYPT")
            return False
        from otp.ai.passlib.crypto._blowfish import raw_bcrypt as _builtin_bcrypt
        return mixin_cls._finalize_backend_mixin(name, dryrun)

    def _calc_checksum(self, secret):
        secret, ident = self._prepare_digest_args(secret)
        chk = _builtin_bcrypt(secret, ident[1:-1], self.salt.encode('ascii'), self.rounds)
        return chk.decode('ascii')


class bcrypt(_NoBackend, _BcryptCommon):
    backends = ('bcrypt', 'pybcrypt', 'bcryptor', 'os_crypt', 'builtin')
    _backend_mixin_target = True
    _backend_mixin_map = {None: _NoBackend, 
       'bcrypt': _BcryptBackend, 
       'pybcrypt': _PyBcryptBackend, 
       'bcryptor': _BcryptorBackend, 
       'os_crypt': _OsCryptBackend, 
       'builtin': _BuiltinBackend}


_UDOLLAR = u('$')

class _wrapped_bcrypt(bcrypt):
    setting_kwds = tuple(elem for elem in bcrypt.setting_kwds if elem not in ('truncate_error', ))
    truncate_size = None

    @classmethod
    def _check_truncate_policy(cls, secret):
        pass


class bcrypt_sha256(_wrapped_bcrypt):
    name = 'bcrypt_sha256'
    ident_values = (
     IDENT_2A, IDENT_2B)
    ident_aliases = (lambda ident_values: dict(item for item in bcrypt.ident_aliases.items() if item[1] in ident_values))(ident_values)
    default_ident = IDENT_2B
    prefix = u('$bcrypt-sha256$')
    _hash_re = re.compile('\n        ^\n        [$]bcrypt-sha256\n        [$](?P<variant>2[ab])\n        ,(?P<rounds>\\d{1,2})\n        [$](?P<salt>[^$]{22})\n        (?:[$](?P<digest>.{31}))?\n        $\n        ', re.X)

    @classmethod
    def identify(cls, hash):
        hash = uh.to_unicode_for_identify(hash)
        if not hash:
            return False
        return hash.startswith(cls.prefix)

    @classmethod
    def from_string(cls, hash):
        hash = to_unicode(hash, 'ascii', 'hash')
        if not hash.startswith(cls.prefix):
            raise uh.exc.InvalidHashError(cls)
        m = cls._hash_re.match(hash)
        if not m:
            raise uh.exc.MalformedHashError(cls)
        rounds = m.group('rounds')
        if rounds.startswith(uh._UZERO) and rounds != uh._UZERO:
            raise uh.exc.ZeroPaddedRoundsError(cls)
        return cls(ident=m.group('variant'), rounds=int(rounds), salt=m.group('salt'), checksum=m.group('digest'))

    _template = u('$bcrypt-sha256$%s,%d$%s$%s')

    def to_string(self):
        hash = self._template % (self.ident.strip(_UDOLLAR),
         self.rounds, self.salt, self.checksum)
        return uascii_to_str(hash)

    def _calc_checksum(self, secret):
        if isinstance(secret, unicode):
            secret = secret.encode('utf-8')
        key = b64encode(sha256(secret).digest())
        return super(bcrypt_sha256, self)._calc_checksum(key)