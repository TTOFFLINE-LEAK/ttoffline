from __future__ import with_statement, division
from functools import partial
from otp.ai.passlib.utils import getrandbytes
from otp.ai.passlib.tests.utils import TestCase

class DesTest(TestCase):
    descriptionPrefix = 'passlib.crypto.des'
    des_test_vectors = [
     (0, 0, 10134873677816210343L),
     (18446744073709551615L, 18446744073709551615L, 8311870395893341272L),
     (3458764513820540928L, 1152921504606846977L, 10776672327577195899L),
     (1229782938247303441L, 1229782938247303441L, 17583031148182684979L),
     (81985529216486895L, 1229782938247303441L, 1686191225890296621L),
     (1229782938247303441L, 81985529216486895L, 9969529180854481629L),
     (0, 0, 10134873677816210343L),
     (18364758544493064720L, 81985529216486895L, 17093932802483993796L),
     (8980477021735513687L, 117611255094011714L, 7570369612612015003L),
     (86088881178490734L, 6689337107006052314L, 8806961764262204017L),
     (549741787767056006L, 164614723499094386L, 9695893007742818714L),
     (4055886516176695710L, 5856169732564009994L, 8176434030039898922L),
     (340327136592049590L, 4827089350059065250L, 12625836341772173461L),
     (77609513531011790L, 404019981405066298L, 9702267560690899035L),
     (103848277426812390L, 528848464848052690L, 924322050668092425L),
     (4839539656546808830L, 8513233451820730474L, 16890586767283661690L),
     (551430852305365526L, 4313623329492117506L, 16129161034940226063L),
     (317663223366892335L, 2780233246153072794L, 6652164766532288648L),
     (4021832892757538118L, 1607044272340030002L, 732660321565846391L),
     (2236079052714821214L, 7711690988273491146L, 17229628950091290458L),
     (6359121586699264374L, 21346945391353954L, 9853609588653157974L),
     (168909270948622343L, 5191868619451491058L, 11671519704656251734L),
     (5294331816167286159L, 4860862602324950266L, 8052186200196056406L),
     (5742192969548264359L, 517143888688272018L, 3396528426238910892L),
     (5325890758360836543L, 215703803915661610L, 6515408130789920330L),
     (108949354149783254L, 2133963297529473218L, 6866867443762671169L),
     (2042522189576687599L, 3482745036057028954L, 7204282554404960147L),
     (72340172838076673L, 81985529216486895L, 7024271870936510720L),
     (2242545357694045710L, 81985529216486895L, 15822700226042971654L),
     (16212643094166696446L, 81985529216486895L, 17131642157689064647L),
     (0, 18446744073709551615L, 3843066582818235473L),
     (18446744073709551615L, 0, 14603677490891316142L),
     (81985529216486895L, 0, 15408028147960528141L),
     (18364758544493064720L, 18446744073709551615L, 3038715925749023474L)]

    def test_01_expand(self):
        from otp.ai.passlib.crypto.des import expand_des_key, shrink_des_key, _KDATA_MASK, INT_56_MASK
        for key1, _, _ in self.des_test_vectors:
            key2 = shrink_des_key(key1)
            key3 = expand_des_key(key2)
            self.assertEqual(key3, key1 & _KDATA_MASK)

        self.assertRaises(TypeError, expand_des_key, 1.0)
        self.assertRaises(ValueError, expand_des_key, INT_56_MASK + 1)
        self.assertRaises(ValueError, expand_des_key, '\x00\x00\x00\x00\x00\x00\x00\x00')
        self.assertRaises(ValueError, expand_des_key, -1)
        self.assertRaises(ValueError, expand_des_key, '\x00\x00\x00\x00\x00\x00')

    def test_02_shrink(self):
        from otp.ai.passlib.crypto.des import expand_des_key, shrink_des_key, INT_64_MASK
        rng = self.getRandom()
        for i in range(20):
            key1 = getrandbytes(rng, 7)
            key2 = expand_des_key(key1)
            key3 = shrink_des_key(key2)
            self.assertEqual(key3, key1)

        self.assertRaises(TypeError, shrink_des_key, 1.0)
        self.assertRaises(ValueError, shrink_des_key, INT_64_MASK + 1)
        self.assertRaises(ValueError, shrink_des_key, '\x00\x00\x00\x00\x00\x00\x00\x00\x00')
        self.assertRaises(ValueError, shrink_des_key, -1)
        self.assertRaises(ValueError, shrink_des_key, '\x00\x00\x00\x00\x00\x00\x00')

    def _random_parity(self, key):
        from otp.ai.passlib.crypto.des import _KDATA_MASK, _KPARITY_MASK, INT_64_MASK
        rng = self.getRandom()
        return key & _KDATA_MASK | rng.randint(0, INT_64_MASK) & _KPARITY_MASK

    def test_03_encrypt_bytes(self):
        from otp.ai.passlib.crypto.des import des_encrypt_block, shrink_des_key, _pack64, _unpack64
        for key, plaintext, correct in self.des_test_vectors:
            key = _pack64(key)
            plaintext = _pack64(plaintext)
            correct = _pack64(correct)
            result = des_encrypt_block(key, plaintext)
            self.assertEqual(result, correct, 'key=%r plaintext=%r:' % (
             key, plaintext))
            key2 = shrink_des_key(key)
            result = des_encrypt_block(key2, plaintext)
            self.assertEqual(result, correct, 'key=%r shrink(key)=%r plaintext=%r:' % (
             key, key2, plaintext))
            for _ in range(20):
                key3 = _pack64(self._random_parity(_unpack64(key)))
                result = des_encrypt_block(key3, plaintext)
                self.assertEqual(result, correct, 'key=%r rndparity(key)=%r plaintext=%r:' % (
                 key, key3, plaintext))

        stub = '\x00\x00\x00\x00\x00\x00\x00\x00'
        self.assertRaises(TypeError, des_encrypt_block, 0, stub)
        self.assertRaises(ValueError, des_encrypt_block, '\x00\x00\x00\x00\x00\x00', stub)
        self.assertRaises(TypeError, des_encrypt_block, stub, 0)
        self.assertRaises(ValueError, des_encrypt_block, stub, '\x00\x00\x00\x00\x00\x00\x00')
        self.assertRaises(ValueError, des_encrypt_block, stub, stub, salt=-1)
        self.assertRaises(ValueError, des_encrypt_block, stub, stub, salt=16777216)
        self.assertRaises(ValueError, des_encrypt_block, stub, stub, 0, rounds=0)

    def test_04_encrypt_ints(self):
        from otp.ai.passlib.crypto.des import des_encrypt_int_block
        for key, plaintext, correct in self.des_test_vectors:
            result = des_encrypt_int_block(key, plaintext)
            self.assertEqual(result, correct, 'key=%r plaintext=%r:' % (
             key, plaintext))
            for _ in range(20):
                key3 = self._random_parity(key)
                result = des_encrypt_int_block(key3, plaintext)
                self.assertEqual(result, correct, 'key=%r rndparity(key)=%r plaintext=%r:' % (
                 key, key3, plaintext))

        self.assertRaises(TypeError, des_encrypt_int_block, '\x00', 0)
        self.assertRaises(ValueError, des_encrypt_int_block, -1, 0)
        self.assertRaises(TypeError, des_encrypt_int_block, 0, '\x00')
        self.assertRaises(ValueError, des_encrypt_int_block, 0, -1)
        self.assertRaises(ValueError, des_encrypt_int_block, 0, 0, salt=-1)
        self.assertRaises(ValueError, des_encrypt_int_block, 0, 0, salt=16777216)
        self.assertRaises(ValueError, des_encrypt_int_block, 0, 0, 0, rounds=0)