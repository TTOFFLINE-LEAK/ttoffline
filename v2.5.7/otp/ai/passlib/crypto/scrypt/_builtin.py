import operator, struct
from otp.ai.passlib.utils.compat import izip
from otp.ai.passlib.crypto.digest import pbkdf2_hmac
from otp.ai.passlib.crypto.scrypt._salsa import salsa20
__all__ = [
 'ScryptEngine']

class ScryptEngine(object):
    n = 0
    r = 0
    p = 0
    smix_bytes = 0
    iv_bytes = 0
    bmix_len = 0
    bmix_half_len = 0
    bmix_struct = None
    integerify = None

    @classmethod
    def execute(cls, secret, salt, n, r, p, keylen):
        return cls(n, r, p).run(secret, salt, keylen)

    def __init__(self, n, r, p):
        self.n = n
        self.r = r
        self.p = p
        self.smix_bytes = r << 7
        self.iv_bytes = self.smix_bytes * p
        self.bmix_len = bmix_len = r << 5
        self.bmix_half_len = r << 4
        self.bmix_struct = struct.Struct('<' + str(bmix_len) + 'I')
        if r == 1:
            self.bmix = self._bmix_1
        if n <= 4294967295L:
            integerify = operator.itemgetter(-16)
        else:
            ig1 = operator.itemgetter(-16)
            ig2 = operator.itemgetter(-17)

            def integerify(X):
                return ig1(X) | ig2(X) << 32

        self.integerify = integerify

    def run(self, secret, salt, keylen):
        iv_bytes = self.iv_bytes
        input = pbkdf2_hmac('sha256', secret, salt, rounds=1, keylen=iv_bytes)
        smix = self.smix
        if self.p == 1:
            output = smix(input)
        else:
            smix_bytes = self.smix_bytes
            output = ('').join(smix(input[offset:offset + smix_bytes]) for offset in range(0, iv_bytes, smix_bytes))
        return pbkdf2_hmac('sha256', secret, output, rounds=1, keylen=keylen)

    def smix(self, input):
        bmix = self.bmix
        bmix_struct = self.bmix_struct
        integerify = self.integerify
        n = self.n
        buffer = list(bmix_struct.unpack(input))

        def vgen():
            i = 0
            while i < n:
                last = tuple(buffer)
                yield last
                bmix(last, buffer)
                i += 1

        V = list(vgen())
        get_v_elem = V.__getitem__
        n_mask = n - 1
        i = 0
        while i < n:
            j = integerify(buffer) & n_mask
            result = tuple(a ^ b for a, b in izip(buffer, get_v_elem(j)))
            bmix(result, buffer)
            i += 1

        return bmix_struct.pack(*buffer)

    def bmix(self, source, target):
        half = self.bmix_half_len
        tmp = source[-16:]
        siter = iter(source)
        j = 0
        while j < half:
            jn = j + 16
            target[j:jn] = tmp = salsa20(a ^ b for a, b in izip(tmp, siter))
            target[(half + j):(half + jn)] = tmp = salsa20(a ^ b for a, b in izip(tmp, siter))
            j = jn

    def _bmix_1(self, source, target):
        B = source[16:]
        target[:16] = tmp = salsa20(a ^ b for a, b in izip(B, iter(source)))
        target[16:] = salsa20(a ^ b for a, b in izip(tmp, B))