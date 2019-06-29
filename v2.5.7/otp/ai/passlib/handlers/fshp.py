from base64 import b64encode, b64decode
import re, logging
log = logging.getLogger(__name__)
from otp.ai.passlib.utils import to_unicode
import otp.ai.passlib.utils.handlers as uh
from otp.ai.passlib.utils.compat import bascii_to_str, iteritems, u, unicode
from otp.ai.passlib.crypto.digest import pbkdf1
__all__ = [
 'fshp']

class fshp(uh.HasRounds, uh.HasRawSalt, uh.HasRawChecksum, uh.GenericHandler):
    name = 'fshp'
    setting_kwds = ('salt', 'salt_size', 'rounds', 'variant')
    checksum_chars = uh.PADDED_BASE64_CHARS
    ident = u('{FSHP')
    default_salt_size = 16
    max_salt_size = None
    default_rounds = 480000
    min_rounds = 1
    max_rounds = 4294967295L
    rounds_cost = 'linear'
    default_variant = 1
    _variant_info = {0: ('sha1', 20), 
       1: ('sha256', 32), 
       2: ('sha384', 48), 
       3: ('sha512', 64)}
    _variant_aliases = dict([ (unicode(k), k) for k in _variant_info ] + [ (v[0], k) for k, v in iteritems(_variant_info) ])

    @classmethod
    def using(cls, variant=None, **kwds):
        subcls = super(fshp, cls).using(**kwds)
        if variant is not None:
            subcls.default_variant = cls._norm_variant(variant)
        return subcls

    variant = None

    def __init__(self, variant=None, **kwds):
        self.use_defaults = kwds.get('use_defaults')
        if variant is not None:
            variant = self._norm_variant(variant)
        else:
            if self.use_defaults:
                variant = self.default_variant
            else:
                raise TypeError('no variant specified')
        self.variant = variant
        super(fshp, self).__init__(**kwds)
        return

    @classmethod
    def _norm_variant(cls, variant):
        if isinstance(variant, bytes):
            variant = variant.decode('ascii')
        if isinstance(variant, unicode):
            try:
                variant = cls._variant_aliases[variant]
            except KeyError:
                raise ValueError('invalid fshp variant')

        if not isinstance(variant, int):
            raise TypeError('fshp variant must be int or known alias')
        if variant not in cls._variant_info:
            raise ValueError('invalid fshp variant')
        return variant

    @property
    def checksum_alg(self):
        return self._variant_info[self.variant][0]

    @property
    def checksum_size(self):
        return self._variant_info[self.variant][1]

    _hash_regex = re.compile(u('\n            ^\n            \\{FSHP\n            (\\d+)\\| # variant\n            (\\d+)\\| # salt size\n            (\\d+)\\} # rounds\n            ([a-zA-Z0-9+/]+={0,3}) # digest\n            $'), re.X)

    @classmethod
    def from_string(cls, hash):
        hash = to_unicode(hash, 'ascii', 'hash')
        m = cls._hash_regex.match(hash)
        if not m:
            raise uh.exc.InvalidHashError(cls)
        variant, salt_size, rounds, data = m.group(1, 2, 3, 4)
        variant = int(variant)
        salt_size = int(salt_size)
        rounds = int(rounds)
        try:
            data = b64decode(data.encode('ascii'))
        except TypeError:
            raise uh.exc.MalformedHashError(cls)

        salt = data[:salt_size]
        chk = data[salt_size:]
        return cls(salt=salt, checksum=chk, rounds=rounds, variant=variant)

    def to_string(self):
        chk = self.checksum
        salt = self.salt
        data = bascii_to_str(b64encode(salt + chk))
        return '{FSHP%d|%d|%d}%s' % (self.variant, len(salt), self.rounds, data)

    def _calc_checksum(self, secret):
        if isinstance(secret, unicode):
            secret = secret.encode('utf-8')
        return pbkdf1(digest=self.checksum_alg, secret=self.salt, salt=secret, rounds=self.rounds, keylen=self.checksum_size)