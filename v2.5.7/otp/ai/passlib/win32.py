from warnings import warn
warn("the 'passlib.win32' module is deprecated, and will be removed in passlib 1.8; please use the 'passlib.hash.nthash' and 'passlib.hash.lmhash' classes instead.", DeprecationWarning)
from binascii import hexlify
from otp.ai.passlib.utils.compat import unicode
from otp.ai.passlib.crypto.des import des_encrypt_block
from otp.ai.passlib.hash import nthash
__all__ = [
 'nthash',
 'raw_lmhash',
 'raw_nthash']
LM_MAGIC = 'KGS!@#$%'
raw_nthash = nthash.raw_nthash

def raw_lmhash(secret, encoding='ascii', hex=False):
    if isinstance(secret, unicode):
        secret = secret.encode(encoding)
    ns = secret.upper()[:14] + '\x00' * (14 - len(secret))
    out = des_encrypt_block(ns[:7], LM_MAGIC) + des_encrypt_block(ns[7:], LM_MAGIC)
    if hex:
        return hexlify(out).decode('ascii')
    return out