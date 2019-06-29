import logging
log = logging.getLogger(__name__)
from itertools import chain
from otp.ai.passlib import hash
from otp.ai.passlib.context import LazyCryptContext
from otp.ai.passlib.utils import sys_bits
__all__ = [
 'custom_app_context',
 'django_context',
 'ldap_context', 'ldap_nocrypt_context',
 'mysql_context', 'mysql4_context', 'mysql3_context',
 'phpass_context',
 'phpbb3_context',
 'postgres_context']

def _load_master_config():
    from otp.ai.passlib.registry import list_crypt_handlers
    schemes = list_crypt_handlers()
    excluded = [
     'bigcrypt',
     'crypt16',
     'cisco_pix',
     'cisco_type7',
     'htdigest',
     'mysql323',
     'oracle10',
     'lmhash',
     'msdcc',
     'msdcc2',
     'nthash',
     'plaintext',
     'ldap_plaintext',
     'django_disabled',
     'unix_disabled',
     'unix_fallback']
    for name in excluded:
        schemes.remove(name)

    return dict(schemes=schemes, default='sha256_crypt')


master_context = LazyCryptContext(onload=_load_master_config)
custom_app_context = LazyCryptContext(schemes=[
 'sha512_crypt', 'sha256_crypt'], default='sha256_crypt' if sys_bits < 64 else 'sha512_crypt', sha512_crypt__min_rounds=535000, sha256_crypt__min_rounds=535000, admin__sha512_crypt__min_rounds=1024000, admin__sha256_crypt__min_rounds=1024000)
_django10_schemes = [
 'django_salted_sha1', 'django_salted_md5', 'django_des_crypt',
 'hex_md5', 'django_disabled']
django10_context = LazyCryptContext(schemes=_django10_schemes, default='django_salted_sha1', deprecated=[
 'hex_md5'])
_django14_schemes = [
 'django_pbkdf2_sha256', 'django_pbkdf2_sha1',
 'django_bcrypt'] + _django10_schemes
django14_context = LazyCryptContext(schemes=_django14_schemes, deprecated=_django10_schemes)
_django16_schemes = _django14_schemes[:]
_django16_schemes.insert(1, 'django_bcrypt_sha256')
django16_context = LazyCryptContext(schemes=_django16_schemes, deprecated=_django10_schemes)
django110_context = LazyCryptContext(schemes=[
 'django_pbkdf2_sha256', 'django_pbkdf2_sha1',
 'django_argon2', 'django_bcrypt', 'django_bcrypt_sha256',
 'django_disabled'])
django_context = django110_context
std_ldap_schemes = [
 'ldap_salted_sha1', 'ldap_salted_md5',
 'ldap_sha1', 'ldap_md5',
 'ldap_plaintext']
ldap_nocrypt_context = LazyCryptContext(std_ldap_schemes)

def _iter_ldap_crypt_schemes():
    from otp.ai.passlib.utils import unix_crypt_schemes
    return ('ldap_' + name for name in unix_crypt_schemes)


def _iter_ldap_schemes():
    return chain(std_ldap_schemes, _iter_ldap_crypt_schemes())


ldap_context = LazyCryptContext(_iter_ldap_schemes())
mysql3_context = LazyCryptContext(['mysql323'])
mysql4_context = LazyCryptContext(['mysql41', 'mysql323'], deprecated='mysql323')
mysql_context = mysql4_context
postgres_context = LazyCryptContext(['postgres_md5'])

def _create_phpass_policy(**kwds):
    kwds['default'] = 'bcrypt' if hash.bcrypt.has_backend() else 'phpass'
    return kwds


phpass_context = LazyCryptContext(schemes=[
 'bcrypt', 'phpass', 'bsdi_crypt'], onload=_create_phpass_policy)
phpbb3_context = LazyCryptContext(['phpass'], phpass__ident='H')
_std_roundup_schemes = [
 'ldap_hex_sha1', 'ldap_hex_md5', 'ldap_des_crypt', 'roundup_plaintext']
roundup10_context = LazyCryptContext(_std_roundup_schemes)
roundup_context = roundup15_context = LazyCryptContext(schemes=_std_roundup_schemes + ['ldap_pbkdf2_sha1'], deprecated=_std_roundup_schemes, default='ldap_pbkdf2_sha1', ldap_pbkdf2_sha1__default_rounds=10000)