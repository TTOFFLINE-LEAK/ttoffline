from hashlib import md5
import logging
log = logging.getLogger(__name__)
from otp.ai.passlib.utils import safe_crypt, test_crypt, repeat_string
from otp.ai.passlib.utils.binary import h64
from otp.ai.passlib.utils.compat import unicode, u
import otp.ai.passlib.utils.handlers as uh
__all__ = [
 'md5_crypt',
 'apr_md5_crypt']
_BNULL = '\x00'
_MD5_MAGIC = '$1$'
_APR_MAGIC = '$apr1$'
_c_digest_offsets = (
 (0, 3), (5, 1), (5, 3), (1, 2), (5, 1), (5, 3), (1, 3),
 (4, 1), (5, 3), (1, 3), (5, 0), (5, 3), (1, 3), (5, 1),
 (4, 3), (1, 3), (5, 1), (5, 2), (1, 3), (5, 1), (5, 3))
_transpose_map = (12, 6, 0, 13, 7, 1, 14, 8, 2, 15, 9, 3, 5, 10, 4, 11)

def _raw_md5_crypt(pwd, salt, use_apr=False):
    if isinstance(pwd, unicode):
        pwd = pwd.encode('utf-8')
    if _BNULL in pwd:
        raise uh.exc.NullPasswordError(md5_crypt)
    pwd_len = len(pwd)
    salt = salt.encode('ascii')
    if use_apr:
        magic = _APR_MAGIC
    else:
        magic = _MD5_MAGIC
    db = md5(pwd + salt + pwd).digest()
    a_ctx = md5(pwd + magic + salt)
    a_ctx_update = a_ctx.update
    a_ctx_update(repeat_string(db, pwd_len))
    i = pwd_len
    evenchar = pwd[:1]
    while i:
        a_ctx_update(_BNULL if i & 1 else evenchar)
        i >>= 1

    da = a_ctx.digest()
    pwd_pwd = pwd + pwd
    pwd_salt = pwd + salt
    perms = [pwd, pwd_pwd, pwd_salt, pwd_salt + pwd, salt + pwd, salt + pwd_pwd]
    data = [ (perms[even], perms[odd]) for even, odd in _c_digest_offsets ]
    dc = da
    blocks = 23
    while blocks:
        for even, odd in data:
            dc = md5(odd + md5(dc + even).digest()).digest()

        blocks -= 1

    for even, odd in data[:17]:
        dc = md5(odd + md5(dc + even).digest()).digest()

    return h64.encode_transposed_bytes(dc, _transpose_map).decode('ascii')


class _MD5_Common(uh.HasSalt, uh.GenericHandler):
    setting_kwds = ('salt', 'salt_size')
    checksum_size = 22
    checksum_chars = uh.HASH64_CHARS
    max_salt_size = 8
    salt_chars = uh.HASH64_CHARS

    @classmethod
    def from_string(cls, hash):
        salt, chk = uh.parse_mc2(hash, cls.ident, handler=cls)
        return cls(salt=salt, checksum=chk)

    def to_string(self):
        return uh.render_mc2(self.ident, self.salt, self.checksum)


class md5_crypt(uh.HasManyBackends, _MD5_Common):
    name = 'md5_crypt'
    ident = u('$1$')
    backends = ('os_crypt', 'builtin')

    @classmethod
    def _load_backend_os_crypt(cls):
        if test_crypt('test', '$1$test$pi/xDtU5WFVRqYS6BMU8X/'):
            cls._set_calc_checksum_backend(cls._calc_checksum_os_crypt)
            return True
        return False

    def _calc_checksum_os_crypt(self, secret):
        config = self.ident + self.salt
        hash = safe_crypt(secret, config)
        if hash:
            return hash[-22:]
        return self._calc_checksum_builtin(secret)

    @classmethod
    def _load_backend_builtin(cls):
        cls._set_calc_checksum_backend(cls._calc_checksum_builtin)
        return True

    def _calc_checksum_builtin(self, secret):
        return _raw_md5_crypt(secret, self.salt)


class apr_md5_crypt(_MD5_Common):
    name = 'apr_md5_crypt'
    ident = u('$apr1$')

    def _calc_checksum(self, secret):
        return _raw_md5_crypt(secret, self.salt, use_apr=True)