import re, logging
log = logging.getLogger(__name__)
from warnings import warn
from otp.ai.passlib.utils import safe_crypt, test_crypt, to_unicode
from otp.ai.passlib.utils.binary import h64, h64big
from otp.ai.passlib.utils.compat import byte_elem_value, u, uascii_to_str, unicode, suppress_cause
from otp.ai.passlib.crypto.des import des_encrypt_int_block
import otp.ai.passlib.utils.handlers as uh
__all__ = [
 'des_crypt',
 'bsdi_crypt',
 'bigcrypt',
 'crypt16']
_BNULL = '\x00'

def _crypt_secret_to_key(secret):
    return sum((byte_elem_value(c) & 127) << 57 - i * 8 for i, c in enumerate(secret[:8]))


def _raw_des_crypt(secret, salt):
    salt_value = h64.decode_int12(salt)
    if isinstance(secret, unicode):
        secret = secret.encode('utf-8')
    if _BNULL in secret:
        raise uh.exc.NullPasswordError(des_crypt)
    key_value = _crypt_secret_to_key(secret)
    result = des_encrypt_int_block(key_value, 0, salt_value, 25)
    return h64big.encode_int64(result)


def _bsdi_secret_to_key(secret):
    key_value = _crypt_secret_to_key(secret)
    idx = 8
    end = len(secret)
    while idx < end:
        next = idx + 8
        tmp_value = _crypt_secret_to_key(secret[idx:next])
        key_value = des_encrypt_int_block(key_value, key_value) ^ tmp_value
        idx = next

    return key_value


def _raw_bsdi_crypt(secret, rounds, salt):
    salt_value = h64.decode_int24(salt)
    if isinstance(secret, unicode):
        secret = secret.encode('utf-8')
    if _BNULL in secret:
        raise uh.exc.NullPasswordError(bsdi_crypt)
    key_value = _bsdi_secret_to_key(secret)
    result = des_encrypt_int_block(key_value, 0, salt_value, rounds)
    return h64big.encode_int64(result)


class des_crypt(uh.TruncateMixin, uh.HasManyBackends, uh.HasSalt, uh.GenericHandler):
    name = 'des_crypt'
    setting_kwds = ('salt', 'truncate_error')
    checksum_chars = uh.HASH64_CHARS
    checksum_size = 11
    min_salt_size = max_salt_size = 2
    salt_chars = uh.HASH64_CHARS
    truncate_size = 8
    _hash_regex = re.compile(u('\n        ^\n        (?P<salt>[./a-z0-9]{2})\n        (?P<chk>[./a-z0-9]{11})?\n        $'), re.X | re.I)

    @classmethod
    def from_string(cls, hash):
        hash = to_unicode(hash, 'ascii', 'hash')
        salt, chk = hash[:2], hash[2:]
        return cls(salt=salt, checksum=chk or None)

    def to_string(self):
        hash = u('%s%s') % (self.salt, self.checksum)
        return uascii_to_str(hash)

    def _calc_checksum(self, secret):
        if self.use_defaults:
            self._check_truncate_policy(secret)
        return self._calc_checksum_backend(secret)

    backends = ('os_crypt', 'builtin')

    @classmethod
    def _load_backend_os_crypt(cls):
        if test_crypt('test', 'abgOeLfPimXQo'):
            cls._set_calc_checksum_backend(cls._calc_checksum_os_crypt)
            return True
        return False

    def _calc_checksum_os_crypt(self, secret):
        hash = safe_crypt(secret, self.salt)
        if hash:
            return hash[2:]
        return self._calc_checksum_builtin(secret)

    @classmethod
    def _load_backend_builtin(cls):
        cls._set_calc_checksum_backend(cls._calc_checksum_builtin)
        return True

    def _calc_checksum_builtin(self, secret):
        return _raw_des_crypt(secret, self.salt.encode('ascii')).decode('ascii')


class bsdi_crypt(uh.HasManyBackends, uh.HasRounds, uh.HasSalt, uh.GenericHandler):
    name = 'bsdi_crypt'
    setting_kwds = ('salt', 'rounds')
    checksum_size = 11
    checksum_chars = uh.HASH64_CHARS
    min_salt_size = max_salt_size = 4
    salt_chars = uh.HASH64_CHARS
    default_rounds = 5001
    min_rounds = 1
    max_rounds = 16777215
    rounds_cost = 'linear'
    _hash_regex = re.compile(u('\n        ^\n        _\n        (?P<rounds>[./a-z0-9]{4})\n        (?P<salt>[./a-z0-9]{4})\n        (?P<chk>[./a-z0-9]{11})?\n        $'), re.X | re.I)

    @classmethod
    def from_string(cls, hash):
        hash = to_unicode(hash, 'ascii', 'hash')
        m = cls._hash_regex.match(hash)
        if not m:
            raise uh.exc.InvalidHashError(cls)
        rounds, salt, chk = m.group('rounds', 'salt', 'chk')
        return cls(rounds=h64.decode_int24(rounds.encode('ascii')), salt=salt, checksum=chk)

    def to_string(self):
        hash = u('_%s%s%s') % (h64.encode_int24(self.rounds).decode('ascii'),
         self.salt, self.checksum)
        return uascii_to_str(hash)

    _avoid_even_rounds = True

    @classmethod
    def using(cls, **kwds):
        subcls = super(bsdi_crypt, cls).using(**kwds)
        if not subcls.default_rounds & 1:
            warn('bsdi_crypt rounds should be odd, as even rounds may reveal weak DES keys', uh.exc.PasslibSecurityWarning)
        return subcls

    @classmethod
    def _generate_rounds(cls):
        rounds = super(bsdi_crypt, cls)._generate_rounds()
        return rounds | 1

    def _calc_needs_update(self, **kwds):
        if not self.rounds & 1:
            return True
        return super(bsdi_crypt, self)._calc_needs_update(**kwds)

    backends = ('os_crypt', 'builtin')

    @classmethod
    def _load_backend_os_crypt(cls):
        if test_crypt('test', '_/...lLDAxARksGCHin.'):
            cls._set_calc_checksum_backend(cls._calc_checksum_os_crypt)
            return True
        return False

    def _calc_checksum_os_crypt(self, secret):
        config = self.to_string()
        hash = safe_crypt(secret, config)
        if hash:
            return hash[-11:]
        return self._calc_checksum_builtin(secret)

    @classmethod
    def _load_backend_builtin(cls):
        cls._set_calc_checksum_backend(cls._calc_checksum_builtin)
        return True

    def _calc_checksum_builtin(self, secret):
        return _raw_bsdi_crypt(secret, self.rounds, self.salt.encode('ascii')).decode('ascii')


class bigcrypt(uh.HasSalt, uh.GenericHandler):
    name = 'bigcrypt'
    setting_kwds = ('salt', )
    checksum_chars = uh.HASH64_CHARS
    min_salt_size = max_salt_size = 2
    salt_chars = uh.HASH64_CHARS
    _hash_regex = re.compile(u('\n        ^\n        (?P<salt>[./a-z0-9]{2})\n        (?P<chk>([./a-z0-9]{11})+)?\n        $'), re.X | re.I)

    @classmethod
    def from_string(cls, hash):
        hash = to_unicode(hash, 'ascii', 'hash')
        m = cls._hash_regex.match(hash)
        if not m:
            raise uh.exc.InvalidHashError(cls)
        salt, chk = m.group('salt', 'chk')
        return cls(salt=salt, checksum=chk)

    def to_string(self):
        hash = u('%s%s') % (self.salt, self.checksum)
        return uascii_to_str(hash)

    def _norm_checksum(self, checksum, relaxed=False):
        checksum = super(bigcrypt, self)._norm_checksum(checksum, relaxed=relaxed)
        if len(checksum) % 11:
            raise uh.exc.InvalidHashError(self)
        return checksum

    def _calc_checksum(self, secret):
        if isinstance(secret, unicode):
            secret = secret.encode('utf-8')
        chk = _raw_des_crypt(secret, self.salt.encode('ascii'))
        idx = 8
        end = len(secret)
        while idx < end:
            next = idx + 8
            chk += _raw_des_crypt(secret[idx:next], chk[-11:-9])
            idx = next

        return chk.decode('ascii')


class crypt16(uh.TruncateMixin, uh.HasSalt, uh.GenericHandler):
    name = 'crypt16'
    setting_kwds = ('salt', 'truncate_error')
    checksum_size = 22
    checksum_chars = uh.HASH64_CHARS
    min_salt_size = max_salt_size = 2
    salt_chars = uh.HASH64_CHARS
    truncate_size = 16
    _hash_regex = re.compile(u('\n        ^\n        (?P<salt>[./a-z0-9]{2})\n        (?P<chk>[./a-z0-9]{22})?\n        $'), re.X | re.I)

    @classmethod
    def from_string(cls, hash):
        hash = to_unicode(hash, 'ascii', 'hash')
        m = cls._hash_regex.match(hash)
        if not m:
            raise uh.exc.InvalidHashError(cls)
        salt, chk = m.group('salt', 'chk')
        return cls(salt=salt, checksum=chk)

    def to_string(self):
        hash = u('%s%s') % (self.salt, self.checksum)
        return uascii_to_str(hash)

    def _calc_checksum(self, secret):
        if isinstance(secret, unicode):
            secret = secret.encode('utf-8')
        if self.use_defaults:
            self._check_truncate_policy(secret)
        try:
            salt_value = h64.decode_int12(self.salt.encode('ascii'))
        except ValueError:
            raise suppress_cause(ValueError('invalid chars in salt'))

        key1 = _crypt_secret_to_key(secret)
        result1 = des_encrypt_int_block(key1, 0, salt_value, 20)
        key2 = _crypt_secret_to_key(secret[8:16])
        result2 = des_encrypt_int_block(key2, 0, salt_value, 5)
        chk = h64big.encode_int64(result1) + h64big.encode_int64(result2)
        return chk.decode('ascii')