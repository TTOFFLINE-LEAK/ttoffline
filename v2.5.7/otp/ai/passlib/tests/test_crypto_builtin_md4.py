from __future__ import with_statement, division
from binascii import hexlify
import hashlib
from otp.ai.passlib.utils.compat import bascii_to_str, PY3, u
from otp.ai.passlib.crypto.digest import lookup_hash
from otp.ai.passlib.tests.utils import TestCase, skipUnless
__all__ = [
 '_Common_MD4_Test',
 'MD4_Builtin_Test',
 'MD4_SSL_Test']

class _Common_MD4_Test(TestCase):
    vectors = [
     ('', '31d6cfe0d16ae931b73c59d7e0c089c0'),
     ('a', 'bde52cb31de33e46245e05fbdbd6fb24'),
     ('abc', 'a448017aaf21d8525fc10ae87aa6729d'),
     ('message digest', 'd9130a8164549fe818874806e1c7014b'),
     ('abcdefghijklmnopqrstuvwxyz', 'd79e1c308aa5bbcdeea8ed63df412da9'),
     ('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789', '043f8582f241db351ce627e153e7f0e4'),
     ('12345678901234567890123456789012345678901234567890123456789012345678901234567890',
 'e33b4ddc9c38f2199c3e7b164fcc0536')]

    def get_md4_const(self):
        return lookup_hash('md4').const

    def test_attrs(self):
        h = self.get_md4_const()()
        self.assertEqual(h.name, 'md4')
        self.assertEqual(h.digest_size, 16)
        self.assertEqual(h.block_size, 64)

    def test_md4_update(self):
        md4 = self.get_md4_const()
        h = md4('')
        self.assertEqual(h.hexdigest(), '31d6cfe0d16ae931b73c59d7e0c089c0')
        h.update('a')
        self.assertEqual(h.hexdigest(), 'bde52cb31de33e46245e05fbdbd6fb24')
        h.update('bcdefghijklmnopqrstuvwxyz')
        self.assertEqual(h.hexdigest(), 'd79e1c308aa5bbcdeea8ed63df412da9')
        if PY3:
            h = md4()
            self.assertRaises(TypeError, h.update, u('a'))
            self.assertEqual(h.hexdigest(), '31d6cfe0d16ae931b73c59d7e0c089c0')
        else:
            h = md4()
            h.update(u('a'))
            self.assertEqual(h.hexdigest(), 'bde52cb31de33e46245e05fbdbd6fb24')

    def test_md4_hexdigest(self):
        md4 = self.get_md4_const()
        for input, hex in self.vectors:
            out = md4(input).hexdigest()
            self.assertEqual(out, hex)

    def test_md4_digest(self):
        md4 = self.get_md4_const()
        for input, hex in self.vectors:
            out = bascii_to_str(hexlify(md4(input).digest()))
            self.assertEqual(out, hex)

    def test_md4_copy(self):
        md4 = self.get_md4_const()
        h = md4('abc')
        h2 = h.copy()
        h2.update('def')
        self.assertEqual(h2.hexdigest(), '804e7f1c2586e50b49ac65db5b645131')
        h.update('ghi')
        self.assertEqual(h.hexdigest(), 'c5225580bfe176f6deeee33dee98732c')


def has_native_md4():
    try:
        hashlib.new('md4')
        return True
    except ValueError:
        return False


@skipUnless(has_native_md4(), 'hashlib lacks ssl/md4 support')
class MD4_SSL_Test(_Common_MD4_Test):
    descriptionPrefix = "hashlib.new('md4')"

    def setUp(self):
        super(MD4_SSL_Test, self).setUp()
        self.assertEqual(self.get_md4_const().__module__, 'hashlib')


class MD4_Builtin_Test(_Common_MD4_Test):
    descriptionPrefix = 'passlib.crypto._md4.md4()'

    def setUp(self):
        super(MD4_Builtin_Test, self).setUp()
        if has_native_md4():
            orig = hashlib.new

            def wrapper(name, *args):
                if name == 'md4':
                    raise ValueError('md4 disabled for testing')
                return orig(name, *args)

            self.patchAttr(hashlib, 'new', wrapper)
            lookup_hash.clear_cache()
            self.addCleanup(lookup_hash.clear_cache)
        self.assertEqual(self.get_md4_const().__module__, 'passlib.crypto._md4')