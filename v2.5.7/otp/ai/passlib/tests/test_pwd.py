import itertools, logging
log = logging.getLogger(__name__)
from otp.ai.passlib.tests.utils import TestCase
__all__ = [
 'UtilsTest',
 'GenerateTest',
 'StrengthTest']

class UtilsTest(TestCase):
    descriptionPrefix = 'passlib.pwd'

    def test_self_info_rate(self):
        from otp.ai.passlib.pwd import _self_info_rate
        self.assertEqual(_self_info_rate(''), 0)
        self.assertEqual(_self_info_rate('aaaaaaaa'), 0)
        self.assertEqual(_self_info_rate('ab'), 1)
        self.assertEqual(_self_info_rate('abababababababab'), 1)
        self.assertEqual(_self_info_rate('abcd'), 2)
        self.assertEqual(_self_info_rate('abcd' * 8), 2)
        self.assertAlmostEqual(_self_info_rate('abcdaaaa'), 1.5488, places=4)


from otp.ai.passlib.pwd import genword, default_charsets
ascii_62 = default_charsets['ascii_62']
hex = default_charsets['hex']

class WordGeneratorTest(TestCase):
    descriptionPrefix = 'passlib.pwd.genword()'

    def setUp(self):
        super(WordGeneratorTest, self).setUp()
        from otp.ai.passlib.pwd import SequenceGenerator
        self.patchAttr(SequenceGenerator, 'rng', self.getRandom('pwd generator'))

    def assertResultContents(self, results, count, chars, unique=True):
        self.assertEqual(len(results), count)
        if unique:
            if unique is True:
                unique = count
            self.assertEqual(len(set(results)), unique)
        self.assertEqual(set(('').join(results)), set(chars))

    def test_general(self):
        result = genword()
        self.assertEqual(len(result), 9)
        self.assertRaisesRegex(TypeError, '(?i)unexpected keyword.*badkwd', genword, badkwd=True)

    def test_returns(self):
        results = genword(returns=5000)
        self.assertResultContents(results, 5000, ascii_62)
        gen = genword(returns=iter)
        results = [ next(gen) for _ in range(5000) ]
        self.assertResultContents(results, 5000, ascii_62)
        self.assertRaises(TypeError, genword, returns='invalid-type')

    def test_charset(self):
        results = genword(charset='hex', returns=5000)
        self.assertResultContents(results, 5000, hex)
        results = genword(length=3, chars='abc', returns=5000)
        self.assertResultContents(results, 5000, 'abc', unique=27)
        self.assertRaises(TypeError, genword, chars='abc', charset='hex')


from otp.ai.passlib.pwd import genphrase
simple_words = [
 'alpha', 'beta', 'gamma']

class PhraseGeneratorTest(TestCase):
    descriptionPrefix = 'passlib.pwd.genphrase()'

    def assertResultContents(self, results, count, words, unique=True, sep=' '):
        self.assertEqual(len(results), count)
        if unique:
            if unique is True:
                unique = count
            self.assertEqual(len(set(results)), unique)
        out = set(itertools.chain.from_iterable(elem.split(sep) for elem in results))
        self.assertEqual(out, set(words))

    def test_general(self):
        result = genphrase()
        self.assertEqual(len(result.split(' ')), 4)
        self.assertRaisesRegex(TypeError, '(?i)unexpected keyword.*badkwd', genphrase, badkwd=True)

    def test_entropy(self):
        result = genphrase(entropy=70)
        self.assertEqual(len(result.split(' ')), 6)
        result = genphrase(length=3)
        self.assertEqual(len(result.split(' ')), 3)
        result = genphrase(length=3, entropy=48)
        self.assertEqual(len(result.split(' ')), 4)
        result = genphrase(length=4, entropy=12)
        self.assertEqual(len(result.split(' ')), 4)

    def test_returns(self):
        results = genphrase(returns=1000, words=simple_words)
        self.assertResultContents(results, 1000, simple_words)
        gen = genphrase(returns=iter, words=simple_words)
        results = [ next(gen) for _ in range(1000) ]
        self.assertResultContents(results, 1000, simple_words)
        self.assertRaises(TypeError, genphrase, returns='invalid-type')

    def test_wordset(self):
        results = genphrase(words=simple_words, returns=5000)
        self.assertResultContents(results, 5000, simple_words)
        results = genphrase(length=3, words=simple_words, returns=5000)
        self.assertResultContents(results, 5000, simple_words, unique=27)
        self.assertRaises(TypeError, genphrase, words=simple_words, wordset='bip39')