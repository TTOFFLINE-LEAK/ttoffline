import logging
log = logging.getLogger(__name__)
import otp.ai.passlib.utils.handlers as uh
from otp.ai.passlib.utils.compat import u
__all__ = [
 'roundup_plaintext',
 'ldap_hex_md5',
 'ldap_hex_sha1']
roundup_plaintext = uh.PrefixWrapper('roundup_plaintext', 'plaintext', prefix=u('{plaintext}'), lazy=True)
ldap_hex_md5 = uh.PrefixWrapper('ldap_hex_md5', 'hex_md5', u('{MD5}'), lazy=True)
ldap_hex_sha1 = uh.PrefixWrapper('ldap_hex_sha1', 'hex_sha1', u('{SHA}'), lazy=True)