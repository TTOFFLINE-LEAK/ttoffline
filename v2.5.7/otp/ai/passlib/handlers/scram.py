import logging
log = logging.getLogger(__name__)
from otp.ai.passlib.utils import consteq, saslprep, to_native_str, splitcomma
from otp.ai.passlib.utils.binary import ab64_decode, ab64_encode
from otp.ai.passlib.utils.compat import bascii_to_str, iteritems, u, native_string_types
from otp.ai.passlib.crypto.digest import pbkdf2_hmac, norm_hash_name
import otp.ai.passlib.utils.handlers as uh
__all__ = [
 'scram']

class scram(uh.HasRounds, uh.HasRawSalt, uh.HasRawChecksum, uh.GenericHandler):
    name = 'scram'
    setting_kwds = ('salt', 'salt_size', 'rounds', 'algs')
    ident = u('$scram$')
    default_salt_size = 12
    max_salt_size = 1024
    default_rounds = 100000
    min_rounds = 1
    max_rounds = 4294967295L
    rounds_cost = 'linear'
    default_algs = [
     'sha-1', 'sha-256', 'sha-512']
    _verify_algs = [
     'sha-256', 'sha-512', 'sha-224', 'sha-384', 'sha-1']
    algs = None

    @classmethod
    def extract_digest_info(cls, hash, alg):
        alg = norm_hash_name(alg, 'iana')
        self = cls.from_string(hash)
        chkmap = self.checksum
        if not chkmap:
            raise ValueError('scram hash contains no digests')
        return (self.salt, self.rounds, chkmap[alg])

    @classmethod
    def extract_digest_algs(cls, hash, format='iana'):
        algs = cls.from_string(hash).algs
        if format == 'iana':
            return algs
        return [ norm_hash_name(alg, format) for alg in algs ]

    @classmethod
    def derive_digest(cls, password, salt, rounds, alg):
        if isinstance(password, bytes):
            password = password.decode('utf-8')
        return pbkdf2_hmac(alg, saslprep(password), salt, rounds)

    @classmethod
    def from_string(cls, hash):
        hash = to_native_str(hash, 'ascii', 'hash')
        if not hash.startswith('$scram$'):
            raise uh.exc.InvalidHashError(cls)
        parts = hash[7:].split('$')
        if len(parts) != 3:
            raise uh.exc.MalformedHashError(cls)
        rounds_str, salt_str, chk_str = parts
        rounds = int(rounds_str)
        if rounds_str != str(rounds):
            raise uh.exc.MalformedHashError(cls)
        try:
            salt = ab64_decode(salt_str.encode('ascii'))
        except TypeError:
            raise uh.exc.MalformedHashError(cls)

        if not chk_str:
            raise uh.exc.MalformedHashError(cls)
        else:
            if '=' in chk_str:
                algs = None
                chkmap = {}
                for pair in chk_str.split(','):
                    alg, digest = pair.split('=')
                    try:
                        chkmap[alg] = ab64_decode(digest.encode('ascii'))
                    except TypeError:
                        raise uh.exc.MalformedHashError(cls)

            else:
                algs = chk_str
                chkmap = None
        return cls(rounds=rounds, salt=salt, checksum=chkmap, algs=algs)

    def to_string(self):
        salt = bascii_to_str(ab64_encode(self.salt))
        chkmap = self.checksum
        chk_str = (',').join('%s=%s' % (alg, bascii_to_str(ab64_encode(chkmap[alg]))) for alg in self.algs)
        return '$scram$%d$%s$%s' % (self.rounds, salt, chk_str)

    @classmethod
    def using(cls, default_algs=None, algs=None, **kwds):
        if algs is not None:
            default_algs = algs
        subcls = super(scram, cls).using(**kwds)
        if default_algs is not None:
            subcls.default_algs = cls._norm_algs(default_algs)
        return subcls

    def __init__(self, algs=None, **kwds):
        super(scram, self).__init__(**kwds)
        digest_map = self.checksum
        if algs is not None:
            if digest_map is not None:
                raise RuntimeError('checksum & algs kwds are mutually exclusive')
            algs = self._norm_algs(algs)
        else:
            if digest_map is not None:
                algs = self._norm_algs(digest_map.keys())
            else:
                if self.use_defaults:
                    algs = list(self.default_algs)
                else:
                    raise TypeError('no algs list specified')
        self.algs = algs
        return

    def _norm_checksum(self, checksum, relaxed=False):
        if not isinstance(checksum, dict):
            raise uh.exc.ExpectedTypeError(checksum, 'dict', 'checksum')
        for alg, digest in iteritems(checksum):
            if alg != norm_hash_name(alg, 'iana'):
                raise ValueError('malformed algorithm name in scram hash: %r' % (
                 alg,))
            if len(alg) > 9:
                raise ValueError('SCRAM limits algorithm names to 9 characters: %r' % (
                 alg,))
            if not isinstance(digest, bytes):
                raise uh.exc.ExpectedTypeError(digest, 'raw bytes', 'digests')

        if 'sha-1' not in checksum:
            raise ValueError('sha-1 must be in algorithm list of scram hash')
        return checksum

    @classmethod
    def _norm_algs(cls, algs):
        if isinstance(algs, native_string_types):
            algs = splitcomma(algs)
        algs = sorted(norm_hash_name(alg, 'iana') for alg in algs)
        if any(len(alg) > 9 for alg in algs):
            raise ValueError('SCRAM limits alg names to max of 9 characters')
        if 'sha-1' not in algs:
            raise ValueError('sha-1 must be in algorithm list of scram hash')
        return algs

    def _calc_needs_update(self, **kwds):
        if not set(self.algs).issuperset(self.default_algs):
            return True
        return super(scram, self)._calc_needs_update(**kwds)

    def _calc_checksum(self, secret, alg=None):
        rounds = self.rounds
        salt = self.salt
        hash = self.derive_digest
        if alg:
            return hash(secret, salt, rounds, alg)
        return dict((alg, hash(secret, salt, rounds, alg)) for alg in self.algs)

    @classmethod
    def verify(cls, secret, hash, full=False):
        uh.validate_secret(secret)
        self = cls.from_string(hash)
        chkmap = self.checksum
        if not chkmap:
            raise ValueError('expected %s hash, got %s config string instead' % (
             cls.name, cls.name))
        if full:
            correct = failed = False
            for alg, digest in iteritems(chkmap):
                other = self._calc_checksum(secret, alg)
                if len(digest) != len(other):
                    raise ValueError('mis-sized %s digest in scram hash: %r != %r' % (
                     alg, len(digest), len(other)))
                if consteq(other, digest):
                    correct = True
                else:
                    failed = True

            if correct and failed:
                raise ValueError('scram hash verified inconsistently, may be corrupted')
            else:
                return correct
        else:
            for alg in self._verify_algs:
                if alg in chkmap:
                    other = self._calc_checksum(secret, alg)
                    return consteq(other, chkmap[alg])

            raise AssertionError('sha-1 digest not found!')