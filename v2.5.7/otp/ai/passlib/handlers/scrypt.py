from __future__ import with_statement, absolute_import
import logging
log = logging.getLogger(__name__)
from otp.ai.passlib.crypto import scrypt as _scrypt
from otp.ai.passlib.utils import h64, to_bytes
from otp.ai.passlib.utils.binary import h64, b64s_decode, b64s_encode
from otp.ai.passlib.utils.compat import u, bascii_to_str, suppress_cause
from otp.ai.passlib.utils.decor import classproperty
import otp.ai.passlib.utils.handlers as uh
__all__ = [
 'scrypt']
IDENT_SCRYPT = u('$scrypt$')
IDENT_7 = u('$7$')
_UDOLLAR = u('$')

class scrypt(uh.ParallelismMixin, uh.HasRounds, uh.HasRawSalt, uh.HasRawChecksum, uh.HasManyIdents, uh.GenericHandler):
    name = 'scrypt'
    setting_kwds = ('ident', 'salt', 'salt_size', 'rounds', 'block_size', 'parallelism')
    checksum_size = 32
    default_ident = IDENT_SCRYPT
    ident_values = (IDENT_SCRYPT, IDENT_7)
    default_salt_size = 16
    max_salt_size = 1024
    default_rounds = 16
    min_rounds = 1
    max_rounds = 31
    rounds_cost = 'log2'
    parallelism = 1
    block_size = 8

    @classmethod
    def using(cls, block_size=None, **kwds):
        subcls = super(scrypt, cls).using(**kwds)
        if block_size is not None:
            if isinstance(block_size, uh.native_string_types):
                block_size = int(block_size)
            subcls.block_size = subcls._norm_block_size(block_size, relaxed=kwds.get('relaxed'))
        try:
            _scrypt.validate(1 << cls.default_rounds, cls.block_size, cls.parallelism)
        except ValueError as err:
            raise suppress_cause(ValueError('scrypt: invalid settings combination: ' + str(err)))

        return subcls

    @classmethod
    def from_string(cls, hash):
        return cls(**cls.parse(hash))

    @classmethod
    def parse(cls, hash):
        ident, suffix = cls._parse_ident(hash)
        func = getattr(cls, '_parse_%s_string' % ident.strip(_UDOLLAR), None)
        if func:
            return func(suffix)
        raise uh.exc.InvalidHashError(cls)
        return

    @classmethod
    def _parse_scrypt_string(cls, suffix):
        parts = suffix.split('$')
        if len(parts) == 3:
            params, salt, digest = parts
        else:
            if len(parts) == 2:
                params, salt = parts
                digest = None
            else:
                raise uh.exc.MalformedHashError(cls, 'malformed hash')
        parts = params.split(',')
        if len(parts) == 3:
            nstr, bstr, pstr = parts
        else:
            raise uh.exc.MalformedHashError(cls, 'malformed settings field')
        return dict(ident=IDENT_SCRYPT, rounds=int(nstr[3:]), block_size=int(bstr[2:]), parallelism=int(pstr[2:]), salt=b64s_decode(salt.encode('ascii')), checksum=b64s_decode(digest.encode('ascii')) if digest else None)

    @classmethod
    def _parse_7_string(cls, suffix):
        parts = suffix.encode('ascii').split('$')
        if len(parts) == 2:
            params, digest = parts
        else:
            if len(parts) == 1:
                params, = parts
                digest = None
            else:
                raise uh.exc.MalformedHashError()
        if len(params) < 11:
            raise uh.exc.MalformedHashError(cls, 'params field too short')
        return dict(ident=IDENT_7, rounds=h64.decode_int6(params[:1]), block_size=h64.decode_int30(params[1:6]), parallelism=h64.decode_int30(params[6:11]), salt=params[11:], checksum=h64.decode_bytes(digest) if digest else None)

    def to_string(self):
        ident = self.ident
        if ident == IDENT_SCRYPT:
            return '$scrypt$ln=%d,r=%d,p=%d$%s$%s' % (
             self.rounds,
             self.block_size,
             self.parallelism,
             bascii_to_str(b64s_encode(self.salt)),
             bascii_to_str(b64s_encode(self.checksum)))
        salt = self.salt
        try:
            salt.decode('ascii')
        except UnicodeDecodeError:
            raise suppress_cause(NotImplementedError('scrypt $7$ hashes dont support non-ascii salts'))

        return bascii_to_str(('').join([
         '$7$',
         h64.encode_int6(self.rounds),
         h64.encode_int30(self.block_size),
         h64.encode_int30(self.parallelism),
         self.salt,
         '$',
         h64.encode_bytes(self.checksum)]))

    def __init__(self, block_size=None, **kwds):
        super(scrypt, self).__init__(**kwds)
        if block_size is None:
            pass
        else:
            self.block_size = self._norm_block_size(block_size)
        return

    @classmethod
    def _norm_block_size(cls, block_size, relaxed=False):
        return uh.norm_integer(cls, block_size, min=1, param='block_size', relaxed=relaxed)

    def _generate_salt(self):
        salt = super(scrypt, self)._generate_salt()
        if self.ident == IDENT_7:
            salt = b64s_encode(salt)
        return salt

    @classproperty
    def backends(cls):
        return _scrypt.backend_values

    @classmethod
    def get_backend(cls):
        return _scrypt.backend

    @classmethod
    def has_backend(cls, name='any'):
        try:
            cls.set_backend(name, dryrun=True)
            return True
        except uh.exc.MissingBackendError:
            return False

    @classmethod
    def set_backend(cls, name='any', dryrun=False):
        _scrypt._set_backend(name, dryrun=dryrun)

    def _calc_checksum(self, secret):
        secret = to_bytes(secret, param='secret')
        return _scrypt.scrypt(secret, self.salt, n=1 << self.rounds, r=self.block_size, p=self.parallelism, keylen=self.checksum_size)

    def _calc_needs_update(self, **kwds):
        if self.block_size != type(self).block_size:
            return True
        return super(scrypt, self)._calc_needs_update(**kwds)