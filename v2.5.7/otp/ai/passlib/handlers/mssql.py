from binascii import hexlify, unhexlify
from hashlib import sha1
import re, logging
log = logging.getLogger(__name__)
from warnings import warn
from otp.ai.passlib.utils import consteq
from otp.ai.passlib.utils.compat import bascii_to_str, unicode, u
import otp.ai.passlib.utils.handlers as uh
__all__ = [
 'mssql2000',
 'mssql2005']

def _raw_mssql(secret, salt):
    return sha1(secret.encode('utf-16-le') + salt).digest()


BIDENT = '0x0100'
UIDENT = u('0x0100')

def _ident_mssql(hash, csize, bsize):
    if isinstance(hash, unicode):
        if len(hash) == csize and hash.startswith(UIDENT):
            return True
    else:
        if isinstance(hash, bytes):
            if len(hash) == csize and hash.startswith(BIDENT):
                return True
        else:
            raise uh.exc.ExpectedStringError(hash, 'hash')
    return False


def _parse_mssql(hash, csize, bsize, handler):
    if isinstance(hash, unicode):
        if len(hash) == csize and hash.startswith(UIDENT):
            try:
                return unhexlify(hash[6:].encode('utf-8'))
            except TypeError:
                pass

    else:
        if isinstance(hash, bytes):
            if len(hash) == csize and hash.startswith(BIDENT):
                try:
                    return unhexlify(hash[6:])
                except TypeError:
                    pass

        else:
            raise uh.exc.ExpectedStringError(hash, 'hash')
    raise uh.exc.InvalidHashError(handler)


class mssql2000(uh.HasRawSalt, uh.HasRawChecksum, uh.GenericHandler):
    name = 'mssql2000'
    setting_kwds = ('salt', )
    checksum_size = 40
    min_salt_size = max_salt_size = 4

    @classmethod
    def identify(cls, hash):
        return _ident_mssql(hash, 94, 46)

    @classmethod
    def from_string(cls, hash):
        data = _parse_mssql(hash, 94, 46, cls)
        return cls(salt=data[:4], checksum=data[4:])

    def to_string(self):
        raw = self.salt + self.checksum
        return '0x0100' + bascii_to_str(hexlify(raw).upper())

    def _calc_checksum(self, secret):
        if isinstance(secret, bytes):
            secret = secret.decode('utf-8')
        salt = self.salt
        return _raw_mssql(secret, salt) + _raw_mssql(secret.upper(), salt)

    @classmethod
    def verify(cls, secret, hash):
        uh.validate_secret(secret)
        self = cls.from_string(hash)
        chk = self.checksum
        if chk is None:
            raise uh.exc.MissingDigestError(cls)
        if isinstance(secret, bytes):
            secret = secret.decode('utf-8')
        result = _raw_mssql(secret.upper(), self.salt)
        return consteq(result, chk[20:])


class mssql2005(uh.HasRawSalt, uh.HasRawChecksum, uh.GenericHandler):
    name = 'mssql2005'
    setting_kwds = ('salt', )
    checksum_size = 20
    min_salt_size = max_salt_size = 4

    @classmethod
    def identify(cls, hash):
        return _ident_mssql(hash, 54, 26)

    @classmethod
    def from_string(cls, hash):
        data = _parse_mssql(hash, 54, 26, cls)
        return cls(salt=data[:4], checksum=data[4:])

    def to_string(self):
        raw = self.salt + self.checksum
        return '0x0100' + bascii_to_str(hexlify(raw)).upper()

    def _calc_checksum(self, secret):
        if isinstance(secret, bytes):
            secret = secret.decode('utf-8')
        return _raw_mssql(secret, self.salt)