from __future__ import with_statement
import re, hashlib
from logging import getLogger
import warnings
from otp.ai.passlib.hash import ldap_md5, sha256_crypt
from otp.ai.passlib.exc import MissingBackendError, PasslibHashWarning
from otp.ai.passlib.utils.compat import str_to_uascii, uascii_to_str, unicode
import otp.ai.passlib.utils.handlers as uh
from otp.ai.passlib.tests.utils import HandlerCase, TestCase
from otp.ai.passlib.utils.compat import u
log = getLogger(__name__)

def _makelang(alphabet, size):

    def helper(size):
        if size < 2:
            for char in alphabet:
                yield char

        else:
            for char in alphabet:
                for tail in helper(size - 1):
                    yield char + tail

    return set(helper(size))


class SkeletonTest(TestCase):

    def test_00_static_handler(self):

        class d1(uh.StaticHandler):
            name = 'd1'
            context_kwds = ('flag', )
            _hash_prefix = u('_')
            checksum_chars = u('ab')
            checksum_size = 1

            def __init__(self, flag=False, **kwds):
                super(d1, self).__init__(**kwds)
                self.flag = flag

            def _calc_checksum(self, secret):
                if self.flag:
                    return u('b')
                return u('a')

        self.assertTrue(d1.identify(u('_a')))
        self.assertTrue(d1.identify('_a'))
        self.assertTrue(d1.identify(u('_b')))
        self.assertFalse(d1.identify(u('_c')))
        self.assertFalse(d1.identify('_c'))
        self.assertFalse(d1.identify(u('a')))
        self.assertFalse(d1.identify(u('b')))
        self.assertFalse(d1.identify(u('c')))
        self.assertRaises(TypeError, d1.identify, None)
        self.assertRaises(TypeError, d1.identify, 1)
        self.assertEqual(d1.genconfig(), d1.hash(''))
        self.assertTrue(d1.verify('s', '_a'))
        self.assertTrue(d1.verify('s', u('_a')))
        self.assertFalse(d1.verify('s', '_b'))
        self.assertFalse(d1.verify('s', u('_b')))
        self.assertTrue(d1.verify('s', '_b', flag=True))
        self.assertRaises(ValueError, d1.verify, 's', '_c')
        self.assertRaises(ValueError, d1.verify, 's', u('_c'))
        self.assertEqual(d1.hash('s'), '_a')
        self.assertEqual(d1.hash('s', flag=True), '_b')
        return

    def test_01_calc_checksum_hack(self):

        class d1(uh.StaticHandler):
            name = 'd1'

            @classmethod
            def identify(cls, hash):
                if not hash or len(hash) != 40:
                    return False
                try:
                    int(hash, 16)
                except ValueError:
                    return False

                return True

            @classmethod
            def genhash(cls, secret, hash):
                if secret is None:
                    raise TypeError('no secret provided')
                if isinstance(secret, unicode):
                    secret = secret.encode('utf-8')
                if hash is not None and not cls.identify(hash):
                    raise ValueError('invalid hash')
                return hashlib.sha1('xyz' + secret).hexdigest()

            @classmethod
            def verify(cls, secret, hash):
                if hash is None:
                    raise ValueError('no hash specified')
                return cls.genhash(secret, hash) == hash.lower()

        with self.assertWarningList('d1.*should be updated.*_calc_checksum'):
            hash = d1.hash('test')
        self.assertEqual(hash, '7c622762588a0e5cc786ad0a143156f9fd38eea3')
        self.assertTrue(d1.verify('test', hash))
        self.assertFalse(d1.verify('xtest', hash))
        del d1.genhash
        self.assertRaises(NotImplementedError, d1.hash, 'test')

    def test_10_identify(self):

        class d1(uh.GenericHandler):

            @classmethod
            def from_string(cls, hash):
                if isinstance(hash, bytes):
                    hash = hash.decode('ascii')
                if hash == u('a'):
                    return cls(checksum=hash)
                raise ValueError

        self.assertRaises(TypeError, d1.identify, None)
        self.assertRaises(TypeError, d1.identify, 1)
        self.assertFalse(d1.identify(''))
        self.assertTrue(d1.identify('a'))
        self.assertFalse(d1.identify('b'))
        d1._hash_regex = re.compile(u('@.'))
        self.assertRaises(TypeError, d1.identify, None)
        self.assertRaises(TypeError, d1.identify, 1)
        self.assertTrue(d1.identify('@a'))
        self.assertFalse(d1.identify('a'))
        del d1._hash_regex
        d1.ident = u('!')
        self.assertRaises(TypeError, d1.identify, None)
        self.assertRaises(TypeError, d1.identify, 1)
        self.assertTrue(d1.identify('!a'))
        self.assertFalse(d1.identify('a'))
        del d1.ident
        return

    def test_11_norm_checksum(self):

        class d1(uh.GenericHandler):
            name = 'd1'
            checksum_size = 4
            checksum_chars = u('xz')

        def norm_checksum(checksum=None, **k):
            return d1(checksum=checksum, **k).checksum

        self.assertRaises(ValueError, norm_checksum, u('xxx'))
        self.assertEqual(norm_checksum(u('xxxx')), u('xxxx'))
        self.assertEqual(norm_checksum(u('xzxz')), u('xzxz'))
        self.assertRaises(ValueError, norm_checksum, u('xxxxx'))
        self.assertRaises(ValueError, norm_checksum, u('xxyx'))
        self.assertRaises(TypeError, norm_checksum, 'xxyx')
        self.assertEqual(d1()._stub_checksum, u('xxxx'))
        return

    def test_12_norm_checksum_raw(self):

        class d1(uh.HasRawChecksum, uh.GenericHandler):
            name = 'd1'
            checksum_size = 4

        def norm_checksum(*a, **k):
            return d1(*a, **k).checksum

        self.assertEqual(norm_checksum('1234'), '1234')
        self.assertRaises(TypeError, norm_checksum, u('xxyx'))
        self.assertEqual(d1()._stub_checksum, '\x00\x00\x00\x00')

    def test_20_norm_salt(self):

        class d1(uh.HasSalt, uh.GenericHandler):
            name = 'd1'
            setting_kwds = ('salt', )
            min_salt_size = 2
            max_salt_size = 4
            default_salt_size = 3
            salt_chars = 'ab'

        def norm_salt(**k):
            return d1(**k).salt

        def gen_salt(sz, **k):
            return d1.using(salt_size=sz, **k)(use_defaults=True).salt

        salts2 = _makelang('ab', 2)
        salts3 = _makelang('ab', 3)
        salts4 = _makelang('ab', 4)
        self.assertRaises(TypeError, norm_salt)
        self.assertRaises(TypeError, norm_salt, salt=None)
        self.assertIn(norm_salt(use_defaults=True), salts3)
        with warnings.catch_warnings(record=True) as (wlog):
            self.assertRaises(ValueError, norm_salt, salt='')
            self.assertRaises(ValueError, norm_salt, salt='a')
            self.consumeWarningList(wlog)
            self.assertEqual(norm_salt(salt='ab'), 'ab')
            self.assertEqual(norm_salt(salt='aba'), 'aba')
            self.assertEqual(norm_salt(salt='abba'), 'abba')
            self.consumeWarningList(wlog)
            self.assertRaises(ValueError, norm_salt, salt='aaaabb')
            self.consumeWarningList(wlog)
        with warnings.catch_warnings(record=True) as (wlog):
            self.assertRaises(ValueError, gen_salt, 0)
            self.assertRaises(ValueError, gen_salt, 1)
            self.consumeWarningList(wlog)
            self.assertIn(gen_salt(2), salts2)
            self.assertIn(gen_salt(3), salts3)
            self.assertIn(gen_salt(4), salts4)
            self.consumeWarningList(wlog)
            self.assertRaises(ValueError, gen_salt, 5)
            self.consumeWarningList(wlog)
            self.assertIn(gen_salt(5, relaxed=True), salts4)
            self.consumeWarningList(wlog, ['salt_size.*above max_salt_size'])
        del d1.max_salt_size
        with self.assertWarningList([]):
            self.assertEqual(len(gen_salt(None)), 3)
            self.assertEqual(len(gen_salt(5)), 5)
        return

    def test_30_init_rounds(self):

        class d1(uh.HasRounds, uh.GenericHandler):
            name = 'd1'
            setting_kwds = ('rounds', )
            min_rounds = 1
            max_rounds = 3
            default_rounds = 2

        def norm_rounds(**k):
            return d1(**k).rounds

        self.assertRaises(TypeError, norm_rounds)
        self.assertRaises(TypeError, norm_rounds, rounds=None)
        self.assertEqual(norm_rounds(use_defaults=True), 2)
        self.assertRaises(TypeError, norm_rounds, rounds=1.5)
        with warnings.catch_warnings(record=True) as (wlog):
            self.assertRaises(ValueError, norm_rounds, rounds=0)
            self.consumeWarningList(wlog)
            self.assertEqual(norm_rounds(rounds=1), 1)
            self.assertEqual(norm_rounds(rounds=2), 2)
            self.assertEqual(norm_rounds(rounds=3), 3)
            self.consumeWarningList(wlog)
            self.assertRaises(ValueError, norm_rounds, rounds=4)
            self.consumeWarningList(wlog)
        d1.default_rounds = None
        self.assertRaises(TypeError, norm_rounds, use_defaults=True)
        return

    def test_40_backends(self):

        class d1(uh.HasManyBackends, uh.GenericHandler):
            name = 'd1'
            setting_kwds = ()
            backends = ('a', 'b')
            _enable_a = False
            _enable_b = False

            @classmethod
            def _load_backend_a(cls):
                if cls._enable_a:
                    cls._set_calc_checksum_backend(cls._calc_checksum_a)
                    return True
                return False

            @classmethod
            def _load_backend_b(cls):
                if cls._enable_b:
                    cls._set_calc_checksum_backend(cls._calc_checksum_b)
                    return True
                return False

            def _calc_checksum_a(self, secret):
                return 'a'

            def _calc_checksum_b(self, secret):
                return 'b'

        self.assertRaises(MissingBackendError, d1.get_backend)
        self.assertRaises(MissingBackendError, d1.set_backend)
        self.assertRaises(MissingBackendError, d1.set_backend, 'any')
        self.assertRaises(MissingBackendError, d1.set_backend, 'default')
        self.assertFalse(d1.has_backend())
        d1._enable_b = True
        obj = d1()
        self.assertEqual(obj._calc_checksum('s'), 'b')
        d1.set_backend('b')
        d1.set_backend('any')
        self.assertEqual(obj._calc_checksum('s'), 'b')
        self.assertRaises(MissingBackendError, d1.set_backend, 'a')
        self.assertTrue(d1.has_backend('b'))
        self.assertFalse(d1.has_backend('a'))
        d1._enable_a = True
        self.assertTrue(d1.has_backend())
        d1.set_backend('a')
        self.assertEqual(obj._calc_checksum('s'), 'a')
        self.assertRaises(ValueError, d1.set_backend, 'c')
        self.assertRaises(ValueError, d1.has_backend, 'c')
        d1.set_backend('b')

        class d2(d1):
            _has_backend_a = True

        self.assertRaises(AssertionError, d2.has_backend, 'a')

    def test_41_backends(self):
        warnings.filterwarnings('ignore', category=DeprecationWarning, message='.* support for \\._has_backend_.* is deprecated.*')

        class d1(uh.HasManyBackends, uh.GenericHandler):
            name = 'd1'
            setting_kwds = ()
            backends = ('a', 'b')
            _has_backend_a = False
            _has_backend_b = False

            def _calc_checksum_a(self, secret):
                return 'a'

            def _calc_checksum_b(self, secret):
                return 'b'

        self.assertRaises(MissingBackendError, d1.get_backend)
        self.assertRaises(MissingBackendError, d1.set_backend)
        self.assertRaises(MissingBackendError, d1.set_backend, 'any')
        self.assertRaises(MissingBackendError, d1.set_backend, 'default')
        self.assertFalse(d1.has_backend())
        d1._has_backend_b = True
        obj = d1()
        self.assertEqual(obj._calc_checksum('s'), 'b')
        d1.set_backend('b')
        d1.set_backend('any')
        self.assertEqual(obj._calc_checksum('s'), 'b')
        self.assertRaises(MissingBackendError, d1.set_backend, 'a')
        self.assertTrue(d1.has_backend('b'))
        self.assertFalse(d1.has_backend('a'))
        d1._has_backend_a = True
        self.assertTrue(d1.has_backend())
        d1.set_backend('a')
        self.assertEqual(obj._calc_checksum('s'), 'a')
        self.assertRaises(ValueError, d1.set_backend, 'c')
        self.assertRaises(ValueError, d1.has_backend, 'c')

    def test_50_norm_ident(self):

        class d1(uh.HasManyIdents, uh.GenericHandler):
            name = 'd1'
            setting_kwds = ('ident', )
            default_ident = u('!A')
            ident_values = (u('!A'), u('!B'))
            ident_aliases = {u('A'): u('!A')}

        def norm_ident(**k):
            return d1(**k).ident

        self.assertRaises(TypeError, norm_ident)
        self.assertRaises(TypeError, norm_ident, ident=None)
        self.assertEqual(norm_ident(use_defaults=True), u('!A'))
        self.assertEqual(norm_ident(ident=u('!A')), u('!A'))
        self.assertEqual(norm_ident(ident=u('!B')), u('!B'))
        self.assertRaises(ValueError, norm_ident, ident=u('!C'))
        self.assertEqual(norm_ident(ident=u('A')), u('!A'))
        self.assertRaises(ValueError, norm_ident, ident=u('B'))
        self.assertTrue(d1.identify(u('!Axxx')))
        self.assertTrue(d1.identify(u('!Bxxx')))
        self.assertFalse(d1.identify(u('!Cxxx')))
        self.assertFalse(d1.identify(u('A')))
        self.assertFalse(d1.identify(u('')))
        self.assertRaises(TypeError, d1.identify, None)
        self.assertRaises(TypeError, d1.identify, 1)
        d1.default_ident = None
        self.assertRaises(AssertionError, norm_ident, use_defaults=True)
        return

    def test_91_parsehash(self):
        from otp.ai.passlib import hash
        result = hash.des_crypt.parsehash('OgAwTx2l6NADI')
        self.assertEqual(result, {'checksum': u('AwTx2l6NADI'), 'salt': u('Og')})
        h = '$5$LKO/Ute40T3FNF95$U0prpBQd4PloSGU0pnpM4z9wKn4vZ1.jsrzQfPqxph9'
        s = u('LKO/Ute40T3FNF95')
        c = u('U0prpBQd4PloSGU0pnpM4z9wKn4vZ1.jsrzQfPqxph9')
        result = hash.sha256_crypt.parsehash(h)
        self.assertEqual(result, dict(salt=s, rounds=5000, implicit_rounds=True, checksum=c))
        result = hash.sha256_crypt.parsehash(h, checksum=False)
        self.assertEqual(result, dict(salt=s, rounds=5000, implicit_rounds=True))
        result = hash.sha256_crypt.parsehash(h, sanitize=True)
        self.assertEqual(result, dict(rounds=5000, implicit_rounds=True, salt=u('LK**************'), checksum=u('U0pr***************************************')))
        result = hash.sha256_crypt.parsehash('$5$rounds=10428$uy/jIAhCetNCTtb0$YWvUOXbkqlqhyoPMpN8BMe.ZGsGx2aBvxTvDFI613c3')
        self.assertEqual(result, dict(checksum=u('YWvUOXbkqlqhyoPMpN8BMe.ZGsGx2aBvxTvDFI613c3'), salt=u('uy/jIAhCetNCTtb0'), rounds=10428))
        h1 = '$pbkdf2$60000$DoEwpvQeA8B4T.k951yLUQ$O26Y3/NJEiLCVaOVPxGXshyjW8k'
        result = hash.pbkdf2_sha1.parsehash(h1)
        self.assertEqual(result, dict(checksum=';n\x98\xdf\xf3I\x12"\xc2U\xa3\x95?\x11\x97\xb2\x1c\xa3[\xc9', rounds=60000, salt='\x0e\x810\xa6\xf4\x1e\x03\xc0xO\xe9=\xe7\\\x8bQ'))
        result = hash.pbkdf2_sha1.parsehash(h1, sanitize=True)
        self.assertEqual(result, dict(checksum=u('O26************************'), rounds=60000, salt=u('Do********************')))

    def test_92_bitsize(self):
        from otp.ai.passlib import hash
        self.assertEqual(hash.des_crypt.bitsize(), {'checksum': 66, 'salt': 12})
        self.assertEqual(hash.bcrypt.bitsize(), {'checksum': 186, 'salt': 132})
        self.patchAttr(hash.sha256_crypt, 'default_rounds', 1 << 17)
        self.assertEqual(hash.sha256_crypt.bitsize(), {'checksum': 258, 'rounds': 14, 'salt': 96})
        self.patchAttr(hash.pbkdf2_sha1, 'default_rounds', 1 << 16)
        self.assertEqual(hash.pbkdf2_sha1.bitsize(), {'checksum': 160, 'rounds': 13, 'salt': 128})


class dummy_handler_in_registry(object):

    def __init__(self, name):
        self.name = name
        self.dummy = type('dummy_' + name, (uh.GenericHandler,), dict(name=name, setting_kwds=()))

    def __enter__(self):
        from otp.ai.passlib import registry
        registry._unload_handler_name(self.name, locations=False)
        registry.register_crypt_handler(self.dummy)
        return self.dummy

    def __exit__(self, *exc_info):
        from otp.ai.passlib import registry
        registry._unload_handler_name(self.name, locations=False)


class PrefixWrapperTest(TestCase):

    def test_00_lazy_loading(self):
        d1 = uh.PrefixWrapper('d1', 'ldap_md5', '{XXX}', '{MD5}', lazy=True)
        self.assertEqual(d1._wrapped_name, 'ldap_md5')
        self.assertIs(d1._wrapped_handler, None)
        self.assertIs(d1.wrapped, ldap_md5)
        self.assertIs(d1._wrapped_handler, ldap_md5)
        with dummy_handler_in_registry('ldap_md5') as (dummy):
            self.assertIs(d1.wrapped, ldap_md5)
        return

    def test_01_active_loading(self):
        d1 = uh.PrefixWrapper('d1', 'ldap_md5', '{XXX}', '{MD5}')
        self.assertEqual(d1._wrapped_name, 'ldap_md5')
        self.assertIs(d1._wrapped_handler, ldap_md5)
        self.assertIs(d1.wrapped, ldap_md5)
        with dummy_handler_in_registry('ldap_md5') as (dummy):
            self.assertIs(d1.wrapped, ldap_md5)

    def test_02_explicit(self):
        d1 = uh.PrefixWrapper('d1', ldap_md5, '{XXX}', '{MD5}')
        self.assertEqual(d1._wrapped_name, None)
        self.assertIs(d1._wrapped_handler, ldap_md5)
        self.assertIs(d1.wrapped, ldap_md5)
        with dummy_handler_in_registry('ldap_md5') as (dummy):
            self.assertIs(d1.wrapped, ldap_md5)
        return

    def test_10_wrapped_attributes(self):
        d1 = uh.PrefixWrapper('d1', 'ldap_md5', '{XXX}', '{MD5}')
        self.assertEqual(d1.name, 'd1')
        self.assertIs(d1.setting_kwds, ldap_md5.setting_kwds)
        self.assertFalse('max_rounds' in dir(d1))
        d2 = uh.PrefixWrapper('d2', 'sha256_crypt', '{XXX}')
        self.assertIs(d2.setting_kwds, sha256_crypt.setting_kwds)
        self.assertTrue('max_rounds' in dir(d2))

    def test_11_wrapped_methods(self):
        d1 = uh.PrefixWrapper('d1', 'ldap_md5', '{XXX}', '{MD5}')
        dph = '{XXX}X03MO1qnZdYdgyfeuILPmQ=='
        lph = '{MD5}X03MO1qnZdYdgyfeuILPmQ=='
        self.assertEqual(d1.genconfig(), '{XXX}1B2M2Y8AsgTpgAmY7PhCfg==')
        self.assertRaises(TypeError, d1.genhash, 'password', None)
        self.assertEqual(d1.genhash('password', dph), dph)
        self.assertRaises(ValueError, d1.genhash, 'password', lph)
        self.assertEqual(d1.hash('password'), dph)
        self.assertTrue(d1.identify(dph))
        self.assertFalse(d1.identify(lph))
        self.assertRaises(ValueError, d1.verify, 'password', lph)
        self.assertTrue(d1.verify('password', dph))
        return

    def test_12_ident(self):
        h = uh.PrefixWrapper('h2', 'ldap_md5', '{XXX}')
        self.assertEqual(h.ident, u('{XXX}{MD5}'))
        self.assertIs(h.ident_values, None)
        h = uh.PrefixWrapper('h2', 'des_crypt', '{XXX}')
        self.assertIs(h.ident, None)
        self.assertIs(h.ident_values, None)
        h = uh.PrefixWrapper('h1', 'ldap_md5', '{XXX}', '{MD5}')
        self.assertIs(h.ident, None)
        self.assertIs(h.ident_values, None)
        h = uh.PrefixWrapper('h3', 'ldap_md5', '{XXX}', ident='{X')
        self.assertEqual(h.ident, u('{X'))
        self.assertIs(h.ident_values, None)
        h = uh.PrefixWrapper('h3', 'ldap_md5', '{XXX}', ident='{XXX}A')
        self.assertRaises(ValueError, uh.PrefixWrapper, 'h3', 'ldap_md5', '{XXX}', ident='{XY')
        self.assertRaises(ValueError, uh.PrefixWrapper, 'h3', 'ldap_md5', '{XXX}', ident='{XXXX')
        h = uh.PrefixWrapper('h4', 'phpass', '{XXX}')
        self.assertIs(h.ident, None)
        self.assertEqual(h.ident_values, (u('{XXX}$P$'), u('{XXX}$H$')))
        h = uh.PrefixWrapper('h5', 'des_crypt', '{XXX}', ident=True)
        self.assertEqual(h.ident, u('{XXX}'))
        self.assertIs(h.ident_values, None)
        self.assertRaises(ValueError, uh.PrefixWrapper, 'h6', 'des_crypt', ident=True)
        with self.assertWarningList('orig_prefix.*may not work correctly'):
            h = uh.PrefixWrapper('h7', 'phpass', orig_prefix='$', prefix='?')
        self.assertEqual(h.ident_values, None)
        self.assertEqual(h.ident, None)
        return

    def test_13_repr(self):
        h = uh.PrefixWrapper('h2', 'md5_crypt', '{XXX}', orig_prefix='$1$')
        self.assertRegex(repr(h), '(?x)^PrefixWrapper\\(\n                [\'"]h2[\'"],\\s+\n                [\'"]md5_crypt[\'"],\\s+\n                prefix=u?["\']{XXX}[\'"],\\s+\n                orig_prefix=u?["\']\\$1\\$[\'"]\n            \\)$')

    def test_14_bad_hash(self):
        h = uh.PrefixWrapper('h2', 'md5_crypt', orig_prefix='$6$')
        self.assertRaises(ValueError, h.hash, 'test')


class UnsaltedHash(uh.StaticHandler):
    name = 'unsalted_test_hash'
    checksum_chars = uh.LOWER_HEX_CHARS
    checksum_size = 40

    def _calc_checksum(self, secret):
        if isinstance(secret, unicode):
            secret = secret.encode('utf-8')
        data = 'boblious' + secret
        return str_to_uascii(hashlib.sha1(data).hexdigest())


class SaltedHash(uh.HasSalt, uh.GenericHandler):
    name = 'salted_test_hash'
    setting_kwds = ('salt', )
    min_salt_size = 2
    max_salt_size = 4
    checksum_size = 40
    salt_chars = checksum_chars = uh.LOWER_HEX_CHARS
    _hash_regex = re.compile(u('^@salt[0-9a-f]{42,44}$'))

    @classmethod
    def from_string(cls, hash):
        if not cls.identify(hash):
            raise uh.exc.InvalidHashError(cls)
        if isinstance(hash, bytes):
            hash = hash.decode('ascii')
        return cls(salt=hash[5:-40], checksum=hash[-40:])

    def to_string(self):
        hash = u('@salt%s%s') % (self.salt, self.checksum)
        return uascii_to_str(hash)

    def _calc_checksum(self, secret):
        if isinstance(secret, unicode):
            secret = secret.encode('utf-8')
        data = self.salt.encode('ascii') + secret + self.salt.encode('ascii')
        return str_to_uascii(hashlib.sha1(data).hexdigest())


UPASS_TEMP = u('\\u0399\\u03c9\\u03b1\\u03bd\\u03bd\\u03b7\\u03c2')

class UnsaltedHashTest(HandlerCase):
    handler = UnsaltedHash
    known_correct_hashes = [
     ('password', '61cfd32684c47de231f1f982c214e884133762c0'),
     (
      UPASS_TEMP, '96b329d120b97ff81ada770042e44ba87343ad2b')]

    def test_bad_kwds(self):
        self.assertRaises(TypeError, UnsaltedHash, salt='x')
        self.assertRaises(TypeError, UnsaltedHash.genconfig, rounds=1)


class SaltedHashTest(HandlerCase):
    handler = SaltedHash
    known_correct_hashes = [
     ('password', '@salt77d71f8fe74f314dac946766c1ac4a2a58365482c0'),
     (
      UPASS_TEMP, '@salt9f978a9bfe360d069b0c13f2afecd570447407fa7e48')]

    def test_bad_kwds(self):
        stub = SaltedHash(use_defaults=True)._stub_checksum
        self.assertRaises(TypeError, SaltedHash, checksum=stub, salt=None)
        self.assertRaises(ValueError, SaltedHash, checksum=stub, salt='xxx')
        return