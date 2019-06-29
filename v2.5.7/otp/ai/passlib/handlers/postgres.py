from hashlib import md5
import logging
log = logging.getLogger(__name__)
from otp.ai.passlib.utils import to_bytes
from otp.ai.passlib.utils.compat import str_to_uascii, unicode, u
import otp.ai.passlib.utils.handlers as uh
__all__ = [
 'postgres_md5']

class postgres_md5(uh.HasUserContext, uh.StaticHandler):
    name = 'postgres_md5'
    _hash_prefix = u('md5')
    checksum_chars = uh.HEX_CHARS
    checksum_size = 32

    def _calc_checksum(self, secret):
        if isinstance(secret, unicode):
            secret = secret.encode('utf-8')
        user = to_bytes(self.user, 'utf-8', param='user')
        return str_to_uascii(md5(secret + user).hexdigest())