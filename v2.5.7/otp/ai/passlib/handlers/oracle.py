from binascii import hexlify, unhexlify
from hashlib import sha1
import re, logging
log = logging.getLogger(__name__)
from otp.ai.passlib.utils import to_unicode, xor_bytes
from otp.ai.passlib.utils.compat import irange, u, uascii_to_str, unicode, str_to_uascii
from otp.ai.passlib.crypto.des import des_encrypt_block
import otp.ai.passlib.utils.handlers as uh
__all__ = [
 'oracle10g',
 'oracle11g']

def des_cbc_encrypt(key, value, iv='\x00\x00\x00\x00\x00\x00\x00\x00', pad='\x00'):
    value += pad * (-len(value) % 8)
    hash = iv
    for offset in irange(0, len(value), 8):
        chunk = xor_bytes(hash, value[offset:offset + 8])
        hash = des_encrypt_block(key, chunk)

    return hash


ORACLE10_MAGIC = '\x01#Eg\x89\xab\xcd\xef'

class oracle10(uh.HasUserContext, uh.StaticHandler):
    name = 'oracle10'
    checksum_chars = uh.HEX_CHARS
    checksum_size = 16

    @classmethod
    def _norm_hash(cls, hash):
        return hash.upper()

    def _calc_checksum(self, secret):
        if isinstance(secret, bytes):
            secret = secret.decode('utf-8')
        user = to_unicode(self.user, 'utf-8', param='user')
        input = (user + secret).upper().encode('utf-16-be')
        hash = des_cbc_encrypt(ORACLE10_MAGIC, input)
        hash = des_cbc_encrypt(hash, input)
        return hexlify(hash).decode('ascii').upper()


class oracle11(uh.HasSalt, uh.GenericHandler):
    name = 'oracle11'
    setting_kwds = ('salt', )
    checksum_size = 40
    checksum_chars = uh.UPPER_HEX_CHARS
    min_salt_size = max_salt_size = 20
    salt_chars = uh.UPPER_HEX_CHARS
    _hash_regex = re.compile(u('^S:(?P<chk>[0-9a-f]{40})(?P<salt>[0-9a-f]{20})$'), re.I)

    @classmethod
    def from_string(cls, hash):
        hash = to_unicode(hash, 'ascii', 'hash')
        m = cls._hash_regex.match(hash)
        if not m:
            raise uh.exc.InvalidHashError(cls)
        salt, chk = m.group('salt', 'chk')
        return cls(salt=salt, checksum=chk.upper())

    def to_string(self):
        chk = self.checksum
        hash = u('S:%s%s') % (chk.upper(), self.salt.upper())
        return uascii_to_str(hash)

    def _calc_checksum(self, secret):
        if isinstance(secret, unicode):
            secret = secret.encode('utf-8')
        chk = sha1(secret + unhexlify(self.salt.encode('ascii'))).hexdigest()
        return str_to_uascii(chk).upper()