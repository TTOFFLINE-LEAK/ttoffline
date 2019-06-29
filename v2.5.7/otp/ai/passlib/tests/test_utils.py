from __future__ import with_statement
from functools import partial
import warnings
from otp.ai.passlib.utils import is_ascii_safe
from otp.ai.passlib.utils.compat import irange, PY2, PY3, u, unicode, join_bytes, PYPY
from otp.ai.passlib.tests.utils import TestCase, hb, run_with_fixed_seeds

class MiscTest(TestCase):

    def test_compat(self):
        from otp.ai.passlib.utils import compat
        self.assertRegex(repr(compat), "^<module 'passlib.utils.compat' from '.*?'>$")
        dir(compat)
        self.assertTrue('UnicodeIO' in dir(compat))
        self.assertTrue('irange' in dir(compat))

    def test_classproperty(self):
        from otp.ai.passlib.utils.decor import classproperty

        class test(object):
            xvar = 1

            @classproperty
            def xprop(cls):
                return cls.xvar

        self.assertEqual(test.xprop, 1)
        prop = test.__dict__['xprop']
        self.assertIs(prop.im_func, prop.__func__)

    def test_deprecated_function(self):
        from otp.ai.passlib.utils.decor import deprecated_function

        @deprecated_function(deprecated='1.6', removed='1.8')
        def test_func(*args):
            return args

        self.assertTrue('.. deprecated::' in test_func.__doc__)
        with self.assertWarningList(dict(category=DeprecationWarning, message='the function passlib.tests.test_utils.test_func() is deprecated as of Passlib 1.6, and will be removed in Passlib 1.8.')):
            self.assertEqual(test_func(1, 2), (1, 2))

    def test_memoized_property(self):
        from otp.ai.passlib.utils.decor import memoized_property

        class dummy(object):
            counter = 0

            @memoized_property
            def value(self):
                value = self.counter
                self.counter = value + 1
                return value

        d = dummy()
        self.assertEqual(d.value, 0)
        self.assertEqual(d.value, 0)
        self.assertEqual(d.counter, 1)
        prop = dummy.value
        if not PY3:
            self.assertIs(prop.im_func, prop.__func__)

    def test_getrandbytes(self):
        from otp.ai.passlib.utils import getrandbytes
        wrapper = partial(getrandbytes, self.getRandom())
        self.assertEqual(len(wrapper(0)), 0)
        a = wrapper(10)
        b = wrapper(10)
        self.assertIsInstance(a, bytes)
        self.assertEqual(len(a), 10)
        self.assertEqual(len(b), 10)
        self.assertNotEqual(a, b)

    @run_with_fixed_seeds(count=1024)
    def test_getrandstr(self, seed):
        from otp.ai.passlib.utils import getrandstr
        wrapper = partial(getrandstr, self.getRandom(seed=seed))
        self.assertEqual(wrapper('abc', 0), '')
        self.assertRaises(ValueError, wrapper, 'abc', -1)
        self.assertRaises(ValueError, wrapper, '', 0)
        self.assertEqual(wrapper('a', 5), 'aaaaa')
        x = wrapper(u('abc'), 32)
        y = wrapper(u('abc'), 32)
        self.assertIsInstance(x, unicode)
        self.assertNotEqual(x, y)
        self.assertEqual(sorted(set(x)), [u('a'), u('b'), u('c')])
        x = wrapper('abc', 32)
        y = wrapper('abc', 32)
        self.assertIsInstance(x, bytes)
        self.assertNotEqual(x, y)
        self.assertEqual(sorted(set(x.decode('ascii'))), [u('a'), u('b'), u('c')])

    def test_generate_password(self):
        from otp.ai.passlib.utils import generate_password
        warnings.filterwarnings('ignore', 'The function.*generate_password\\(\\) is deprecated')
        self.assertEqual(len(generate_password(15)), 15)

    def test_is_crypt_context(self):
        from otp.ai.passlib.utils import is_crypt_context
        from otp.ai.passlib.context import CryptContext
        cc = CryptContext(['des_crypt'])
        self.assertTrue(is_crypt_context(cc))
        self.assertFalse(not is_crypt_context(cc))

    def test_genseed(self):
        import random
        from otp.ai.passlib.utils import genseed
        rng = random.Random(genseed())
        a = rng.randint(0, 10000000000L)
        rng = random.Random(genseed())
        b = rng.randint(0, 10000000000L)
        self.assertNotEqual(a, b)
        rng.seed(genseed(rng))

    def test_crypt(self):
        from otp.ai.passlib.utils import has_crypt, safe_crypt, test_crypt
        if not has_crypt:
            self.assertEqual(safe_crypt('test', 'aa'), None)
            self.assertFalse(test_crypt('test', 'aaqPiZY5xR5l.'))
            raise self.skipTest('crypt.crypt() not available')
        self.assertIsInstance(safe_crypt(u('test'), u('aa')), unicode)
        h1 = u('aaqPiZY5xR5l.')
        self.assertEqual(safe_crypt(u('test'), u('aa')), h1)
        self.assertEqual(safe_crypt('test', 'aa'), h1)
        h2 = u('aahWwbrUsKZk.')
        self.assertEqual(safe_crypt(u('test\\u1234'), 'aa'), h2)
        self.assertEqual(safe_crypt('test\xe1\x88\xb4', 'aa'), h2)
        hash = safe_crypt('test\xff', 'aa')
        if PY3:
            self.assertEqual(hash, None)
        else:
            self.assertEqual(hash, u('aaOx.5nbTU/.M'))
        self.assertRaises(ValueError, safe_crypt, '\x00', 'aa')
        h1x = h1[:-1] + 'x'
        self.assertTrue(test_crypt('test', h1))
        self.assertFalse(test_crypt('test', h1x))
        import otp.ai.passlib.utils as mod
        orig = mod._crypt
        try:
            fake = None
            mod._crypt = lambda secret, hash: fake
            for fake in [None, '', ':', ':0', '*0']:
                self.assertEqual(safe_crypt('test', 'aa'), None)
                self.assertFalse(test_crypt('test', h1))

            fake = 'xxx'
            self.assertEqual(safe_crypt('test', 'aa'), 'xxx')
        finally:
            mod._crypt = orig

        return

    def test_consteq(self):
        from otp.ai.passlib.utils import consteq, str_consteq
        self.assertRaises(TypeError, consteq, u(''), '')
        self.assertRaises(TypeError, consteq, u(''), 1)
        self.assertRaises(TypeError, consteq, u(''), None)
        self.assertRaises(TypeError, consteq, '', u(''))
        self.assertRaises(TypeError, consteq, '', 1)
        self.assertRaises(TypeError, consteq, '', None)
        self.assertRaises(TypeError, consteq, None, u(''))
        self.assertRaises(TypeError, consteq, None, '')
        self.assertRaises(TypeError, consteq, 1, u(''))
        self.assertRaises(TypeError, consteq, 1, '')

        def consteq_supports_string(value):
            return consteq is str_consteq or PY2 or is_ascii_safe(value)

        for value in [
         u('a'),
         u('abc'),
         u('\xff\xa2\x12\x00') * 10]:
            if consteq_supports_string(value):
                self.assertTrue(consteq(value, value), 'value %r:' % (value,))
            else:
                self.assertRaises(TypeError, consteq, value, value)
            self.assertTrue(str_consteq(value, value), 'value %r:' % (value,))
            value = value.encode('latin-1')
            self.assertTrue(consteq(value, value), 'value %r:' % (value,))

        for l, r in [
         (
          u('a'), u('c')),
         (
          u('abcabc'), u('zbaabc')),
         (
          u('abcabc'), u('abzabc')),
         (
          u('abcabc'), u('abcabz')),
         (
          (u('\xff\xa2\x12\x00') * 10)[:-1] + u('\x01'),
          u('\xff\xa2\x12\x00') * 10),
         (
          u(''), u('a')),
         (
          u('abc'), u('abcdef')),
         (
          u('abc'), u('defabc')),
         (
          u('qwertyuiopasdfghjklzxcvbnm'), u('abc'))]:
            if consteq_supports_string(l) and consteq_supports_string(r):
                self.assertFalse(consteq(l, r), 'values %r %r:' % (l, r))
                self.assertFalse(consteq(r, l), 'values %r %r:' % (r, l))
            else:
                self.assertRaises(TypeError, consteq, l, r)
                self.assertRaises(TypeError, consteq, r, l)
            self.assertFalse(str_consteq(l, r), 'values %r %r:' % (l, r))
            self.assertFalse(str_consteq(r, l), 'values %r %r:' % (r, l))
            l = l.encode('latin-1')
            r = r.encode('latin-1')
            self.assertFalse(consteq(l, r), 'values %r %r:' % (l, r))
            self.assertFalse(consteq(r, l), 'values %r %r:' % (r, l))

        return

    def test_saslprep(self):
        self.require_stringprep()
        from otp.ai.passlib.utils import saslprep as sp
        self.assertRaises(TypeError, sp, None)
        self.assertRaises(TypeError, sp, 1)
        self.assertRaises(TypeError, sp, '')
        self.assertEqual(sp(u('')), u(''))
        self.assertEqual(sp(u('\\u00AD')), u(''))
        self.assertEqual(sp(u('$\\u00AD$\\u200D$')), u('$$$'))
        self.assertEqual(sp(u('$ $\\u00A0$\\u3000$')), u('$ $ $ $'))
        self.assertEqual(sp(u('a\\u0300')), u('\\u00E0'))
        self.assertEqual(sp(u('\\u00E0')), u('\\u00E0'))
        self.assertRaises(ValueError, sp, u('\\u0000'))
        self.assertRaises(ValueError, sp, u('\\u007F'))
        self.assertRaises(ValueError, sp, u('\\u180E'))
        self.assertRaises(ValueError, sp, u('\\uFFF9'))
        self.assertRaises(ValueError, sp, u('\\uE000'))
        self.assertRaises(ValueError, sp, u('\\uFDD0'))
        self.assertRaises(ValueError, sp, u('\\uD800'))
        self.assertRaises(ValueError, sp, u('\\uFFFD'))
        self.assertRaises(ValueError, sp, u('\\u2FF0'))
        self.assertRaises(ValueError, sp, u('\\u200E'))
        self.assertRaises(ValueError, sp, u('\\u206F'))
        self.assertRaises(ValueError, sp, u('\\u0900'))
        self.assertRaises(ValueError, sp, u('\\uFFF8'))
        self.assertRaises(ValueError, sp, u('\\U000e0001'))
        self.assertRaises(ValueError, sp, u('\\u0627\\u0031'))
        self.assertEqual(sp(u('\\u0627')), u('\\u0627'))
        self.assertEqual(sp(u('\\u0627\\u0628')), u('\\u0627\\u0628'))
        self.assertEqual(sp(u('\\u0627\\u0031\\u0628')), u('\\u0627\\u0031\\u0628'))
        self.assertRaises(ValueError, sp, u('\\u0627\\u0041\\u0628'))
        self.assertRaises(ValueError, sp, u('x\\u0627z'))
        self.assertEqual(sp(u('x\\u0041z')), u('x\\u0041z'))
        self.assertEqual(sp(u('I\\u00ADX')), u('IX'))
        self.assertEqual(sp(u('user')), u('user'))
        self.assertEqual(sp(u('USER')), u('USER'))
        self.assertEqual(sp(u('\\u00AA')), u('a'))
        self.assertEqual(sp(u('\\u2168')), u('IX'))
        self.assertRaises(ValueError, sp, u('\\u0007'))
        self.assertRaises(ValueError, sp, u('\\u0627\\u0031'))
        self.assertRaises(ValueError, sp, u('\\u0627\\u0031'))
        self.assertEqual(sp(u('\\u0627\\u0031\\u0628')), u('\\u0627\\u0031\\u0628'))
        return

    def test_splitcomma(self):
        from otp.ai.passlib.utils import splitcomma
        self.assertEqual(splitcomma(''), [])
        self.assertEqual(splitcomma(','), [])
        self.assertEqual(splitcomma('a'), ['a'])
        self.assertEqual(splitcomma(' a , '), ['a'])
        self.assertEqual(splitcomma(' a , b'), ['a', 'b'])
        self.assertEqual(splitcomma(' a, b, '), ['a', 'b'])


class CodecTest(TestCase):

    def test_bytes(self):
        if PY3:
            import builtins
            self.assertIs(bytes, builtins.bytes)
        else:
            import __builtin__ as builtins
            self.assertIs(bytes, builtins.str)
        self.assertIsInstance('', bytes)
        self.assertIsInstance('\x00\xff', bytes)
        if PY3:
            self.assertEqual(('\x00\xff').decode('latin-1'), '\x00\xff')
        else:
            self.assertEqual('\x00\xff', '\x00\xff')

    def test_to_bytes(self):
        from otp.ai.passlib.utils import to_bytes
        self.assertEqual(to_bytes(u('abc')), 'abc')
        self.assertEqual(to_bytes(u('\x00\xff')), '\x00\xc3\xbf')
        self.assertEqual(to_bytes(u('\x00\xff'), 'latin-1'), '\x00\xff')
        self.assertRaises(ValueError, to_bytes, u('\x00\xff'), 'ascii')
        self.assertEqual(to_bytes('abc'), 'abc')
        self.assertEqual(to_bytes('\x00\xff'), '\x00\xff')
        self.assertEqual(to_bytes('\x00\xc3\xbf'), '\x00\xc3\xbf')
        self.assertEqual(to_bytes('\x00\xc3\xbf', 'latin-1'), '\x00\xc3\xbf')
        self.assertEqual(to_bytes('\x00\xc3\xbf', 'latin-1', '', 'utf-8'), '\x00\xff')
        self.assertRaises(AssertionError, to_bytes, 'abc', None)
        self.assertRaises(TypeError, to_bytes, None)
        return

    def test_to_unicode(self):
        from otp.ai.passlib.utils import to_unicode
        self.assertEqual(to_unicode(u('abc')), u('abc'))
        self.assertEqual(to_unicode(u('\x00\xff')), u('\x00\xff'))
        self.assertEqual(to_unicode(u('\x00\xff'), 'ascii'), u('\x00\xff'))
        self.assertEqual(to_unicode('abc'), u('abc'))
        self.assertEqual(to_unicode('\x00\xc3\xbf'), u('\x00\xff'))
        self.assertEqual(to_unicode('\x00\xff', 'latin-1'), u('\x00\xff'))
        self.assertRaises(ValueError, to_unicode, '\x00\xff')
        self.assertRaises(AssertionError, to_unicode, 'abc', None)
        self.assertRaises(TypeError, to_unicode, None)
        return

    def test_to_native_str(self):
        from otp.ai.passlib.utils import to_native_str
        self.assertEqual(to_native_str(u('abc'), 'ascii'), 'abc')
        self.assertEqual(to_native_str('abc', 'ascii'), 'abc')
        if PY3:
            self.assertEqual(to_native_str(u('\xe0'), 'ascii'), '\xe0')
            self.assertRaises(UnicodeDecodeError, to_native_str, '\xc3\xa0', 'ascii')
        else:
            self.assertRaises(UnicodeEncodeError, to_native_str, u('\xe0'), 'ascii')
            self.assertEqual(to_native_str('\xc3\xa0', 'ascii'), '\xc3\xa0')
        self.assertEqual(to_native_str(u('\xe0'), 'latin-1'), '\xe0')
        self.assertEqual(to_native_str('\xe0', 'latin-1'), '\xe0')
        self.assertEqual(to_native_str(u('\xe0'), 'utf-8'), '\xe0' if PY3 else '\xc3\xa0')
        self.assertEqual(to_native_str('\xc3\xa0', 'utf-8'), '\xe0' if PY3 else '\xc3\xa0')
        self.assertRaises(TypeError, to_native_str, None, 'ascii')
        return

    def test_is_ascii_safe(self):
        from otp.ai.passlib.utils import is_ascii_safe
        self.assertTrue(is_ascii_safe('\x00abc\x7f'))
        self.assertTrue(is_ascii_safe(u('\x00abc\x7f')))
        self.assertFalse(is_ascii_safe('\x00abc\x80'))
        self.assertFalse(is_ascii_safe(u('\x00abc\x80')))

    def test_is_same_codec(self):
        from otp.ai.passlib.utils import is_same_codec
        self.assertTrue(is_same_codec(None, None))
        self.assertFalse(is_same_codec(None, 'ascii'))
        self.assertTrue(is_same_codec('ascii', 'ascii'))
        self.assertTrue(is_same_codec('ascii', 'ASCII'))
        self.assertTrue(is_same_codec('utf-8', 'utf-8'))
        self.assertTrue(is_same_codec('utf-8', 'utf8'))
        self.assertTrue(is_same_codec('utf-8', 'UTF_8'))
        self.assertFalse(is_same_codec('ascii', 'utf-8'))
        return


class Base64EngineTest(TestCase):

    def test_constructor(self):
        from otp.ai.passlib.utils.binary import Base64Engine, AB64_CHARS
        self.assertRaises(TypeError, Base64Engine, 1)
        self.assertRaises(ValueError, Base64Engine, AB64_CHARS[:-1])
        self.assertRaises(ValueError, Base64Engine, AB64_CHARS[:-1] + 'A')

    def test_ab64_decode(self):
        from otp.ai.passlib.utils.binary import ab64_decode
        self.assertEqual(ab64_decode('abc'), hb('69b7'))
        self.assertEqual(ab64_decode(u('abc')), hb('69b7'))
        self.assertRaises(ValueError, ab64_decode, u('ab\xff'))
        self.assertRaises(TypeError, ab64_decode, 'ab\xff')
        self.assertRaises(TypeError, ab64_decode, 'ab!')
        self.assertRaises(TypeError, ab64_decode, u('ab!'))
        self.assertEqual(ab64_decode('abcd'), hb('69b71d'))
        self.assertRaises(ValueError, ab64_decode, 'abcde')
        self.assertEqual(ab64_decode('abcdef'), hb('69b71d79'))
        self.assertEqual(ab64_decode('abcdeQ'), hb('69b71d79'))
        self.assertEqual(ab64_decode('abcdefg'), hb('69b71d79f8'))
        self.assertEqual(ab64_decode('ab+/'), hb('69bfbf'))
        self.assertEqual(ab64_decode('ab./'), hb('69bfbf'))

    def test_ab64_encode(self):
        from otp.ai.passlib.utils.binary import ab64_encode
        self.assertEqual(ab64_encode(hb('69b7')), 'abc')
        self.assertRaises(TypeError if PY3 else UnicodeEncodeError, ab64_encode, hb('69b7').decode('latin-1'))
        self.assertEqual(ab64_encode(hb('69b71d')), 'abcd')
        self.assertEqual(ab64_encode(hb('69b71d79')), 'abcdeQ')
        self.assertEqual(ab64_encode(hb('69b71d79f8')), 'abcdefg')
        self.assertEqual(ab64_encode(hb('69bfbf')), 'ab./')

    def test_b64s_decode(self):
        from otp.ai.passlib.utils.binary import b64s_decode
        self.assertEqual(b64s_decode('abc'), hb('69b7'))
        self.assertEqual(b64s_decode(u('abc')), hb('69b7'))
        self.assertRaises(ValueError, b64s_decode, u('ab\xff'))
        self.assertRaises(TypeError, b64s_decode, 'ab\xff')
        self.assertRaises(TypeError, b64s_decode, 'ab!')
        self.assertRaises(TypeError, b64s_decode, u('ab!'))
        self.assertEqual(b64s_decode('abcd'), hb('69b71d'))
        self.assertRaises(ValueError, b64s_decode, 'abcde')
        self.assertEqual(b64s_decode('abcdef'), hb('69b71d79'))
        self.assertEqual(b64s_decode('abcdeQ'), hb('69b71d79'))
        self.assertEqual(b64s_decode('abcdefg'), hb('69b71d79f8'))

    def test_b64s_encode(self):
        from otp.ai.passlib.utils.binary import b64s_encode
        self.assertEqual(b64s_encode(hb('69b7')), 'abc')
        self.assertRaises(TypeError if PY3 else UnicodeEncodeError, b64s_encode, hb('69b7').decode('latin-1'))
        self.assertEqual(b64s_encode(hb('69b71d')), 'abcd')
        self.assertEqual(b64s_encode(hb('69b71d79')), 'abcdeQ')
        self.assertEqual(b64s_encode(hb('69b71d79f8')), 'abcdefg')
        self.assertEqual(b64s_encode(hb('69bfbf')), 'ab+/')


class _Base64Test(TestCase):
    engine = None
    encoded_data = None
    encoded_ints = None
    bad_byte = '?'

    def m(self, *offsets):
        return join_bytes(self.engine.bytemap[o:o + 1] for o in offsets)

    def test_encode_bytes(self):
        engine = self.engine
        encode = engine.encode_bytes
        for raw, encoded in self.encoded_data:
            result = encode(raw)
            self.assertEqual(result, encoded, 'encode %r:' % (raw,))

    def test_encode_bytes_bad(self):
        engine = self.engine
        encode = engine.encode_bytes
        self.assertRaises(TypeError, encode, u('\x00'))
        self.assertRaises(TypeError, encode, None)
        return

    def test_decode_bytes(self):
        engine = self.engine
        decode = engine.decode_bytes
        for raw, encoded in self.encoded_data:
            result = decode(encoded)
            self.assertEqual(result, raw, 'decode %r:' % (encoded,))

    def test_decode_bytes_padding(self):
        bchr = (lambda v: bytes([v])) if PY3 else chr
        engine = self.engine
        m = self.m
        decode = engine.decode_bytes
        BNULL = '\x00'
        self.assertEqual(decode(m(0, 0)), BNULL)
        for i in range(0, 6):
            if engine.big:
                correct = BNULL if i < 4 else bchr(1 << i - 4)
            else:
                correct = bchr(1 << i + 6) if i < 2 else BNULL
            self.assertEqual(decode(m(0, 1 << i)), correct, '%d/4 bits:' % i)

        self.assertEqual(decode(m(0, 0, 0)), BNULL * 2)
        for i in range(0, 6):
            if engine.big:
                correct = BNULL if i < 2 else bchr(1 << i - 2)
            else:
                correct = bchr(1 << i + 4) if i < 4 else BNULL
            self.assertEqual(decode(m(0, 0, 1 << i)), BNULL + correct, '%d/2 bits:' % i)

    def test_decode_bytes_bad(self):
        engine = self.engine
        decode = engine.decode_bytes
        self.assertRaises(ValueError, decode, engine.bytemap[:5])
        self.assertTrue(self.bad_byte not in engine.bytemap)
        self.assertRaises(ValueError, decode, self.bad_byte * 4)
        self.assertRaises(TypeError, decode, engine.charmap[:4])
        self.assertRaises(TypeError, decode, None)
        return

    def test_codec(self):
        engine = self.engine
        from otp.ai.passlib.utils import getrandbytes, getrandstr
        rng = self.getRandom()
        saw_zero = False
        for i in irange(500):
            size = rng.randint(1 if saw_zero else 0, 12)
            if not size:
                saw_zero = True
            enc_size = (4 * size + 2) // 3
            raw = getrandbytes(rng, size)
            encoded = engine.encode_bytes(raw)
            self.assertEqual(len(encoded), enc_size)
            result = engine.decode_bytes(encoded)
            self.assertEqual(result, raw)
            if size % 4 == 1:
                size += rng.choice([-1, 1, 2])
            raw_size = 3 * size // 4
            encoded = getrandstr(rng, engine.bytemap, size)
            raw = engine.decode_bytes(encoded)
            self.assertEqual(len(raw), raw_size, 'encoded %d:' % size)
            result = engine.encode_bytes(raw)
            if size % 4:
                self.assertEqual(result[:-1], encoded[:-1])
            else:
                self.assertEqual(result, encoded)

    def test_repair_unused(self):
        from otp.ai.passlib.utils import getrandstr
        rng = self.getRandom()
        engine = self.engine
        check_repair_unused = self.engine.check_repair_unused
        i = 0
        while i < 300:
            size = rng.randint(0, 23)
            cdata = getrandstr(rng, engine.charmap, size).encode('ascii')
            if size & 3 == 1:
                self.assertRaises(ValueError, check_repair_unused, cdata)
                continue
            rdata = engine.encode_bytes(engine.decode_bytes(cdata))
            if rng.random() < 0.5:
                cdata = cdata.decode('ascii')
                rdata = rdata.decode('ascii')
            if cdata == rdata:
                ok, result = check_repair_unused(cdata)
                self.assertFalse(ok)
                self.assertEqual(result, rdata)
            else:
                self.assertNotEqual(size % 4, 0)
                ok, result = check_repair_unused(cdata)
                self.assertTrue(ok)
                self.assertEqual(result, rdata)
            i += 1

    transposed = [
     (
      '3"\x11', '\x11"3', [2, 1, 0]),
     (
      '"3\x11', '\x11"3', [1, 2, 0])]
    transposed_dups = [
     (
      '\x11\x11"', '\x11"3', [0, 0, 1])]

    def test_encode_transposed_bytes(self):
        engine = self.engine
        for result, input, offsets in self.transposed + self.transposed_dups:
            tmp = engine.encode_transposed_bytes(input, offsets)
            out = engine.decode_bytes(tmp)
            self.assertEqual(out, result)

        self.assertRaises(TypeError, engine.encode_transposed_bytes, u('a'), [])

    def test_decode_transposed_bytes(self):
        engine = self.engine
        for input, result, offsets in self.transposed:
            tmp = engine.encode_bytes(input)
            out = engine.decode_transposed_bytes(tmp, offsets)
            self.assertEqual(out, result)

    def test_decode_transposed_bytes_bad(self):
        engine = self.engine
        for input, _, offsets in self.transposed_dups:
            tmp = engine.encode_bytes(input)
            self.assertRaises(TypeError, engine.decode_transposed_bytes, tmp, offsets)

    def check_int_pair(self, bits, encoded_pairs):
        rng = self.getRandom()
        engine = self.engine
        encode = getattr(engine, 'encode_int%s' % bits)
        decode = getattr(engine, 'decode_int%s' % bits)
        pad = -bits % 6
        chars = (bits + pad) // 6
        upper = 1 << bits
        for value, encoded in encoded_pairs:
            result = encode(value)
            self.assertIsInstance(result, bytes)
            self.assertEqual(result, encoded)

        self.assertRaises(ValueError, encode, -1)
        self.assertRaises(ValueError, encode, upper)
        for value, encoded in encoded_pairs:
            self.assertEqual(decode(encoded), value, 'encoded %r:' % (encoded,))

        m = self.m
        self.assertRaises(ValueError, decode, m(0) * (chars + 1))
        self.assertRaises(ValueError, decode, m(0) * (chars - 1))
        self.assertRaises(ValueError, decode, self.bad_byte * chars)
        self.assertRaises(TypeError, decode, engine.charmap[0])
        self.assertRaises(TypeError, decode, None)
        from otp.ai.passlib.utils import getrandstr
        for i in irange(100):
            value = rng.randint(0, upper - 1)
            encoded = encode(value)
            self.assertEqual(len(encoded), chars)
            self.assertEqual(decode(encoded), value)
            encoded = getrandstr(rng, engine.bytemap, chars)
            value = decode(encoded)
            self.assertGreaterEqual(value, 0, 'decode %r out of bounds:' % encoded)
            self.assertLess(value, upper, 'decode %r out of bounds:' % encoded)
            result = encode(value)
            if pad:
                self.assertEqual(result[:-2], encoded[:-2])
            else:
                self.assertEqual(result, encoded)

        return

    def test_int6(self):
        engine = self.engine
        m = self.m
        self.check_int_pair(6, [(0, m(0)), (63, m(63))])

    def test_int12(self):
        engine = self.engine
        m = self.m
        self.check_int_pair(12, [(0, m(0, 0)),
         (
          63, m(0, 63) if engine.big else m(63, 0)), (4095, m(63, 63))])

    def test_int24(self):
        engine = self.engine
        m = self.m
        self.check_int_pair(24, [(0, m(0, 0, 0, 0)),
         (
          63, m(0, 0, 0, 63) if engine.big else m(63, 0, 0, 0)),
         (
          16777215, m(63, 63, 63, 63))])

    def test_int64(self):
        engine = self.engine
        m = self.m
        self.check_int_pair(64, [(0, m(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)),
         (
          63,
          m(0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 60) if engine.big else m(63, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)),
         (
          18446744073709551615L,
          m(63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 60) if engine.big else m(63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 15))])

    def test_encoded_ints(self):
        if not self.encoded_ints:
            raise self.skipTests('none defined for class')
        engine = self.engine
        for data, value, bits in self.encoded_ints:
            encode = getattr(engine, 'encode_int%d' % bits)
            decode = getattr(engine, 'decode_int%d' % bits)
            self.assertEqual(encode(value), data)
            self.assertEqual(decode(data), value)


from otp.ai.passlib.utils.binary import h64, h64big

class H64_Test(_Base64Test):
    engine = h64
    descriptionPrefix = 'h64 codec'
    encoded_data = [
     ('', ''),
     ('U', 'J/'),
     ('U\xaa', 'Jd8'),
     ('U\xaaU', 'JdOJ'),
     ('U\xaaU\xaa', 'JdOJe0'),
     ('U\xaaU\xaaU', 'JdOJeK3'),
     ('U\xaaU\xaaU\xaa', 'JdOJeKZe'),
     ('U\xaaU\xaf', 'JdOJj0'),
     ('U\xaaU\xaa_', 'JdOJey3')]
    encoded_ints = [
     ('z.', 63, 12),
     ('.z', 4032, 12)]


class H64Big_Test(_Base64Test):
    engine = h64big
    descriptionPrefix = 'h64big codec'
    encoded_data = [
     ('', ''),
     ('U', 'JE'),
     ('U\xaa', 'JOc'),
     ('U\xaaU', 'JOdJ'),
     ('U\xaaU\xaa', 'JOdJeU'),
     ('U\xaaU\xaaU', 'JOdJeZI'),
     ('U\xaaU\xaaU\xaa', 'JOdJeZKe'),
     ('U\xaaU\xaf', 'JOdJfk'),
     ('U\xaaU\xaa_', 'JOdJeZw')]
    encoded_ints = [
     ('.z', 63, 12),
     ('z.', 4032, 12)]