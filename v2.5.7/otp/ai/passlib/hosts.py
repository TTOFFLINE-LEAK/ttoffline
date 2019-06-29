from warnings import warn
from otp.ai.passlib.context import LazyCryptContext
from otp.ai.passlib.exc import PasslibRuntimeWarning
from otp.ai.passlib import registry
from otp.ai.passlib.utils import has_crypt, unix_crypt_schemes
__all__ = [
 'linux_context', 'linux2_context',
 'openbsd_context',
 'netbsd_context',
 'freebsd_context',
 'host_context']
linux_context = linux2_context = LazyCryptContext(schemes=[
 'sha512_crypt', 'sha256_crypt', 'md5_crypt',
 'des_crypt', 'unix_disabled'], deprecated=[
 'des_crypt'])
freebsd_context = LazyCryptContext(['bcrypt', 'md5_crypt', 'bsd_nthash',
 'des_crypt', 'unix_disabled'])
openbsd_context = LazyCryptContext(['bcrypt', 'md5_crypt', 'bsdi_crypt',
 'des_crypt', 'unix_disabled'])
netbsd_context = LazyCryptContext(['bcrypt', 'sha1_crypt', 'md5_crypt',
 'bsdi_crypt', 'des_crypt', 'unix_disabled'])
if registry.os_crypt_present:

    def _iter_os_crypt_schemes():
        out = registry.get_supported_os_crypt_schemes()
        if out:
            out += ('unix_disabled', )
        return out


    host_context = LazyCryptContext(_iter_os_crypt_schemes())