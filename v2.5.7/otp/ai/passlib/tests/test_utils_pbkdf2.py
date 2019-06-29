from __future__ import with_statement
import hashlib, warnings
from otp.ai.passlib.utils.compat import u, JYTHON
from otp.ai.passlib.tests.utils import TestCase, hb

class UtilsTest(TestCase):
    descriptionPrefix = 'passlib.utils.pbkdf2'
    ndn_formats = [
     'hashlib', 'iana']
    ndn_values = [
     ('md5', 'md5', 'SCRAM-MD5-PLUS', 'MD-5'),
     ('sha1', 'sha-1', 'SCRAM-SHA-1', 'SHA1'),
     ('sha256', 'sha-256', 'SHA_256', 'sha2-256'),
     ('ripemd', 'ripemd', 'SCRAM-RIPEMD', 'RIPEMD'),
     ('ripemd160', 'ripemd-160', 'SCRAM-RIPEMD-160', 'RIPEmd160'),
     ('test128', 'test-128', 'TEST128'),
     ('test2', 'test2', 'TEST-2'),
     ('test3_128', 'test3-128', 'TEST-3-128')]

    def setUp(self):
        super(UtilsTest, self).setUp()
        warnings.filterwarnings('ignore', '.*passlib.utils.pbkdf2.*deprecated', DeprecationWarning)

    def test_norm_hash_name(self):
        from itertools import chain
        from otp.ai.passlib.utils.pbkdf2 import norm_hash_name
        from otp.ai.passlib.crypto.digest import _known_hash_names
        for format in self.ndn_formats:
            norm_hash_name('md4', format)

        self.assertRaises(ValueError, norm_hash_name, 'md4', None)
        self.assertRaises(ValueError, norm_hash_name, 'md4', 'fake')
        self.assertEqual(norm_hash_name(u('MD4')), 'md4')
        self.assertEqual(norm_hash_name('MD4'), 'md4')
        self.assertRaises(TypeError, norm_hash_name, None)
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore', '.*unknown hash')
            for row in chain(_known_hash_names, self.ndn_values):
                for idx, format in enumerate(self.ndn_formats):
                    correct = row[idx]
                    for value in row:
                        result = norm_hash_name(value, format)
                        self.assertEqual(result, correct, 'name=%r, format=%r:' % (value,
                         format))

        return


class Pbkdf1_Test(TestCase):
    descriptionPrefix = 'passlib.utils.pbkdf2.pbkdf1()'
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

    def setUp(self):
        super(Pbkdf1_Test, self).setUp()
        warnings.filterwarnings('ignore', '.*passlib.utils.pbkdf2.*deprecated', DeprecationWarning)

    def test_known(self):
        from otp.ai.passlib.utils.pbkdf2 import pbkdf1
        for secret, salt, rounds, keylen, digest, correct in self.pbkdf1_tests:
            result = pbkdf1(secret, salt, rounds, keylen, digest)
            self.assertEqual(result, correct)

    def test_border(self):
        from otp.ai.passlib.utils.pbkdf2 import pbkdf1

        def helper(secret='secret', salt='salt', rounds=1, keylen=1, hash='md5'):
            return pbkdf1(secret, salt, rounds, keylen, hash)

        helper()
        self.assertRaises(TypeError, helper, secret=1)
        self.assertRaises(TypeError, helper, salt=1)
        self.assertRaises(ValueError, helper, hash='missing')
        self.assertRaises(ValueError, helper, rounds=0)
        self.assertRaises(TypeError, helper, rounds='1')
        self.assertRaises(ValueError, helper, keylen=-1)
        self.assertRaises(ValueError, helper, keylen=17, hash='md5')
        self.assertRaises(TypeError, helper, keylen='1')


class Pbkdf2_Test(TestCase):
    descriptionPrefix = 'passlib.utils.pbkdf2.pbkdf2()'
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
      10000, 64, 'hmac-sha512'),
     (
      hb('e248fb6b13365146f8ac6307cc222812'),
      'secret', 'salt', 10, 16, 'hmac-sha1'),
     (
      hb('e248fb6b13365146f8ac6307cc2228127872da6d'),
      'secret', 'salt', 10, None, 'hmac-sha1')]

    def setUp(self):
        super(Pbkdf2_Test, self).setUp()
        warnings.filterwarnings('ignore', '.*passlib.utils.pbkdf2.*deprecated', DeprecationWarning)

    def test_known(self):
        from otp.ai.passlib.utils.pbkdf2 import pbkdf2
        for row in self.pbkdf2_test_vectors:
            correct, secret, salt, rounds, keylen = row[:5]
            prf = row[5] if len(row) == 6 else 'hmac-sha1'
            result = pbkdf2(secret, salt, rounds, keylen, prf)
            self.assertEqual(result, correct)

    def test_border(self):
        from otp.ai.passlib.utils.pbkdf2 import pbkdf2

        def helper(secret='password', salt='salt', rounds=1, keylen=None, prf='hmac-sha1'):
            return pbkdf2(secret, salt, rounds, keylen, prf)

        helper()
        self.assertRaises(ValueError, helper, rounds=-1)
        self.assertRaises(ValueError, helper, rounds=0)
        self.assertRaises(TypeError, helper, rounds='x')
        self.assertRaises(ValueError, helper, keylen=-1)
        self.assertRaises(ValueError, helper, keylen=0)
        helper(keylen=1)
        self.assertRaises(OverflowError, helper, keylen=20 * 4294967295L + 1)
        self.assertRaises(TypeError, helper, keylen='x')
        self.assertRaises(TypeError, helper, salt=5)
        self.assertRaises(TypeError, helper, secret=5)
        self.assertRaises(ValueError, helper, prf='hmac-foo')
        self.assertRaises(NotImplementedError, helper, prf='foo')
        self.assertRaises(TypeError, helper, prf=5)
        return

    def test_default_keylen(self):
        from otp.ai.passlib.utils.pbkdf2 import pbkdf2

        def helper(secret='password', salt='salt', rounds=1, keylen=None, prf='hmac-sha1'):
            return pbkdf2(secret, salt, rounds, keylen, prf)

        self.assertEqual(len(helper(prf='hmac-sha1')), 20)
        self.assertEqual(len(helper(prf='hmac-sha256')), 32)
        return

    def test_custom_prf(self):
        from otp.ai.passlib.utils.pbkdf2 import pbkdf2

        def prf(key, msg):
            return hashlib.md5(key + msg + 'fooey').digest()

        self.assertRaises(NotImplementedError, pbkdf2, 'secret', 'salt', 1000, 20, prf)