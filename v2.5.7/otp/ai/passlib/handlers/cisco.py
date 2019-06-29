from binascii import hexlify, unhexlify
from hashlib import md5
import logging
log = logging.getLogger(__name__)
from warnings import warn
from otp.ai.passlib.utils import right_pad_string, to_unicode, repeat_string, to_bytes
from otp.ai.passlib.utils.binary import h64
from otp.ai.passlib.utils.compat import unicode, u, join_byte_values, join_byte_elems, iter_byte_values, uascii_to_str
import otp.ai.passlib.utils.handlers as uh
__all__ = [
 'cisco_pix',
 'cisco_asa',
 'cisco_type7']
_DUMMY_BYTES = '\xff' * 32

class cisco_pix(uh.HasUserContext, uh.StaticHandler):
    name = 'cisco_pix'
    truncate_size = 16
    truncate_error = True
    truncate_verify_reject = True
    checksum_size = 16
    checksum_chars = uh.HASH64_CHARS
    _is_asa = False

    def _calc_checksum(self, secret):
        asa = self._is_asa
        if isinstance(secret, unicode):
            secret = secret.encode('utf-8')
        spoil_digest = None
        if len(secret) > self.truncate_size:
            if self.use_defaults:
                msg = 'Password too long (%s allows at most %d bytes)' % (
                 self.name, self.truncate_size)
                raise uh.exc.PasswordSizeError(self.truncate_size, msg=msg)
            else:
                spoil_digest = secret + _DUMMY_BYTES
        user = self.user
        if user:
            if isinstance(user, unicode):
                user = user.encode('utf-8')
            if not asa or len(secret) < 28:
                secret += repeat_string(user, 4)
        if asa and len(secret) > 16:
            pad_size = 32
        else:
            pad_size = 16
        secret = right_pad_string(secret, pad_size)
        if spoil_digest:
            secret += spoil_digest
        digest = md5(secret).digest()
        digest = join_byte_elems(c for i, c in enumerate(digest) if i + 1 & 3)
        return h64.encode_bytes(digest).decode('ascii')


class cisco_asa(cisco_pix):
    name = 'cisco_asa'
    truncate_size = 32
    _is_asa = True


class cisco_type7(uh.GenericHandler):
    name = 'cisco_type7'
    setting_kwds = ('salt', )
    checksum_chars = uh.UPPER_HEX_CHARS
    min_salt_value = 0
    max_salt_value = 52

    @classmethod
    def using(cls, salt=None, **kwds):
        subcls = super(cisco_type7, cls).using(**kwds)
        if salt is not None:
            salt = subcls._norm_salt(salt, relaxed=kwds.get('relaxed'))
            subcls._generate_salt = staticmethod(lambda : salt)
        return subcls

    @classmethod
    def from_string(cls, hash):
        hash = to_unicode(hash, 'ascii', 'hash')
        if len(hash) < 2:
            raise uh.exc.InvalidHashError(cls)
        salt = int(hash[:2])
        return cls(salt=salt, checksum=hash[2:].upper())

    def __init__(self, salt=None, **kwds):
        super(cisco_type7, self).__init__(**kwds)
        if salt is not None:
            salt = self._norm_salt(salt)
        else:
            if self.use_defaults:
                salt = self._generate_salt()
            else:
                raise TypeError('no salt specified')
        self.salt = salt
        return

    @classmethod
    def _norm_salt(cls, salt, relaxed=False):
        if not isinstance(salt, int):
            raise uh.exc.ExpectedTypeError(salt, 'integer', 'salt')
        if 0 <= salt <= cls.max_salt_value:
            return salt
        msg = 'salt/offset must be in 0..52 range'
        if relaxed:
            warn(msg, uh.PasslibHashWarning)
            if salt < 0:
                return 0
            return cls.max_salt_value
        raise ValueError(msg)

    @staticmethod
    def _generate_salt():
        return uh.rng.randint(0, 15)

    def to_string(self):
        return '%02d%s' % (self.salt, uascii_to_str(self.checksum))

    def _calc_checksum(self, secret):
        if isinstance(secret, unicode):
            secret = secret.encode('utf-8')
        return hexlify(self._cipher(secret, self.salt)).decode('ascii').upper()

    @classmethod
    def decode(cls, hash, encoding='utf-8'):
        self = cls.from_string(hash)
        tmp = unhexlify(self.checksum.encode('ascii'))
        raw = self._cipher(tmp, self.salt)
        if encoding:
            return raw.decode(encoding)
        return raw

    _key = u('dsfd;kfoA,.iyewrkldJKDHSUBsgvca69834ncxv9873254k;fg87')

    @classmethod
    def _cipher(cls, data, salt):
        key = cls._key
        key_size = len(key)
        return join_byte_values(value ^ ord(key[((salt + idx) % key_size)]) for idx, value in enumerate(iter_byte_values(data)))