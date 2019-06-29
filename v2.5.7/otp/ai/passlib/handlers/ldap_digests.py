from base64 import b64encode, b64decode
from hashlib import md5, sha1
import logging
log = logging.getLogger(__name__)
import re
from otp.ai.passlib.handlers.misc import plaintext
from otp.ai.passlib.utils import unix_crypt_schemes, to_unicode
from otp.ai.passlib.utils.compat import uascii_to_str, unicode, u
from otp.ai.passlib.utils.decor import classproperty
import otp.ai.passlib.utils.handlers as uh
__all__ = [
 'ldap_plaintext',
 'ldap_md5',
 'ldap_sha1',
 'ldap_salted_md5',
 'ldap_salted_sha1',
 'ldap_des_crypt',
 'ldap_bsdi_crypt',
 'ldap_md5_crypt',
 'ldap_sha1_cryptldap_bcrypt',
 'ldap_sha256_crypt',
 'ldap_sha512_crypt']

class _Base64DigestHelper(uh.StaticHandler):
    ident = None
    _hash_func = None
    _hash_regex = None
    checksum_chars = uh.PADDED_BASE64_CHARS

    @classproperty
    def _hash_prefix(cls):
        return cls.ident

    def _calc_checksum(self, secret):
        if isinstance(secret, unicode):
            secret = secret.encode('utf-8')
        chk = self._hash_func(secret).digest()
        return b64encode(chk).decode('ascii')


class _SaltedBase64DigestHelper(uh.HasRawSalt, uh.HasRawChecksum, uh.GenericHandler):
    setting_kwds = ('salt', 'salt_size')
    checksum_chars = uh.PADDED_BASE64_CHARS
    ident = None
    _hash_func = None
    _hash_regex = None
    min_salt_size = max_salt_size = 4
    min_salt_size = 4
    default_salt_size = 4
    max_salt_size = 16

    @classmethod
    def from_string(cls, hash):
        hash = to_unicode(hash, 'ascii', 'hash')
        m = cls._hash_regex.match(hash)
        if not m:
            raise uh.exc.InvalidHashError(cls)
        try:
            data = b64decode(m.group('tmp').encode('ascii'))
        except TypeError:
            raise uh.exc.MalformedHashError(cls)

        cs = cls.checksum_size
        return cls(checksum=data[:cs], salt=data[cs:])

    def to_string(self):
        data = self.checksum + self.salt
        hash = self.ident + b64encode(data).decode('ascii')
        return uascii_to_str(hash)

    def _calc_checksum(self, secret):
        if isinstance(secret, unicode):
            secret = secret.encode('utf-8')
        return self._hash_func(secret + self.salt).digest()


class ldap_md5(_Base64DigestHelper):
    name = 'ldap_md5'
    ident = u('{MD5}')
    _hash_func = md5
    _hash_regex = re.compile(u('^\\{MD5\\}(?P<chk>[+/a-zA-Z0-9]{22}==)$'))


class ldap_sha1(_Base64DigestHelper):
    name = 'ldap_sha1'
    ident = u('{SHA}')
    _hash_func = sha1
    _hash_regex = re.compile(u('^\\{SHA\\}(?P<chk>[+/a-zA-Z0-9]{27}=)$'))


class ldap_salted_md5(_SaltedBase64DigestHelper):
    name = 'ldap_salted_md5'
    ident = u('{SMD5}')
    checksum_size = 16
    _hash_func = md5
    _hash_regex = re.compile(u('^\\{SMD5\\}(?P<tmp>[+/a-zA-Z0-9]{27,}={0,2})$'))


class ldap_salted_sha1(_SaltedBase64DigestHelper):
    name = 'ldap_salted_sha1'
    ident = u('{SSHA}')
    checksum_size = 20
    _hash_func = sha1
    _hash_regex = re.compile(u('^\\{SSHA\\}(?P<tmp>[+/a-zA-Z0-9]{32,}={0,2})$'))


class ldap_plaintext(plaintext):
    name = 'ldap_plaintext'
    _2307_pat = re.compile(u('^\\{\\w+\\}.*$'))

    @uh.deprecated_method(deprecated='1.7', removed='2.0')
    @classmethod
    def genconfig(cls):
        return '!'

    @classmethod
    def identify(cls, hash):
        hash = uh.to_unicode_for_identify(hash)
        return bool(hash) and cls._2307_pat.match(hash) is None


ldap_crypt_schemes = [ 'ldap_' + name for name in unix_crypt_schemes ]

def _init_ldap_crypt_handlers():
    g = globals()
    for wname in unix_crypt_schemes:
        name = 'ldap_' + wname
        g[name] = uh.PrefixWrapper(name, wname, prefix=u('{CRYPT}'), lazy=True)

    del g


_init_ldap_crypt_handlers()