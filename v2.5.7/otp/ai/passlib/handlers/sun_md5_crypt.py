from hashlib import md5
import re, logging
log = logging.getLogger(__name__)
from warnings import warn
from otp.ai.passlib.utils import to_unicode
from otp.ai.passlib.utils.binary import h64
from otp.ai.passlib.utils.compat import byte_elem_value, irange, u, uascii_to_str, unicode, str_to_bascii
import otp.ai.passlib.utils.handlers as uh
__all__ = [
 'sun_md5_crypt']
MAGIC_HAMLET = "To be, or not to be,--that is the question:--\nWhether 'tis nobler in the mind to suffer\nThe slings and arrows of outrageous fortune\nOr to take arms against a sea of troubles,\nAnd by opposing end them?--To die,--to sleep,--\nNo more; and by a sleep to say we end\nThe heartache, and the thousand natural shocks\nThat flesh is heir to,--'tis a consummation\nDevoutly to be wish'd. To die,--to sleep;--\nTo sleep! perchance to dream:--ay, there's the rub;\nFor in that sleep of death what dreams may come,\nWhen we have shuffled off this mortal coil,\nMust give us pause: there's the respect\nThat makes calamity of so long life;\nFor who would bear the whips and scorns of time,\nThe oppressor's wrong, the proud man's contumely,\nThe pangs of despis'd love, the law's delay,\nThe insolence of office, and the spurns\nThat patient merit of the unworthy takes,\nWhen he himself might his quietus make\nWith a bare bodkin? who would these fardels bear,\nTo grunt and sweat under a weary life,\nBut that the dread of something after death,--\nThe undiscover'd country, from whose bourn\nNo traveller returns,--puzzles the will,\nAnd makes us rather bear those ills we have\nThan fly to others that we know not of?\nThus conscience does make cowards of us all;\nAnd thus the native hue of resolution\nIs sicklied o'er with the pale cast of thought;\nAnd enterprises of great pith and moment,\nWith this regard, their currents turn awry,\nAnd lose the name of action.--Soft you now!\nThe fair Ophelia!--Nymph, in thy orisons\nBe all my sins remember'd.\n\x00"
xr = irange(7)
_XY_ROUNDS = [
 tuple((i, i, i + 3) for i in xr),
 tuple((i, i + 1, i + 4) for i in xr),
 tuple((i, i + 8, i + 11 & 15) for i in xr),
 tuple((i, i + 9 & 15, i + 12 & 15) for i in xr)]
del xr

def raw_sun_md5_crypt(secret, rounds, salt):
    global MAGIC_HAMLET
    if rounds <= 0:
        rounds = 0
    real_rounds = 4096 + rounds
    result = md5(secret + salt).digest()
    X_ROUNDS_0, X_ROUNDS_1, Y_ROUNDS_0, Y_ROUNDS_1 = _XY_ROUNDS
    round = 0
    while round < real_rounds:
        rval = [ byte_elem_value(c) for c in result ].__getitem__
        x = 0
        xrounds = X_ROUNDS_1 if rval(round >> 3 & 15) >> (round & 7) & 1 else X_ROUNDS_0
        for i, ia, ib in xrounds:
            a = rval(ia)
            b = rval(ib)
            v = rval(a >> b % 5 & 15) >> (b >> (a & 7) & 1)
            x |= (rval(v >> 3 & 15) >> (v & 7) & 1) << i

        y = 0
        yrounds = Y_ROUNDS_1 if rval(round + 64 >> 3 & 15) >> (round & 7) & 1 else Y_ROUNDS_0
        for i, ia, ib in yrounds:
            a = rval(ia)
            b = rval(ib)
            v = rval(a >> b % 5 & 15) >> (b >> (a & 7) & 1)
            y |= (rval(v >> 3 & 15) >> (v & 7) & 1) << i

        coin = (rval(x >> 3) >> (x & 7) ^ rval(y >> 3) >> (y & 7)) & 1
        h = md5(result)
        if coin:
            h.update(MAGIC_HAMLET)
        h.update(unicode(round).encode('ascii'))
        result = h.digest()
        round += 1

    return h64.encode_transposed_bytes(result, _chk_offsets)


_chk_offsets = (12, 6, 0, 13, 7, 1, 14, 8, 2, 15, 9, 3, 5, 10, 4, 11)

class sun_md5_crypt(uh.HasRounds, uh.HasSalt, uh.GenericHandler):
    name = 'sun_md5_crypt'
    setting_kwds = ('salt', 'rounds', 'bare_salt', 'salt_size')
    checksum_chars = uh.HASH64_CHARS
    checksum_size = 22
    default_salt_size = 8
    max_salt_size = None
    salt_chars = uh.HASH64_CHARS
    default_rounds = 34000
    min_rounds = 0
    max_rounds = 4294963199L
    rounds_cost = 'linear'
    ident_values = (
     u('$md5$'), u('$md5,'))
    bare_salt = False

    def __init__(self, bare_salt=False, **kwds):
        self.bare_salt = bare_salt
        super(sun_md5_crypt, self).__init__(**kwds)

    @classmethod
    def identify(cls, hash):
        hash = uh.to_unicode_for_identify(hash)
        return hash.startswith(cls.ident_values)

    @classmethod
    def from_string(cls, hash):
        hash = to_unicode(hash, 'ascii', 'hash')
        if hash.startswith(u('$md5$')):
            rounds = 0
            salt_idx = 5
        else:
            if hash.startswith(u('$md5,rounds=')):
                idx = hash.find(u('$'), 12)
                if idx == -1:
                    raise uh.exc.MalformedHashError(cls, 'unexpected end of rounds')
                rstr = hash[12:idx]
                try:
                    rounds = int(rstr)
                except ValueError:
                    raise uh.exc.MalformedHashError(cls, 'bad rounds')

                if rstr != unicode(rounds):
                    raise uh.exc.ZeroPaddedRoundsError(cls)
                if rounds == 0:
                    raise uh.exc.MalformedHashError(cls, 'explicit zero rounds')
                salt_idx = idx + 1
            else:
                raise uh.exc.InvalidHashError(cls)
        chk_idx = hash.rfind(u('$'), salt_idx)
        if chk_idx == -1:
            salt = hash[salt_idx:]
            chk = None
            bare_salt = True
        else:
            if chk_idx == len(hash) - 1:
                if chk_idx > salt_idx and hash[(-2)] == u('$'):
                    raise uh.exc.MalformedHashError(cls, "too many '$' separators")
                salt = hash[salt_idx:-1]
                chk = None
                bare_salt = False
            else:
                if chk_idx > 0 and hash[(chk_idx - 1)] == u('$'):
                    salt = hash[salt_idx:chk_idx - 1]
                    chk = hash[chk_idx + 1:]
                    bare_salt = False
                else:
                    salt = hash[salt_idx:chk_idx]
                    chk = hash[chk_idx + 1:]
                    bare_salt = True
        return cls(rounds=rounds, salt=salt, checksum=chk, bare_salt=bare_salt)

    def to_string(self, _withchk=True):
        ss = u('') if self.bare_salt else u('$')
        rounds = self.rounds
        if rounds > 0:
            hash = u('$md5,rounds=%d$%s%s') % (rounds, self.salt, ss)
        else:
            hash = u('$md5$%s%s') % (self.salt, ss)
        if _withchk:
            chk = self.checksum
            hash = u('%s$%s') % (hash, chk)
        return uascii_to_str(hash)

    def _calc_checksum(self, secret):
        if isinstance(secret, unicode):
            secret = secret.encode('utf-8')
        config = str_to_bascii(self.to_string(_withchk=False))
        return raw_sun_md5_crypt(secret, self.rounds, config).decode('ascii')