from __future__ import with_statement, division
from binascii import hexlify
import hashlib, warnings
from otp.ai.passlib.utils.compat import PY3, u, JYTHON
from otp.ai.passlib.tests.utils import TestCase, TEST_MODE, skipUnless, hb

class HashInfoTest(TestCase):
    descriptionPrefix = 'passlib.crypto.digest'
    norm_hash_formats = [
     'hashlib', 'iana']
    norm_hash_samples = [
     ('md5', 'md5', 'SCRAM-MD5-PLUS', 'MD-5'),
     ('sha1', 'sha-1', 'SCRAM-SHA-1', 'SHA1'),
     ('sha256', 'sha-256', 'SHA_256', 'sha2-256'),
     ('ripemd', 'ripemd', 'SCRAM-RIPEMD', 'RIPEMD'),
     ('ripemd160', 'ripemd-160', 'SCRAM-RIPEMD-160', 'RIPEmd160'),
     ('sha4_256', 'sha4-256', 'SHA4-256', 'SHA-4-256'),
     ('test128', 'test-128', 'TEST128'),
     ('test2', 'test2', 'TEST-2'),
     ('test3_128', 'test3-128', 'TEST-3-128')]

    def test_norm_hash_name(self):
        from itertools import chain
        from otp.ai.passlib.crypto.digest import norm_hash_name, _known_hash_names
        ctx = warnings.catch_warnings()
        ctx.__enter__()
        self.addCleanup(ctx.__exit__)
        warnings.filterwarnings('ignore', '.*unknown hash')
        self.assertEqual(norm_hash_name(u('MD4')), 'md4')
        self.assertEqual(norm_hash_name('MD4'), 'md4')
        self.assertRaises(TypeError, norm_hash_name, None)
        for row in chain(_known_hash_names, self.norm_hash_samples):
            for idx, format in enumerate(self.norm_hash_formats):
                correct = row[idx]
                for value in row:
                    result = norm_hash_name(value, format)
                    self.assertEqual(result, correct, 'name=%r, format=%r:' % (value,
                     format))

        return

    def test_lookup_hash_ctor(self):
        from otp.ai.passlib.crypto.digest import lookup_hash
        self.assertRaises(ValueError, lookup_hash, 'new')
        self.assertRaises(ValueError, lookup_hash, '__name__')
        self.assertRaises(ValueError, lookup_hash, 'sha4')
        self.assertEqual(lookup_hash('md5'), (hashlib.md5, 16, 64))
        try:
            hashlib.new('sha')
            has_sha = True
        except ValueError:
            has_sha = False
        else:
            if has_sha:
                record = lookup_hash('sha')
                const = record[0]
                self.assertEqual(record, (const, 20, 64))
                self.assertEqual(hexlify(const('abc').digest()), '0164b8a914cd2a5e74c4f7ff082c4d97f1edf880')
            else:
                self.assertRaises(ValueError, lookup_hash, 'sha')
            try:
                hashlib.new('md4')
                has_md4 = True
            except ValueError:
                has_md4 = False

        record = lookup_hash('md4')
        const = record[0]
        if not has_md4:
            from otp.ai.passlib.crypto._md4 import md4
            self.assertIs(const, md4)
        self.assertEqual(record, (const, 16, 64))
        self.assertEqual(hexlify(const('abc').digest()), 'a448017aaf21d8525fc10ae87aa6729d')
        self.assertRaises(ValueError, lookup_hash, 'xxx256')
        self.assertIs(lookup_hash('md5'), lookup_hash('md5'))

    def test_lookup_hash_metadata(self):
        from otp.ai.passlib.crypto.digest import lookup_hash
        info = lookup_hash('sha256')
        self.assertEqual(info.name, 'sha256')
        self.assertEqual(info.iana_name, 'sha-256')
        self.assertEqual(info.block_size, 64)
        self.assertEqual(info.digest_size, 32)
        self.assertIs(lookup_hash('SHA2-256'), info)
        info = lookup_hash('md5')
        self.assertEqual(info.name, 'md5')
        self.assertEqual(info.iana_name, 'md5')
        self.assertEqual(info.block_size, 64)
        self.assertEqual(info.digest_size, 16)

    def test_lookup_hash_alt_types(self):
        from otp.ai.passlib.crypto.digest import lookup_hash
        info = lookup_hash('sha256')
        self.assertIs(lookup_hash(info), info)
        self.assertIs(lookup_hash(info.const), info)
        self.assertRaises(TypeError, lookup_hash, 123)


class Pbkdf1_Test(TestCase):
    descriptionPrefix = 'passlib.crypto.digest.pbkdf1'
    pbkdf1_tests = [
     (
      'password', hb('78578E5A5D63CB06'), 1000, 16, 'sha1', hb('dc19847e05c64d2faf10ebfb4a3d2a20')),
     ('password', 'salt', 1000, 0, 'md5', ''),
     (
      'password', 'salt', 1000, 1, 'md5', hb('84')),
     (
      'password', 'salt', 1000, 8, 'md5', hb('8475c6a8531a5d27')),
     (
      'password', 'salt', 1000, 16, 'md5', hb('8475c6a8531a5d27e386cd496457812c')),
     (
      'password', 'salt', 1000, None, 'md5', hb('8475c6a8531a5d27e386cd496457812c')),
     (
      'password', 'salt', 1000, None, 'sha1', hb('4a8fd48e426ed081b535be5769892fa396293efb'))]
    if not JYTHON:
        pbkdf1_tests.append((
         'password', 'salt', 1000, None, 'md4', hb('f7f2e91100a8f96190f2dd177cb26453')))

    def test_known(self):
        from otp.ai.passlib.crypto.digest import pbkdf1
        for secret, salt, rounds, keylen, digest, correct in self.pbkdf1_tests:
            result = pbkdf1(digest, secret, salt, rounds, keylen)
            self.assertEqual(result, correct)

    def test_border(self):
        from otp.ai.passlib.crypto.digest import pbkdf1

        def helper(secret='secret', salt='salt', rounds=1, keylen=1, hash='md5'):
            return pbkdf1(hash, secret, salt, rounds, keylen)

        helper()
        self.assertRaises(TypeError, helper, secret=1)
        self.assertRaises(TypeError, helper, salt=1)
        self.assertRaises(ValueError, helper, hash='missing')
        self.assertRaises(ValueError, helper, rounds=0)
        self.assertRaises(TypeError, helper, rounds='1')
        self.assertRaises(ValueError, helper, keylen=-1)
        self.assertRaises(ValueError, helper, keylen=17, hash='md5')
        self.assertRaises(TypeError, helper, keylen='1')


from otp.ai.passlib.crypto.digest import pbkdf2_hmac, PBKDF2_BACKENDS

class Pbkdf2Test(TestCase):
    descriptionPrefix = 'passlib.crypto.digest.pbkdf2_hmac() <backends: %s>' % (', ').join(PBKDF2_BACKENDS)
    pbkdf2_test_vectors = [
     (
      hb('cdedb5281bb2f801565a1122b2563515'),
      'password', 'ATHENA.MIT.EDUraeburn', 1, 16),
     (
      hb('01dbee7f4a9e243e988b62c73cda935d'),
      'password', 'ATHENA.MIT.EDUraeburn', 2, 16),
     (
      hb('01dbee7f4a9e243e988b62c73cda935da05378b93244ec8f48a99e61ad799d86'),
      'password', 'ATHENA.MIT.EDUraeburn', 2, 32),
     (
      hb('5c08eb61fdf71e4e4ec3cf6ba1f5512ba7e52ddbc5e5142f708a31e2e62b1e13'),
      'password', 'ATHENA.MIT.EDUraeburn', 1200, 32),
     (
      hb('d1daa78615f287e6a1c8b120d7062a493f98d203e6be49a6adf4fa574b6e64ee'),
      'password', '\x124VxxV4\x12', 5, 32),
     (
      hb('139c30c0966bc32ba55fdbf212530ac9c5ec59f1a452f5cc9ad940fea0598ed1'),
      'X' * 64, 'pass phrase equals block size', 1200, 32),
     (
      hb('9ccad6d468770cd51b10e6a68721be611a8b4d282601db3b36be9246915ec82a'),
      'X' * 65, 'pass phrase exceeds block size', 1200, 32),
     (
      hb('0c60c80f961f0e71f3a9b524af6012062fe037a6'),
      'password', 'salt', 1, 20),
     (
      hb('ea6c014dc72d6f8ccd1ed92ace1d41f0d8de8957'),
      'password', 'salt', 2, 20),
     (
      hb('4b007901b765489abead49d926f721d065a429c1'),
      'password', 'salt', 4096, 20),
     (
      hb('3d2eec4fe41c849b80c8d83662c0e44a8b291a964cf2f07038'),
      'passwordPASSWORDpassword',
      'saltSALTsaltSALTsaltSALTsaltSALTsalt',
      4096, 25),
     (
      hb('56fa6aa75548099dcc37d7f03425e0c3'),
      'pass\x00word', 'sa\x00lt', 4096, 16),
     (
      hb('887CFF169EA8335235D8004242AA7D6187A41E3187DF0CE14E256D85ED97A97357AAA8FF0A3871AB9EEFF458392F462F495487387F685B7472FC6C29E293F0A0'),
      'hello',
      hb('9290F727ED06C38BA4549EF7DE25CF5642659211B7FC076F2D28FEFD71784BB8D8F6FB244A8CC5C06240631B97008565A120764C0EE9C2CB0073994D79080136'),
      10000, 64, 'sha512'),
     (
      hb('55ac046e56e3089fec1691c22544b605f94185216dde0465e68b9d57c20dacbc49ca9cccf179b645991664b39d77ef317c71b845b1e30bd509112041d3a19783'),
      'passwd', 'salt', 1, 64, 'sha256'),
     (
      hb('4ddcd8f60b98be21830cee5ef22701f9641a4418d04c0414aeff08876b34ab56a1d425a1225833549adb841b51c9b3176a272bdebba1d078478f62b397f33c8d'),
      'Password', 'NaCl', 80000, 64, 'sha256'),
     (
      hb('120fb6cffcf8b32c43e7225256c4f837a86548c92ccc35480805987cb70be17b'),
      'password', 'salt', 1, 32, 'sha256'),
     (
      hb('ae4d0c95af6b46d32d0adff928f06dd02a303f8ef3c251dfd6e2d85a95474c43'),
      'password', 'salt', 2, 32, 'sha256'),
     (
      hb('c5e478d59288c841aa530db6845c4c8d962893a001ce4e11a4963873aa98134a'),
      'password', 'salt', 4096, 32, 'sha256'),
     (
      hb('348c89dbcbd32b2f32d814b8116e84cf2b17347ebc1800181c4e2a1fb8dd53e1c635518c7dac47e9'),
      'passwordPASSWORDpassword', 'saltSALTsaltSALTsaltSALTsaltSALTsalt',
      4096, 40, 'sha256'),
     (
      hb('9e83f279c040f2a11aa4a02b24c418f2d3cb39560c9627fa4f47e3bcc2897c3d'),
      '', 'salt', 1024, 32, 'sha256'),
     (
      hb('ea5808411eb0c7e830deab55096cee582761e22a9bc034e3ece925225b07bf46'),
      'password', '', 1024, 32, 'sha256'),
     (
      hb('89b69d0516f829893c696226650a8687'),
      'pass\x00word', 'sa\x00lt', 4096, 16, 'sha256'),
     (
      hb('867f70cf1ade02cff3752599a3a53dc4af34c7a669815ae5d513554e1c8cf252'),
      'password', 'salt', 1, 32, 'sha512'),
     (
      hb('e1d9c16aa681708a45f5c7c4e215ceb66e011a2e9f0040713f18aefdb866d53c'),
      'password', 'salt', 2, 32, 'sha512'),
     (
      hb('d197b1b33db0143e018b12f3d1d1479e6cdebdcc97c5c0f87f6902e072f457b5'),
      'password', 'salt', 4096, 32, 'sha512'),
     (
      hb('6e23f27638084b0f7ea1734e0d9841f55dd29ea60a834466f3396bac801fac1eeb63802f03a0b4acd7603e3699c8b74437be83ff01ad7f55dac1ef60f4d56480c35ee68fd52c6936'),
      'passwordPASSWORDpassword', 'saltSALTsaltSALTsaltSALTsaltSALTsalt',
      1, 72, 'sha512'),
     (
      hb('0c60c80f961f0e71f3a9b524af6012062fe037a6'),
      'password', 'salt', 1, 20, 'sha1'),
     (
      hb('e248fb6b13365146f8ac6307cc222812'),
      'secret', 'salt', 10, 16, 'sha1'),
     (
      hb('e248fb6b13365146f8ac6307cc2228127872da6d'),
      'secret', 'salt', 10, None, 'sha1'),
     (
      hb('b1d5485772e6f76d5ebdc11b38d3eff0a5b2bd50dc11f937e86ecacd0cd40d1b9113e0734e3b76a3'),
      'secret', 'salt', 62, 40, 'md5'),
     (
      hb('ea014cc01f78d3883cac364bb5d054e2be238fb0b6081795a9d84512126e3129062104d2183464c4'),
      'secret', 'salt', 62, 40, 'md4')]

    def test_known(self):
        for row in self.pbkdf2_test_vectors:
            correct, secret, salt, rounds, keylen = row[:5]
            digest = row[5] if len(row) == 6 else 'sha1'
            result = pbkdf2_hmac(digest, secret, salt, rounds, keylen)
            self.assertEqual(result, correct)

    def test_backends(self):
        from otp.ai.passlib.crypto.digest import PBKDF2_BACKENDS
        try:
            import fastpbkdf2
            has_fastpbkdf2 = True
        except ImportError:
            has_fastpbkdf2 = False
        else:
            self.assertEqual('fastpbkdf2' in PBKDF2_BACKENDS, has_fastpbkdf2)
            try:
                from hashlib import pbkdf2_hmac
                has_hashlib_ssl = pbkdf2_hmac.__module__ != 'hashlib'
            except ImportError:
                has_hashlib_ssl = False

        self.assertEqual('hashlib-ssl' in PBKDF2_BACKENDS, has_hashlib_ssl)
        from otp.ai.passlib.utils.compat import PY3
        if PY3:
            self.assertIn('builtin-from-bytes', PBKDF2_BACKENDS)
        else:
            self.assertIn('builtin-unpack', PBKDF2_BACKENDS)

    def test_border(self):

        def helper(secret='password', salt='salt', rounds=1, keylen=None, digest='sha1'):
            return pbkdf2_hmac(digest, secret, salt, rounds, keylen)

        helper()
        self.assertRaises(ValueError, helper, rounds=-1)
        self.assertRaises(ValueError, helper, rounds=0)
        self.assertRaises(TypeError, helper, rounds='x')
        helper(keylen=1)
        self.assertRaises(ValueError, helper, keylen=-1)
        self.assertRaises(ValueError, helper, keylen=0)
        self.assertRaises(OverflowError, helper, keylen=20 * 4294967295L + 1)
        self.assertRaises(TypeError, helper, keylen='x')
        self.assertRaises(TypeError, helper, salt=5)
        self.assertRaises(TypeError, helper, secret=5)
        self.assertRaises(ValueError, helper, digest='foo')
        self.assertRaises(TypeError, helper, digest=5)
        return

    def test_default_keylen(self):

        def helper(secret='password', salt='salt', rounds=1, keylen=None, digest='sha1'):
            return pbkdf2_hmac(digest, secret, salt, rounds, keylen)

        self.assertEqual(len(helper(digest='sha1')), 20)
        self.assertEqual(len(helper(digest='sha256')), 32)
        return