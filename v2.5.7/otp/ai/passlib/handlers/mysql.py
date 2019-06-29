from hashlib import sha1
import re, logging
log = logging.getLogger(__name__)
from warnings import warn
from otp.ai.passlib.utils import to_native_str
from otp.ai.passlib.utils.compat import bascii_to_str, unicode, u, byte_elem_value, str_to_uascii
import otp.ai.passlib.utils.handlers as uh
__all__ = [
 'mysql323',
 'mysq41']

class mysql323(uh.StaticHandler):
    name = 'mysql323'
    checksum_size = 16
    checksum_chars = uh.HEX_CHARS

    @classmethod
    def _norm_hash(cls, hash):
        return hash.lower()

    def _calc_checksum(self, secret):
        if isinstance(secret, unicode):
            secret = secret.encode('utf-8')
        MASK_32 = 4294967295L
        MASK_31 = 2147483647
        WHITE = ' \t'
        nr1 = 1345345333
        nr2 = 305419889
        add = 7
        for c in secret:
            if c in WHITE:
                continue
            tmp = byte_elem_value(c)
            nr1 ^= ((nr1 & 63) + add) * tmp + (nr1 << 8) & MASK_32
            nr2 = nr2 + (nr2 << 8 ^ nr1) & MASK_32
            add = add + tmp & MASK_32

        return u('%08x%08x') % (nr1 & MASK_31, nr2 & MASK_31)


class mysql41(uh.StaticHandler):
    name = 'mysql41'
    _hash_prefix = u('*')
    checksum_chars = uh.HEX_CHARS
    checksum_size = 40

    @classmethod
    def _norm_hash(cls, hash):
        return hash.upper()

    def _calc_checksum(self, secret):
        if isinstance(secret, unicode):
            secret = secret.encode('utf-8')
        return str_to_uascii(sha1(sha1(secret).digest()).hexdigest()).upper()