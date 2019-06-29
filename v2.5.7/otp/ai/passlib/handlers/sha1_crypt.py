import logging
log = logging.getLogger(__name__)
from otp.ai.passlib.utils import safe_crypt, test_crypt
from otp.ai.passlib.utils.binary import h64
from otp.ai.passlib.utils.compat import u, unicode, irange
from otp.ai.passlib.crypto.digest import compile_hmac
import otp.ai.passlib.utils.handlers as uh
__all__ = []
_BNULL = '\x00'

class sha1_crypt(uh.HasManyBackends, uh.HasRounds, uh.HasSalt, uh.GenericHandler):
    name = 'sha1_crypt'
    setting_kwds = ('salt', 'salt_size', 'rounds')
    ident = u('$sha1$')
    checksum_size = 28
    checksum_chars = uh.HASH64_CHARS
    default_salt_size = 8
    max_salt_size = 64
    salt_chars = uh.HASH64_CHARS
    default_rounds = 480000
    min_rounds = 1
    max_rounds = 4294967295L
    rounds_cost = 'linear'

    @classmethod
    def from_string(cls, hash):
        rounds, salt, chk = uh.parse_mc3(hash, cls.ident, handler=cls)
        return cls(rounds=rounds, salt=salt, checksum=chk)

    def to_string(self, config=False):
        chk = None if config else self.checksum
        return uh.render_mc3(self.ident, self.rounds, self.salt, chk)

    backends = ('os_crypt', 'builtin')

    @classmethod
    def _load_backend_os_crypt(cls):
        if test_crypt('test', '$sha1$1$Wq3GL2Vp$C8U25GvfHS8qGHimExLaiSFlGkAe'):
            cls._set_calc_checksum_backend(cls._calc_checksum_os_crypt)
            return True
        return False

    def _calc_checksum_os_crypt(self, secret):
        config = self.to_string(config=True)
        hash = safe_crypt(secret, config)
        if hash:
            return hash[-28:]
        return self._calc_checksum_builtin(secret)

    @classmethod
    def _load_backend_builtin(cls):
        cls._set_calc_checksum_backend(cls._calc_checksum_builtin)
        return True

    def _calc_checksum_builtin(self, secret):
        if isinstance(secret, unicode):
            secret = secret.encode('utf-8')
        if _BNULL in secret:
            raise uh.exc.NullPasswordError(self)
        rounds = self.rounds
        result = (u('%s$sha1$%s') % (self.salt, rounds)).encode('ascii')
        keyed_hmac = compile_hmac('sha1', secret)
        for _ in irange(rounds):
            result = keyed_hmac(result)

        return h64.encode_transposed_bytes(result, self._chk_offsets).decode('ascii')

    _chk_offsets = [
     2, 1, 0,
     5, 4, 3,
     8, 7, 6,
     11, 10, 9,
     14, 13, 12,
     17, 16, 15,
     0, 19, 18]