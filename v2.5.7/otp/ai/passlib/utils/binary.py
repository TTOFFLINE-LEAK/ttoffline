from __future__ import absolute_import, division, print_function
from base64 import b64encode, b64decode, b32decode as _b32decode, b32encode as _b32encode
from binascii import b2a_base64, a2b_base64, Error as _BinAsciiError
import logging
log = logging.getLogger(__name__)
from otp.ai.passlib import exc
from otp.ai.passlib.utils.compat import PY3, bascii_to_str, irange, imap, iter_byte_chars, join_byte_values, join_byte_elems, nextgetter, suppress_cause, u, unicode, unicode_or_bytes_types
from otp.ai.passlib.utils.decor import memoized_property
__all__ = [
 'BASE64_CHARS', 'PADDED_BASE64_CHARS',
 'AB64_CHARS',
 'HASH64_CHARS',
 'BCRYPT_CHARS',
 'HEX_CHARS', 'LOWER_HEX_CHARS', 'UPPER_HEX_CHARS',
 'ALL_BYTE_VALUES',
 'compile_byte_translation',
 'ab64_encode', 'ab64_decode',
 'b64s_encode', 'b64s_decode',
 'b32encode', 'b32decode',
 'Base64Engine',
 'LazyBase64Engine',
 'h64',
 'h64big',
 'bcrypt64']
BASE64_CHARS = u('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/')
AB64_CHARS = u('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789./')
HASH64_CHARS = u('./0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz')
BCRYPT_CHARS = u('./ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789')
PADDED_BASE64_CHARS = BASE64_CHARS + u('=')
HEX_CHARS = u('0123456789abcdefABCDEF')
UPPER_HEX_CHARS = u('0123456789ABCDEF')
LOWER_HEX_CHARS = u('0123456789abcdef')
ALL_BYTE_VALUES = join_byte_values(irange(256))
B_EMPTY = ''
B_NULL = '\x00'
B_EQUAL = '='
_TRANSLATE_SOURCE = list(iter_byte_chars(ALL_BYTE_VALUES))

def compile_byte_translation(mapping, source=None):
    if source is None:
        target = _TRANSLATE_SOURCE[:]
    else:
        target = list(iter_byte_chars(source))
    for k, v in mapping.items():
        if isinstance(k, unicode_or_bytes_types):
            k = ord(k)
        if isinstance(v, unicode):
            v = v.encode('ascii')
        target[k] = v

    return B_EMPTY.join(target)


def b64s_encode(data):
    return b2a_base64(data).rstrip(_BASE64_STRIP)


def b64s_decode(data):
    if isinstance(data, unicode):
        try:
            data = data.encode('ascii')
        except UnicodeEncodeError:
            raise suppress_cause(ValueError('string argument should contain only ASCII characters'))

    off = len(data) & 3
    if off == 0:
        pass
    else:
        if off == 2:
            data += _BASE64_PAD2
        else:
            if off == 3:
                data += _BASE64_PAD1
            else:
                raise ValueError('invalid base64 input')
    try:
        return a2b_base64(data)
    except _BinAsciiError as err:
        raise suppress_cause(TypeError(err))


_BASE64_STRIP = '=\n'
_BASE64_PAD1 = '='
_BASE64_PAD2 = '=='

def ab64_encode(data):
    return b64s_encode(data).replace('+', '.')


def ab64_decode(data):
    if isinstance(data, unicode):
        try:
            data = data.encode('ascii')
        except UnicodeEncodeError:
            raise suppress_cause(ValueError('string argument should contain only ASCII characters'))

    return b64s_decode(data.replace('.', '+'))


def b32encode(source):
    return bascii_to_str(_b32encode(source).rstrip(B_EQUAL))


_b32_translate = compile_byte_translation({'8': 'B', '0': 'O'})
_b32_decode_pad = B_EQUAL * 8

def b32decode(source):
    if isinstance(source, unicode):
        source = source.encode('ascii')
    source = source.translate(_b32_translate)
    remainder = len(source) & 7
    if remainder:
        source += _b32_decode_pad[:-remainder]
    return _b32decode(source, True)


class Base64Engine(object):
    bytemap = None
    big = None
    _encode64 = None
    _decode64 = None
    _encode_bytes = None
    _decode_bytes = None

    def __init__(self, charmap, big=False):
        if isinstance(charmap, unicode):
            charmap = charmap.encode('latin-1')
        else:
            if not isinstance(charmap, bytes):
                raise exc.ExpectedStringError(charmap, 'charmap')
        if len(charmap) != 64:
            raise ValueError('charmap must be 64 characters in length')
        if len(set(charmap)) != 64:
            raise ValueError('charmap must not contain duplicate characters')
        self.bytemap = charmap
        self._encode64 = charmap.__getitem__
        lookup = dict((value, idx) for idx, value in enumerate(charmap))
        self._decode64 = lookup.__getitem__
        self.big = big
        if big:
            self._encode_bytes = self._encode_bytes_big
            self._decode_bytes = self._decode_bytes_big
        else:
            self._encode_bytes = self._encode_bytes_little
            self._decode_bytes = self._decode_bytes_little

    @property
    def charmap(self):
        return self.bytemap.decode('latin-1')

    def encode_bytes(self, source):
        if not isinstance(source, bytes):
            raise TypeError('source must be bytes, not %s' % (type(source),))
        chunks, tail = divmod(len(source), 3)
        if PY3:
            next_value = nextgetter(iter(source))
        else:
            next_value = nextgetter(ord(elem) for elem in source)
        gen = self._encode_bytes(next_value, chunks, tail)
        out = join_byte_elems(imap(self._encode64, gen))
        return out

    def _encode_bytes_little(self, next_value, chunks, tail):
        idx = 0
        while idx < chunks:
            v1 = next_value()
            v2 = next_value()
            v3 = next_value()
            yield v1 & 63
            yield (v2 & 15) << 2 | v1 >> 6
            yield (v3 & 3) << 4 | v2 >> 4
            yield v3 >> 2
            idx += 1

        if tail:
            v1 = next_value()
            if tail == 1:
                yield v1 & 63
                yield v1 >> 6
            else:
                v2 = next_value()
                yield v1 & 63
                yield (v2 & 15) << 2 | v1 >> 6
                yield v2 >> 4

    def _encode_bytes_big(self, next_value, chunks, tail):
        idx = 0
        while idx < chunks:
            v1 = next_value()
            v2 = next_value()
            v3 = next_value()
            yield v1 >> 2
            yield (v1 & 3) << 4 | v2 >> 4
            yield (v2 & 15) << 2 | v3 >> 6
            yield v3 & 63
            idx += 1

        if tail:
            v1 = next_value()
            if tail == 1:
                yield v1 >> 2
                yield (v1 & 3) << 4
            else:
                v2 = next_value()
                yield v1 >> 2
                yield (v1 & 3) << 4 | v2 >> 4
                yield (v2 & 15) << 2

    def decode_bytes(self, source):
        if not isinstance(source, bytes):
            raise TypeError('source must be bytes, not %s' % (type(source),))
        chunks, tail = divmod(len(source), 4)
        if tail == 1:
            raise ValueError('input string length cannot be == 1 mod 4')
        next_value = nextgetter(imap(self._decode64, source))
        try:
            return join_byte_values(self._decode_bytes(next_value, chunks, tail))
        except KeyError as err:
            raise ValueError('invalid character: %r' % (err.args[0],))

    def _decode_bytes_little(self, next_value, chunks, tail):
        idx = 0
        while idx < chunks:
            v1 = next_value()
            v2 = next_value()
            v3 = next_value()
            v4 = next_value()
            yield v1 | (v2 & 3) << 6
            yield v2 >> 2 | (v3 & 15) << 4
            yield v3 >> 4 | v4 << 2
            idx += 1

        if tail:
            v1 = next_value()
            v2 = next_value()
            yield v1 | (v2 & 3) << 6
            if tail == 3:
                v3 = next_value()
                yield v2 >> 2 | (v3 & 15) << 4

    def _decode_bytes_big(self, next_value, chunks, tail):
        idx = 0
        while idx < chunks:
            v1 = next_value()
            v2 = next_value()
            v3 = next_value()
            v4 = next_value()
            yield v1 << 2 | v2 >> 4
            yield (v2 & 15) << 4 | v3 >> 2
            yield (v3 & 3) << 6 | v4
            idx += 1

        if tail:
            v1 = next_value()
            v2 = next_value()
            yield v1 << 2 | v2 >> 4
            if tail == 3:
                v3 = next_value()
                yield (v2 & 15) << 4 | v3 >> 2

    def __make_padset(self, bits):
        pset = set(c for i, c in enumerate(self.bytemap) if not i & bits)
        pset.update(c for i, c in enumerate(self.charmap) if not i & bits)
        return frozenset(pset)

    @memoized_property
    def _padinfo2(self):
        bits = 15 if self.big else 60
        return (
         ~bits, self.__make_padset(bits))

    @memoized_property
    def _padinfo3(self):
        bits = 3 if self.big else 48
        return (
         ~bits, self.__make_padset(bits))

    def check_repair_unused(self, source):
        tail = len(source) & 3
        if tail == 2:
            mask, padset = self._padinfo2
        else:
            if tail == 3:
                mask, padset = self._padinfo3
            else:
                if not tail:
                    return (False, source)
                raise ValueError('source length must != 1 mod 4')
        last = source[(-1)]
        if last in padset:
            return (False, source)
        if isinstance(source, unicode):
            cm = self.charmap
            last = cm[(cm.index(last) & mask)]
        else:
            last = self._encode64(self._decode64(last) & mask)
            if PY3:
                last = bytes([last])
        return (
         True, source[:-1] + last)

    def repair_unused(self, source):
        return self.check_repair_unused(source)[1]

    def encode_transposed_bytes(self, source, offsets):
        if not isinstance(source, bytes):
            raise TypeError('source must be bytes, not %s' % (type(source),))
        tmp = join_byte_elems(source[off] for off in offsets)
        return self.encode_bytes(tmp)

    def decode_transposed_bytes(self, source, offsets):
        tmp = self.decode_bytes(source)
        buf = [None] * len(offsets)
        for off, char in zip(offsets, tmp):
            buf[off] = char

        return join_byte_elems(buf)

    def _decode_int(self, source, bits):
        if not isinstance(source, bytes):
            raise TypeError('source must be bytes, not %s' % (type(source),))
        big = self.big
        pad = -bits % 6
        chars = (bits + pad) / 6
        if len(source) != chars:
            raise ValueError('source must be %d chars' % (chars,))
        decode = self._decode64
        out = 0
        try:
            for c in source if big else reversed(source):
                out = (out << 6) + decode(c)

        except KeyError:
            raise ValueError('invalid character in string: %r' % (c,))

        if pad:
            if big:
                out >>= pad
            else:
                out &= (1 << bits) - 1
        return out

    def decode_int6(self, source):
        if not isinstance(source, bytes):
            raise TypeError('source must be bytes, not %s' % (type(source),))
        if len(source) != 1:
            raise ValueError('source must be exactly 1 byte')
        if PY3:
            source = source[0]
        try:
            return self._decode64(source)
        except KeyError:
            raise ValueError('invalid character')

    def decode_int12(self, source):
        if not isinstance(source, bytes):
            raise TypeError('source must be bytes, not %s' % (type(source),))
        if len(source) != 2:
            raise ValueError('source must be exactly 2 bytes')
        decode = self._decode64
        try:
            if self.big:
                return decode(source[1]) + (decode(source[0]) << 6)
            return decode(source[0]) + (decode(source[1]) << 6)
        except KeyError:
            raise ValueError('invalid character')

    def decode_int24(self, source):
        if not isinstance(source, bytes):
            raise TypeError('source must be bytes, not %s' % (type(source),))
        if len(source) != 4:
            raise ValueError('source must be exactly 4 bytes')
        decode = self._decode64
        try:
            if self.big:
                return decode(source[3]) + (decode(source[2]) << 6) + (decode(source[1]) << 12) + (decode(source[0]) << 18)
            return decode(source[0]) + (decode(source[1]) << 6) + (decode(source[2]) << 12) + (decode(source[3]) << 18)
        except KeyError:
            raise ValueError('invalid character')

    def decode_int30(self, source):
        return self._decode_int(source, 30)

    def decode_int64(self, source):
        return self._decode_int(source, 64)

    def _encode_int(self, value, bits):
        pad = -bits % 6
        bits += pad
        if self.big:
            itr = irange(bits - 6, -6, -6)
            value <<= pad
        else:
            itr = irange(0, bits, 6)
        return join_byte_elems(imap(self._encode64, (value >> off & 63 for off in itr)))

    def encode_int6(self, value):
        if value < 0 or value > 63:
            raise ValueError('value out of range')
        if PY3:
            return self.bytemap[value:value + 1]
        return self._encode64(value)

    def encode_int12(self, value):
        if value < 0 or value > 4095:
            raise ValueError('value out of range')
        raw = [
         value & 63, value >> 6 & 63]
        if self.big:
            raw = reversed(raw)
        return join_byte_elems(imap(self._encode64, raw))

    def encode_int24(self, value):
        if value < 0 or value > 16777215:
            raise ValueError('value out of range')
        raw = [
         value & 63, value >> 6 & 63,
         value >> 12 & 63, value >> 18 & 63]
        if self.big:
            raw = reversed(raw)
        return join_byte_elems(imap(self._encode64, raw))

    def encode_int30(self, value):
        if value < 0 or value > 1073741823:
            raise ValueError('value out of range')
        return self._encode_int(value, 30)

    def encode_int64(self, value):
        if value < 0 or value > 18446744073709551615L:
            raise ValueError('value out of range')
        return self._encode_int(value, 64)


class LazyBase64Engine(Base64Engine):
    _lazy_opts = None

    def __init__(self, *args, **kwds):
        self._lazy_opts = (
         args, kwds)

    def _lazy_init(self):
        args, kwds = self._lazy_opts
        super(LazyBase64Engine, self).__init__(*args, **kwds)
        del self._lazy_opts
        self.__class__ = Base64Engine

    def __getattribute__(self, attr):
        if not attr.startswith('_'):
            self._lazy_init()
        return object.__getattribute__(self, attr)


h64 = LazyBase64Engine(HASH64_CHARS)
h64big = LazyBase64Engine(HASH64_CHARS, big=True)
bcrypt64 = LazyBase64Engine(BCRYPT_CHARS, big=True)