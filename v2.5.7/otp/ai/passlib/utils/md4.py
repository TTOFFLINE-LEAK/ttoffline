from warnings import warn
warn('the module \'passlib.utils.md4\' is deprecated as of Passlib 1.7, and will be removed in Passlib 2.0, please use \'lookup_hash("md4").const()\' from \'passlib.crypto\' instead', DeprecationWarning)
__all__ = [
 'md4']
from otp.ai.passlib.crypto.digest import lookup_hash
md4 = lookup_hash('md4').const
del lookup_hash