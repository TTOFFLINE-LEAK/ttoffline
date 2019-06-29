from __future__ import division
import logging
log = logging.getLogger(__name__)
from otp.ai.passlib.exc import ExpectedTypeError
from otp.ai.passlib.utils.decor import deprecated_function
from otp.ai.passlib.utils.compat import native_string_types
from otp.ai.passlib.crypto.digest import norm_hash_name, lookup_hash, pbkdf1 as _pbkdf1, pbkdf2_hmac, compile_hmac
__all__ = [
 'norm_hash_name',
 'get_prf',
 'pbkdf1',
 'pbkdf2']
from warnings import warn
warn("the module 'passlib.utils.pbkdf2' is deprecated as of Passlib 1.7, and will be removed in Passlib 2.0, please use 'passlib.crypto' instead", DeprecationWarning)
norm_hash_name = deprecated_function(deprecated='1.7', removed='1.8', func_module=__name__, replacement='passlib.crypto.digest.norm_hash_name')(norm_hash_name)
_prf_cache = {}
_HMAC_PREFIXES = ('hmac_', 'hmac-')

def get_prf(name):
    global _prf_cache
    if name in _prf_cache:
        return _prf_cache[name]
    if isinstance(name, native_string_types):
        if not name.startswith(_HMAC_PREFIXES):
            raise ValueError('unknown prf algorithm: %r' % (name,))
        digest = lookup_hash(name[5:]).name

        def hmac(key, msg):
            return compile_hmac(digest, key)(msg)

        record = (hmac, hmac.digest_info.digest_size)
    else:
        if callable(name):
            digest_size = len(name('x', 'y'))
            record = (name, digest_size)
        else:
            raise ExpectedTypeError(name, 'str or callable', 'prf name')
    _prf_cache[name] = record
    return record


def pbkdf1(secret, salt, rounds, keylen=None, hash='sha1'):
    return _pbkdf1(hash, secret, salt, rounds, keylen)


def pbkdf2(secret, salt, rounds, keylen=None, prf='hmac-sha1'):
    if callable(prf) or isinstance(prf, native_string_types) and not prf.startswith(_HMAC_PREFIXES):
        raise NotImplementedError('non-HMAC prfs are not supported as of Passlib 1.7')
    digest = prf[5:]
    return pbkdf2_hmac(digest, secret, salt, rounds, keylen)