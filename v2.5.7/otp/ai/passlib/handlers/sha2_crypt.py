import hashlib, logging
log = logging.getLogger(__name__)
from otp.ai.passlib.utils import safe_crypt, test_crypt, repeat_string, to_unicode
from otp.ai.passlib.utils.binary import h64
from otp.ai.passlib.utils.compat import byte_elem_value, u, uascii_to_str, unicode
import otp.ai.passlib.utils.handlers as uh
__all__ = [
 'sha512_crypt',
 'sha256_crypt']
_BNULL = '\x00'
_c_digest_offsets = (
 (0, 3), (5, 1), (5, 3), (1, 2), (5, 1), (5, 3), (1, 3),
 (4, 1), (5, 3), (1, 3), (5, 0), (5, 3), (1, 3), (5, 1),
 (4, 3), (1, 3), (5, 1), (5, 2), (1, 3), (5, 1), (5, 3))
_256_transpose_map = (20, 10, 0, 11, 1, 21, 2, 22, 12, 23, 13, 3, 14, 4, 24, 5, 25,
                      15, 26, 16, 6, 17, 7, 27, 8, 28, 18, 29, 19, 9, 30, 31)
_512_transpose_map = (42, 21, 0, 1, 43, 22, 23, 2, 44, 45, 24, 3, 4, 46, 25, 26, 5,
                      47, 48, 27, 6, 7, 49, 28, 29, 8, 50, 51, 30, 9, 10, 52, 31,
                      32, 11, 53, 54, 33, 12, 13, 55, 34, 35, 14, 56, 57, 36, 15,
                      16, 58, 37, 38, 17, 59, 60, 39, 18, 19, 61, 40, 41, 20, 62,
                      63)

def _raw_sha2_crypt(pwd, salt, rounds, use_512=False):
    if isinstance(pwd, unicode):
        pwd = pwd.encode('utf-8')
    if _BNULL in pwd:
        raise uh.exc.NullPasswordError(sha512_crypt if use_512 else sha256_crypt)
    pwd_len = len(pwd)
    salt = salt.encode('ascii')
    salt_len = len(salt)
    if use_512:
        hash_const = hashlib.sha512
        transpose_map = _512_transpose_map
    else:
        hash_const = hashlib.sha256
        transpose_map = _256_transpose_map
    db = hash_const(pwd + salt + pwd).digest()
    a_ctx = hash_const(pwd + salt)
    a_ctx_update = a_ctx.update
    a_ctx_update(repeat_string(db, pwd_len))
    i = pwd_len
    while i:
        a_ctx_update(db if i & 1 else pwd)
        i >>= 1

    da = a_ctx.digest()
    if pwd_len < 96:
        dp = repeat_string(hash_const(pwd * pwd_len).digest(), pwd_len)
    else:
        tmp_ctx = hash_const(pwd)
        tmp_ctx_update = tmp_ctx.update
        i = pwd_len - 1
        while i:
            tmp_ctx_update(pwd)
            i -= 1

        dp = repeat_string(tmp_ctx.digest(), pwd_len)
    ds = hash_const(salt * (16 + byte_elem_value(da[0]))).digest()[:salt_len]
    dp_dp = dp + dp
    dp_ds = dp + ds
    perms = [dp, dp_dp, dp_ds, dp_ds + dp, ds + dp, ds + dp_dp]
    data = [ (perms[even], perms[odd]) for even, odd in _c_digest_offsets ]
    dc = da
    blocks, tail = divmod(rounds, 42)
    while blocks:
        for even, odd in data:
            dc = hash_const(odd + hash_const(dc + even).digest()).digest()

        blocks -= 1

    if tail:
        pairs = tail >> 1
        for even, odd in data[:pairs]:
            dc = hash_const(odd + hash_const(dc + even).digest()).digest()

        if tail & 1:
            dc = hash_const(dc + data[pairs][0]).digest()
    return h64.encode_transposed_bytes(dc, transpose_map).decode('ascii')


_UROUNDS = u('rounds=')
_UDOLLAR = u('$')
_UZERO = u('0')

class _SHA2_Common(uh.HasManyBackends, uh.HasRounds, uh.HasSalt, uh.GenericHandler):
    setting_kwds = ('salt', 'rounds', 'implicit_rounds', 'salt_size')
    checksum_chars = uh.HASH64_CHARS
    max_salt_size = 16
    salt_chars = uh.HASH64_CHARS
    min_rounds = 1000
    max_rounds = 999999999
    rounds_cost = 'linear'
    _cdb_use_512 = False
    _rounds_prefix = None
    implicit_rounds = False

    def __init__(self, implicit_rounds=None, **kwds):
        super(_SHA2_Common, self).__init__(**kwds)
        if implicit_rounds is None:
            implicit_rounds = self.use_defaults and self.rounds == 5000
        self.implicit_rounds = implicit_rounds
        return

    def _parse_salt(self, salt):
        return self._norm_salt(salt, relaxed=self.checksum is None)

    def _parse_rounds(self, rounds):
        return self._norm_rounds(rounds, relaxed=self.checksum is None)

    @classmethod
    def from_string(cls, hash):
        hash = to_unicode(hash, 'ascii', 'hash')
        ident = cls.ident
        if not hash.startswith(ident):
            raise uh.exc.InvalidHashError(cls)
        parts = hash[3:].split(_UDOLLAR)
        if parts[0].startswith(_UROUNDS):
            rounds = parts.pop(0)[7:]
            if rounds.startswith(_UZERO) and rounds != _UZERO:
                raise uh.exc.ZeroPaddedRoundsError(cls)
            rounds = int(rounds)
            implicit_rounds = False
        else:
            rounds = 5000
            implicit_rounds = True
        if len(parts) == 2:
            salt, chk = parts
        else:
            if len(parts) == 1:
                salt = parts[0]
                chk = None
            else:
                raise uh.exc.MalformedHashError(cls)
        return cls(rounds=rounds, salt=salt, checksum=chk or None, implicit_rounds=implicit_rounds)

    def to_string(self):
        if self.rounds == 5000 and self.implicit_rounds:
            hash = u('%s%s$%s') % (self.ident, self.salt,
             self.checksum or u(''))
        else:
            hash = u('%srounds=%d$%s$%s') % (self.ident, self.rounds,
             self.salt, self.checksum or u(''))
        return uascii_to_str(hash)

    backends = ('os_crypt', 'builtin')
    _test_hash = None

    @classmethod
    def _load_backend_os_crypt(cls):
        if test_crypt(*cls._test_hash):
            cls._set_calc_checksum_backend(cls._calc_checksum_os_crypt)
            return True
        return False

    def _calc_checksum_os_crypt(self, secret):
        hash = safe_crypt(secret, self.to_string())
        if hash:
            cs = self.checksum_size
            return hash[-cs:]
        return self._calc_checksum_builtin(secret)

    @classmethod
    def _load_backend_builtin(cls):
        cls._set_calc_checksum_backend(cls._calc_checksum_builtin)
        return True

    def _calc_checksum_builtin(self, secret):
        return _raw_sha2_crypt(secret, self.salt, self.rounds, self._cdb_use_512)


class sha256_crypt(_SHA2_Common):
    name = 'sha256_crypt'
    ident = u('$5$')
    checksum_size = 43
    default_rounds = 535000
    _test_hash = ('test', '$5$rounds=1000$test$QmQADEXMG8POI5WDsaeho0P36yK3Tcrgboabng6bkb/')


class sha512_crypt(_SHA2_Common):
    name = 'sha512_crypt'
    ident = u('$6$')
    checksum_size = 86
    _cdb_use_512 = True
    default_rounds = 656000
    _test_hash = ('test', '$6$rounds=1000$test$2M/Lx6MtobqjLjobw0Wmo4Q5OFx5nVLJvmgseatA6oMnyWeBdRDx4DU.1H3eGmse6pgsOgDisWBGI5c7TZauS0')