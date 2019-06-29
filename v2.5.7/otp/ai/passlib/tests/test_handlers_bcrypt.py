from __future__ import with_statement
import logging
log = logging.getLogger(__name__)
import os, warnings
from otp.ai.passlib import hash
from otp.ai.passlib.handlers.bcrypt import IDENT_2, IDENT_2X
from otp.ai.passlib.utils import repeat_string, to_bytes
from otp.ai.passlib.utils.compat import irange
from otp.ai.passlib.tests.utils import HandlerCase, TEST_MODE
from otp.ai.passlib.tests.test_handlers import UPASS_TABLE

class _bcrypt_test(HandlerCase):
    handler = hash.bcrypt
    reduce_default_rounds = True
    fuzz_salts_need_bcrypt_repair = True
    has_os_crypt_fallback = False
    known_correct_hashes = [
     ('U*U*U*U*', '$2a$05$c92SVSfjeiCD6F2nAD6y0uBpJDjdRkt0EgeC4/31Rf2LUZbDRDE.O'),
     ('U*U***U', '$2a$05$WY62Xk2TXZ7EvVDQ5fmjNu7b0GEzSzUXUh2cllxJwhtOeMtWV3Ujq'),
     ('U*U***U*', '$2a$05$Fa0iKV3E2SYVUlMknirWU.CFYGvJ67UwVKI1E2FP6XeLiZGcH3MJi'),
     ('*U*U*U*U', '$2a$05$.WRrXibc1zPgIdRXYfv.4uu6TD1KWf0VnHzq/0imhUhuxSxCyeBs2'),
     ('', '$2a$05$Otz9agnajgrAe0.kFVF9V.tzaStZ2s1s4ZWi/LY4sw2k/MTVFj/IO'),
     ('U*U', '$2a$05$CCCCCCCCCCCCCCCCCCCCC.E5YPO9kmyuRGyh0XouQYb4YMJKvyOeW'),
     ('U*U*', '$2a$05$CCCCCCCCCCCCCCCCCCCCC.VGOzA784oUp/Z0DY336zx7pLYAy0lwK'),
     ('U*U*U', '$2a$05$XXXXXXXXXXXXXXXXXXXXXOAcXxm9kjPGEMsLznoKqmqw7tc8WCx4a'),
     ('', '$2a$05$CCCCCCCCCCCCCCCCCCCCC.7uG0VCzI2bS7j6ymqJi9CdcdxiRTWNy'),
     ('0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789chars after 72 are ignored',
 '$2a$05$abcdefghijklmnopqrstuu5s2v8.iXieOjg/.AySBTTZIIVFJeBui'),
     ('\xa3', '$2a$05$/OK.fbVrR/bpIqNJ5ianF.Sa7shbm4.OzKpvFnX1pQLmQW96oUlCq'),
     ('\xff\xa3345', '$2a$05$/OK.fbVrR/bpIqNJ5ianF.nRht2l/HRhr6zmCp9vYUvvsqynflf9e'),
     ('\xa3ab', '$2a$05$/OK.fbVrR/bpIqNJ5ianF.6IflQkJytoRVc1yuaNtHfiuq.FRlSIS'),
     (
      '\xaa' * 72 + 'chars after 72 are ignored as usual',
      '$2a$05$/OK.fbVrR/bpIqNJ5ianF.swQOIzjOiJ9GHEPuhEkvqrUyvWhEMx6'),
     (
      '\xaaU' * 36,
      '$2a$05$/OK.fbVrR/bpIqNJ5ianF.R9xrDjiycxMbQE2bp.vgqlYpW5wx2yy'),
     (
      'U\xaa\xff' * 24,
      '$2a$05$/OK.fbVrR/bpIqNJ5ianF.9tQZzcJfm3uj2NvJ/n5xkhpqLrMpWCe'),
     ('\xa3', '$2y$05$/OK.fbVrR/bpIqNJ5ianF.Sa7shbm4.OzKpvFnX1pQLmQW96oUlCq'),
     (
      ('0123456789' * 26)[:254], '$2a$04$R1lJ2gkNaoPGdafE.H.16.1MKHPvmKwryeulRe225LKProWYwt9Oi'),
     (
      ('0123456789' * 26)[:255], '$2a$04$R1lJ2gkNaoPGdafE.H.16.1MKHPvmKwryeulRe225LKProWYwt9Oi'),
     (
      ('0123456789' * 26)[:256], '$2a$04$R1lJ2gkNaoPGdafE.H.16.1MKHPvmKwryeulRe225LKProWYwt9Oi'),
     (
      ('0123456789' * 26)[:257], '$2a$04$R1lJ2gkNaoPGdafE.H.16.1MKHPvmKwryeulRe225LKProWYwt9Oi'),
     ('', '$2a$06$DCq7YPn5Rq63x1Lad4cll.TV4S6ytwfsfvkgY8jIucDrjc8deX1s.'),
     ('a', '$2a$10$k87L/MF28Q673VKh8/cPi.SUl7MU/rWuSiIDDFayrKk/1tBsSQu4u'),
     ('abc', '$2a$10$WvvTPHKwdBJ3uk0Z37EMR.hLA2W6N9AEBhEgrAOljy2Ae5MtaSIUi'),
     ('abcdefghijklmnopqrstuvwxyz', '$2a$10$fVH8e28OQRj9tqiDXs1e1uxpsjN0c7II7YPKXua2NAKYvM6iQk7dq'),
     ('~!@#$%^&*()      ~!@#$%^&*()PNBFRD', '$2a$10$LgfYWkbzEvQ4JakH7rOvHe0y8pHKF9OaFgwUZ2q7W2FFZmZzJYlfS'),
     (
      UPASS_TABLE,
      '$2a$05$Z17AXnnlpzddNUvnC6cZNOSwMA/8oNiKnHTHTwLlBijfucQQlHjaG'),
     (
      UPASS_TABLE,
      '$2b$05$Z17AXnnlpzddNUvnC6cZNOSwMA/8oNiKnHTHTwLlBijfucQQlHjaG')]
    if TEST_MODE('full'):
        CONFIG_2 = '$2$05$' + '.' * 22
        CONFIG_A = '$2a$05$' + '.' * 22
        known_correct_hashes.extend([
         (
          '', CONFIG_2 + 'J2ihDv8vVf7QZ9BsaRrKyqs2tkn55Yq'),
         (
          '', CONFIG_A + 'J2ihDv8vVf7QZ9BsaRrKyqs2tkn55Yq'),
         (
          'abc', CONFIG_2 + 'XuQjdH.wPVNUZ/bOfstdW/FqB8QSjte'),
         (
          'abc', CONFIG_A + 'ev6gDwpVye3oMCUpLY85aTpfBNHD0Ga'),
         (
          'abc' * 23, CONFIG_2 + 'XuQjdH.wPVNUZ/bOfstdW/FqB8QSjte'),
         (
          'abc' * 23, CONFIG_A + '2kIdfSj/4/R/Q6n847VTvc68BXiRYZC'),
         (
          'abc' * 24, CONFIG_2 + 'XuQjdH.wPVNUZ/bOfstdW/FqB8QSjte'),
         (
          'abc' * 24, CONFIG_A + 'XuQjdH.wPVNUZ/bOfstdW/FqB8QSjte'),
         (
          'abc' * 24 + 'x', CONFIG_2 + 'XuQjdH.wPVNUZ/bOfstdW/FqB8QSjte'),
         (
          'abc' * 24 + 'x', CONFIG_A + 'XuQjdH.wPVNUZ/bOfstdW/FqB8QSjte')])
    known_correct_configs = [
     (
      '$2a$04$uM6csdM8R9SXTex/gbTaye', UPASS_TABLE,
      '$2a$04$uM6csdM8R9SXTex/gbTayezuvzFEufYGd2uB6of7qScLjQ4GwcD4G')]
    known_unidentified_hashes = [
     '$2f$12$EXRkfkdmXnagzds2SSitu.MW9.gAVqa9eLS1//RYtYCmB1eLHg.9q',
     '$2`$12$EXRkfkdmXnagzds2SSitu.MW9.gAVqa9eLS1//RYtYCmB1eLHg.9q']
    known_malformed_hashes = [
     '$2a$12$EXRkfkdmXn!gzds2SSitu.MW9.gAVqa9eLS1//RYtYCmB1eLHg.9q',
     '$2x$12$EXRkfkdmXnagzds2SSitu.MW9.gAVqa9eLS1//RYtYCmB1eLHg.9q',
     '$2a$6$DCq7YPn5Rq63x1Lad4cll.TV4S6ytwfsfvkgY8jIucDrjc8deX1s.']
    platform_crypt_support = [
     (
      'freedbsd|openbsd|netbsd', True),
     (
      'darwin', False)]

    def setUp(self):
        if TEST_MODE('full') and self.backend == 'builtin':
            key = 'PASSLIB_BUILTIN_BCRYPT'
            orig = os.environ.get(key)
            if orig:
                self.addCleanup(os.environ.__setitem__, key, orig)
            else:
                self.addCleanup(os.environ.__delitem__, key)
            os.environ[key] = 'true'
        super(_bcrypt_test, self).setUp()
        warnings.filterwarnings('ignore', '.*backend is vulnerable to the bsd wraparound bug.*')

    def populate_settings(self, kwds):
        if self.backend == 'builtin':
            kwds.setdefault('rounds', 4)
        super(_bcrypt_test, self).populate_settings(kwds)

    def crypt_supports_variant(self, hash):
        from otp.ai.passlib.handlers.bcrypt import bcrypt, IDENT_2X, IDENT_2Y
        from otp.ai.passlib.utils import safe_crypt
        ident = bcrypt.from_string(hash)
        return (safe_crypt('test', ident + '04$5BJqKfqMQvV7nS.yUguNcu') or '').startswith(ident)

    fuzz_verifiers = HandlerCase.fuzz_verifiers + ('fuzz_verifier_bcrypt', 'fuzz_verifier_pybcrypt',
                                                   'fuzz_verifier_bcryptor')

    def fuzz_verifier_bcrypt(self):
        from otp.ai.passlib.handlers.bcrypt import IDENT_2, IDENT_2A, IDENT_2B, IDENT_2X, IDENT_2Y, _detect_pybcrypt
        from otp.ai.passlib.utils import to_native_str, to_bytes
        try:
            import bcrypt
        except ImportError:
            return
        else:
            if _detect_pybcrypt():
                return

        def check_bcrypt(secret, hash):
            secret = to_bytes(secret, self.FuzzHashGenerator.password_encoding)
            if hash.startswith(IDENT_2B):
                hash = IDENT_2A + hash[4:]
            else:
                if hash.startswith(IDENT_2):
                    hash = IDENT_2A + hash[3:]
                    if secret:
                        secret = repeat_string(secret, 72)
                else:
                    if hash.startswith(IDENT_2Y) and bcrypt.__version__ == '3.0.0':
                        hash = IDENT_2B + hash[4:]
                hash = to_bytes(hash)
                try:
                    return bcrypt.hashpw(secret, hash) == hash
                except ValueError:
                    raise ValueError('bcrypt rejected hash: %r (secret=%r)' % (hash, secret))

        return check_bcrypt

    def fuzz_verifier_pybcrypt(self):
        from otp.ai.passlib.handlers.bcrypt import IDENT_2, IDENT_2A, IDENT_2B, IDENT_2X, IDENT_2Y, _PyBcryptBackend
        from otp.ai.passlib.utils import to_native_str
        loaded = _PyBcryptBackend._load_backend_mixin('pybcrypt', False)
        if not loaded:
            return
        from otp.ai.passlib.handlers.bcrypt import _pybcrypt as bcrypt_mod
        lock = _PyBcryptBackend._calc_lock

        def check_pybcrypt(secret, hash):
            secret = to_native_str(secret, self.FuzzHashGenerator.password_encoding)
            if len(secret) > 200:
                secret = secret[:200]
            if hash.startswith((IDENT_2B, IDENT_2Y)):
                hash = IDENT_2A + hash[4:]
            try:
                if lock:
                    with lock:
                        return bcrypt_mod.hashpw(secret, hash) == hash
                else:
                    return bcrypt_mod.hashpw(secret, hash) == hash
            except ValueError:
                raise ValueError('py-bcrypt rejected hash: %r' % (hash,))

        return check_pybcrypt

    def fuzz_verifier_bcryptor(self):
        from otp.ai.passlib.handlers.bcrypt import IDENT_2, IDENT_2A, IDENT_2Y, IDENT_2B
        from otp.ai.passlib.utils import to_native_str
        try:
            from bcryptor.engine import Engine
        except ImportError:
            return

        def check_bcryptor(secret, hash):
            secret = to_native_str(secret, self.FuzzHashGenerator.password_encoding)
            if hash.startswith((IDENT_2B, IDENT_2Y)):
                hash = IDENT_2A + hash[4:]
            else:
                if hash.startswith(IDENT_2):
                    hash = IDENT_2A + hash[3:]
                    if secret:
                        secret = repeat_string(secret, 72)
            return Engine(False).hash_key(secret, hash) == hash

        return check_bcryptor

    class FuzzHashGenerator(HandlerCase.FuzzHashGenerator):

        def generate(self):
            opts = super(_bcrypt_test.FuzzHashGenerator, self).generate()
            secret = opts['secret']
            other = opts['other']
            settings = opts['settings']
            ident = settings.get('ident')
            if ident == IDENT_2X:
                del settings['ident']
            else:
                if ident == IDENT_2 and other and repeat_string(to_bytes(other), len(to_bytes(secret))) == to_bytes(secret):
                    opts['secret'], opts['other'] = self.random_password_pair()
            return opts

        def random_rounds(self):
            return self.randintgauss(5, 8, 6, 1)

    known_incorrect_padding = [
     ('test', '$2a$04$oaQbBqq8JnSM1NHRPQGXORY4Vw3bdHKLIXTecPDRAcJ98cz1ilveO', '$2a$04$oaQbBqq8JnSM1NHRPQGXOOY4Vw3bdHKLIXTecPDRAcJ98cz1ilveO'),
     ('test', '$2a$04$yjDgE74RJkeqC0/1NheSScrvKeu9IbKDpcQf/Ox3qsrRS/Kw42qIS', '$2a$04$yjDgE74RJkeqC0/1NheSSOrvKeu9IbKDpcQf/Ox3qsrRS/Kw42qIS'),
     ('test', '$2a$04$yjDgE74RJkeqC0/1NheSSOrvKeu9IbKDpcQf/Ox3qsrRS/Kw42qIV', '$2a$04$yjDgE74RJkeqC0/1NheSSOrvKeu9IbKDpcQf/Ox3qsrRS/Kw42qIS')]

    def test_90_bcrypt_padding(self):
        self.require_TEST_MODE('full')
        bcrypt = self.handler
        corr_desc = '.*incorrectly set padding bits'

        def check_padding(hash):
            self.assertTrue(hash[28] in '.Oeu', 'unused bits incorrectly set in hash: %r' % (hash,))

        for i in irange(6):
            check_padding(bcrypt.genconfig())

        for i in irange(3):
            check_padding(bcrypt.using(rounds=bcrypt.min_rounds).hash('bob'))

        with self.assertWarningList(['salt too large', corr_desc]):
            hash = bcrypt.genconfig(salt='.' * 21 + 'A.', rounds=5, relaxed=True)
        self.assertEqual(hash, '$2b$05$' + '.' * 53)
        samples = self.known_incorrect_padding
        for pwd, bad, good in samples:
            with self.assertWarningList([corr_desc]):
                self.assertEqual(bcrypt.genhash(pwd, bad), good)
            with self.assertWarningList([]):
                self.assertEqual(bcrypt.genhash(pwd, good), good)
            with self.assertWarningList([corr_desc]):
                self.assertTrue(bcrypt.verify(pwd, bad))
            with self.assertWarningList([]):
                self.assertTrue(bcrypt.verify(pwd, good))
            with self.assertWarningList([corr_desc]):
                self.assertEqual(bcrypt.normhash(bad), good)
            with self.assertWarningList([]):
                self.assertEqual(bcrypt.normhash(good), good)

        self.assertEqual(bcrypt.normhash('$md5$abc'), '$md5$abc')

    def test_needs_update_w_padding(self):
        bcrypt = self.handler.using(rounds=4)
        BAD1 = '$2a$04$yjDgE74RJkeqC0/1NheSScrvKeu9IbKDpcQf/Ox3qsrRS/Kw42qIS'
        GOOD1 = '$2a$04$yjDgE74RJkeqC0/1NheSSOrvKeu9IbKDpcQf/Ox3qsrRS/Kw42qIS'
        self.assertTrue(bcrypt.needs_update(BAD1))
        self.assertFalse(bcrypt.needs_update(GOOD1))


bcrypt_bcrypt_test = _bcrypt_test.create_backend_case('bcrypt')
bcrypt_pybcrypt_test = _bcrypt_test.create_backend_case('pybcrypt')
bcrypt_bcryptor_test = _bcrypt_test.create_backend_case('bcryptor')
bcrypt_os_crypt_test = _bcrypt_test.create_backend_case('os_crypt')
bcrypt_builtin_test = _bcrypt_test.create_backend_case('builtin')

class _bcrypt_sha256_test(HandlerCase):
    handler = hash.bcrypt_sha256
    reduce_default_rounds = True
    forbidden_characters = None
    fuzz_salts_need_bcrypt_repair = True
    alt_safe_crypt_handler = hash.bcrypt
    has_os_crypt_fallback = True
    known_correct_hashes = [
     ('', '$bcrypt-sha256$2a,5$E/e/2AOhqM5W/KJTFQzLce$F6dYSxOdAEoJZO2eoHUZWZljW/e0TXO'),
     ('password', '$bcrypt-sha256$2a,5$5Hg1DKFqPE8C2aflZ5vVoe$12BjNE0p7axMg55.Y/mHsYiVuFBDQyu'),
     (
      UPASS_TABLE,
      '$bcrypt-sha256$2a,5$.US1fQ4TQS.ZTz/uJ5Kyn.$QNdPDOTKKT5/sovNz1iWg26quOU4Pje'),
     (
      UPASS_TABLE.encode('utf-8'),
      '$bcrypt-sha256$2a,5$.US1fQ4TQS.ZTz/uJ5Kyn.$QNdPDOTKKT5/sovNz1iWg26quOU4Pje'),
     ('password', '$bcrypt-sha256$2b,5$5Hg1DKFqPE8C2aflZ5vVoe$12BjNE0p7axMg55.Y/mHsYiVuFBDQyu'),
     (
      UPASS_TABLE,
      '$bcrypt-sha256$2b,5$.US1fQ4TQS.ZTz/uJ5Kyn.$QNdPDOTKKT5/sovNz1iWg26quOU4Pje'),
     (
      repeat_string('abc123', 72),
      '$bcrypt-sha256$2b,5$X1g1nh3g0v4h6970O68cxe$r/hyEtqJ0teqPEmfTLoZ83ciAI1Q74.'),
     (
      repeat_string('abc123', 72) + 'qwr',
      '$bcrypt-sha256$2b,5$X1g1nh3g0v4h6970O68cxe$021KLEif6epjot5yoxk0m8I0929ohEa'),
     (
      repeat_string('abc123', 72) + 'xyz',
      '$bcrypt-sha256$2b,5$X1g1nh3g0v4h6970O68cxe$7.1kgpHduMGEjvM3fX6e/QCvfn6OKja')]
    known_correct_configs = [
     ('$bcrypt-sha256$2a,5$5Hg1DKFqPE8C2aflZ5vVoe', 'password', '$bcrypt-sha256$2a,5$5Hg1DKFqPE8C2aflZ5vVoe$12BjNE0p7axMg55.Y/mHsYiVuFBDQyu')]
    known_malformed_hashes = [
     '$bcrypt-sha256$2a,5$5Hg1DKF!PE8C2aflZ5vVoe$12BjNE0p7axMg55.Y/mHsYiVuFBDQyu',
     '$bcrypt-sha256$2c,5$5Hg1DKFqPE8C2aflZ5vVoe$12BjNE0p7axMg55.Y/mHsYiVuFBDQyu',
     '$bcrypt-sha256$2x,5$5Hg1DKFqPE8C2aflZ5vVoe$12BjNE0p7axMg55.Y/mHsYiVuFBDQyu',
     '$bcrypt-sha256$2a,05$5Hg1DKFqPE8C2aflZ5vVoe$12BjNE0p7axMg55.Y/mHsYiVuFBDQyu',
     '$bcrypt-sha256$2a,5$5Hg1DKFqPE8C2aflZ5vVoe$']

    def setUp(self):
        if TEST_MODE('full') and self.backend == 'builtin':
            key = 'PASSLIB_BUILTIN_BCRYPT'
            orig = os.environ.get(key)
            if orig:
                self.addCleanup(os.environ.__setitem__, key, orig)
            else:
                self.addCleanup(os.environ.__delitem__, key)
            os.environ[key] = 'enabled'
        super(_bcrypt_sha256_test, self).setUp()
        warnings.filterwarnings('ignore', '.*backend is vulnerable to the bsd wraparound bug.*')

    def populate_settings(self, kwds):
        if self.backend == 'builtin':
            kwds.setdefault('rounds', 4)
        super(_bcrypt_sha256_test, self).populate_settings(kwds)

    def test_30_HasManyIdents(self):
        raise self.skipTest('multiple idents not supported')

    def test_30_HasOneIdent(self):
        handler = self.handler
        handler(use_defaults=True)
        self.assertRaises(ValueError, handler, ident='$2y$', use_defaults=True)

    class FuzzHashGenerator(HandlerCase.FuzzHashGenerator):

        def random_rounds(self):
            return self.randintgauss(5, 8, 6, 1)


bcrypt_sha256_bcrypt_test = _bcrypt_sha256_test.create_backend_case('bcrypt')
bcrypt_sha256_pybcrypt_test = _bcrypt_sha256_test.create_backend_case('pybcrypt')
bcrypt_sha256_bcryptor_test = _bcrypt_sha256_test.create_backend_case('bcryptor')
bcrypt_sha256_os_crypt_test = _bcrypt_sha256_test.create_backend_case('os_crypt')
bcrypt_sha256_builtin_test = _bcrypt_sha256_test.create_backend_case('builtin')