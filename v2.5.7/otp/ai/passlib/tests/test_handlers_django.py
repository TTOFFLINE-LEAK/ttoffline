from __future__ import with_statement
import logging
log = logging.getLogger(__name__)
import warnings
from otp.ai.passlib import hash
from otp.ai.passlib.utils import repeat_string
from otp.ai.passlib.utils.compat import u
from otp.ai.passlib.tests.utils import TestCase, HandlerCase, skipUnless, SkipTest
from otp.ai.passlib.tests.test_handlers import UPASS_USD, UPASS_TABLE
from otp.ai.passlib.tests.test_ext_django import DJANGO_VERSION, MIN_DJANGO_VERSION
UPASS_LETMEIN = u('l\xe8tmein')

def vstr(version):
    return ('.').join(str(e) for e in version)


class _DjangoHelper(TestCase):
    __unittest_skip = True
    min_django_version = MIN_DJANGO_VERSION
    max_django_version = None

    def _require_django_support(self):
        if DJANGO_VERSION < self.min_django_version:
            raise self.skipTest('Django >= %s not installed' % vstr(self.min_django_version))
        if self.max_django_version and DJANGO_VERSION > self.max_django_version:
            raise self.skipTest('Django <= %s not installed' % vstr(self.max_django_version))
        return True

    extra_fuzz_verifiers = HandlerCase.fuzz_verifiers + ('fuzz_verifier_django', )

    def fuzz_verifier_django(self):
        try:
            self._require_django_support()
        except SkipTest:
            return

        from django.contrib.auth.hashers import check_password

        def verify_django(secret, hash):
            if self.handler.name == 'django_bcrypt' and hash.startswith('bcrypt$$2y$'):
                hash = hash.replace('$$2y$', '$$2a$')
            if self.django_has_encoding_glitch and isinstance(secret, bytes):
                secret = secret.decode('utf-8')
            return check_password(secret, hash)

        return verify_django

    def test_90_django_reference(self):
        self._require_django_support()
        from django.contrib.auth.hashers import check_password
        for secret, hash in self.iter_known_hashes():
            self.assertTrue(check_password(secret, hash), 'secret=%r hash=%r failed to verify' % (
             secret, hash))
            self.assertFalse(check_password('x' + secret, hash), 'mangled secret=%r hash=%r incorrect verified' % (
             secret, hash))

    django_has_encoding_glitch = False

    def test_91_django_generation(self):
        self._require_django_support()
        from otp.ai.passlib.utils import tick
        from django.contrib.auth.hashers import make_password
        name = self.handler.django_name
        end = tick() + self.max_fuzz_time / 2
        generator = self.FuzzHashGenerator(self, self.getRandom())
        while tick() < end:
            secret, other = generator.random_password_pair()
            if not secret:
                continue
            if self.django_has_encoding_glitch and isinstance(secret, bytes):
                secret = secret.decode('utf-8')
            hash = make_password(secret, hasher=name)
            self.assertTrue(self.do_identify(hash))
            self.assertTrue(self.do_verify(secret, hash))
            self.assertFalse(self.do_verify(other, hash))


class django_disabled_test(HandlerCase):
    handler = hash.django_disabled
    disabled_contains_salt = True
    known_correct_hashes = [
     ('password', '!'),
     ('', '!'),
     (
      UPASS_TABLE, '!')]
    known_alternate_hashes = [
     ('!9wa845vn7098ythaehasldkfj', 'password', '!')]


class django_des_crypt_test(HandlerCase, _DjangoHelper):
    handler = hash.django_des_crypt
    max_django_version = (1, 9)
    known_correct_hashes = [
     ('password', 'crypt$c2$c2M87q...WWcU'),
     ('password', 'crypt$c2e86$c2M87q...WWcU'),
     ('passwordignoreme', 'crypt$c2.AZ$c2M87q...WWcU'),
     (
      UPASS_USD, 'crypt$c2e86$c2hN1Bxd6ZiWs'),
     (
      UPASS_TABLE, 'crypt$0.aQs$0.wB.TT0Czvlo'),
     (
      u('hell\\u00D6'), 'crypt$sa$saykDgk3BPZ9E'),
     ('foo', 'crypt$MNVY.9ajgdvDQ$MNVY.9ajgdvDQ')]
    known_alternate_hashes = [
     ('crypt$$c2M87q...WWcU', 'password', 'crypt$c2$c2M87q...WWcU')]
    known_unidentified_hashes = [
     'sha1$aa$bb']
    known_malformed_hashes = [
     'crypt$c2$c2M87q',
     'crypt$f$c2M87q...WWcU',
     'crypt$ffe86$c2M87q...WWcU']


class django_salted_md5_test(HandlerCase, _DjangoHelper):
    handler = hash.django_salted_md5
    max_django_version = (1, 9)
    django_has_encoding_glitch = True
    known_correct_hashes = [
     ('password', 'md5$123abcdef$c8272612932975ee80e8a35995708e80'),
     ('test', 'md5$3OpqnFAHW5CT$54b29300675271049a1ebae07b395e20'),
     (
      UPASS_USD, 'md5$c2e86$92105508419a81a6babfaecf876a2fa0'),
     (
      UPASS_TABLE, 'md5$d9eb8$01495b32852bffb27cf5d4394fe7a54c')]
    known_unidentified_hashes = [
     'sha1$aa$bb']
    known_malformed_hashes = [
     'md5$aa$bb']

    class FuzzHashGenerator(HandlerCase.FuzzHashGenerator):

        def random_salt_size(self):
            handler = self.handler
            default = handler.default_salt_size
            lower = 1
            upper = handler.max_salt_size or default * 4
            return self.randintgauss(lower, upper, default, default * 0.5)


class django_salted_sha1_test(HandlerCase, _DjangoHelper):
    handler = hash.django_salted_sha1
    max_django_version = (1, 9)
    django_has_encoding_glitch = True
    known_correct_hashes = [
     ('password', 'sha1$123abcdef$e4a1877b0e35c47329e7ed7e58014276168a37ba'),
     ('test', 'sha1$bcwHF9Hy8lxS$6b4cfa0651b43161c6f1471ce9523acf1f751ba3'),
     (
      UPASS_USD, 'sha1$c2e86$0f75c5d7fbd100d587c127ef0b693cde611b4ada'),
     (
      UPASS_TABLE, 'sha1$6d853$ef13a4d8fb57aed0cb573fe9c82e28dc7fd372d4'),
     ('MyPassword', 'sha1$54123$893cf12e134c3c215f3a76bd50d13f92404a54d3')]
    known_unidentified_hashes = [
     'md5$aa$bb']
    known_malformed_hashes = [
     'sha1$c2e86$0f75']
    FuzzHashGenerator = django_salted_md5_test.FuzzHashGenerator


class django_pbkdf2_sha256_test(HandlerCase, _DjangoHelper):
    handler = hash.django_pbkdf2_sha256
    known_correct_hashes = [
     ('not a password', 'pbkdf2_sha256$10000$kjVJaVz6qsnJ$5yPHw3rwJGECpUf70daLGhOrQ5+AMxIJdz1c3bqK1Rs='),
     (
      UPASS_TABLE,
      'pbkdf2_sha256$10000$bEwAfNrH1TlQ$OgYUblFNUX1B8GfMqaCYUK/iHyO0pa7STTDdaEJBuY0=')]


class django_pbkdf2_sha1_test(HandlerCase, _DjangoHelper):
    handler = hash.django_pbkdf2_sha1
    known_correct_hashes = [
     ('not a password', 'pbkdf2_sha1$10000$wz5B6WkasRoF$atJmJ1o+XfJxKq1+Nu1f1i57Z5I='),
     (
      UPASS_TABLE,
      'pbkdf2_sha1$10000$KZKWwvqb8BfL$rw5pWsxJEU4JrZAQhHTCO+u0f5Y=')]


@skipUnless(hash.bcrypt.has_backend(), 'no bcrypt backends available')
class django_bcrypt_test(HandlerCase, _DjangoHelper):
    handler = hash.django_bcrypt
    fuzz_salts_need_bcrypt_repair = True
    known_correct_hashes = [
     ('', 'bcrypt$$2a$06$DCq7YPn5Rq63x1Lad4cll.TV4S6ytwfsfvkgY8jIucDrjc8deX1s.'),
     ('abcdefghijklmnopqrstuvwxyz', 'bcrypt$$2a$10$fVH8e28OQRj9tqiDXs1e1uxpsjN0c7II7YPKXua2NAKYvM6iQk7dq'),
     (
      UPASS_TABLE,
      'bcrypt$$2a$05$Z17AXnnlpzddNUvnC6cZNOSwMA/8oNiKnHTHTwLlBijfucQQlHjaG')]

    def populate_settings(self, kwds):
        kwds.setdefault('rounds', 4)
        super(django_bcrypt_test, self).populate_settings(kwds)

    class FuzzHashGenerator(HandlerCase.FuzzHashGenerator):

        def random_rounds(self):
            return self.randintgauss(5, 8, 6, 1)

        def random_ident(self):
            return


@skipUnless(hash.bcrypt.has_backend(), 'no bcrypt backends available')
class django_bcrypt_sha256_test(HandlerCase, _DjangoHelper):
    handler = hash.django_bcrypt_sha256
    forbidden_characters = None
    fuzz_salts_need_bcrypt_repair = True
    known_correct_hashes = [
     ('', 'bcrypt_sha256$$2a$06$/3OeRpbOf8/l6nPPRdZPp.nRiyYqPobEZGdNRBWihQhiFDh1ws1tu'),
     (
      UPASS_LETMEIN,
      'bcrypt_sha256$$2a$08$NDjSAIcas.EcoxCRiArvT.MkNiPYVhrsrnJsRkLueZOoV1bsQqlmC'),
     (
      UPASS_TABLE,
      'bcrypt_sha256$$2a$06$kCXUnRFQptGg491siDKNTu8RxjBGSjALHRuvhPYNFsa4Ea5d9M48u'),
     (
      repeat_string('abc123', 72),
      'bcrypt_sha256$$2a$06$Tg/oYyZTyAf.Nb3qSgN61OySmyXA8FoY4PjGizjE1QSDfuL5MXNni'),
     (
      repeat_string('abc123', 72) + 'qwr',
      'bcrypt_sha256$$2a$06$Tg/oYyZTyAf.Nb3qSgN61Ocy0BEz1RK6xslSNi8PlaLX2pe7x/KQG'),
     (
      repeat_string('abc123', 72) + 'xyz',
      'bcrypt_sha256$$2a$06$Tg/oYyZTyAf.Nb3qSgN61OvY2zoRVUa2Pugv2ExVOUT2YmhvxUFUa')]
    known_malformed_hashers = [
     'bcrypt_sha256$xyz$2a$06$/3OeRpbOf8/l6nPPRdZPp.nRiyYqPobEZGdNRBWihQhiFDh1ws1tu']

    def populate_settings(self, kwds):
        kwds.setdefault('rounds', 4)
        super(django_bcrypt_sha256_test, self).populate_settings(kwds)

    class FuzzHashGenerator(HandlerCase.FuzzHashGenerator):

        def random_rounds(self):
            return self.randintgauss(5, 8, 6, 1)

        def random_ident(self):
            return


from otp.ai.passlib.tests.test_handlers_argon2 import _base_argon2_test

@skipUnless(hash.argon2.has_backend(), 'no argon2 backends available')
class django_argon2_test(HandlerCase, _DjangoHelper):
    handler = hash.django_argon2
    known_correct_hashes = [
     ('password', 'argon2$argon2i$v=19$m=256,t=1,p=1$c29tZXNhbHQ$AJFIsNZTMKTAewB4+ETN1A'),
     ('password', 'argon2$argon2i$v=19$m=380,t=2,p=2$c29tZXNhbHQ$SrssP8n7m/12VWPM8dvNrw'),
     (
      UPASS_LETMEIN, 'argon2$argon2i$v=19$m=512,t=2,p=2$V25jN1l4UUJZWkR1$MxpA1BD2Gh7+D79gaAw6sQ')]

    def setUpWarnings(self):
        super(django_argon2_test, self).setUpWarnings()
        warnings.filterwarnings('ignore', '.*Using argon2pure backend.*')

    def do_stub_encrypt(self, handler=None, **settings):
        handler = (handler or self.handler).using(**settings)
        self = handler.wrapped(use_defaults=True)
        self.checksum = self._stub_checksum
        return handler._wrap_hash(self.to_string())

    def test_03_legacy_hash_workflow(self):
        raise self.skipTest('legacy 1.6 workflow not supported')

    class FuzzHashGenerator(_base_argon2_test.FuzzHashGenerator):

        def random_rounds(self):
            return self.randintgauss(1, 3, 2, 1)