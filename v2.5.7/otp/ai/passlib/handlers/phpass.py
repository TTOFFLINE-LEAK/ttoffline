from hashlib import md5
import logging
log = logging.getLogger(__name__)
from otp.ai.passlib.utils.binary import h64
from otp.ai.passlib.utils.compat import u, uascii_to_str, unicode
import otp.ai.passlib.utils.handlers as uh
__all__ = [
 'phpass']

class phpass(uh.HasManyIdents, uh.HasRounds, uh.HasSalt, uh.GenericHandler):
    name = 'phpass'
    setting_kwds = ('salt', 'rounds', 'ident')
    checksum_chars = uh.HASH64_CHARS
    min_salt_size = max_salt_size = 8
    salt_chars = uh.HASH64_CHARS
    default_rounds = 19
    min_rounds = 7
    max_rounds = 30
    rounds_cost = 'log2'
    default_ident = u('$P$')
    ident_values = (u('$P$'), u('$H$'))
    ident_aliases = {u('P'): u('$P$'), u('H'): u('$H$')}

    @classmethod
    def from_string(cls, hash):
        ident, data = cls._parse_ident(hash)
        rounds, salt, chk = data[0], data[1:9], data[9:]
        return cls(ident=ident, rounds=h64.decode_int6(rounds.encode('ascii')), salt=salt, checksum=chk or None)

    def to_string(self):
        hash = u('%s%s%s%s') % (self.ident,
         h64.encode_int6(self.rounds).decode('ascii'),
         self.salt,
         self.checksum or u(''))
        return uascii_to_str(hash)

    def _calc_checksum(self, secret):
        if isinstance(secret, unicode):
            secret = secret.encode('utf-8')
        real_rounds = 1 << self.rounds
        result = md5(self.salt.encode('ascii') + secret).digest()
        r = 0
        while r < real_rounds:
            result = md5(result + secret).digest()
            r += 1

        return h64.encode_bytes(result).decode('ascii')