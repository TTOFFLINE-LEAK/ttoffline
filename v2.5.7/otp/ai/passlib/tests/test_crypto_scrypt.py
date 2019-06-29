from binascii import hexlify
import hashlib, logging
log = logging.getLogger(__name__)
import struct, warnings
warnings.filterwarnings('ignore', '.*using builtin scrypt backend.*')
from otp.ai.passlib import exc
from otp.ai.passlib.utils import getrandbytes
from otp.ai.passlib.utils.compat import PYPY, u, bascii_to_str
from otp.ai.passlib.utils.decor import classproperty
from otp.ai.passlib.tests.utils import TestCase, skipUnless, TEST_MODE, hb
from otp.ai.passlib.crypto import scrypt as scrypt_mod
__all__ = [
 'ScryptEngineTest',
 'BuiltinScryptTest',
 'FastScryptTest']

def hexstr(data):
    return bascii_to_str(hexlify(data))


def unpack_uint32_list(data, check_count=None):
    count = len(data) // 4
    return struct.unpack('<%dI' % count, data)


def seed_bytes(seed, count):
    if hasattr(seed, 'encode'):
        seed = seed.encode('ascii')
    buf = ''
    i = 0
    while len(buf) < count:
        buf += hashlib.sha256(seed + struct.pack('<I', i)).digest()
        i += 1

    return buf[:count]


class ScryptEngineTest(TestCase):
    descriptionPrefix = 'passlib.crypto.scrypt._builtin'

    def test_smix(self):
        from otp.ai.passlib.crypto.scrypt._builtin import ScryptEngine
        rng = self.getRandom()
        input = hb('\n            f7 ce 0b 65 3d 2d 72 a4 10 8c f5 ab e9 12 ff dd\n            77 76 16 db bb 27 a7 0e 82 04 f3 ae 2d 0f 6f ad\n            89 f6 8f 48 11 d1 e8 7b cc 3b d7 40 0a 9f fd 29\n            09 4f 01 84 63 95 74 f3 9a e5 a1 31 52 17 bc d7\n            89 49 91 44 72 13 bb 22 6c 25 b5 4d a8 63 70 fb\n            cd 98 43 80 37 46 66 bb 8f fc b5 bf 40 c2 54 b0\n            67 d2 7c 51 ce 4a d5 fe d8 29 c9 0b 50 5a 57 1b\n            7f 4d 1c ad 6a 52 3c da 77 0e 67 bc ea af 7e 89\n            ')
        output = hb('\n            79 cc c1 93 62 9d eb ca 04 7f 0b 70 60 4b f6 b6\n            2c e3 dd 4a 96 26 e3 55 fa fc 61 98 e6 ea 2b 46\n            d5 84 13 67 3b 99 b0 29 d6 65 c3 57 60 1f b4 26\n            a0 b2 f4 bb a2 00 ee 9f 0a 43 d1 9b 57 1a 9c 71\n            ef 11 42 e6 5d 5a 26 6f dd ca 83 2c e5 9f aa 7c\n            ac 0b 9c f1 be 2b ff ca 30 0d 01 ee 38 76 19 c4\n            ae 12 fd 44 38 f2 03 a0 e4 e1 c4 7e c3 14 86 1f\n            4e 90 87 cb 33 39 6a 68 73 e8 f9 d2 53 9a 4b 8e\n            ')
        engine = ScryptEngine(n=16, r=1, p=rng.randint(1, 1023))
        self.assertEqual(engine.smix(input), output)

    def test_bmix(self):
        from otp.ai.passlib.crypto.scrypt._builtin import ScryptEngine
        rng = self.getRandom()

        def check_bmix(r, input, output):
            engine = ScryptEngine(r=r, n=1 << rng.randint(1, 32), p=rng.randint(1, 1023))
            target = [ rng.randint(0, 4294967296L) for _ in range(2 * r * 16) ]
            engine.bmix(input, target)
            self.assertEqual(target, list(output))
            if r == 1:
                del engine.bmix
                target = [ rng.randint(0, 4294967296L) for _ in range(2 * r * 16) ]
                engine.bmix(input, target)
                self.assertEqual(target, list(output))

        input = unpack_uint32_list(hb('\n                f7 ce 0b 65 3d 2d 72 a4 10 8c f5 ab e9 12 ff dd\n                77 76 16 db bb 27 a7 0e 82 04 f3 ae 2d 0f 6f ad\n                89 f6 8f 48 11 d1 e8 7b cc 3b d7 40 0a 9f fd 29\n                09 4f 01 84 63 95 74 f3 9a e5 a1 31 52 17 bc d7\n\n                89 49 91 44 72 13 bb 22 6c 25 b5 4d a8 63 70 fb\n                cd 98 43 80 37 46 66 bb 8f fc b5 bf 40 c2 54 b0\n                67 d2 7c 51 ce 4a d5 fe d8 29 c9 0b 50 5a 57 1b\n                7f 4d 1c ad 6a 52 3c da 77 0e 67 bc ea af 7e 89\n            '), 32)
        output = unpack_uint32_list(hb('\n                a4 1f 85 9c 66 08 cc 99 3b 81 ca cb 02 0c ef 05\n                04 4b 21 81 a2 fd 33 7d fd 7b 1c 63 96 68 2f 29\n                b4 39 31 68 e3 c9 e6 bc fe 6b c5 b7 a0 6d 96 ba\n                e4 24 cc 10 2c 91 74 5c 24 ad 67 3d c7 61 8f 81\n\n                20 ed c9 75 32 38 81 a8 05 40 f6 4c 16 2d cd 3c\n                21 07 7c fe 5f 8d 5f e2 b1 a4 16 8f 95 36 78 b7\n                7d 3b 3d 80 3b 60 e4 ab 92 09 96 e5 9b 4d 53 b6\n                5d 2a 22 58 77 d5 ed f5 84 2c b9 f1 4e ef e4 25\n            '), 32)
        r = 2
        input = unpack_uint32_list(seed_bytes('bmix with r=2', 128 * r))
        output = unpack_uint32_list(hb('\n            ba240854954f4585f3d0573321f10beee96f12acdc1feb498131e40512934fd7\n            43e8139c17d0743c89d09ac8c3582c273c60ab85db63e410d049a9e17a42c6a1\n\n            6c7831b11bf370266afdaff997ae1286920dea1dedf0f4a1795ba710ba9017f1\n            a374400766f13ebd8969362de2d153965e9941bdde0768fa5b53e8522f116ce0\n\n            d14774afb88f46cd919cba4bc64af7fca0ecb8732d1fc2191e0d7d1b6475cb2e\n            e3db789ee478d056c4eb6c6e28b99043602dbb8dfb60c6e048bf90719da8d57d\n\n            3c42250e40ab79a1ada6aae9299b9790f767f54f388d024a1465b30cbbe9eb89\n            002d4f5c215c4259fac4d083bac5fb0b47463747d568f40bb7fa87c42f0a1dc1\n            '), 32 * r)
        check_bmix(r, input, output)
        r = 3
        input = unpack_uint32_list(seed_bytes('bmix with r=3', 128 * r))
        output = unpack_uint32_list(hb('\n            11ddd8cf60c61f59a6e5b128239bdc77b464101312c88bd1ccf6be6e75461b29\n            7370d4770c904d0b09c402573cf409bf2db47b91ba87d5a3de469df8fb7a003c\n\n            95a66af96dbdd88beddc8df51a2f72a6f588d67e7926e9c2b676c875da13161e\n            b6262adac39e6b3003e9a6fbc8c1a6ecf1e227c03bc0af3e5f8736c339b14f84\n\n            c7ae5b89f5e16d0faf8983551165f4bb712d97e4f81426e6b78eb63892d3ff54\n            80bf406c98e479496d0f76d23d728e67d2a3d2cdbc4a932be6db36dc37c60209\n\n            a5ca76ca2d2979f995f73fe8182eefa1ce0ba0d4fc27d5b827cb8e67edd6552f\n            00a5b3ab6b371bd985a158e728011314eb77f32ade619b3162d7b5078a19886c\n\n            06f12bc8ae8afa46489e5b0239954d5216967c928982984101e4a88bae1f60ae\n            3f8a456e169a8a1c7450e7955b8a13a202382ae19d41ce8ef8b6a15eeef569a7\n\n            20f54c48e44cb5543dda032c1a50d5ddf2919030624978704eb8db0290052a1f\n            5d88989b0ef931b6befcc09e9d5162320e71e80b89862de7e2f0b6c67229b93f\n            '), 32 * r)
        check_bmix(r, input, output)
        r = 4
        input = unpack_uint32_list(seed_bytes('bmix with r=4', 128 * r))
        output = unpack_uint32_list(hb('\n            803fcf7362702f30ef43250f20bc6b1b8925bf5c4a0f5a14bbfd90edce545997\n            3047bd81655f72588ca93f5c2f4128adaea805e0705a35e14417101fdb1c498c\n\n            33bec6f4e5950d66098da8469f3fe633f9a17617c0ea21275185697c0e4608f7\n            e6b38b7ec71704a810424637e2c296ca30d9cbf8172a71a266e0393deccf98eb\n\n            abc430d5f144eb0805308c38522f2973b7b6a48498851e4c762874497da76b88\n            b769b471fbfc144c0e8e859b2b3f5a11f51604d268c8fd28db55dff79832741a\n\n            1ac0dfdaff10f0ada0d93d3b1f13062e4107c640c51df05f4110bdda15f51b53\n            3a75bfe56489a6d8463440c78fb8c0794135e38591bdc5fa6cec96a124178a4a\n\n            d1a976e985bfe13d2b4af51bd0fc36dd4cfc3af08efe033b2323a235205dc43d\n            e57778a492153f9527338b3f6f5493a03d8015cd69737ee5096ad4cbe660b10f\n\n            b75b1595ddc96e3748f5c9f61fba1ef1f0c51b6ceef8bbfcc34b46088652e6f7\n            edab61521cbad6e69b77be30c9c97ea04a4af359dafc205c7878cc9a6c5d122f\n\n            8d77f3cbe65ab14c3c491ef94ecb3f5d2c2dd13027ea4c3606262bb3c9ce46e7\n            dc424729dc75f6e8f06096c0ad8ad4d549c42f0cad9b33cb95d10fb3cadba27c\n\n            5f4bf0c1ac677c23ba23b64f56afc3546e62d96f96b58d7afc5029f8168cbab4\n            533fd29fc83c8d2a32b81923992e4938281334e0c3694f0ee56f8ff7df7dc4ae\n            '), 32 * r)
        check_bmix(r, input, output)

    def test_salsa(self):
        from otp.ai.passlib.crypto.scrypt._builtin import salsa20
        input = unpack_uint32_list(hb('\n            7e 87 9a 21 4f 3e c9 86 7c a9 40 e6 41 71 8f 26\n            ba ee 55 5b 8c 61 c1 b5 0d f8 46 11 6d cd 3b 1d\n            ee 24 f3 19 df 9b 3d 85 14 12 1e 4b 5a c5 aa 32\n            76 02 1d 29 09 c7 48 29 ed eb c6 8d b8 b8 c2 5e\n            '))
        output = unpack_uint32_list(hb('\n            a4 1f 85 9c 66 08 cc 99 3b 81 ca cb 02 0c ef 05\n            04 4b 21 81 a2 fd 33 7d fd 7b 1c 63 96 68 2f 29\n            b4 39 31 68 e3 c9 e6 bc fe 6b c5 b7 a0 6d 96 ba\n            e4 24 cc 10 2c 91 74 5c 24 ad 67 3d c7 61 8f 81\n            '))
        self.assertEqual(salsa20(input), output)
        input = list(range(16))
        output = unpack_uint32_list(hb('\n            f518dd4fb98883e0a87954c05cab867083bb8808552810752285a05822f56c16\n            9d4a2a0fd2142523d758c60b36411b682d53860514b871d27659042a5afa475d\n            '))
        self.assertEqual(salsa20(input), output)


class _CommonScryptTest(TestCase):

    @classproperty
    def descriptionPrefix(cls):
        return 'passlib.utils.scrypt.scrypt() <%s backend>' % cls.backend

    backend = None

    def setUp(self):
        scrypt_mod._set_backend(self.backend)
        super(_CommonScryptTest, self).setUp()

    reference_vectors = [
     (
      '', '', 16, 1, 1, 64,
      hb('\n        77 d6 57 62 38 65 7b 20 3b 19 ca 42 c1 8a 04 97\n        f1 6b 48 44 e3 07 4a e8 df df fa 3f ed e2 14 42\n        fc d0 06 9d ed 09 48 f8 32 6a 75 3a 0f c8 1f 17\n        e8 d3 e0 fb 2e 0d 36 28 cf 35 e2 0c 38 d1 89 06\n        ')),
     (
      'password', 'NaCl', 1024, 8, 16, 64,
      hb('\n        fd ba be 1c 9d 34 72 00 78 56 e7 19 0d 01 e9 fe\n        7c 6a d7 cb c8 23 78 30 e7 73 76 63 4b 37 31 62\n        2e af 30 d9 2e 22 a3 88 6f f1 09 27 9d 98 30 da\n        c7 27 af b9 4a 83 ee 6d 83 60 cb df a2 cc 06 40\n        ')),
     (
      'pleaseletmein', 'SodiumChloride', 16384, 8, 1, 64,
      hb('\n        70 23 bd cb 3a fd 73 48 46 1c 06 cd 81 fd 38 eb\n        fd a8 fb ba 90 4f 8e 3e a9 b5 43 f6 54 5d a1 f2\n        d5 43 29 55 61 3f 0f cf 62 d4 97 05 24 2a 9a f9\n        e6 1e 85 dc 0d 65 1e 40 df cf 01 7b 45 57 58 87\n        ')),
     (
      'pleaseletmein', 'SodiumChloride', 1048576, 8, 1, 64,
      hb('\n        21 01 cb 9b 6a 51 1a ae ad db be 09 cf 70 f8 81\n        ec 56 8d 57 4a 2f fd 4d ab e5 ee 98 20 ad aa 47\n        8e 56 fd 8f 4b a5 d0 9f fa 1c 6d 92 7c 40 f4 c3\n        37 30 40 49 e8 a9 52 fb cb f4 5c 6f a7 7a 41 a4\n        '))]

    def test_reference_vectors(self):
        for secret, salt, n, r, p, keylen, result in self.reference_vectors:
            if n >= 1024 and TEST_MODE(max='default'):
                continue
            if n > 16384 and self.backend == 'builtin':
                continue
            log.debug('scrypt reference vector: %r %r n=%r r=%r p=%r', secret, salt, n, r, p)
            self.assertEqual(scrypt_mod.scrypt(secret, salt, n, r, p, keylen), result)

    _already_tested_others = None

    def test_other_backends(self):
        if self._already_tested_others:
            raise self.skipTest('already run under %r backend test' % self._already_tested_others)
        self._already_tested_others = self.backend
        rng = self.getRandom()
        orig = scrypt_mod.backend
        available = set(name for name in scrypt_mod.backend_values if scrypt_mod._has_backend(name))
        scrypt_mod._set_backend(orig)
        available.discard(self.backend)
        if not available:
            raise self.skipTest('no other backends found')
        warnings.filterwarnings('ignore', '(?i)using builtin scrypt backend', category=exc.PasslibSecurityWarning)
        for _ in range(10):
            secret = getrandbytes(rng, rng.randint(0, 64))
            salt = getrandbytes(rng, rng.randint(0, 64))
            n = 1 << rng.randint(1, 10)
            r = rng.randint(1, 8)
            p = rng.randint(1, 3)
            ks = rng.randint(1, 64)
            previous = None
            backends = set()
            for name in available:
                scrypt_mod._set_backend(name)
                self.assertNotIn(scrypt_mod._scrypt, backends)
                backends.add(scrypt_mod._scrypt)
                result = hexstr(scrypt_mod.scrypt(secret, salt, n, r, p, ks))
                self.assertEqual(len(result), 2 * ks)
                if previous is not None:
                    self.assertEqual(result, previous, msg='%r output differs from others %r: %r' % (
                     name, available, [secret, salt, n, r, p, ks]))

        return

    def test_backend(self):
        scrypt_mod.backend = None
        scrypt_mod._scrypt = None
        self.assertRaises(TypeError, scrypt_mod.scrypt, 's', 's', 2, 2, 2, 16)
        scrypt_mod._set_backend(self.backend)
        self.assertEqual(scrypt_mod.backend, self.backend)
        scrypt_mod.scrypt('s', 's', 2, 2, 2, 16)
        self.assertRaises(ValueError, scrypt_mod._set_backend, 'xxx')
        self.assertEqual(scrypt_mod.backend, self.backend)
        return

    def test_secret_param(self):

        def run_scrypt(secret):
            return hexstr(scrypt_mod.scrypt(secret, 'salt', 2, 2, 2, 16))

        TEXT = u('abc\\u00defg')
        self.assertEqual(run_scrypt(TEXT), '05717106997bfe0da42cf4779a2f8bd8')
        TEXT_UTF8 = 'abc\xc3\x9efg'
        self.assertEqual(run_scrypt(TEXT_UTF8), '05717106997bfe0da42cf4779a2f8bd8')
        TEXT_LATIN1 = 'abc\xdefg'
        self.assertEqual(run_scrypt(TEXT_LATIN1), '770825d10eeaaeaf98e8a3c40f9f441d')
        self.assertEqual(run_scrypt(''), 'ca1399e5fae5d3b9578dcd2b1faff6e2')
        self.assertRaises(TypeError, run_scrypt, None)
        self.assertRaises(TypeError, run_scrypt, 1)
        return

    def test_salt_param(self):

        def run_scrypt(salt):
            return hexstr(scrypt_mod.scrypt('secret', salt, 2, 2, 2, 16))

        TEXT = u('abc\\u00defg')
        self.assertEqual(run_scrypt(TEXT), 'a748ec0f4613929e9e5f03d1ab741d88')
        TEXT_UTF8 = 'abc\xc3\x9efg'
        self.assertEqual(run_scrypt(TEXT_UTF8), 'a748ec0f4613929e9e5f03d1ab741d88')
        TEXT_LATIN1 = 'abc\xdefg'
        self.assertEqual(run_scrypt(TEXT_LATIN1), '91d056fb76fb6e9a7d1cdfffc0a16cd1')
        self.assertRaises(TypeError, run_scrypt, None)
        self.assertRaises(TypeError, run_scrypt, 1)
        return

    def test_n_param(self):

        def run_scrypt(n):
            return hexstr(scrypt_mod.scrypt('secret', 'salt', n, 2, 2, 16))

        self.assertRaises(ValueError, run_scrypt, -1)
        self.assertRaises(ValueError, run_scrypt, 0)
        self.assertRaises(ValueError, run_scrypt, 1)
        self.assertEqual(run_scrypt(2), 'dacf2bca255e2870e6636fa8c8957a66')
        self.assertRaises(ValueError, run_scrypt, 3)
        self.assertRaises(ValueError, run_scrypt, 15)
        self.assertEqual(run_scrypt(16), '0272b8fc72bc54b1159340ed99425233')

    def test_r_param(self):

        def run_scrypt(r, n=2, p=2):
            return hexstr(scrypt_mod.scrypt('secret', 'salt', n, r, p, 16))

        self.assertRaises(ValueError, run_scrypt, -1)
        self.assertRaises(ValueError, run_scrypt, 0)
        self.assertEqual(run_scrypt(1), '3d630447d9f065363b8a79b0b3670251')
        self.assertEqual(run_scrypt(2), 'dacf2bca255e2870e6636fa8c8957a66')
        self.assertEqual(run_scrypt(5), '114f05e985a903c27237b5578e763736')
        self.assertRaises(ValueError, run_scrypt, 1073741824, p=1)
        self.assertRaises(ValueError, run_scrypt, 1073741824 / 2, p=2)

    def test_p_param(self):

        def run_scrypt(p, n=2, r=2):
            return hexstr(scrypt_mod.scrypt('secret', 'salt', n, r, p, 16))

        self.assertRaises(ValueError, run_scrypt, -1)
        self.assertRaises(ValueError, run_scrypt, 0)
        self.assertEqual(run_scrypt(1), 'f2960ea8b7d48231fcec1b89b784a6fa')
        self.assertEqual(run_scrypt(2), 'dacf2bca255e2870e6636fa8c8957a66')
        self.assertEqual(run_scrypt(5), '848a0eeb2b3543e7f543844d6ca79782')
        self.assertRaises(ValueError, run_scrypt, 1073741824, r=1)
        self.assertRaises(ValueError, run_scrypt, 1073741824 / 2, r=2)

    def test_keylen_param(self):
        rng = self.getRandom()

        def run_scrypt(keylen):
            return hexstr(scrypt_mod.scrypt('secret', 'salt', 2, 2, 2, keylen))

        self.assertRaises(ValueError, run_scrypt, -1)
        self.assertRaises(ValueError, run_scrypt, 0)
        self.assertEqual(run_scrypt(1), 'da')
        ksize = rng.randint(0, 1024)
        self.assertEqual(len(run_scrypt(ksize)), 2 * ksize)
        self.assertRaises(ValueError, run_scrypt, 137438953441L)


@skipUnless(PYPY or TEST_MODE(min='default'), 'skipped under current test mode')
class BuiltinScryptTest(_CommonScryptTest):
    backend = 'builtin'

    def setUp(self):
        super(BuiltinScryptTest, self).setUp()
        warnings.filterwarnings('ignore', '(?i)using builtin scrypt backend', category=exc.PasslibSecurityWarning)

    def test_missing_backend(self):
        if _can_import_scrypt():
            raise self.skipTest("'scrypt' backend is present")
        self.assertRaises(exc.MissingBackendError, scrypt_mod._set_backend, 'scrypt')


def _can_import_scrypt():
    try:
        import scrypt
    except ImportError as err:
        if 'scrypt' in str(err):
            return False
        raise

    return True


@skipUnless(_can_import_scrypt(), "'scrypt' package not found")
class ScryptPackageTest(_CommonScryptTest):
    backend = 'scrypt'

    def test_default_backend(self):
        scrypt_mod._set_backend('default')
        self.assertEqual(scrypt_mod.backend, 'scrypt')