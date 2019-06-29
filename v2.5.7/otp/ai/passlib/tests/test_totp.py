import datetime
from functools import partial
import logging
log = logging.getLogger(__name__)
import sys, time as _time
from otp.ai.passlib import exc
from otp.ai.passlib.utils.compat import unicode, u
from otp.ai.passlib.tests.utils import TestCase, time_call
from otp.ai.passlib import totp as totp_module
from otp.ai.passlib.totp import TOTP, AppWallet, AES_SUPPORT
__all__ = [
 'EngineTest']
Base32DecodeError = Base16DecodeError = TypeError
if sys.version_info >= (3, 0):
    from binascii import Error as Base16DecodeError
if sys.version_info >= (3, 3):
    from binascii import Error as Base32DecodeError
PASS1 = 'abcdef'
PASS2 = '\x00\xff'
KEY1 = '4AOGGDBBQSYHNTUZ'
KEY1_RAW = '\xe0\x1cc\x0c!\x84\xb0v\xce\x99'
KEY2_RAW = '\xee]\xcb9\x870\x06 D\xc8y/\xa54&\xe4\x9c\x13\xc2\x18'
KEY3 = 'S3JDVB7QD2R7JPXX'
KEY4 = 'JBSWY3DPEHPK3PXP'
KEY4_RAW = 'Hello!\xde\xad\xbe\xef'

def _get_max_time_t():
    value = 1073741824
    year = 0
    while True:
        next_value = value << 1
        try:
            next_year = datetime.datetime.utcfromtimestamp(next_value - 1).year
        except (ValueError, OSError, OverflowError):
            break
        else:
            if next_year < year:
                break
            value = next_value

    value -= 1
    max_datetime_timestamp = 253402318800L
    return min(value, max_datetime_timestamp)


max_time_t = _get_max_time_t()

def to_b32_size(raw_size):
    return (raw_size * 8 + 4) // 5


class AppWalletTest(TestCase):
    descriptionPrefix = 'passlib.totp.AppWallet'

    def test_secrets_types(self):
        wallet = AppWallet()
        self.assertEqual(wallet._secrets, {})
        self.assertFalse(wallet.has_secrets)
        ref = {'1': 'aaa', '2': 'bbb'}
        wallet = AppWallet(ref)
        self.assertEqual(wallet._secrets, ref)
        self.assertTrue(wallet.has_secrets)
        wallet = AppWallet('\n 1: aaa\n# comment\n \n2: bbb   ')
        self.assertEqual(wallet._secrets, ref)
        wallet = AppWallet('1: aaa: bbb \n# comment\n \n2: bbb   ')
        self.assertEqual(wallet._secrets, {'1': 'aaa: bbb', '2': 'bbb'})
        wallet = AppWallet('{"1":"aaa","2":"bbb"}')
        self.assertEqual(wallet._secrets, ref)
        self.assertRaises(TypeError, AppWallet, 123)
        self.assertRaises(TypeError, AppWallet, '[123]')
        self.assertRaises(ValueError, AppWallet, {'1': 'aaa', '2': ''})

    def test_secrets_tags(self):
        ref = {'1': 'aaa', '02': 'bbb', 'C': 'ccc'}
        wallet = AppWallet(ref)
        self.assertEqual(wallet._secrets, ref)
        wallet = AppWallet({u('1'): 'aaa', u('02'): 'bbb', u('C'): 'ccc'})
        self.assertEqual(wallet._secrets, ref)
        wallet = AppWallet({1: 'aaa', '02': 'bbb', 'C': 'ccc'})
        self.assertEqual(wallet._secrets, ref)
        self.assertRaises(TypeError, AppWallet, {(1, ): 'aaa'})
        wallet = AppWallet({'1-2_3.4': 'aaa'})
        self.assertRaises(ValueError, AppWallet, {'-abc': 'aaa'})
        self.assertRaises(ValueError, AppWallet, {'ab*$': 'aaa'})
        wallet = AppWallet({'1': u('aaa'), '02': 'bbb', 'C': 'ccc'})
        self.assertEqual(wallet._secrets, ref)
        self.assertRaises(TypeError, AppWallet, {'1': 123})
        self.assertRaises(TypeError, AppWallet, {'1': None})
        self.assertRaises(TypeError, AppWallet, {'1': []})
        return

    def test_default_tag(self):
        wallet = AppWallet({'1': 'one', '02': 'two'})
        self.assertEqual(wallet.default_tag, '02')
        self.assertEqual(wallet.get_secret(wallet.default_tag), 'two')
        wallet = AppWallet({'1': 'one', '02': 'two', 'A': 'aaa'})
        self.assertEqual(wallet.default_tag, 'A')
        self.assertEqual(wallet.get_secret(wallet.default_tag), 'aaa')
        wallet = AppWallet({'1': 'one', '02': 'two', 'A': 'aaa'}, default_tag='1')
        self.assertEqual(wallet.default_tag, '1')
        self.assertEqual(wallet.get_secret(wallet.default_tag), 'one')
        self.assertRaises(KeyError, AppWallet, {'1': 'one', '02': 'two', 'A': 'aaa'}, default_tag='B')
        wallet = AppWallet()
        self.assertEqual(wallet.default_tag, None)
        self.assertRaises(KeyError, wallet.get_secret, None)
        return

    def require_aes_support(self, canary=None):
        if AES_SUPPORT:
            canary and canary()
        else:
            canary and self.assertRaises(RuntimeError, canary)
            raise self.skipTest("'cryptography' package not installed")

    def test_decrypt_key(self):
        wallet = AppWallet({'1': PASS1, '2': PASS2})
        CIPHER1 = dict(v=1, c=13, s='6D7N7W53O7HHS37NLUFQ', k='MHCTEGSNPFN5CGBJ', t='1')
        self.require_aes_support(canary=partial(wallet.decrypt_key, CIPHER1))
        self.assertEqual(wallet.decrypt_key(CIPHER1)[0], KEY1_RAW)
        CIPHER2 = dict(v=1, c=13, s='SPZJ54Y6IPUD2BYA4C6A', k='ZGDXXTVQOWYLC2AU', t='1')
        self.assertEqual(wallet.decrypt_key(CIPHER2)[0], KEY1_RAW)
        CIPHER3 = dict(v=1, c=8, s='FCCTARTIJWE7CPQHUDKA', k='D2DRS32YESGHHINWFFCELKN7Z6NAHM4M', t='2')
        self.assertEqual(wallet.decrypt_key(CIPHER3)[0], KEY2_RAW)
        temp = CIPHER1.copy()
        temp.update(t='2')
        self.assertEqual(wallet.decrypt_key(temp)[0], '\xafD6.F7\xeb\x19\x05Q')
        temp = CIPHER1.copy()
        temp.update(t='3')
        self.assertRaises(KeyError, wallet.decrypt_key, temp)
        temp = CIPHER1.copy()
        temp.update(v=999)
        self.assertRaises(ValueError, wallet.decrypt_key, temp)

    def test_decrypt_key_needs_recrypt(self):
        self.require_aes_support()
        wallet = AppWallet({'1': PASS1, '2': PASS2}, encrypt_cost=13)
        ref = dict(v=1, c=13, s='AAAA', k='AAAA', t='2')
        self.assertFalse(wallet.decrypt_key(ref)[1])
        temp = ref.copy()
        temp.update(c=8)
        self.assertTrue(wallet.decrypt_key(temp)[1])
        temp = ref.copy()
        temp.update(t='1')
        self.assertTrue(wallet.decrypt_key(temp)[1])

    def assertSaneResult(self, result, wallet, key, tag='1', needs_recrypt=False):
        self.assertEqual(set(result), set(['v', 't', 'c', 's', 'k']))
        self.assertEqual(result['v'], 1)
        self.assertEqual(result['t'], tag)
        self.assertEqual(result['c'], wallet.encrypt_cost)
        self.assertEqual(len(result['s']), to_b32_size(wallet.salt_size))
        self.assertEqual(len(result['k']), to_b32_size(len(key)))
        result_key, result_needs_recrypt = wallet.decrypt_key(result)
        self.assertEqual(result_key, key)
        self.assertEqual(result_needs_recrypt, needs_recrypt)

    def test_encrypt_key(self):
        wallet = AppWallet({'1': PASS1}, encrypt_cost=5)
        self.require_aes_support(canary=partial(wallet.encrypt_key, KEY1_RAW))
        result = wallet.encrypt_key(KEY1_RAW)
        self.assertSaneResult(result, wallet, KEY1_RAW)
        other = wallet.encrypt_key(KEY1_RAW)
        self.assertSaneResult(result, wallet, KEY1_RAW)
        self.assertNotEqual(other['s'], result['s'])
        self.assertNotEqual(other['k'], result['k'])
        wallet2 = AppWallet({'1': PASS1}, encrypt_cost=6)
        result = wallet2.encrypt_key(KEY1_RAW)
        self.assertSaneResult(result, wallet2, KEY1_RAW)
        wallet2 = AppWallet({'1': PASS1, '2': PASS2})
        result = wallet2.encrypt_key(KEY1_RAW)
        self.assertSaneResult(result, wallet2, KEY1_RAW, tag='2')
        wallet2 = AppWallet({'1': PASS1})
        wallet2.salt_size = 64
        result = wallet2.encrypt_key(KEY1_RAW)
        self.assertSaneResult(result, wallet2, KEY1_RAW)
        result = wallet.encrypt_key(KEY2_RAW)
        self.assertSaneResult(result, wallet, KEY2_RAW)
        self.assertRaises(ValueError, wallet.encrypt_key, '')

    def test_encrypt_cost_timing(self):
        self.require_aes_support()
        wallet = AppWallet({'1': 'aaa'})
        wallet.encrypt_cost -= 2
        delta, _ = time_call(partial(wallet.encrypt_key, KEY1_RAW), maxtime=0)
        wallet.encrypt_cost += 3
        delta2, _ = time_call(partial(wallet.encrypt_key, KEY1_RAW), maxtime=0)
        self.assertAlmostEqual(delta2, delta * 8, delta=delta * 8 * 0.5)


RFC_KEY_BYTES_20 = ('12345678901234567890').encode('ascii')
RFC_KEY_BYTES_32 = (RFC_KEY_BYTES_20 * 2)[:32]
RFC_KEY_BYTES_64 = (RFC_KEY_BYTES_20 * 4)[:64]

class TotpTest(TestCase):
    descriptionPrefix = 'passlib.totp.TOTP'

    def setUp(self):
        super(TotpTest, self).setUp()
        from otp.ai.passlib.crypto.digest import lookup_hash
        lookup_hash.clear_cache()
        self.patchAttr(totp_module, 'rng', self.getRandom())

    def randtime(self):
        return self.getRandom().random() * max_time_t

    def randotp(self, cls=None, **kwds):
        rng = self.getRandom()
        if 'key' not in kwds:
            kwds['new'] = True
        kwds.setdefault('digits', rng.randint(6, 10))
        kwds.setdefault('alg', rng.choice(['sha1', 'sha256', 'sha512']))
        kwds.setdefault('period', rng.randint(10, 120))
        return (cls or TOTP)(**kwds)

    def test_randotp(self):
        otp1 = self.randotp()
        otp2 = self.randotp()
        self.assertNotEqual(otp1.key, otp2.key, 'key not randomized:')
        for _ in range(10):
            if otp1.digits != otp2.digits:
                break
            otp2 = self.randotp()
        else:
            self.fail('digits not randomized')

        for _ in range(10):
            if otp1.alg != otp2.alg:
                break
            otp2 = self.randotp()
        else:
            self.fail('alg not randomized')

    vector_defaults = dict(format='base32', alg='sha1', period=30, digits=8)
    vectors = [
     [
      dict(key='ACDEFGHJKL234567', digits=6),
      (1412873399, '221105'),
      (1412873400, '178491'),
      (1412873401, '178491'),
      (1412873429, '178491'),
      (1412873430, '915114')],
     [
      dict(key='ACDEFGHJKL234567', digits=8),
      (1412873399, '20221105'),
      (1412873400, '86178491'),
      (1412873401, '86178491'),
      (1412873429, '86178491'),
      (1412873430, '03915114')],
     [
      dict(key='S3JD-VB7Q-D2R7-JPXX', digits=6),
      (1419622709, '000492'),
      (1419622739, '897212')],
     [
      dict(key=RFC_KEY_BYTES_20, format='raw', alg='sha1'),
      (59, '94287082'),
      (1111111109, '07081804'),
      (1111111111, '14050471'),
      (1234567890, '89005924'),
      (2000000000, '69279037'),
      (20000000000L, '65353130')],
     [
      dict(key=RFC_KEY_BYTES_32, format='raw', alg='sha256'),
      (59, '46119246'),
      (1111111109, '68084774'),
      (1111111111, '67062674'),
      (1234567890, '91819424'),
      (2000000000, '90698825'),
      (20000000000L, '77737706')],
     [
      dict(key=RFC_KEY_BYTES_64, format='raw', alg='sha512'),
      (59, '90693936'),
      (1111111109, '25091201'),
      (1111111111, '99943326'),
      (1234567890, '93441116'),
      (2000000000, '38618901'),
      (20000000000L, '47863826')],
     [
      dict(key='JBSWY3DPEHPK3PXP', digits=6), (1409192430, '727248'), (1419890990, '122419')],
     [
      dict(key='JBSWY3DPEHPK3PXP', digits=9, period=41), (1419891152, '662331049')],
     [
      dict(key=RFC_KEY_BYTES_20, format='raw', period=60), (1111111111, '19360094')],
     [
      dict(key=RFC_KEY_BYTES_32, format='raw', alg='sha256', period=60), (1111111111, '40857319')],
     [
      dict(key=RFC_KEY_BYTES_64, format='raw', alg='sha512', period=60), (1111111111, '37023009')]]

    def iter_test_vectors(self):
        from otp.ai.passlib.totp import TOTP
        for row in self.vectors:
            kwds = self.vector_defaults.copy()
            kwds.update(row[0])
            for entry in row[1:]:
                if len(entry) == 3:
                    time, token, expires = entry
                else:
                    time, token = entry
                    expires = None
                log.debug('test vector: %r time=%r token=%r expires=%r', kwds, time, token, expires)
                otp = TOTP(**kwds)
                prefix = 'alg=%r time=%r token=%r: ' % (otp.alg, time, token)
                yield (otp, time, token, expires, prefix)

        return

    def test_ctor_w_new(self):
        self.assertRaises(TypeError, TOTP)
        self.assertRaises(TypeError, TOTP, key='4aoggdbbqsyhntuz', new=True)
        otp = TOTP(new=True)
        otp2 = TOTP(new=True)
        self.assertNotEqual(otp.key, otp2.key)

    def test_ctor_w_size(self):
        self.assertEqual(len(TOTP(new=True, alg='sha1').key), 20)
        self.assertEqual(len(TOTP(new=True, alg='sha256').key), 32)
        self.assertEqual(len(TOTP(new=True, alg='sha512').key), 64)
        self.assertEqual(len(TOTP(new=True, size=10).key), 10)
        self.assertEqual(len(TOTP(new=True, size=16).key), 16)
        self.assertRaises(ValueError, TOTP, new=True, size=21, alg='sha1')
        self.assertRaises(ValueError, TOTP, new=True, size=9)
        with self.assertWarningList([
         dict(category=exc.PasslibSecurityWarning, message_re='.*for security purposes, secret key must be.*')]):
            _ = TOTP('0A0A0A0A0A0A0A0A0A', 'hex')

    def test_ctor_w_key_and_format(self):
        self.assertEqual(TOTP(KEY1).key, KEY1_RAW)
        self.assertEqual(TOTP(KEY1.lower()).key, KEY1_RAW)
        self.assertEqual(TOTP(' 4aog gdbb qsyh ntuz ').key, KEY1_RAW)
        self.assertRaises(Base32DecodeError, TOTP, 'ao!ggdbbqsyhntuz')
        self.assertEqual(TOTP('e01c630c2184b076ce99', 'hex').key, KEY1_RAW)
        self.assertRaises(Base16DecodeError, TOTP, 'X01c630c2184b076ce99', 'hex')
        self.assertEqual(TOTP(KEY1_RAW, 'raw').key, KEY1_RAW)

    def test_ctor_w_alg(self):
        self.assertEqual(TOTP(KEY1, alg='SHA-256').alg, 'sha256')
        self.assertEqual(TOTP(KEY1, alg='SHA256').alg, 'sha256')
        self.assertRaises(ValueError, TOTP, KEY1, alg='SHA-333')

    def test_ctor_w_digits(self):
        self.assertRaises(ValueError, TOTP, KEY1, digits=5)
        self.assertEqual(TOTP(KEY1, digits=6).digits, 6)
        self.assertEqual(TOTP(KEY1, digits=10).digits, 10)
        self.assertRaises(ValueError, TOTP, KEY1, digits=11)

    def test_ctor_w_period(self):
        self.assertEqual(TOTP(KEY1).period, 30)
        self.assertEqual(TOTP(KEY1, period=63).period, 63)
        self.assertRaises(TypeError, TOTP, KEY1, period=1.5)
        self.assertRaises(TypeError, TOTP, KEY1, period='abc')
        self.assertRaises(ValueError, TOTP, KEY1, period=0)
        self.assertRaises(ValueError, TOTP, KEY1, period=-1)

    def test_ctor_w_label(self):
        self.assertEqual(TOTP(KEY1).label, None)
        self.assertEqual(TOTP(KEY1, label='foo@bar').label, 'foo@bar')
        self.assertRaises(ValueError, TOTP, KEY1, label='foo:bar')
        return

    def test_ctor_w_issuer(self):
        self.assertEqual(TOTP(KEY1).issuer, None)
        self.assertEqual(TOTP(KEY1, issuer='foo.com').issuer, 'foo.com')
        self.assertRaises(ValueError, TOTP, KEY1, issuer='foo.com:bar')
        return

    def test_using_w_period(self):
        self.assertEqual(TOTP(KEY1).period, 30)
        self.assertEqual(TOTP.using(period=63)(KEY1).period, 63)
        self.assertRaises(TypeError, TOTP.using, period=1.5)
        self.assertRaises(TypeError, TOTP.using, period='abc')
        self.assertRaises(ValueError, TOTP.using, period=0)
        self.assertRaises(ValueError, TOTP.using, period=-1)

    def test_using_w_now(self):
        otp = self.randotp()
        self.assertIs(otp.now, _time.time)
        self.assertAlmostEqual(otp.normalize_time(None), int(_time.time()))
        counter = [
         123.12]

        def now():
            counter[0] += 1
            return counter[0]

        otp = self.randotp(cls=TOTP.using(now=now))
        self.assertEqual(otp.normalize_time(None), 126)
        self.assertEqual(otp.normalize_time(None), 127)
        self.assertRaises(TypeError, TOTP.using, now=123)
        msg_re = 'now\\(\\) function must return non-negative'
        self.assertRaisesRegex(AssertionError, msg_re, TOTP.using, now=lambda : 'abc')
        self.assertRaisesRegex(AssertionError, msg_re, TOTP.using, now=lambda : -1)
        return

    def test_normalize_token_instance(self, otp=None):
        if otp is None:
            otp = self.randotp(digits=7)
        self.assertEqual(otp.normalize_token(u('1234567')), '1234567')
        self.assertEqual(otp.normalize_token('1234567'), '1234567')
        self.assertEqual(otp.normalize_token(1234567), '1234567')
        self.assertEqual(otp.normalize_token(234567), '0234567')
        self.assertRaises(TypeError, otp.normalize_token, 1234567.0)
        self.assertRaises(TypeError, otp.normalize_token, None)
        self.assertRaises(exc.MalformedTokenError, otp.normalize_token, '123456')
        self.assertRaises(exc.MalformedTokenError, otp.normalize_token, '01234567')
        self.assertRaises(exc.MalformedTokenError, otp.normalize_token, 12345678)
        return

    def test_normalize_token_class(self):
        self.test_normalize_token_instance(otp=TOTP.using(digits=7))

    def test_normalize_time(self):
        TotpFactory = TOTP.using()
        otp = self.randotp(TotpFactory)
        for _ in range(10):
            time = self.randtime()
            tint = int(time)
            self.assertEqual(otp.normalize_time(time), tint)
            self.assertEqual(otp.normalize_time(tint + 0.5), tint)
            self.assertEqual(otp.normalize_time(tint), tint)
            dt = datetime.datetime.utcfromtimestamp(time)
            self.assertEqual(otp.normalize_time(dt), tint)
            orig = TotpFactory.now
            try:
                TotpFactory.now = staticmethod(lambda : time)
                self.assertEqual(otp.normalize_time(None), tint)
            finally:
                TotpFactory.now = orig

        self.assertRaises(TypeError, otp.normalize_time, '1234')
        return

    def test_key_attrs(self):
        rng = self.getRandom()
        otp = TOTP(KEY1_RAW, 'raw')
        self.assertEqual(otp.key, KEY1_RAW)
        self.assertEqual(otp.hex_key, 'e01c630c2184b076ce99')
        self.assertEqual(otp.base32_key, KEY1)
        self.assertEqual(otp.pretty_key(), '4AOG-GDBB-QSYH-NTUZ')
        self.assertEqual(otp.pretty_key(sep=' '), '4AOG GDBB QSYH NTUZ')
        self.assertEqual(otp.pretty_key(sep=False), KEY1)
        self.assertEqual(otp.pretty_key(format='hex'), 'e01c-630c-2184-b076-ce99')
        otp = TOTP(new=True, size=rng.randint(10, 20))
        _ = otp.hex_key
        _ = otp.base32_key
        _ = otp.pretty_key()

    def test_totp_token(self):
        from otp.ai.passlib.totp import TOTP, TotpToken
        otp = TOTP('s3jdvb7qd2r7jpxx')
        result = otp.generate(1419622739)
        self.assertIsInstance(result, TotpToken)
        self.assertEqual(result.token, '897212')
        self.assertEqual(result.counter, 47320757)
        self.assertEqual(result.expire_time, 1419622740)
        self.assertEqual(result, ('897212', 1419622740))
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], '897212')
        self.assertEqual(result[1], 1419622740)
        self.assertRaises(IndexError, result.__getitem__, -3)
        self.assertRaises(IndexError, result.__getitem__, 2)
        self.assertTrue(result)
        otp.now = lambda : 1419622739.5
        self.assertEqual(result.remaining, 0.5)
        self.assertTrue(result.valid)
        otp.now = lambda : 1419622741
        self.assertEqual(result.remaining, 0)
        self.assertFalse(result.valid)
        result2 = otp.generate(1419622739)
        self.assertIsNot(result2, result)
        self.assertEqual(result2, result)
        result3 = otp.generate(1419622711)
        self.assertIsNot(result3, result)
        self.assertEqual(result3, result)
        result4 = otp.generate(1419622999)
        self.assertNotEqual(result4, result)

    def test_generate(self):
        from otp.ai.passlib.totp import TOTP
        otp = TOTP(new=True)
        time = self.randtime()
        result = otp.generate(time)
        token = result.token
        self.assertIsInstance(token, unicode)
        start_time = result.counter * 30
        self.assertEqual(otp.generate(start_time + 29).token, token)
        self.assertNotEqual(otp.generate(start_time + 30).token, token)
        dt = datetime.datetime.utcfromtimestamp(time)
        self.assertEqual(int(otp.normalize_time(dt)), int(time))
        self.assertEqual(otp.generate(dt).token, token)
        otp2 = TOTP.using(now=lambda : time)(key=otp.base32_key)
        self.assertEqual(otp2.generate().token, token)
        self.assertRaises(ValueError, otp.generate, -1)

    def test_generate_w_reference_vectors(self):
        for otp, time, token, expires, prefix in self.iter_test_vectors():
            result = otp.generate(time)
            self.assertEqual(result.token, token, msg=prefix)
            self.assertEqual(result.counter, time // otp.period, msg=prefix)
            if expires:
                self.assertEqual(result.expire_time, expires)

    def assertTotpMatch(self, match, time, skipped=0, period=30, window=30, msg=''):
        from otp.ai.passlib.totp import TotpMatch
        self.assertIsInstance(match, TotpMatch)
        self.assertIsInstance(match.totp, TOTP)
        self.assertEqual(match.totp.period, period)
        self.assertEqual(match.time, time, msg=msg + ' matched time:')
        expected = time // period
        counter = expected + skipped
        self.assertEqual(match.counter, counter, msg=msg + ' matched counter:')
        self.assertEqual(match.expected_counter, expected, msg=msg + ' expected counter:')
        self.assertEqual(match.skipped, skipped, msg=msg + ' skipped:')
        self.assertEqual(match.cache_seconds, period + window)
        expire_time = (counter + 1) * period
        self.assertEqual(match.expire_time, expire_time)
        self.assertEqual(match.cache_time, expire_time + window)
        self.assertEqual(len(match), 2)
        self.assertEqual(match, (counter, time))
        self.assertRaises(IndexError, match.__getitem__, -3)
        self.assertEqual(match[0], counter)
        self.assertEqual(match[1], time)
        self.assertRaises(IndexError, match.__getitem__, 2)
        self.assertTrue(match)

    def test_totp_match_w_valid_token(self):
        time = 141230981
        token = '781501'
        otp = TOTP.using(now=lambda : time + 86400)(KEY3)
        result = otp.match(token, time)
        self.assertTotpMatch(result, time=time, skipped=0)

    def test_totp_match_w_older_token(self):
        from otp.ai.passlib.totp import TotpMatch
        time = 141230981
        token = '781501'
        otp = TOTP.using(now=lambda : time + 86400)(KEY3)
        result = otp.match(token, time - 30)
        self.assertTotpMatch(result, time=time - 30, skipped=1)

    def test_totp_match_w_new_token(self):
        time = 141230981
        token = '781501'
        otp = TOTP.using(now=lambda : time + 86400)(KEY3)
        result = otp.match(token, time + 30)
        self.assertTotpMatch(result, time=time + 30, skipped=-1)

    def test_totp_match_w_invalid_token(self):
        time = 141230981
        token = '781501'
        otp = TOTP.using(now=lambda : time + 86400)(KEY3)
        self.assertRaises(exc.InvalidTokenError, otp.match, token, time + 60)

    def assertVerifyMatches(self, expect_skipped, token, time, otp, gen_time=None, **kwds):
        msg = 'key=%r alg=%r period=%r token=%r gen_time=%r time=%r:' % (
         otp.base32_key, otp.alg, otp.period, token, gen_time, time)
        result = otp.match(token, time, **kwds)
        self.assertTotpMatch(result, time=otp.normalize_time(time), period=otp.period, window=kwds.get('window', 30), skipped=expect_skipped, msg=msg)

    def assertVerifyRaises(self, exc_class, token, time, otp, gen_time=None, **kwds):
        msg = 'key=%r alg=%r period=%r token=%r gen_time=%r time=%r:' % (
         otp.base32_key, otp.alg, otp.period, token, gen_time, time)
        return self.assertRaises(exc_class, otp.match, token, time, __msg__=msg, **kwds)

    def test_match_w_window(self):
        otp = self.randotp()
        period = otp.period
        time = self.randtime()
        token = otp.generate(time).token
        common = dict(otp=otp, gen_time=time)
        assertMatches = partial(self.assertVerifyMatches, **common)
        assertRaises = partial(self.assertVerifyRaises, **common)
        assertRaises(exc.InvalidTokenError, token, time - period, window=0)
        assertMatches(+1, token, time - period, window=period)
        assertMatches(+1, token, time - period, window=2 * period)
        assertMatches(0, token, time, window=0)
        assertRaises(exc.InvalidTokenError, token, time + period, window=0)
        assertMatches(-1, token, time + period, window=period)
        assertMatches(-1, token, time + period, window=2 * period)
        assertRaises(exc.InvalidTokenError, token, time + 2 * period, window=0)
        assertRaises(exc.InvalidTokenError, token, time + 2 * period, window=period)
        assertMatches(-2, token, time + 2 * period, window=2 * period)
        dt = datetime.datetime.utcfromtimestamp(time)
        assertMatches(0, token, dt, window=0)
        assertRaises(ValueError, token, -1)

    def test_match_w_skew(self):
        otp = self.randotp()
        period = otp.period
        time = self.randtime()
        common = dict(otp=otp, gen_time=time)
        assertMatches = partial(self.assertVerifyMatches, **common)
        assertRaises = partial(self.assertVerifyRaises, **common)
        skew = 3 * period
        behind_token = otp.generate(time - skew).token
        assertRaises(exc.InvalidTokenError, behind_token, time, window=0)
        assertMatches(-3, behind_token, time, window=0, skew=-skew)
        ahead_token = otp.generate(time + skew).token
        assertRaises(exc.InvalidTokenError, ahead_token, time, window=0)
        assertMatches(+3, ahead_token, time, window=0, skew=skew)

    def test_match_w_reuse(self):
        otp = self.randotp()
        period = otp.period
        time = self.randtime()
        tdata = otp.generate(time)
        token = tdata.token
        counter = tdata.counter
        expire_time = tdata.expire_time
        common = dict(otp=otp, gen_time=time)
        assertMatches = partial(self.assertVerifyMatches, **common)
        assertRaises = partial(self.assertVerifyRaises, **common)
        assertMatches(-1, token, time + period, window=period)
        assertMatches(-1, token, time + period, last_counter=counter - 1, window=period)
        assertRaises(exc.InvalidTokenError, token, time + 2 * period, last_counter=counter, window=period)
        err = assertRaises(exc.UsedTokenError, token, time + period, last_counter=counter, window=period)
        self.assertEqual(err.expire_time, expire_time)
        err = assertRaises(exc.UsedTokenError, token, time, last_counter=counter, window=0)
        self.assertEqual(err.expire_time, expire_time)

    def test_match_w_token_normalization(self):
        otp = TOTP('otxl2f5cctbprpzx')
        match = otp.match
        time = 1412889861
        self.assertTrue(match('    3 32-136  ', time))
        self.assertTrue(match('332136', time))
        self.assertRaises(exc.MalformedTokenError, match, '12345', time)
        self.assertRaises(exc.MalformedTokenError, match, '12345X', time)
        self.assertRaises(exc.MalformedTokenError, match, '0123456', time)

    def test_match_w_reference_vectors(self):
        for otp, time, token, expires, msg in self.iter_test_vectors():
            match = otp.match
            result = match(token, time)
            self.assertTrue(result)
            self.assertEqual(result.counter, time // otp.period, msg=msg)
            self.assertRaises(exc.InvalidTokenError, match, token, time + 100, window=0)

    def test_verify(self):
        from otp.ai.passlib.totp import TOTP
        time = 1412889861
        TotpFactory = TOTP.using(now=lambda : time)
        source1 = dict(v=1, type='totp', key='otxl2f5cctbprpzx')
        match = TotpFactory.verify('332136', source1)
        self.assertTotpMatch(match, time=time)
        source1 = dict(v=1, type='totp', key='otxl2f5cctbprpzx')
        self.assertRaises(exc.InvalidTokenError, TotpFactory.verify, '332155', source1)
        source1 = dict(v=1, type='totp')
        self.assertRaises(ValueError, TotpFactory.verify, '332155', source1)
        source1json = '{"v": 1, "type": "totp", "key": "otxl2f5cctbprpzx"}'
        match = TotpFactory.verify('332136', source1json)
        self.assertTotpMatch(match, time=time)
        source1uri = 'otpauth://totp/Label?secret=otxl2f5cctbprpzx'
        match = TotpFactory.verify('332136', source1uri)
        self.assertTotpMatch(match, time=time)

    def test_from_source(self):
        from otp.ai.passlib.totp import TOTP
        from_source = TOTP.from_source
        otp = from_source(u('otpauth://totp/Example:alice@google.com?secret=JBSWY3DPEHPK3PXP&issuer=Example'))
        self.assertEqual(otp.key, KEY4_RAW)
        otp = from_source('otpauth://totp/Example:alice@google.com?secret=JBSWY3DPEHPK3PXP&issuer=Example')
        self.assertEqual(otp.key, KEY4_RAW)
        otp = from_source(dict(v=1, type='totp', key=KEY4))
        self.assertEqual(otp.key, KEY4_RAW)
        otp = from_source(u('{"v": 1, "type": "totp", "key": "JBSWY3DPEHPK3PXP"}'))
        self.assertEqual(otp.key, KEY4_RAW)
        otp = from_source('{"v": 1, "type": "totp", "key": "JBSWY3DPEHPK3PXP"}')
        self.assertEqual(otp.key, KEY4_RAW)
        self.assertIs(from_source(otp), otp)
        wallet1 = AppWallet()
        otp1 = TOTP.using(wallet=wallet1).from_source(otp)
        self.assertIsNot(otp1, otp)
        self.assertEqual(otp1.to_dict(), otp.to_dict())
        otp2 = TOTP.using(wallet=wallet1).from_source(otp1)
        self.assertIs(otp2, otp1)
        self.assertRaises(ValueError, from_source, u('foo'))
        self.assertRaises(ValueError, from_source, 'foo')

    def test_from_uri(self):
        from otp.ai.passlib.totp import TOTP
        from_uri = TOTP.from_uri
        otp = from_uri('otpauth://totp/Example:alice@google.com?secret=JBSWY3DPEHPK3PXP&issuer=Example')
        self.assertIsInstance(otp, TOTP)
        self.assertEqual(otp.key, KEY4_RAW)
        self.assertEqual(otp.label, 'alice@google.com')
        self.assertEqual(otp.issuer, 'Example')
        self.assertEqual(otp.alg, 'sha1')
        self.assertEqual(otp.period, 30)
        self.assertEqual(otp.digits, 6)
        otp = from_uri('otpauth://totp/Example:alice@google.com?secret=jbswy3dpehpk3pxp&issuer=Example')
        self.assertEqual(otp.key, KEY4_RAW)
        self.assertRaises(ValueError, from_uri, 'otpauth://totp/Example:alice@google.com?digits=6')
        self.assertRaises(Base32DecodeError, from_uri, 'otpauth://totp/Example:alice@google.com?secret=JBSWY3DPEHP@3PXP')
        otp = from_uri('otpauth://totp/Provider1:Alice%20Smith?secret=JBSWY3DPEHPK3PXP&issuer=Provider1')
        self.assertEqual(otp.label, 'Alice Smith')
        self.assertEqual(otp.issuer, 'Provider1')
        otp = from_uri('otpauth://totp/Big%20Corporation%3A%20alice@bigco.com?secret=JBSWY3DPEHPK3PXP')
        self.assertEqual(otp.label, 'alice@bigco.com')
        self.assertEqual(otp.issuer, 'Big Corporation')
        otp = from_uri('otpauth://totp/alice@bigco.com?secret=JBSWY3DPEHPK3PXP&issuer=Big%20Corporation')
        self.assertEqual(otp.label, 'alice@bigco.com')
        self.assertEqual(otp.issuer, 'Big Corporation')
        self.assertRaises(ValueError, TOTP.from_uri, 'otpauth://totp/Provider1:alice?secret=JBSWY3DPEHPK3PXP&issuer=Provider2')
        otp = from_uri('otpauth://totp/Example:alice@google.com?secret=JBSWY3DPEHPK3PXP&algorithm=SHA256')
        self.assertEqual(otp.alg, 'sha256')
        self.assertRaises(ValueError, from_uri, 'otpauth://totp/Example:alice@google.com?secret=JBSWY3DPEHPK3PXP&algorithm=SHA333')
        otp = from_uri('otpauth://totp/Example:alice@google.com?secret=JBSWY3DPEHPK3PXP&digits=8')
        self.assertEqual(otp.digits, 8)
        self.assertRaises(ValueError, from_uri, 'otpauth://totp/Example:alice@google.com?secret=JBSWY3DPEHPK3PXP&digits=A')
        self.assertRaises(ValueError, from_uri, 'otpauth://totp/Example:alice@google.com?secret=JBSWY3DPEHPK3PXP&digits=%20')
        self.assertRaises(ValueError, from_uri, 'otpauth://totp/Example:alice@google.com?secret=JBSWY3DPEHPK3PXP&digits=15')
        otp = from_uri('otpauth://totp/Example:alice@google.com?secret=JBSWY3DPEHPK3PXP&period=63')
        self.assertEqual(otp.period, 63)
        self.assertRaises(ValueError, from_uri, 'otpauth://totp/Example:alice@google.com?secret=JBSWY3DPEHPK3PXP&period=0')
        self.assertRaises(ValueError, from_uri, 'otpauth://totp/Example:alice@google.com?secret=JBSWY3DPEHPK3PXP&period=-1')
        with self.assertWarningList([
         dict(category=exc.PasslibRuntimeWarning, message_re='unexpected parameters encountered')]):
            otp = from_uri('otpauth://totp/Example:alice@google.com?secret=JBSWY3DPEHPK3PXP&foo=bar&period=63')
        self.assertEqual(otp.base32_key, KEY4)
        self.assertEqual(otp.period, 63)

    def test_to_uri(self):
        otp = TOTP(KEY4, alg='sha1', digits=6, period=30)
        self.assertEqual(otp.to_uri('alice@google.com', 'Example Org'), 'otpauth://totp/alice@google.com?secret=JBSWY3DPEHPK3PXP&issuer=Example%20Org')
        self.assertRaises(ValueError, otp.to_uri, None, 'Example Org')
        self.assertEqual(otp.to_uri('alice@google.com'), 'otpauth://totp/alice@google.com?secret=JBSWY3DPEHPK3PXP')
        otp.label = 'alice@google.com'
        self.assertEqual(otp.to_uri(), 'otpauth://totp/alice@google.com?secret=JBSWY3DPEHPK3PXP')
        otp.issuer = 'Example Org'
        self.assertEqual(otp.to_uri(), 'otpauth://totp/alice@google.com?secret=JBSWY3DPEHPK3PXP&issuer=Example%20Org')
        self.assertRaises(ValueError, otp.to_uri, 'label:with:semicolons')
        self.assertRaises(ValueError, otp.to_uri, 'alice@google.com', 'issuer:with:semicolons')
        self.assertEqual(TOTP(KEY4, alg='sha256').to_uri('alice@google.com'), 'otpauth://totp/alice@google.com?secret=JBSWY3DPEHPK3PXP&algorithm=SHA256')
        self.assertEqual(TOTP(KEY4, digits=8).to_uri('alice@google.com'), 'otpauth://totp/alice@google.com?secret=JBSWY3DPEHPK3PXP&digits=8')
        self.assertEqual(TOTP(KEY4, period=63).to_uri('alice@google.com'), 'otpauth://totp/alice@google.com?secret=JBSWY3DPEHPK3PXP&period=63')
        return

    def test_from_dict(self):
        from otp.ai.passlib.totp import TOTP
        from_dict = TOTP.from_dict
        otp = from_dict(dict(v=1, type='totp', key=KEY4, label='alice@google.com', issuer='Example'))
        self.assertIsInstance(otp, TOTP)
        self.assertEqual(otp.key, KEY4_RAW)
        self.assertEqual(otp.label, 'alice@google.com')
        self.assertEqual(otp.issuer, 'Example')
        self.assertEqual(otp.alg, 'sha1')
        self.assertEqual(otp.period, 30)
        self.assertEqual(otp.digits, 6)
        self.assertRaises(ValueError, from_dict, dict(type='totp', key=KEY4))
        self.assertRaises(ValueError, from_dict, dict(v=0, type='totp', key=KEY4))
        self.assertRaises(ValueError, from_dict, dict(v=999, type='totp', key=KEY4))
        self.assertRaises(ValueError, from_dict, dict(v=1, key=KEY4))
        otp = from_dict(dict(v=1, type='totp', key=KEY4.lower(), label='alice@google.com', issuer='Example'))
        self.assertEqual(otp.key, KEY4_RAW)
        self.assertRaises(ValueError, from_dict, dict(v=1, type='totp'))
        self.assertRaises(Base32DecodeError, from_dict, dict(v=1, type='totp', key='JBSWY3DPEHP@3PXP'))
        otp = from_dict(dict(v=1, type='totp', key=KEY4, label='Alice Smith', issuer='Provider1'))
        self.assertEqual(otp.label, 'Alice Smith')
        self.assertEqual(otp.issuer, 'Provider1')
        otp = from_dict(dict(v=1, type='totp', key=KEY4, alg='sha256'))
        self.assertEqual(otp.alg, 'sha256')
        self.assertRaises(ValueError, from_dict, dict(v=1, type='totp', key=KEY4, alg='sha333'))
        otp = from_dict(dict(v=1, type='totp', key=KEY4, digits=8))
        self.assertEqual(otp.digits, 8)
        self.assertRaises(TypeError, from_dict, dict(v=1, type='totp', key=KEY4, digits='A'))
        self.assertRaises(ValueError, from_dict, dict(v=1, type='totp', key=KEY4, digits=15))
        otp = from_dict(dict(v=1, type='totp', key=KEY4, period=63))
        self.assertEqual(otp.period, 63)
        self.assertRaises(ValueError, from_dict, dict(v=1, type='totp', key=KEY4, period=0))
        self.assertRaises(ValueError, from_dict, dict(v=1, type='totp', key=KEY4, period=-1))
        self.assertRaises(TypeError, from_dict, dict(v=1, type='totp', key=KEY4, INVALID=123))

    def test_to_dict(self):
        otp = TOTP(KEY4, alg='sha1', digits=6, period=30)
        self.assertEqual(otp.to_dict(), dict(v=1, type='totp', key=KEY4))
        otp = TOTP(KEY4, alg='sha1', digits=6, period=30, label='alice@google.com', issuer='Example Org')
        self.assertEqual(otp.to_dict(), dict(v=1, type='totp', key=KEY4, label='alice@google.com', issuer='Example Org'))
        otp = TOTP(KEY4, alg='sha1', digits=6, period=30, label='alice@google.com')
        self.assertEqual(otp.to_dict(), dict(v=1, type='totp', key=KEY4, label='alice@google.com'))
        otp = TOTP(KEY4, alg='sha1', digits=6, period=30, issuer='Example Org')
        self.assertEqual(otp.to_dict(), dict(v=1, type='totp', key=KEY4, issuer='Example Org'))
        TotpFactory = TOTP.using(issuer='Example Org')
        otp = TotpFactory(KEY4)
        self.assertEqual(otp.to_dict(), dict(v=1, type='totp', key=KEY4))
        otp = TotpFactory(KEY4, issuer='Example Org')
        self.assertEqual(otp.to_dict(), dict(v=1, type='totp', key=KEY4))
        self.assertEqual(TOTP(KEY4, alg='sha256').to_dict(), dict(v=1, type='totp', key=KEY4, alg='sha256'))
        self.assertEqual(TOTP(KEY4, digits=8).to_dict(), dict(v=1, type='totp', key=KEY4, digits=8))
        self.assertEqual(TOTP(KEY4, period=63).to_dict(), dict(v=1, type='totp', key=KEY4, period=63))