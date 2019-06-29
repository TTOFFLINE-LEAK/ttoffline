from warnings import warn
warn("the 'passlib.utils.des' module has been relocated to 'passlib.crypto.des' as of passlib 1.7, and the old location will be removed in passlib 2.0", DeprecationWarning)
from otp.ai.passlib.utils.decor import deprecated_function
from otp.ai.passlib.crypto.des import expand_des_key, des_encrypt_block, des_encrypt_int_block
expand_des_key = deprecated_function(deprecated='1.7', removed='1.8', replacement='passlib.crypto.des.expand_des_key')(expand_des_key)
des_encrypt_block = deprecated_function(deprecated='1.7', removed='1.8', replacement='passlib.crypto.des.des_encrypt_block')(des_encrypt_block)
des_encrypt_int_block = deprecated_function(deprecated='1.7', removed='1.8', replacement='passlib.crypto.des.des_encrypt_int_block')(des_encrypt_int_block)
import struct
_unpack_uint64 = struct.Struct('>Q').unpack

@deprecated_function(deprecated='1.6', removed='1.8', replacement='passlib.crypto.des.des_encrypt_int_block()')
def mdes_encrypt_int_block(key, input, salt=0, rounds=1):
    if isinstance(key, bytes):
        if len(key) == 7:
            key = expand_des_key(key)
        key = _unpack_uint64(key)[0]
    return des_encrypt_int_block(key, input, salt, rounds)