from binascii import hexlify
import logging
log = logging.getLogger(__name__)
from warnings import warn
from otp.ai.passlib.utils import to_unicode, right_pad_string
from otp.ai.passlib.utils.compat import unicode
from otp.ai.passlib.crypto.digest import lookup_hash
md4 = lookup_hash('md4').const
import otp.ai.passlib.utils.handlers as uh
__all__ = [
 'lmhash',
 'nthash',
 'bsd_nthash',
 'msdcc',
 'msdcc2']

class lmhash(uh.TruncateMixin, uh.HasEncodingContext, uh.StaticHandler):
    name = 'lmhash'
    setting_kwds = ('truncate_error', )
    checksum_chars = uh.HEX_CHARS
    checksum_size = 32
    truncate_size = 14
    default_encoding = 'cp437'

    @classmethod
    def _norm_hash(cls, hash):
        return hash.lower()

    def _calc_checksum(self, secret):
        if self.use_defaults:
            self._check_truncate_policy(secret)
        return hexlify(self.raw(secret, self.encoding)).decode('ascii')

    _magic = 'KGS!@#$%'

    @classmethod
    def raw(cls, secret, encoding=None):
        if not encoding:
            encoding = cls.default_encoding
        from otp.ai.passlib.crypto.des import des_encrypt_block
        MAGIC = cls._magic
        if isinstance(secret, unicode):
            secret = secret.upper().encode(encoding)
        else:
            if isinstance(secret, bytes):
                secret = secret.upper()
            else:
                raise TypeError('secret must be unicode or bytes')
        secret = right_pad_string(secret, 14)
        return des_encrypt_block(secret[0:7], MAGIC) + des_encrypt_block(secret[7:14], MAGIC)


class nthash(uh.StaticHandler):
    name = 'nthash'
    checksum_chars = uh.HEX_CHARS
    checksum_size = 32

    @classmethod
    def _norm_hash(cls, hash):
        return hash.lower()

    def _calc_checksum(self, secret):
        return hexlify(self.raw(secret)).decode('ascii')

    @classmethod
    def raw(cls, secret):
        secret = to_unicode(secret, 'utf-8', param='secret')
        return md4(secret.encode('utf-16-le')).digest()

    @classmethod
    def raw_nthash(cls, secret, hex=False):
        warn('nthash.raw_nthash() is deprecated, and will be removed in Passlib 1.8, please use nthash.raw() instead', DeprecationWarning)
        ret = nthash.raw(secret)
        if hex:
            return hexlify(ret).decode('ascii')
        return ret


bsd_nthash = uh.PrefixWrapper('bsd_nthash', nthash, prefix='$3$$', ident='$3$$', doc="The class support FreeBSD's representation of NTHASH\n    (which is compatible with the :ref:`modular-crypt-format`),\n    and follows the :ref:`password-hash-api`.\n\n    It has no salt and a single fixed round.\n\n    The :meth:`~passlib.ifc.PasswordHash.hash` and :meth:`~passlib.ifc.PasswordHash.genconfig` methods accept no optional keywords.\n    ")

class msdcc(uh.HasUserContext, uh.StaticHandler):
    name = 'msdcc'
    checksum_chars = uh.HEX_CHARS
    checksum_size = 32

    @classmethod
    def _norm_hash(cls, hash):
        return hash.lower()

    def _calc_checksum(self, secret):
        return hexlify(self.raw(secret, self.user)).decode('ascii')

    @classmethod
    def raw(cls, secret, user):
        secret = to_unicode(secret, 'utf-8', param='secret').encode('utf-16-le')
        user = to_unicode(user, 'utf-8', param='user').lower().encode('utf-16-le')
        return md4(md4(secret).digest() + user).digest()


class msdcc2(uh.HasUserContext, uh.StaticHandler):
    name = 'msdcc2'
    checksum_chars = uh.HEX_CHARS
    checksum_size = 32

    @classmethod
    def _norm_hash(cls, hash):
        return hash.lower()

    def _calc_checksum(self, secret):
        return hexlify(self.raw(secret, self.user)).decode('ascii')

    @classmethod
    def raw(cls, secret, user):
        from otp.ai.passlib.crypto.digest import pbkdf2_hmac
        secret = to_unicode(secret, 'utf-8', param='secret').encode('utf-16-le')
        user = to_unicode(user, 'utf-8', param='user').lower().encode('utf-16-le')
        tmp = md4(md4(secret).digest() + user).digest()
        return pbkdf2_hmac('sha1', tmp, user, 10240, 16)