from binascii import hexlify
import struct
from otp.ai.passlib.utils.compat import bascii_to_str, irange, PY3
__all__ = [
 'md4']

def F(x, y, z):
    return x & y | ~x & z


def G(x, y, z):
    return x & y | x & z | y & z


MASK_32 = 4294967295L

class md4(object):
    name = 'md4'
    digest_size = digestsize = 16
    block_size = 64
    _count = 0
    _state = None
    _buf = None

    def __init__(self, content=None):
        self._count = 0
        self._state = [1732584193, 4023233417L, 2562383102L, 271733878]
        self._buf = ''
        if content:
            self.update(content)

    _round1 = [
     [
      0, 1, 2, 3, 0, 3],
     [
      3, 0, 1, 2, 1, 7],
     [
      2, 3, 0, 1, 2, 11],
     [
      1, 2, 3, 0, 3, 19],
     [
      0, 1, 2, 3, 4, 3],
     [
      3, 0, 1, 2, 5, 7],
     [
      2, 3, 0, 1, 6, 11],
     [
      1, 2, 3, 0, 7, 19],
     [
      0, 1, 2, 3, 8, 3],
     [
      3, 0, 1, 2, 9, 7],
     [
      2, 3, 0, 1, 10, 11],
     [
      1, 2, 3, 0, 11, 19],
     [
      0, 1, 2, 3, 12, 3],
     [
      3, 0, 1, 2, 13, 7],
     [
      2, 3, 0, 1, 14, 11],
     [
      1, 2, 3, 0, 15, 19]]
    _round2 = [
     [
      0, 1, 2, 3, 0, 3],
     [
      3, 0, 1, 2, 4, 5],
     [
      2, 3, 0, 1, 8, 9],
     [
      1, 2, 3, 0, 12, 13],
     [
      0, 1, 2, 3, 1, 3],
     [
      3, 0, 1, 2, 5, 5],
     [
      2, 3, 0, 1, 9, 9],
     [
      1, 2, 3, 0, 13, 13],
     [
      0, 1, 2, 3, 2, 3],
     [
      3, 0, 1, 2, 6, 5],
     [
      2, 3, 0, 1, 10, 9],
     [
      1, 2, 3, 0, 14, 13],
     [
      0, 1, 2, 3, 3, 3],
     [
      3, 0, 1, 2, 7, 5],
     [
      2, 3, 0, 1, 11, 9],
     [
      1, 2, 3, 0, 15, 13]]
    _round3 = [
     [
      0, 1, 2, 3, 0, 3],
     [
      3, 0, 1, 2, 8, 9],
     [
      2, 3, 0, 1, 4, 11],
     [
      1, 2, 3, 0, 12, 15],
     [
      0, 1, 2, 3, 2, 3],
     [
      3, 0, 1, 2, 10, 9],
     [
      2, 3, 0, 1, 6, 11],
     [
      1, 2, 3, 0, 14, 15],
     [
      0, 1, 2, 3, 1, 3],
     [
      3, 0, 1, 2, 9, 9],
     [
      2, 3, 0, 1, 5, 11],
     [
      1, 2, 3, 0, 13, 15],
     [
      0, 1, 2, 3, 3, 3],
     [
      3, 0, 1, 2, 11, 9],
     [
      2, 3, 0, 1, 7, 11],
     [
      1, 2, 3, 0, 15, 15]]

    def _process(self, block):
        X = struct.unpack('<16I', block)
        orig = self._state
        state = list(orig)
        for a, b, c, d, k, s in self._round1:
            t = state[a] + F(state[b], state[c], state[d]) + X[k] & MASK_32
            state[a] = (t << s & MASK_32) + (t >> 32 - s)

        for a, b, c, d, k, s in self._round2:
            t = state[a] + G(state[b], state[c], state[d]) + X[k] + 1518500249 & MASK_32
            state[a] = (t << s & MASK_32) + (t >> 32 - s)

        for a, b, c, d, k, s in self._round3:
            t = state[a] + (state[b] ^ state[c] ^ state[d]) + X[k] + 1859775393 & MASK_32
            state[a] = (t << s & MASK_32) + (t >> 32 - s)

        for i in irange(4):
            orig[i] = orig[i] + state[i] & MASK_32

    def update(self, content):
        if not isinstance(content, bytes):
            if PY3:
                raise TypeError('expected bytes')
            else:
                content = content.encode('ascii')
        buf = self._buf
        if buf:
            content = buf + content
        idx = 0
        end = len(content)
        while True:
            next = idx + 64
            if next <= end:
                self._process(content[idx:next])
                self._count += 1
                idx = next
            else:
                self._buf = content[idx:]
                return

    def copy(self):
        other = md4()
        other._count = self._count
        other._state = list(self._state)
        other._buf = self._buf
        return other

    def digest(self):
        orig = list(self._state)
        buf = self._buf
        msglen = self._count * 512 + len(buf) * 8
        block = buf + '\x80' + '\x00' * ((119 - len(buf)) % 64) + struct.pack('<2I', msglen & MASK_32, msglen >> 32 & MASK_32)
        if len(block) == 128:
            self._process(block[:64])
            self._process(block[64:])
        else:
            self._process(block)
        out = struct.pack('<4I', *self._state)
        self._state = orig
        return out

    def hexdigest(self):
        return bascii_to_str(hexlify(self.digest()))