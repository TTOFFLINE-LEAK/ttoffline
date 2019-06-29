from __future__ import absolute_import, division, print_function, unicode_literals
import codecs
from collections import defaultdict, MutableMapping
from math import ceil, log as logf
import logging
log = logging.getLogger(__name__)
import pkg_resources, os
from otp.ai.passlib import exc
from otp.ai.passlib.utils.compat import PY2, irange, itervalues, int_types
from otp.ai.passlib.utils import rng, getrandstr, to_unicode
from otp.ai.passlib.utils.decor import memoized_property
__all__ = [
 'genword', 'default_charsets',
 'genphrase', 'default_wordsets']
entropy_aliases = dict(unsafe=12, weak=24, fair=36, strong=48, secure=60)

def _superclasses(obj, cls):
    mro = type(obj).__mro__
    return mro[mro.index(cls) + 1:]


def _self_info_rate(source):
    try:
        size = len(source)
    except TypeError:
        size = None
    else:
        counts = defaultdict(int)
        for char in source:
            counts[char] += 1

        if size is None:
            values = counts.values()
            size = sum(values)
        else:
            values = itervalues(counts)
        if not size:
            return 0

    return logf(size, 2) - sum(value * logf(value, 2) for value in values) / size


def _open_asset_path(path, encoding=None):
    if encoding:
        return codecs.getreader(encoding)(_open_asset_path(path))
    if os.path.isabs(path):
        return open(path, 'rb')
    package, sep, subpath = path.partition(':')
    if not sep:
        raise ValueError("asset path must be absolute file path or use 'pkg.name:sub/path' format: %r" % (
         path,))
    return pkg_resources.resource_stream(package, subpath)


_sequence_types = (
 list, tuple)
_set_types = (set, frozenset)
_ensure_unique_cache = set()

def _ensure_unique(source, param='source'):
    cache = _ensure_unique_cache
    hashable = True
    try:
        if source in cache:
            return True
    except TypeError:
        hashable = False

    if isinstance(source, _set_types) or len(set(source)) == len(source):
        if hashable:
            try:
                cache.add(source)
            except TypeError:
                pass

        return True
    seen = set()
    dups = set()
    for elem in source:
        (dups if elem in seen else seen).add(elem)

    dups = sorted(dups)
    trunc = 8
    if len(dups) > trunc:
        trunc = 5
    dup_repr = (', ').join(repr(str(word)) for word in dups[:trunc])
    if len(dups) > trunc:
        dup_repr += ', ... plus %d others' % (len(dups) - trunc)
    raise ValueError('`%s` cannot contain duplicate elements: %s' % (
     param, dup_repr))


class SequenceGenerator(object):
    length = None
    requested_entropy = 'strong'
    rng = rng
    symbol_count = None

    def __init__(self, entropy=None, length=None, rng=None, **kwds):
        if entropy is not None or length is None:
            if entropy is None:
                entropy = self.requested_entropy
            entropy = entropy_aliases.get(entropy, entropy)
            if entropy <= 0:
                raise ValueError('`entropy` must be positive number')
            min_length = int(ceil(entropy / self.entropy_per_symbol))
            if length is None or length < min_length:
                length = min_length
        self.requested_entropy = entropy
        if length < 1:
            raise ValueError('`length` must be positive integer')
        self.length = length
        if rng is not None:
            self.rng = rng
        if kwds and _superclasses(self, SequenceGenerator) == (object,):
            raise TypeError('Unexpected keyword(s): %s' % (', ').join(kwds.keys()))
        super(SequenceGenerator, self).__init__(**kwds)
        return

    @memoized_property
    def entropy_per_symbol(self):
        return logf(self.symbol_count, 2)

    @memoized_property
    def entropy(self):
        return self.length * self.entropy_per_symbol

    def __next__(self):
        raise NotImplementedError('implement in subclass')

    def __call__(self, returns=None):
        if returns is None:
            return next(self)
        if isinstance(returns, int_types):
            return [ next(self) for _ in irange(returns) ]
        if returns is iter:
            return self
        raise exc.ExpectedTypeError(returns, '<None>, int, or <iter>', 'returns')
        return

    def __iter__(self):
        return self

    if PY2:

        def next(self):
            return self.__next__()


default_charsets = dict(ascii_72='0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*?/', ascii_62='0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ', ascii_50='234679abcdefghjkmnpqrstuvwxyzACDEFGHJKMNPQRTUVWXYZ', hex='0123456789abcdef')

class WordGenerator(SequenceGenerator):
    charset = 'ascii_62'
    chars = None

    def __init__(self, chars=None, charset=None, **kwds):
        if chars:
            if charset:
                raise TypeError('`chars` and `charset` are mutually exclusive')
        else:
            if not charset:
                charset = self.charset
            chars = default_charsets[charset]
        self.charset = charset
        chars = to_unicode(chars, param='chars')
        _ensure_unique(chars, param='chars')
        self.chars = chars
        super(WordGenerator, self).__init__(**kwds)

    @memoized_property
    def symbol_count(self):
        return len(self.chars)

    def __next__(self):
        return getrandstr(self.rng, self.chars, self.length)


def genword(entropy=None, length=None, returns=None, **kwds):
    gen = WordGenerator(length=length, entropy=entropy, **kwds)
    return gen(returns)


def _load_wordset(asset_path):
    with _open_asset_path(asset_path, 'utf-8') as (fh):
        gen = (word.strip() for word in fh)
        words = tuple(word for word in gen if word)
    log.debug('loaded %d-element wordset from %r', len(words), asset_path)
    return words


class WordsetDict(MutableMapping):
    paths = None
    _loaded = None

    def __init__(self, *args, **kwds):
        self.paths = {}
        self._loaded = {}
        super(WordsetDict, self).__init__(*args, **kwds)

    def __getitem__(self, key):
        try:
            return self._loaded[key]
        except KeyError:
            pass

        path = self.paths[key]
        value = self._loaded[key] = _load_wordset(path)
        return value

    def set_path(self, key, path):
        self.paths[key] = path

    def __setitem__(self, key, value):
        self._loaded[key] = value

    def __delitem__(self, key):
        if key in self:
            del self._loaded[key]
            self.paths.pop(key, None)
        else:
            del self.paths[key]
        return

    @property
    def _keyset(self):
        keys = set(self._loaded)
        keys.update(self.paths)
        return keys

    def __iter__(self):
        return iter(self._keyset)

    def __len__(self):
        return len(self._keyset)

    def __contains__(self, key):
        return key in self._loaded or key in self.paths


default_wordsets = WordsetDict()
for name in ('eff_long eff_short eff_prefixed bip39').split():
    default_wordsets.set_path(name, 'passlib:_data/wordsets/%s.txt' % name)

class PhraseGenerator(SequenceGenerator):
    wordset = 'eff_long'
    words = None
    sep = ' '

    def __init__(self, wordset=None, words=None, sep=None, **kwds):
        if words is not None:
            if wordset is not None:
                raise TypeError('`words` and `wordset` are mutually exclusive')
        else:
            if wordset is None:
                wordset = self.wordset
            words = default_wordsets[wordset]
        self.wordset = wordset
        if not isinstance(words, _sequence_types):
            words = tuple(words)
        _ensure_unique(words, param='words')
        self.words = words
        if sep is None:
            sep = self.sep
        sep = to_unicode(sep, param='sep')
        self.sep = sep
        super(PhraseGenerator, self).__init__(**kwds)
        return

    @memoized_property
    def symbol_count(self):
        return len(self.words)

    def __next__(self):
        words = (self.rng.choice(self.words) for _ in irange(self.length))
        return self.sep.join(words)


def genphrase(entropy=None, length=None, returns=None, **kwds):
    gen = PhraseGenerator(entropy=entropy, length=length, **kwds)
    return gen(returns)