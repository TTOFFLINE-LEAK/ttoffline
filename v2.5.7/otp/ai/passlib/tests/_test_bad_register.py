from otp.ai.passlib.registry import register_crypt_handler
import otp.ai.passlib.utils.handlers as uh

class dummy_bad(uh.StaticHandler):
    name = 'dummy_bad'


class alt_dummy_bad(uh.StaticHandler):
    name = 'dummy_bad'


if __name__.startswith('passlib.tests'):
    register_crypt_handler(alt_dummy_bad)