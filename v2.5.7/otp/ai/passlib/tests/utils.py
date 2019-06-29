from __future__ import with_statement
from binascii import unhexlify
import contextlib
from functools import wraps, partial
import hashlib, logging
log = logging.getLogger(__name__)
import random, re, os, sys, tempfile, threading, time
from otp.ai.passlib.exc import PasslibHashWarning, PasslibConfigWarning
from otp.ai.passlib.utils.compat import PY3, JYTHON
import warnings
from warnings import warn
from otp.ai.passlib import exc
from otp.ai.passlib.exc import MissingBackendError
import otp.ai.passlib.registry as registry
from otp.ai.passlib.tests.backports import TestCase as _TestCase, skip, skipIf, skipUnless, SkipTest
from otp.ai.passlib.utils import has_rounds_info, has_salt_info, rounds_cost_values, rng as sys_rng, getrandstr, is_ascii_safe, to_native_str, repeat_string, tick, batch
from otp.ai.passlib.utils.compat import iteritems, irange, u, unicode, PY2
from otp.ai.passlib.utils.decor import classproperty
import otp.ai.passlib.utils.handlers as uh
__all__ = [
 'TEST_MODE',
 'set_file', 'get_file',
 'TestCase',
 'HandlerCase']
try:
    import google.appengine
except ImportError:
    GAE = False
else:
    GAE = True

def ensure_mtime_changed(path):
    last = os.path.getmtime(path)
    while os.path.getmtime(path) == last:
        time.sleep(0.1)
        os.utime(path, None)

    return


def _get_timer_resolution(timer):

    def sample():
        start = cur = timer()
        while start == cur:
            cur = timer()

        return cur - start

    return min(sample() for _ in range(3))


TICK_RESOLUTION = _get_timer_resolution(tick)
_TEST_MODES = [
 'quick', 'default', 'full']
_test_mode = _TEST_MODES.index(os.environ.get('PASSLIB_TEST_MODE', 'default').strip().lower())

def TEST_MODE(min=None, max=None):
    if min and _test_mode < _TEST_MODES.index(min):
        return False
    if max and _test_mode > _TEST_MODES.index(max):
        return False
    return True


def has_relaxed_setting(handler):
    if hasattr(handler, 'orig_prefix'):
        return False
    return 'relaxed' in handler.setting_kwds or issubclass(handler, uh.GenericHandler)


def get_effective_rounds(handler, rounds=None):
    handler = unwrap_handler(handler)
    return handler(rounds=rounds, use_defaults=True).rounds


def is_default_backend(handler, backend):
    try:
        orig = handler.get_backend()
    except MissingBackendError:
        return False

    try:
        handler.set_backend('default')
        return handler.get_backend() == backend
    finally:
        handler.set_backend(orig)


def iter_alt_backends(handler, current=None, fallback=False):
    if current is None:
        current = handler.get_backend()
    backends = handler.backends
    idx = backends.index(current) + 1 if fallback else 0
    for backend in backends[idx:]:
        if backend != current and handler.has_backend(backend):
            yield backend

    return


def get_alt_backend(*args, **kwds):
    for backend in iter_alt_backends(*args, **kwds):
        return backend

    return


def unwrap_handler(handler):
    while hasattr(handler, 'wrapped'):
        handler = handler.wrapped

    return handler


def handler_derived_from(handler, base):
    if handler == base:
        return True
    if isinstance(handler, uh.PrefixWrapper):
        while handler:
            if handler == base:
                return True
            handler = handler._derived_from

        return False
    if isinstance(handler, type) and issubclass(handler, uh.MinimalHandler):
        return issubclass(handler, base)
    raise NotImplementedError("don't know how to inspect handler: %r" % (handler,))


@contextlib.contextmanager
def patch_calc_min_rounds(handler):
    if isinstance(handler, type) and issubclass(handler, uh.HasRounds):
        wrapped = handler._calc_checksum

        def wrapper(self, *args, **kwds):
            rounds = self.rounds
            try:
                self.rounds = self.min_rounds
                return wrapped(self, *args, **kwds)
            finally:
                self.rounds = rounds

        handler._calc_checksum = wrapper
        try:
            yield
        finally:
            handler._calc_checksum = wrapped

    else:
        if isinstance(handler, uh.PrefixWrapper):
            with patch_calc_min_rounds(handler.wrapped):
                yield
        else:
            yield
            return


def set_file(path, content):
    if isinstance(content, unicode):
        content = content.encode('utf-8')
    with open(path, 'wb') as (fh):
        fh.write(content)


def get_file(path):
    with open(path, 'rb') as (fh):
        return fh.read()


def tonn(source):
    if not isinstance(source, str):
        return source
    if PY3:
        return source.encode('utf-8')
    try:
        return source.decode('utf-8')
    except UnicodeDecodeError:
        return source.decode('latin-1')


def hb(source):
    return unhexlify(re.sub('\\s', '', source))


def limit(value, lower, upper):
    if value < lower:
        return lower
    if value > upper:
        return upper
    return value


def quicksleep(delay):
    start = tick()
    while tick() - start < delay:
        pass


def time_call(func, setup=None, maxtime=1, bestof=10):
    from timeit import Timer
    from math import log
    timer = Timer(func, setup=setup or '')
    number = 1
    end = tick() + maxtime
    while True:
        delta = min(timer.repeat(bestof, number))
        if tick() >= end:
            return (delta / number, int(log(number, 10)))
        number *= 10


def run_with_fixed_seeds(count=128, master_seed=2611923443488327891L):

    def builder(func):

        @wraps(func)
        def wrapper(*args, **kwds):
            rng = random.Random(master_seed)
            for _ in irange(count):
                kwds['seed'] = rng.getrandbits(32)
                func(*args, **kwds)

        return wrapper

    return builder


class TestCase(_TestCase):
    descriptionPrefix = None

    def shortDescription(self):
        desc = super(TestCase, self).shortDescription()
        prefix = self.descriptionPrefix
        if prefix:
            desc = '%s: %s' % (prefix, desc or str(self))
        return desc

    @classproperty
    def __unittest_skip__(cls):
        name = cls.__name__
        return name.startswith('_') or getattr(cls, '_%s__unittest_skip' % name, False)

    @classproperty
    def __test__(cls):
        return not cls.__unittest_skip__

    __unittest_skip = True
    resetWarningState = True

    def setUp(self):
        super(TestCase, self).setUp()
        self.setUpWarnings()

    def setUpWarnings(self):
        if self.resetWarningState:
            ctx = reset_warnings()
            ctx.__enter__()
            self.addCleanup(ctx.__exit__)
            warnings.filterwarnings('ignore', 'the method .*\\.(encrypt|genconfig|genhash)\\(\\) is deprecated')
            warnings.filterwarnings('ignore', "the 'vary_rounds' option is deprecated")

    longMessage = True

    def _formatMessage(self, msg, std):
        if self.longMessage and msg and msg.rstrip().endswith(':'):
            return '%s %s' % (msg.rstrip(), std)
        return msg or std

    def assertRaises(self, _exc_type, _callable=None, *args, **kwds):
        msg = kwds.pop('__msg__', None)
        if _callable is None:
            return super(TestCase, self).assertRaises(_exc_type, None, *args, **kwds)
        try:
            result = _callable(*args, **kwds)
        except _exc_type as err:
            return err

        std = 'function returned %r, expected it to raise %r' % (result,
         _exc_type)
        raise self.failureException(self._formatMessage(msg, std))
        return

    def assertEquals(self, *a, **k):
        raise AssertionError('this alias is deprecated by unittest2')

    assertNotEquals = assertRegexMatches = assertEquals

    def assertWarning(self, warning, message_re=None, message=None, category=None, filename_re=None, filename=None, lineno=None, msg=None):
        if hasattr(warning, 'category'):
            wmsg = warning
            warning = warning.message
        else:
            wmsg = None
        if message:
            self.assertEqual(str(warning), message, msg)
        if message_re:
            self.assertRegex(str(warning), message_re, msg)
        if category:
            self.assertIsInstance(warning, category, msg)
        if filename or filename_re:
            if not wmsg:
                raise TypeError('matching on filename requires a WarningMessage instance')
            real = wmsg.filename
            if real.endswith('.pyc') or real.endswith('.pyo'):
                real = real[:-1]
            if filename:
                self.assertEqual(real, filename, msg)
            if filename_re:
                self.assertRegex(real, filename_re, msg)
        if lineno:
            if not wmsg:
                raise TypeError('matching on lineno requires a WarningMessage instance')
            self.assertEqual(wmsg.lineno, lineno, msg)
        return

    class _AssertWarningList(warnings.catch_warnings):

        def __init__(self, case, **kwds):
            self.case = case
            self.kwds = kwds
            self.__super = super(TestCase._AssertWarningList, self)
            self.__super.__init__(record=True)

        def __enter__(self):
            self.log = self.__super.__enter__()

        def __exit__(self, *exc_info):
            self.__super.__exit__(*exc_info)
            if exc_info[0] is None:
                self.case.assertWarningList(self.log, **self.kwds)
            return

    def assertWarningList(self, wlist=None, desc=None, msg=None):
        if desc is None:
            return self._AssertWarningList(self, desc=wlist, msg=msg)
        if not isinstance(desc, (list, tuple)):
            desc = [
             desc]
        for idx, entry in enumerate(desc):
            if isinstance(entry, str):
                entry = dict(message_re=entry)
            else:
                if isinstance(entry, type) and issubclass(entry, Warning):
                    entry = dict(category=entry)
                else:
                    if not isinstance(entry, dict):
                        raise TypeError('entry must be str, warning, or dict')
            try:
                data = wlist[idx]
            except IndexError:
                break
            else:
                self.assertWarning(data, msg=msg, **entry)
        else:
            if len(wlist) == len(desc):
                return

        std = 'expected %d warnings, found %d: wlist=%s desc=%r' % (
         len(desc), len(wlist), self._formatWarningList(wlist), desc)
        raise self.failureException(self._formatMessage(msg, std))
        return

    def consumeWarningList(self, wlist, desc=None, *args, **kwds):
        if desc is None:
            desc = []
        self.assertWarningList(wlist, desc, *args, **kwds)
        del wlist[:]
        return

    def _formatWarning(self, entry):
        tail = ''
        if hasattr(entry, 'message'):
            tail = ' filename=%r lineno=%r' % (entry.filename, entry.lineno)
            if entry.line:
                tail += ' line=%r' % (entry.line,)
            entry = entry.message
        cls = type(entry)
        return '<%s.%s message=%r%s>' % (cls.__module__, cls.__name__,
         str(entry), tail)

    def _formatWarningList(self, wlist):
        return '[%s]' % (', ').join(self._formatWarning(entry) for entry in wlist)

    def require_stringprep(self):
        from otp.ai.passlib.utils import stringprep
        if not stringprep:
            from otp.ai.passlib.utils import _stringprep_missing_reason
            raise self.skipTest('not available - stringprep module is ' + _stringprep_missing_reason)

    def require_TEST_MODE(self, level):
        if not TEST_MODE(level):
            raise self.skipTest('requires >= %r test mode' % level)

    def require_writeable_filesystem(self):
        if GAE:
            return self.skipTest("GAE doesn't offer read/write filesystem access")

    _random_global_lock = threading.Lock()
    _random_global_seed = None
    _random_cache = None

    def getRandom(self, name='default', seed=None):
        cache = self._random_cache
        if cache and name in cache:
            return cache[name]
        with self._random_global_lock:
            cache = self._random_cache
            if cache and name in cache:
                return cache[name]
            if not cache:
                cache = self._random_cache = {}
            global_seed = seed or TestCase._random_global_seed
            if global_seed is None:
                global_seed = TestCase._random_global_seed = int(os.environ.get('RANDOM_TEST_SEED') or os.environ.get('PYTHONHASHSEED') or sys_rng.getrandbits(32))
                log.info('using RANDOM_TEST_SEED=%d', global_seed)
            cls = type(self)
            source = ('\n').join([str(global_seed), cls.__module__, cls.__name__,
             self._testMethodName, name])
            digest = hashlib.sha256(source.encode('utf-8')).hexdigest()
            seed = int(digest[:16], 16)
            value = cache[name] = random.Random(seed)
            return value
        return

    _mktemp_queue = None

    def mktemp(self, *args, **kwds):
        self.require_writeable_filesystem()
        fd, path = tempfile.mkstemp(*args, **kwds)
        os.close(fd)
        queue = self._mktemp_queue
        if queue is None:
            queue = self._mktemp_queue = []

            def cleaner():
                for path in queue:
                    if os.path.exists(path):
                        os.remove(path)

                del queue[:]

            self.addCleanup(cleaner)
        queue.append(path)
        return path

    def patchAttr(self, obj, attr, value, require_existing=True, wrap=False):
        try:
            orig = getattr(obj, attr)
        except AttributeError:
            if require_existing:
                raise

            def cleanup():
                try:
                    delattr(obj, attr)
                except AttributeError:
                    pass

            self.addCleanup(cleanup)
        else:
            self.addCleanup(setattr, obj, attr, orig)

        if wrap:
            value = partial(value, orig)
            wraps(orig)(value)
        setattr(obj, attr, value)


RESERVED_BACKEND_NAMES = [
 'any', 'default']

class HandlerCase(TestCase):
    handler = None
    backend = None
    known_correct_hashes = []
    known_correct_configs = []
    known_alternate_hashes = []
    known_unidentified_hashes = []
    known_malformed_hashes = []
    known_other_hashes = [
     ('des_crypt', '6f8c114b58f2c'),
     ('md5_crypt', '$1$dOHYPKoP$tnxS1T8Q6VVn3kpV8cN6o.'),
     ('sha512_crypt', '$6$rounds=123456$asaltof16chars..$BtCwjqMJGx5hrJhZywWvt0RLE8uZ4oPwcelCjmw2kSYu.Ec6ycULevoBK25fs2xXgMNrCzIMVcgEJAstJeonj1')]
    stock_passwords = [
     u('test'),
     u('\\u20AC\\u00A5$'),
     '\xe2\x82\xac\xc2\xa5$']
    secret_case_insensitive = False
    accepts_all_hashes = False
    disabled_contains_salt = False
    filter_config_warnings = False

    @classproperty
    def forbidden_characters(cls):
        if 'os_crypt' in getattr(cls.handler, 'backends', ()):
            return '\x00'
        return

    __unittest_skip = True

    @property
    def descriptionPrefix(self):
        handler = self.handler
        name = handler.name
        if hasattr(handler, 'get_backend'):
            name += ' (%s backend)' % (handler.get_backend(),)
        return name

    @classmethod
    def iter_known_hashes(cls):
        for secret, hash in cls.known_correct_hashes:
            yield (secret, hash)

        for config, secret, hash in cls.known_correct_configs:
            yield (
             secret, hash)

        for alt, secret, hash in cls.known_alternate_hashes:
            yield (
             secret, hash)

    def get_sample_hash(self):
        known = list(self.iter_known_hashes())
        return self.getRandom().choice(known)

    def check_verify(self, secret, hash, msg=None, negate=False):
        result = self.do_verify(secret, hash)
        self.assertTrue(result is True or result is False, 'verify() returned non-boolean value: %r' % (result,))
        if self.handler.is_disabled or negate:
            if not result:
                return
            if not msg:
                msg = 'verify incorrectly returned True: secret=%r, hash=%r' % (
                 secret, hash)
            raise self.failureException(msg)
        else:
            if result:
                return
            if not msg:
                msg = 'verify failed: secret=%r, hash=%r' % (secret, hash)
            raise self.failureException(msg)

    def check_returned_native_str(self, result, func_name):
        self.assertIsInstance(result, str, '%s() failed to return native string: %r' % (func_name, result))

    def populate_settings(self, kwds):
        handler = self.handler
        if 'rounds' in handler.setting_kwds and 'rounds' not in kwds:
            mn = handler.min_rounds
            df = handler.default_rounds
            if TEST_MODE(max='quick'):
                kwds['rounds'] = max(3, mn)
            else:
                factor = 3
                if getattr(handler, 'rounds_cost', None) == 'log2':
                    df -= factor
                else:
                    df //= 1 << factor
                kwds['rounds'] = max(3, mn, df)
        return

    def populate_context(self, secret, kwds):
        return secret

    def do_encrypt(self, secret, use_encrypt=False, handler=None, context=None, **settings):
        self.populate_settings(settings)
        if context is None:
            context = {}
        secret = self.populate_context(secret, context)
        if use_encrypt:
            warnings = []
            if settings:
                context.update(**settings)
                warnings.append('passing settings to.*is deprecated')
            with self.assertWarningList(warnings):
                return (handler or self.handler).encrypt(secret, **context)
        else:
            return (handler or self.handler).using(**settings).hash(secret, **context)
        return

    def do_verify(self, secret, hash, handler=None, **kwds):
        secret = self.populate_context(secret, kwds)
        return (handler or self.handler).verify(secret, hash, **kwds)

    def do_identify(self, hash):
        return self.handler.identify(hash)

    def do_genconfig(self, **kwds):
        self.populate_settings(kwds)
        return self.handler.genconfig(**kwds)

    def do_genhash(self, secret, config, **kwds):
        secret = self.populate_context(secret, kwds)
        return self.handler.genhash(secret, config, **kwds)

    def do_stub_encrypt(self, handler=None, context=None, **settings):
        handler = (handler or self.handler).using(**settings)
        if context is None:
            context = {}
        secret = self.populate_context('', context)
        with patch_calc_min_rounds(handler):
            return handler.hash(secret, **context)
        return

    BACKEND_NOT_AVAILABLE = 'backend not available'

    @classmethod
    def _get_skip_backend_reason(cls, backend):
        handler = cls.handler
        if not is_default_backend(handler, backend) and not TEST_MODE('full'):
            return 'only default backend is being tested'
        if handler.has_backend(backend):
            return None
        return cls.BACKEND_NOT_AVAILABLE

    @classmethod
    def create_backend_case(cls, backend):
        handler = cls.handler
        name = handler.name
        bases = (
         cls,)
        if backend == 'os_crypt':
            bases += (OsCryptMixin,)
        subcls = type('%s_%s_test' % (name, backend), bases, dict(descriptionPrefix='%s (%s backend)' % (name, backend), backend=backend, __module__=cls.__module__))
        skip_reason = cls._get_skip_backend_reason(backend)
        if skip_reason:
            subcls = skip(skip_reason)(subcls)
        return subcls

    def setUp(self):
        super(HandlerCase, self).setUp()
        handler = self.handler
        backend = self.backend
        if backend:
            if not hasattr(handler, 'set_backend'):
                raise RuntimeError("handler doesn't support multiple backends")
            self.addCleanup(handler.set_backend, handler.get_backend())
            handler.set_backend(backend)
        from otp.ai.passlib.utils import handlers
        self.patchAttr(handlers, 'rng', self.getRandom('salt generator'))

    def test_01_required_attributes(self):
        handler = self.handler

        def ga(name):
            return getattr(handler, name, None)

        name = ga('name')
        self.assertTrue(name, 'name not defined:')
        self.assertIsInstance(name, str, 'name must be native str')
        self.assertTrue(name.lower() == name, 'name not lower-case:')
        self.assertTrue(re.match('^[a-z0-9_]+$', name), 'name must be alphanum + underscore: %r' % (name,))
        settings = ga('setting_kwds')
        self.assertTrue(settings is not None, 'setting_kwds must be defined:')
        self.assertIsInstance(settings, tuple, 'setting_kwds must be a tuple:')
        context = ga('context_kwds')
        self.assertTrue(context is not None, 'context_kwds must be defined:')
        self.assertIsInstance(context, tuple, 'context_kwds must be a tuple:')
        return

    def test_02_config_workflow(self):
        config = self.do_genconfig()
        self.check_returned_native_str(config, 'genconfig')
        result = self.do_genhash('stub', config)
        self.check_returned_native_str(result, 'genhash')
        self.do_verify('', config)
        self.assertTrue(self.do_identify(config), 'identify() failed to identify genconfig() output: %r' % (
         config,))

    def test_02_using_workflow(self):
        handler = self.handler
        subcls = handler.using()
        self.assertIsNot(subcls, handler)
        self.assertEqual(subcls.name, handler.name)

    def test_03_hash_workflow(self, use_16_legacy=False):
        wrong_secret = 'stub'
        for secret in self.stock_passwords:
            result = self.do_encrypt(secret, use_encrypt=use_16_legacy)
            self.check_returned_native_str(result, 'hash')
            self.check_verify(secret, result)
            self.check_verify(wrong_secret, result, negate=True)
            other = self.do_genhash(secret, result)
            self.check_returned_native_str(other, 'genhash')
            if self.handler.is_disabled and self.disabled_contains_salt:
                self.assertNotEqual(other, result, 'genhash() failed to salt result hash: secret=%r hash=%r: result=%r' % (
                 secret, result, other))
            else:
                self.assertEqual(other, result, 'genhash() failed to reproduce hash: secret=%r hash=%r: result=%r' % (
                 secret, result, other))
            other = self.do_genhash(wrong_secret, result)
            self.check_returned_native_str(other, 'genhash')
            if self.handler.is_disabled and not self.disabled_contains_salt:
                self.assertEqual(other, result, 'genhash() failed to reproduce disabled-hash: secret=%r hash=%r other_secret=%r: result=%r' % (
                 secret, result, wrong_secret, other))
            else:
                self.assertNotEqual(other, result, 'genhash() duplicated hash: secret=%r hash=%r wrong_secret=%r: result=%r' % (
                 secret, result, wrong_secret, other))
            self.assertTrue(self.do_identify(result))

    def test_03_legacy_hash_workflow(self):
        self.test_03_hash_workflow(use_16_legacy=True)

    def test_04_hash_types(self):
        result = self.do_encrypt(tonn('stub'))
        self.check_returned_native_str(result, 'hash')
        self.check_verify('stub', tonn(result))
        self.check_verify(tonn('stub'), tonn(result))
        other = self.do_genhash('stub', tonn(result))
        self.check_returned_native_str(other, 'genhash')
        if self.handler.is_disabled and self.disabled_contains_salt:
            self.assertNotEqual(other, result)
        else:
            self.assertEqual(other, result)
        other = self.do_genhash(tonn('stub'), tonn(result))
        self.check_returned_native_str(other, 'genhash')
        if self.handler.is_disabled and self.disabled_contains_salt:
            self.assertNotEqual(other, result)
        else:
            self.assertEqual(other, result)
        self.assertTrue(self.do_identify(tonn(result)))

    def test_05_backends(self):
        handler = self.handler
        if not hasattr(handler, 'set_backend'):
            raise self.skipTest('handler only has one backend')
        self.addCleanup(handler.set_backend, handler.get_backend())
        for backend in handler.backends:
            self.assertIsInstance(backend, str)
            self.assertNotIn(backend, RESERVED_BACKEND_NAMES, 'invalid backend name: %r' % (backend,))
            ret = handler.has_backend(backend)
            if ret is True:
                handler.set_backend(backend)
                self.assertEqual(handler.get_backend(), backend)
            elif ret is False:
                self.assertRaises(MissingBackendError, handler.set_backend, backend)
            else:
                raise TypeError('has_backend(%r) returned invalid value: %r' % (
                 backend, ret))

    def require_salt(self):
        if 'salt' not in self.handler.setting_kwds:
            raise self.skipTest("handler doesn't have salt")

    def require_salt_info(self):
        self.require_salt()
        if not has_salt_info(self.handler):
            raise self.skipTest("handler doesn't provide salt info")

    def test_10_optional_salt_attributes(self):
        self.require_salt_info()
        AssertionError = self.failureException
        cls = self.handler
        mx_set = cls.max_salt_size is not None
        if mx_set and cls.max_salt_size < 1:
            raise AssertionError('max_salt_chars must be >= 1')
        if cls.min_salt_size < 0:
            raise AssertionError('min_salt_chars must be >= 0')
        if mx_set and cls.min_salt_size > cls.max_salt_size:
            raise AssertionError('min_salt_chars must be <= max_salt_chars')
        if cls.default_salt_size < cls.min_salt_size:
            raise AssertionError('default_salt_size must be >= min_salt_size')
        if mx_set and cls.default_salt_size > cls.max_salt_size:
            raise AssertionError('default_salt_size must be <= max_salt_size')
        if 'salt_size' not in cls.setting_kwds and (not mx_set or cls.default_salt_size < cls.max_salt_size):
            warn("%s: hash handler supports range of salt sizes, but doesn't offer 'salt_size' setting" % (
             cls.name,))
        if cls.salt_chars:
            if not cls.default_salt_chars:
                raise AssertionError('default_salt_chars must not be empty')
            for c in cls.default_salt_chars:
                if c not in cls.salt_chars:
                    raise AssertionError('default_salt_chars must be subset of salt_chars: %r not in salt_chars' % (c,))

        else:
            if not cls.default_salt_chars:
                raise AssertionError('default_salt_chars MUST be specified if salt_chars is empty')
        return

    @property
    def salt_bits(self):
        handler = self.handler
        from math import log
        return int(handler.default_salt_size * log(len(handler.default_salt_chars), 2))

    def test_11_unique_salt(self):
        self.require_salt()
        samples = max(1, 16 - self.salt_bits)

        def sampler(func):
            value1 = func()
            for _ in irange(samples):
                value2 = func()
                if value1 != value2:
                    return

            raise self.failureException('failed to find different salt after %d samples' % (
             samples,))

        sampler(self.do_genconfig)
        sampler(lambda : self.do_encrypt('stub'))

    def test_12_min_salt_size(self):
        self.require_salt_info()
        handler = self.handler
        salt_char = handler.salt_chars[0:1]
        min_size = handler.min_salt_size
        s1 = salt_char * min_size
        self.do_genconfig(salt=s1)
        self.do_encrypt('stub', salt_size=min_size)
        if min_size > 0:
            self.assertRaises(ValueError, self.do_genconfig, salt=s1[:-1])
        self.assertRaises(ValueError, self.do_encrypt, 'stub', salt_size=min_size - 1)

    def test_13_max_salt_size(self):
        self.require_salt_info()
        handler = self.handler
        max_size = handler.max_salt_size
        salt_char = handler.salt_chars[0:1]
        if max_size is None or max_size > 1048576:
            s1 = salt_char * 1024
            c1 = self.do_stub_encrypt(salt=s1)
            c2 = self.do_stub_encrypt(salt=s1 + salt_char)
            self.assertNotEqual(c1, c2)
            self.do_stub_encrypt(salt_size=1024)
        else:
            s1 = salt_char * max_size
            c1 = self.do_stub_encrypt(salt=s1)
            self.do_stub_encrypt(salt_size=max_size)
            s2 = s1 + salt_char
            self.assertRaises(ValueError, self.do_stub_encrypt, salt=s2)
            self.assertRaises(ValueError, self.do_stub_encrypt, salt_size=max_size + 1)
            if has_relaxed_setting(handler):
                with warnings.catch_warnings(record=True):
                    c2 = self.do_stub_encrypt(salt=s2, relaxed=True)
                self.assertEqual(c2, c1)
            if handler.min_salt_size < max_size:
                c3 = self.do_stub_encrypt(salt=s1[:-1])
                self.assertNotEqual(c3, c1)
        return

    fuzz_salts_need_bcrypt_repair = False

    def prepare_salt(self, salt):
        if self.fuzz_salts_need_bcrypt_repair:
            from otp.ai.passlib.utils.binary import bcrypt64
            salt = bcrypt64.repair_unused(salt)
        return salt

    def test_14_salt_chars(self):
        self.require_salt_info()
        handler = self.handler
        mx = handler.max_salt_size
        mn = handler.min_salt_size
        cs = handler.salt_chars
        raw = isinstance(cs, bytes)
        for salt in batch(cs, mx or 32):
            if len(salt) < mn:
                salt = repeat_string(salt, mn)
            salt = self.prepare_salt(salt)
            self.do_stub_encrypt(salt=salt)

        source = u('\x00\xff')
        if raw:
            source = source.encode('latin-1')
        chunk = max(mn, 1)
        for c in source:
            if c not in cs:
                self.assertRaises(ValueError, self.do_stub_encrypt, salt=c * chunk, __msg__='invalid salt char %r:' % (c,))

    @property
    def salt_type(self):
        if getattr(self.handler, '_salt_is_bytes', False):
            return bytes
        return unicode

    def test_15_salt_type(self):
        self.require_salt()
        salt_type = self.salt_type
        salt_size = getattr(self.handler, 'min_salt_size', 0) or 8

        class fake(object):
            pass

        self.assertRaises(TypeError, self.do_encrypt, 'stub', salt=fake())
        if salt_type is not unicode:
            self.assertRaises(TypeError, self.do_encrypt, 'stub', salt=u('x') * salt_size)
        if not (salt_type is bytes or PY2 and salt_type is unicode):
            self.assertRaises(TypeError, self.do_encrypt, 'stub', salt='x' * salt_size)

    def test_using_salt_size(self):
        self.require_salt_info()
        handler = self.handler
        mn = handler.min_salt_size
        mx = handler.max_salt_size
        df = handler.default_salt_size
        self.assertRaises(ValueError, handler.using, default_salt_size=-1)
        with self.assertWarningList([PasslibHashWarning]):
            temp = handler.using(default_salt_size=-1, relaxed=True)
        self.assertEqual(temp.default_salt_size, mn)
        if mx:
            self.assertRaises(ValueError, handler.using, default_salt_size=mx + 1)
            with self.assertWarningList([PasslibHashWarning]):
                temp = handler.using(default_salt_size=mx + 1, relaxed=True)
            self.assertEqual(temp.default_salt_size, mx)
        if mn != mx:
            temp = handler.using(default_salt_size=mn + 1)
            self.assertEqual(temp.default_salt_size, mn + 1)
            self.assertEqual(handler.default_salt_size, df)
            temp = handler.using(default_salt_size=mn + 2)
            self.assertEqual(temp.default_salt_size, mn + 2)
            self.assertEqual(handler.default_salt_size, df)
        if mn == mx:
            ref = mn
        else:
            ref = mn + 1
        temp = handler.using(default_salt_size=str(ref))
        self.assertEqual(temp.default_salt_size, ref)
        self.assertRaises(ValueError, handler.using, default_salt_size=str(ref) + 'xxx')
        temp = handler.using(salt_size=ref)
        self.assertEqual(temp.default_salt_size, ref)

    def require_rounds_info(self):
        if not has_rounds_info(self.handler):
            raise self.skipTest('handler lacks rounds attributes')

    def test_20_optional_rounds_attributes(self):
        self.require_rounds_info()
        cls = self.handler
        AssertionError = self.failureException
        if cls.max_rounds is None:
            raise AssertionError('max_rounds not specified')
        if cls.max_rounds < 1:
            raise AssertionError('max_rounds must be >= 1')
        if cls.min_rounds < 0:
            raise AssertionError('min_rounds must be >= 0')
        if cls.min_rounds > cls.max_rounds:
            raise AssertionError('min_rounds must be <= max_rounds')
        if cls.default_rounds is not None:
            if cls.default_rounds < cls.min_rounds:
                raise AssertionError('default_rounds must be >= min_rounds')
            if cls.default_rounds > cls.max_rounds:
                raise AssertionError('default_rounds must be <= max_rounds')
        if cls.rounds_cost not in rounds_cost_values:
            raise AssertionError('unknown rounds cost constant: %r' % (cls.rounds_cost,))
        return

    def test_21_min_rounds(self):
        self.require_rounds_info()
        handler = self.handler
        min_rounds = handler.min_rounds
        self.do_genconfig(rounds=min_rounds)
        self.do_encrypt('stub', rounds=min_rounds)
        self.assertRaises(ValueError, self.do_genconfig, rounds=min_rounds - 1)
        self.assertRaises(ValueError, self.do_encrypt, 'stub', rounds=min_rounds - 1)

    def test_21b_max_rounds(self):
        self.require_rounds_info()
        handler = self.handler
        max_rounds = handler.max_rounds
        if max_rounds is not None:
            self.assertRaises(ValueError, self.do_genconfig, rounds=max_rounds + 1)
            self.assertRaises(ValueError, self.do_encrypt, 'stub', rounds=max_rounds + 1)
        if max_rounds is None:
            self.do_stub_encrypt(rounds=2147483647L)
        else:
            self.do_stub_encrypt(rounds=max_rounds)
        return

    def _create_using_rounds_helper(self):
        self.require_rounds_info()
        handler = self.handler
        if handler.name == 'bsdi_crypt':
            orig_handler = handler
            handler = handler.using()
            handler._generate_rounds = classmethod(lambda cls: super(orig_handler, cls)._generate_rounds())
        orig_min_rounds = handler.min_rounds
        orig_max_rounds = handler.max_rounds
        orig_default_rounds = handler.default_rounds
        medium = ((orig_max_rounds or 9999) + orig_min_rounds) // 2
        if medium == orig_default_rounds:
            medium += 1
        small = (orig_min_rounds + medium) // 2
        large = ((orig_max_rounds or 9999) + medium) // 2
        if handler.name == 'bsdi_crypt':
            small |= 1
            medium |= 1
            large |= 1
            adj = 2
        else:
            adj = 1
        with self.assertWarningList([]):
            subcls = handler.using(min_desired_rounds=small, max_desired_rounds=large, default_rounds=medium)
        return (
         handler, subcls, small, medium, large, adj)

    def test_has_rounds_using_harness(self):
        self.require_rounds_info()
        handler = self.handler
        orig_min_rounds = handler.min_rounds
        orig_max_rounds = handler.max_rounds
        orig_default_rounds = handler.default_rounds
        handler, subcls, small, medium, large, adj = self._create_using_rounds_helper()
        self.assertEqual(handler.min_rounds, orig_min_rounds)
        self.assertEqual(handler.max_rounds, orig_max_rounds)
        self.assertEqual(handler.min_desired_rounds, None)
        self.assertEqual(handler.max_desired_rounds, None)
        self.assertEqual(handler.default_rounds, orig_default_rounds)
        self.assertEqual(subcls.min_rounds, orig_min_rounds)
        self.assertEqual(subcls.max_rounds, orig_max_rounds)
        self.assertEqual(subcls.default_rounds, medium)
        self.assertEqual(subcls.min_desired_rounds, small)
        self.assertEqual(subcls.max_desired_rounds, large)
        return

    def test_has_rounds_using_w_min_rounds(self):
        handler, subcls, small, medium, large, adj = self._create_using_rounds_helper()
        orig_min_rounds = handler.min_rounds
        orig_max_rounds = handler.max_rounds
        orig_default_rounds = handler.default_rounds
        if orig_min_rounds > 0:
            self.assertRaises(ValueError, handler.using, min_desired_rounds=orig_min_rounds - adj)
            with self.assertWarningList([PasslibHashWarning]):
                temp = handler.using(min_desired_rounds=orig_min_rounds - adj, relaxed=True)
            self.assertEqual(temp.min_desired_rounds, orig_min_rounds)
        if orig_max_rounds:
            self.assertRaises(ValueError, handler.using, min_desired_rounds=orig_max_rounds + adj)
            with self.assertWarningList([PasslibHashWarning]):
                temp = handler.using(min_desired_rounds=orig_max_rounds + adj, relaxed=True)
            self.assertEqual(temp.min_desired_rounds, orig_max_rounds)
        with self.assertWarningList([]):
            temp = subcls.using(min_desired_rounds=small - adj)
        self.assertEqual(temp.min_desired_rounds, small - adj)
        temp = subcls.using(min_desired_rounds=small + 2 * adj)
        self.assertEqual(temp.min_desired_rounds, small + 2 * adj)
        with self.assertWarningList([]):
            temp = subcls.using(min_desired_rounds=large + adj)
        self.assertEqual(temp.min_desired_rounds, large + adj)
        self.assertEqual(get_effective_rounds(subcls, small + adj), small + adj)
        self.assertEqual(get_effective_rounds(subcls, small), small)
        with self.assertWarningList([]):
            self.assertEqual(get_effective_rounds(subcls, small - adj), small - adj)
        temp = handler.using(min_rounds=small)
        self.assertEqual(temp.min_desired_rounds, small)
        temp = handler.using(min_rounds=str(small))
        self.assertEqual(temp.min_desired_rounds, small)
        self.assertRaises(ValueError, handler.using, min_rounds=str(small) + 'xxx')

    def test_has_rounds_replace_w_max_rounds(self):
        handler, subcls, small, medium, large, adj = self._create_using_rounds_helper()
        orig_min_rounds = handler.min_rounds
        orig_max_rounds = handler.max_rounds
        if orig_min_rounds > 0:
            self.assertRaises(ValueError, handler.using, max_desired_rounds=orig_min_rounds - adj)
            with self.assertWarningList([PasslibHashWarning]):
                temp = handler.using(max_desired_rounds=orig_min_rounds - adj, relaxed=True)
            self.assertEqual(temp.max_desired_rounds, orig_min_rounds)
        if orig_max_rounds:
            self.assertRaises(ValueError, handler.using, max_desired_rounds=orig_max_rounds + adj)
            with self.assertWarningList([PasslibHashWarning]):
                temp = handler.using(max_desired_rounds=orig_max_rounds + adj, relaxed=True)
            self.assertEqual(temp.max_desired_rounds, orig_max_rounds)
        with self.assertWarningList([PasslibConfigWarning]):
            temp = subcls.using(max_desired_rounds=small - adj)
        self.assertEqual(temp.max_desired_rounds, small)
        self.assertRaises(ValueError, subcls.using, min_desired_rounds=medium + adj, max_desired_rounds=medium - adj)
        temp = subcls.using(min_desired_rounds=large - 2 * adj)
        self.assertEqual(temp.min_desired_rounds, large - 2 * adj)
        with self.assertWarningList([]):
            temp = subcls.using(max_desired_rounds=large + adj)
        self.assertEqual(temp.max_desired_rounds, large + adj)
        self.assertEqual(get_effective_rounds(subcls, large - adj), large - adj)
        self.assertEqual(get_effective_rounds(subcls, large), large)
        with self.assertWarningList([]):
            self.assertEqual(get_effective_rounds(subcls, large + adj), large + adj)
        temp = handler.using(max_rounds=large)
        self.assertEqual(temp.max_desired_rounds, large)
        temp = handler.using(max_desired_rounds=str(large))
        self.assertEqual(temp.max_desired_rounds, large)
        self.assertRaises(ValueError, handler.using, max_desired_rounds=str(large) + 'xxx')

    def test_has_rounds_using_w_default_rounds(self):
        handler, subcls, small, medium, large, adj = self._create_using_rounds_helper()
        orig_max_rounds = handler.max_rounds
        temp = subcls.using(min_rounds=medium + adj)
        self.assertEqual(temp.default_rounds, medium + adj)
        temp = subcls.using(max_rounds=medium - adj)
        self.assertEqual(temp.default_rounds, medium - adj)
        self.assertRaises(ValueError, subcls.using, default_rounds=small - adj)
        if orig_max_rounds:
            self.assertRaises(ValueError, subcls.using, default_rounds=large + adj)
        self.assertEqual(get_effective_rounds(subcls), medium)
        self.assertEqual(get_effective_rounds(subcls, medium + adj), medium + adj)
        temp = handler.using(default_rounds=str(medium))
        self.assertEqual(temp.default_rounds, medium)
        self.assertRaises(ValueError, handler.using, default_rounds=str(medium) + 'xxx')

    def test_has_rounds_using_w_rounds(self):
        handler, subcls, small, medium, large, adj = self._create_using_rounds_helper()
        orig_max_rounds = handler.max_rounds
        temp = subcls.using(rounds=medium + adj)
        self.assertEqual(temp.min_desired_rounds, medium + adj)
        self.assertEqual(temp.default_rounds, medium + adj)
        self.assertEqual(temp.max_desired_rounds, medium + adj)
        temp = subcls.using(rounds=medium + 1, min_rounds=small + adj, default_rounds=medium, max_rounds=large - adj)
        self.assertEqual(temp.min_desired_rounds, small + adj)
        self.assertEqual(temp.default_rounds, medium)
        self.assertEqual(temp.max_desired_rounds, large - adj)

    def test_has_rounds_using_w_vary_rounds_parsing(self):
        handler, subcls, small, medium, large, adj = self._create_using_rounds_helper()

        def parse(value):
            return subcls.using(vary_rounds=value).vary_rounds

        self.assertEqual(parse(0.1), 0.1)
        self.assertEqual(parse('0.1'), 0.1)
        self.assertEqual(parse('10%'), 0.1)
        self.assertEqual(parse(1000), 1000)
        self.assertEqual(parse('1000'), 1000)
        self.assertRaises(ValueError, parse, -0.1)
        self.assertRaises(ValueError, parse, 1.1)

    def test_has_rounds_using_w_vary_rounds_generation(self):
        handler, subcls, small, medium, large, adj = self._create_using_rounds_helper()

        def get_effective_range(cls):
            seen = set(get_effective_rounds(cls) for _ in irange(1000))
            return (
             min(seen), max(seen))

        def assert_rounds_range(vary_rounds, lower, upper):
            temp = subcls.using(vary_rounds=vary_rounds)
            seen_lower, seen_upper = get_effective_range(temp)
            self.assertEqual(seen_lower, lower, 'vary_rounds had wrong lower limit:')
            self.assertEqual(seen_upper, upper, 'vary_rounds had wrong upper limit:')

        assert_rounds_range(0, medium, medium)
        assert_rounds_range('0%', medium, medium)
        assert_rounds_range(adj, medium - adj, medium + adj)
        assert_rounds_range(50, max(small, medium - 50), min(large, medium + 50))
        if handler.rounds_cost == 'log2':
            assert_rounds_range('1%', medium, medium)
            assert_rounds_range('49%', medium, medium)
            assert_rounds_range('50%', medium - adj, medium)
        else:
            lower, upper = get_effective_range(subcls.using(vary_rounds='50%'))
            self.assertGreaterEqual(lower, max(small, medium * 0.5))
            self.assertLessEqual(lower, max(small, medium * 0.8))
            self.assertGreaterEqual(upper, min(large, medium * 1.2))
            self.assertLessEqual(upper, min(large, medium * 1.5))

    def test_has_rounds_using_and_needs_update(self):
        handler, subcls, small, medium, large, adj = self._create_using_rounds_helper()
        temp = subcls.using(min_desired_rounds=small + 2, max_desired_rounds=large - 2)
        small_hash = self.do_stub_encrypt(subcls, rounds=small)
        medium_hash = self.do_stub_encrypt(subcls, rounds=medium)
        large_hash = self.do_stub_encrypt(subcls, rounds=large)
        self.assertFalse(subcls.needs_update(small_hash))
        self.assertFalse(subcls.needs_update(medium_hash))
        self.assertFalse(subcls.needs_update(large_hash))
        self.assertTrue(temp.needs_update(small_hash))
        self.assertFalse(temp.needs_update(medium_hash))
        self.assertTrue(temp.needs_update(large_hash))

    def require_many_idents(self):
        handler = self.handler
        if not isinstance(handler, type) or not issubclass(handler, uh.HasManyIdents):
            raise self.skipTest("handler doesn't derive from HasManyIdents")

    def test_30_HasManyIdents(self):
        cls = self.handler
        self.require_many_idents()
        self.assertTrue('ident' in cls.setting_kwds)
        for value in cls.ident_values:
            self.assertIsInstance(value, unicode, 'cls.ident_values must be unicode:')

        self.assertTrue(len(cls.ident_values) > 1, 'cls.ident_values must have 2+ elements:')
        self.assertIsInstance(cls.default_ident, unicode, 'cls.default_ident must be unicode:')
        self.assertTrue(cls.default_ident in cls.ident_values, 'cls.default_ident must specify member of cls.ident_values')
        if cls.ident_aliases:
            for alias, ident in iteritems(cls.ident_aliases):
                self.assertIsInstance(alias, unicode, 'cls.ident_aliases keys must be unicode:')
                self.assertIsInstance(ident, unicode, 'cls.ident_aliases values must be unicode:')
                self.assertTrue(ident in cls.ident_values, 'cls.ident_aliases must map to cls.ident_values members: %r' % (ident,))

        handler = cls
        hash = self.get_sample_hash()[1]
        kwds = handler.parsehash(hash)
        del kwds['ident']
        handler(ident=cls.default_ident, **kwds)
        self.assertRaises(TypeError, handler, **kwds)
        handler(use_defaults=True, **kwds)
        self.assertRaises(ValueError, handler, ident='xXx', **kwds)

    def test_has_many_idents_using(self):
        self.require_many_idents()
        handler = self.handler
        orig_ident = handler.default_ident
        for alt_ident in handler.ident_values:
            if alt_ident != orig_ident:
                break
        else:
            raise AssertionError('expected to find alternate ident: default=%r values=%r' % (
             orig_ident, handler.ident_values))

        def effective_ident(cls):
            cls = unwrap_handler(cls)
            return cls(use_defaults=True).ident

        subcls = handler.using()
        self.assertEqual(subcls.default_ident, orig_ident)
        subcls = handler.using(default_ident=alt_ident)
        self.assertEqual(subcls.default_ident, alt_ident)
        self.assertEqual(handler.default_ident, orig_ident)
        self.assertEqual(effective_ident(subcls), alt_ident)
        self.assertEqual(effective_ident(handler), orig_ident)
        self.assertRaises(ValueError, handler.using, default_ident='xXx')
        subcls = handler.using(ident=alt_ident)
        self.assertEqual(subcls.default_ident, alt_ident)
        self.assertEqual(handler.default_ident, orig_ident)
        self.assertRaises(TypeError, handler.using, default_ident=alt_ident, ident=alt_ident)
        if handler.ident_aliases:
            for alias, ident in handler.ident_aliases.items():
                subcls = handler.using(ident=alias)
                self.assertEqual(subcls.default_ident, ident, msg='alias %r:' % alias)

    def test_truncate_error_setting(self):
        hasher = self.handler
        if hasher.truncate_size is None:
            self.assertNotIn('truncate_error', hasher.setting_kwds)
            return
        if not hasher.truncate_error:
            self.assertFalse(hasher.truncate_verify_reject)
        if 'truncate_error' not in hasher.setting_kwds:
            self.assertTrue(hasher.truncate_error)
            return

        def parse_value(value):
            return hasher.using(truncate_error=value).truncate_error

        self.assertEqual(parse_value(None), hasher.truncate_error)
        self.assertEqual(parse_value(True), True)
        self.assertEqual(parse_value('true'), True)
        self.assertEqual(parse_value(False), False)
        self.assertEqual(parse_value('false'), False)
        self.assertRaises(ValueError, parse_value, 'xxx')
        return

    def test_secret_wo_truncate_size(self):
        hasher = self.handler
        if hasher.truncate_size is not None:
            self.assertGreaterEqual(hasher.truncate_size, 1)
            raise self.skipTest('truncate_size is set')
        secret = 'too many secrets' * 16
        alt = 'x'
        hash = self.do_encrypt(secret)
        verify_success = not hasher.is_disabled
        self.assertEqual(self.do_verify(secret, hash), verify_success, msg='verify rejected correct secret')
        alt_secret = secret[:-1] + alt
        self.assertFalse(self.do_verify(alt_secret, hash), 'full password not used in digest')
        return

    def test_secret_w_truncate_size(self):
        handler = self.handler
        truncate_size = handler.truncate_size
        if not truncate_size:
            raise self.skipTest('truncate_size not set')
        size_error_type = exc.PasswordSizeError
        if 'truncate_error' in handler.setting_kwds:
            without_error = handler.using(truncate_error=False)
            with_error = handler.using(truncate_error=True)
            size_error_type = exc.PasswordTruncateError
        else:
            if handler.truncate_error:
                without_error = None
                with_error = handler
            else:
                without_error = handler
                with_error = None
        base = 'too many secrets'
        alt = 'x'
        long_secret = repeat_string(base, truncate_size + 1)
        short_secret = long_secret[:-1]
        alt_long_secret = long_secret[:-1] + alt
        alt_short_secret = short_secret[:-1] + alt
        short_verify_success = not handler.is_disabled
        long_verify_success = short_verify_success and not handler.truncate_verify_reject
        for cand_hasher in [without_error, with_error]:
            short_hash = self.do_encrypt(short_secret, handler=cand_hasher)
            self.assertEqual(self.do_verify(short_secret, short_hash, handler=cand_hasher), short_verify_success)
            self.assertFalse(self.do_verify(alt_short_secret, short_hash, handler=with_error), 'truncate_size value is too large')
            self.assertEqual(self.do_verify(long_secret, short_hash, handler=cand_hasher), long_verify_success)

        if without_error:
            long_hash = self.do_encrypt(long_secret, handler=without_error)
            self.assertEqual(self.do_verify(long_secret, long_hash, handler=without_error), short_verify_success)
            self.assertEqual(self.do_verify(alt_long_secret, long_hash, handler=without_error), short_verify_success)
            self.assertTrue(self.do_verify(short_secret, long_hash, handler=without_error))
        if with_error:
            err = self.assertRaises(size_error_type, self.do_encrypt, long_secret, handler=with_error)
            self.assertEqual(err.max_size, truncate_size)
        return

    def test_61_secret_case_sensitive(self):
        hash_insensitive = self.secret_case_insensitive is True
        verify_insensitive = self.secret_case_insensitive in [True,
         'verify-only']
        lower = 'test'
        upper = 'TEST'
        h1 = self.do_encrypt(lower)
        if verify_insensitive and not self.handler.is_disabled:
            self.assertTrue(self.do_verify(upper, h1), 'verify() should not be case sensitive')
        else:
            self.assertFalse(self.do_verify(upper, h1), 'verify() should be case sensitive')
        h2 = self.do_encrypt(upper)
        if verify_insensitive and not self.handler.is_disabled:
            self.assertTrue(self.do_verify(lower, h2), 'verify() should not be case sensitive')
        else:
            self.assertFalse(self.do_verify(lower, h2), 'verify() should be case sensitive')
        h2 = self.do_genhash(upper, h1)
        if hash_insensitive or self.handler.is_disabled and not self.disabled_contains_salt:
            self.assertEqual(h2, h1, 'genhash() should not be case sensitive')
        else:
            self.assertNotEqual(h2, h1, 'genhash() should be case sensitive')

    def test_62_secret_border(self):
        hash = self.get_sample_hash()[1]
        self.assertRaises(TypeError, self.do_encrypt, None)
        self.assertRaises(TypeError, self.do_genhash, None, hash)
        self.assertRaises(TypeError, self.do_verify, None, hash)
        self.assertRaises(TypeError, self.do_encrypt, 1)
        self.assertRaises(TypeError, self.do_genhash, 1, hash)
        self.assertRaises(TypeError, self.do_verify, 1, hash)
        return

    def test_63_large_secret(self):
        from otp.ai.passlib.exc import PasswordSizeError
        from otp.ai.passlib.utils import MAX_PASSWORD_SIZE
        secret = '.' * (1 + MAX_PASSWORD_SIZE)
        hash = self.get_sample_hash()[1]
        err = self.assertRaises(PasswordSizeError, self.do_genhash, secret, hash)
        self.assertEqual(err.max_size, MAX_PASSWORD_SIZE)
        self.assertRaises(PasswordSizeError, self.do_encrypt, secret)
        self.assertRaises(PasswordSizeError, self.do_verify, secret, hash)

    def test_64_forbidden_chars(self):
        chars = self.forbidden_characters
        if not chars:
            raise self.skipTest('none listed')
        base = u('stub')
        if isinstance(chars, bytes):
            from otp.ai.passlib.utils.compat import iter_byte_chars
            chars = iter_byte_chars(chars)
            base = base.encode('ascii')
        for c in chars:
            self.assertRaises(ValueError, self.do_encrypt, base + c + base)

    def is_secret_8bit(self, secret):
        secret = self.populate_context(secret, {})
        return not is_ascii_safe(secret)

    def expect_os_crypt_failure(self, secret):
        if PY3 and self.backend == 'os_crypt' and isinstance(secret, bytes):
            try:
                secret.decode('utf-8')
            except UnicodeDecodeError:
                return True

        return False

    def test_70_hashes(self):
        self.assertTrue(self.known_correct_hashes or self.known_correct_configs, "test must set at least one of 'known_correct_hashes' or 'known_correct_configs'")
        saw8bit = False
        for secret, hash in self.iter_known_hashes():
            if self.is_secret_8bit(secret):
                saw8bit = True
            self.assertTrue(self.do_identify(hash), 'identify() failed to identify hash: %r' % (hash,))
            expect_os_crypt_failure = self.expect_os_crypt_failure(secret)
            try:
                self.check_verify(secret, hash, 'verify() of known hash failed: secret=%r, hash=%r' % (
                 secret, hash))
                result = self.do_genhash(secret, hash)
                self.assertIsInstance(result, str, 'genhash() failed to return native string: %r' % (result,))
                if self.handler.is_disabled and self.disabled_contains_salt:
                    continue
                self.assertEqual(result, hash, 'genhash() failed to reproduce known hash: secret=%r, hash=%r: result=%r' % (
                 secret, hash, result))
            except MissingBackendError:
                if not expect_os_crypt_failure:
                    raise

        if not saw8bit:
            warn('%s: no 8-bit secrets tested' % self.__class__)

    def test_71_alternates(self):
        if not self.known_alternate_hashes:
            raise self.skipTest('no alternate hashes provided')
        for alt, secret, hash in self.known_alternate_hashes:
            self.assertTrue(self.do_identify(hash), 'identify() failed to identify alternate hash: %r' % (
             hash,))
            self.check_verify(secret, alt, 'verify() of known alternate hash failed: secret=%r, hash=%r' % (
             secret, alt))
            result = self.do_genhash(secret, alt)
            self.assertIsInstance(result, str, 'genhash() failed to return native string: %r' % (result,))
            if self.handler.is_disabled and self.disabled_contains_salt:
                continue
            self.assertEqual(result, hash, 'genhash() failed to normalize known alternate hash: secret=%r, alt=%r, hash=%r: result=%r' % (
             secret, alt, hash, result))

    def test_72_configs(self):
        if not self.handler.setting_kwds:
            self.assertFalse(self.known_correct_configs, 'handler should not have config strings')
            raise self.skipTest('hash has no settings')
        if not self.known_correct_configs:
            raise self.skipTest('no config strings provided')
        if self.filter_config_warnings:
            warnings.filterwarnings('ignore', category=PasslibHashWarning)
        for config, secret, hash in self.known_correct_configs:
            self.assertTrue(self.do_identify(config), 'identify() failed to identify known config string: %r' % (
             config,))
            self.assertRaises(ValueError, self.do_verify, secret, config, __msg__='verify() failed to reject config string: %r' % (
             config,))
            result = self.do_genhash(secret, config)
            self.assertIsInstance(result, str, 'genhash() failed to return native string: %r' % (result,))
            self.assertEqual(result, hash, 'genhash() failed to reproduce known hash from config: secret=%r, config=%r, hash=%r: result=%r' % (
             secret, config, hash, result))

    def test_73_unidentified(self):
        if not self.known_unidentified_hashes:
            raise self.skipTest('no unidentified hashes provided')
        for hash in self.known_unidentified_hashes:
            self.assertFalse(self.do_identify(hash), 'identify() incorrectly identified known unidentifiable hash: %r' % (
             hash,))
            self.assertRaises(ValueError, self.do_verify, 'stub', hash, __msg__='verify() failed to throw error for unidentifiable hash: %r' % (
             hash,))
            self.assertRaises(ValueError, self.do_genhash, 'stub', hash, __msg__='genhash() failed to throw error for unidentifiable hash: %r' % (
             hash,))

    def test_74_malformed(self):
        if not self.known_malformed_hashes:
            raise self.skipTest('no malformed hashes provided')
        for hash in self.known_malformed_hashes:
            self.assertTrue(self.do_identify(hash), 'identify() failed to identify known malformed hash: %r' % (
             hash,))
            self.assertRaises(ValueError, self.do_verify, 'stub', hash, __msg__='verify() failed to throw error for malformed hash: %r' % (
             hash,))
            self.assertRaises(ValueError, self.do_genhash, 'stub', hash, __msg__='genhash() failed to throw error for malformed hash: %r' % (
             hash,))

    def test_75_foreign(self):
        if self.accepts_all_hashes:
            raise self.skipTest('not applicable')
        if not self.known_other_hashes:
            raise self.skipTest('no foreign hashes provided')
        for name, hash in self.known_other_hashes:
            if name == self.handler.name:
                self.assertTrue(self.do_identify(hash), 'identify() failed to identify known hash: %r' % (hash,))
                self.do_verify('stub', hash)
                result = self.do_genhash('stub', hash)
                self.assertIsInstance(result, str, 'genhash() failed to return native string: %r' % (result,))
            else:
                self.assertFalse(self.do_identify(hash), 'identify() incorrectly identified hash belonging to %s: %r' % (
                 name, hash))
                self.assertRaises(ValueError, self.do_verify, 'stub', hash, __msg__='verify() failed to throw error for hash belonging to %s: %r' % (
                 name, hash))
                self.assertRaises(ValueError, self.do_genhash, 'stub', hash, __msg__='genhash() failed to throw error for hash belonging to %s: %r' % (
                 name, hash))

    def test_76_hash_border(self):
        self.assertRaises(TypeError, self.do_identify, None)
        self.assertRaises(TypeError, self.do_verify, 'stub', None)
        self.assertRaises(TypeError, self.do_genhash, 'stub', None)
        self.assertRaises(TypeError, self.do_identify, 1)
        self.assertRaises(TypeError, self.do_verify, 'stub', 1)
        self.assertRaises(TypeError, self.do_genhash, 'stub', 1)
        for hash in [u(''), '']:
            if self.accepts_all_hashes:
                self.assertTrue(self.do_identify(hash))
                self.do_verify('stub', hash)
                result = self.do_genhash('stub', hash)
                self.check_returned_native_str(result, 'genhash')
            else:
                self.assertFalse(self.do_identify(hash), 'identify() incorrectly identified empty hash')
                self.assertRaises(ValueError, self.do_verify, 'stub', hash, __msg__='verify() failed to reject empty hash')
                self.assertRaises(ValueError, self.do_genhash, 'stub', hash, __msg__='genhash() failed to reject empty hash')

        self.do_identify('\xe2\x82\xac\xc2\xa5$')
        self.do_identify('abc\x91\x00')
        return

    def test_77_fuzz_input(self, threaded=False):
        if self.handler.is_disabled:
            raise self.skipTest('not applicable')
        from otp.ai.passlib.utils import tick
        max_time = self.max_fuzz_time
        if max_time <= 0:
            raise self.skipTest('disabled by test mode')
        verifiers = self.get_fuzz_verifiers(threaded=threaded)

        def vname(v):
            return (v.__doc__ or v.__name__).splitlines()[0]

        if threaded:
            thread_name = threading.current_thread().name
        else:
            thread_name = 'fuzz test'
        rng = self.getRandom(name=thread_name)
        generator = self.FuzzHashGenerator(self, rng)
        log.debug('%s: %s: started; max_time=%r verifiers=%d (%s)', self.descriptionPrefix, thread_name, max_time, len(verifiers), (', ').join(vname(v) for v in verifiers))
        start = tick()
        stop = start + max_time
        count = 0
        while tick() <= stop:
            opts = generator.generate()
            secret = opts['secret']
            other = opts['other']
            settings = opts['settings']
            ctx = opts['context']
            if ctx:
                settings['context'] = ctx
            hash = self.do_encrypt(secret, **settings)
            for verify in verifiers:
                name = vname(verify)
                result = verify(secret, hash, **ctx)
                if result == 'skip':
                    continue
                if not result:
                    raise self.failureException('failed to verify against %r verifier: secret=%r config=%r hash=%r' % (
                     name, secret, settings, hash))
                if rng.random() < 0.1:
                    result = verify(other, hash, **ctx)
                    if result and result != 'skip':
                        raise self.failureException('was able to verify wrong password using %s: wrong_secret=%r real_secret=%r config=%r hash=%r' % (
                         name, other, secret, settings, hash))

            count += 1

        log.debug('%s: %s: done; elapsed=%r count=%r', self.descriptionPrefix, thread_name, tick() - start, count)

    def test_78_fuzz_threading(self):
        self.require_TEST_MODE('full')
        import threading
        if self.handler.is_disabled:
            raise self.skipTest('not applicable')
        thread_count = self.fuzz_thread_count
        if thread_count < 1 or self.max_fuzz_time <= 0:
            raise self.skipTest('disabled by test mode')
        failed_lock = threading.Lock()
        failed = [0]

        def wrapper():
            try:
                self.test_77_fuzz_input(threaded=True)
            except SkipTest:
                pass
            except:
                with failed_lock:
                    failed[0] += 1
                raise

        def launch(n):
            name = 'Fuzz-Thread-%d' % (n,)
            thread = threading.Thread(target=wrapper, name=name)
            thread.setDaemon(True)
            thread.start()
            return thread

        threads = [ launch(n) for n in irange(thread_count) ]
        timeout = self.max_fuzz_time * thread_count * 4
        stalled = 0
        for thread in threads:
            thread.join(timeout)
            if not thread.is_alive():
                continue
            log.error('%s timed out after %f seconds', thread.name, timeout)
            stalled += 1

        if failed[0]:
            raise self.fail('%d/%d threads failed concurrent fuzz testing (see error log for details)' % (
             failed[0], thread_count))
        if stalled:
            raise self.fail('%d/%d threads stalled during concurrent fuzz testing (see error log for details)' % (
             stalled, thread_count))

    @property
    def max_fuzz_time(self):
        value = float(os.environ.get('PASSLIB_TEST_FUZZ_TIME') or 0)
        if value:
            return value
        if TEST_MODE(max='quick'):
            return 0
        if TEST_MODE(max='default'):
            return 1
        return 5

    @property
    def fuzz_thread_count(self):
        value = int(os.environ.get('PASSLIB_TEST_FUZZ_THREADS') or 0)
        if value:
            return value
        if TEST_MODE(max='quick'):
            return 0
        return 10

    fuzz_verifiers = ('fuzz_verifier_default', )

    def get_fuzz_verifiers(self, threaded=False):
        handler = self.handler
        verifiers = []
        for method_name in self.fuzz_verifiers:
            func = getattr(self, method_name)()
            if func is not None:
                verifiers.append(func)

        if hasattr(handler, 'backends') and TEST_MODE('full') and not threaded:

            def maker(backend):

                def func(secret, hash):
                    orig_backend = handler.get_backend()
                    try:
                        handler.set_backend(backend)
                        return handler.verify(secret, hash)
                    finally:
                        handler.set_backend(orig_backend)

                func.__name__ = 'check_' + backend + '_backend'
                func.__doc__ = backend + '-backend'
                return func

            for backend in iter_alt_backends(handler):
                verifiers.append(maker(backend))

        return verifiers

    def fuzz_verifier_default(self):

        def check_default(secret, hash, **ctx):
            return self.do_verify(secret, hash, **ctx)

        if self.backend:
            check_default.__doc__ = self.backend + '-backend'
        else:
            check_default.__doc__ = 'self'
        return check_default

    class FuzzHashGenerator(object):
        password_alphabet = u('qwertyASDF1234<>.@*#! \\u00E1\\u0259\\u0411\\u2113')
        password_encoding = 'utf-8'
        settings_map = dict(rounds='random_rounds', salt_size='random_salt_size', ident='random_ident')
        context_map = {}

        def __init__(self, test, rng):
            self.test = test
            self.handler = test.handler
            self.rng = rng

        def generate(self):

            def gendict(map):
                out = {}
                for key, meth in map.items():
                    func = getattr(self, meth)
                    value = getattr(self, meth)()
                    if value is not None:
                        out[key] = value

                return out

            secret, other = self.random_password_pair()
            return dict(secret=secret, other=other, settings=gendict(self.settings_map), context=gendict(self.context_map))

        def randintgauss(self, lower, upper, mu, sigma):
            value = self.rng.normalvariate(mu, sigma)
            return int(limit(value, lower, upper))

        def random_rounds(self):
            handler = self.handler
            if not has_rounds_info(handler):
                return None
            default = handler.default_rounds or handler.min_rounds
            lower = handler.min_rounds
            if handler.rounds_cost == 'log2':
                upper = default
            else:
                upper = min(default * 2, handler.max_rounds)
            return self.randintgauss(lower, upper, default, default * 0.5)

        def random_salt_size(self):
            handler = self.handler
            if not (has_salt_info(handler) and 'salt_size' in handler.setting_kwds):
                return None
            default = handler.default_salt_size
            lower = handler.min_salt_size
            upper = handler.max_salt_size or default * 4
            return self.randintgauss(lower, upper, default, default * 0.5)

        def random_ident(self):
            rng = self.rng
            handler = self.handler
            if 'ident' not in handler.setting_kwds or not hasattr(handler, 'ident_values'):
                return None
            if rng.random() < 0.5:
                return None
            handler = getattr(handler, 'wrapped', handler)
            return rng.choice(handler.ident_values)

        def random_password_pair(self):
            secret = self.random_password()
            while True:
                other = self.random_password()
                if self.accept_password_pair(secret, other):
                    break

            rng = self.rng
            if rng.randint(0, 1):
                secret = secret.encode(self.password_encoding)
            if rng.randint(0, 1):
                other = other.encode(self.password_encoding)
            return (secret, other)

        def random_password(self):
            rng = self.rng
            if rng.random() < 0.0001:
                return u('')
            handler = self.handler
            truncate_size = handler.truncate_error and handler.truncate_size
            max_size = truncate_size or 999999
            if max_size < 50 or rng.random() < 0.5:
                size = self.randintgauss(1, min(max_size, 50), 15, 15)
            else:
                size = self.randintgauss(50, min(max_size, 99), 70, 20)
            result = getrandstr(rng, self.password_alphabet, size)
            if truncate_size and isinstance(result, unicode):
                while len(result.encode('utf-8')) > truncate_size:
                    result = result[:-1]

            return result

        def accept_password_pair(self, secret, other):
            return secret != other

    def test_disable_and_enable(self):
        handler = self.handler
        if not handler.is_disabled:
            self.assertFalse(hasattr(handler, 'disable'))
            self.assertFalse(hasattr(handler, 'enable'))
            self.assertFalse(self.disabled_contains_salt)
            raise self.skipTest('not applicable')
        disabled_default = handler.disable()
        self.assertIsInstance(disabled_default, str, msg='disable() must return native string')
        self.assertTrue(handler.identify(disabled_default), msg="identify() didn't recognize disable() result: %r" % disabled_default)
        stub = self.getRandom().choice(self.known_other_hashes)[1]
        disabled_stub = handler.disable(stub)
        self.assertIsInstance(disabled_stub, str, msg='disable() must return native string')
        self.assertTrue(handler.identify(disabled_stub), msg="identify() didn't recognize disable() result: %r" % disabled_stub)
        self.assertRaisesRegex(ValueError, 'cannot restore original hash', handler.enable, disabled_default)
        try:
            result = handler.enable(disabled_stub)
            error = None
        except ValueError as e:
            result = None
            error = e

        if error is None:
            self.assertIsInstance(result, str, msg='enable() must return native string')
            self.assertEqual(result, stub)
        else:
            self.assertIsInstance(error, ValueError)
            self.assertRegex('cannot restore original hash', str(error))
        disabled_default2 = handler.disable()
        if self.disabled_contains_salt:
            self.assertNotEqual(disabled_default2, disabled_default)
        else:
            if error is None:
                self.assertEqual(disabled_default2, disabled_default)
        disabled_stub2 = handler.disable(stub)
        if self.disabled_contains_salt:
            self.assertNotEqual(disabled_stub2, disabled_stub)
        else:
            self.assertEqual(disabled_stub2, disabled_stub)
        disabled_other = handler.disable(stub + 'xxx')
        if self.disabled_contains_salt or error is None:
            self.assertNotEqual(disabled_other, disabled_stub)
        else:
            self.assertEqual(disabled_other, disabled_stub)
        return


class OsCryptMixin(HandlerCase):
    platform_crypt_support = []
    has_os_crypt_fallback = True
    alt_safe_crypt_handler = None
    __unittest_skip = True
    backend = 'os_crypt'
    using_patched_crypt = False

    def setUp(self):
        if not self.handler.has_backend('os_crypt'):
            self._patch_safe_crypt()
        super(OsCryptMixin, self).setUp()

    @classmethod
    def _get_safe_crypt_handler_backend(cls):
        handler = cls.alt_safe_crypt_handler
        if not handler:
            handler = unwrap_handler(cls.handler)
        handler.get_backend()
        alt_backend = get_alt_backend(handler, 'os_crypt')
        return (
         handler, alt_backend)

    def _patch_safe_crypt(self):
        handler, alt_backend = self._get_safe_crypt_handler_backend()
        if not alt_backend:
            raise AssertionError('handler has no available alternate backends!')
        alt_handler = handler.using()
        alt_handler.set_backend(alt_backend)

        def crypt_stub(secret, hash):
            hash = alt_handler.genhash(secret, hash)
            return hash

        import otp.ai.passlib.utils as mod
        self.patchAttr(mod, '_crypt', crypt_stub)
        self.using_patched_crypt = True

    @classmethod
    def _get_skip_backend_reason(cls, backend):
        reason = super(OsCryptMixin, cls)._get_skip_backend_reason(backend)
        from otp.ai.passlib.utils import has_crypt
        if reason == cls.BACKEND_NOT_AVAILABLE and has_crypt:
            if TEST_MODE('full') and cls._get_safe_crypt_handler_backend()[1]:
                return None
            return 'hash not supported by os crypt()'
        return reason

    def _use_mock_crypt(self):
        import otp.ai.passlib.utils as mod

        def mock_crypt(secret, config):
            if secret == 'test':
                return mock_crypt.__wrapped__(secret, config)
            return mock_crypt.return_value

        mock_crypt.__wrapped__ = mod._crypt
        mock_crypt.return_value = None
        self.patchAttr(mod, '_crypt', mock_crypt)
        return mock_crypt

    def test_80_faulty_crypt(self):
        hash = self.get_sample_hash()[1]
        exc_types = (AssertionError,)
        mock_crypt = self._use_mock_crypt()

        def test(value):
            mock_crypt.return_value = value
            self.assertRaises(exc_types, self.do_genhash, 'stub', hash)
            self.assertRaises(exc_types, self.do_encrypt, 'stub')
            self.assertRaises(exc_types, self.do_verify, 'stub', hash)

        test('$x' + hash[2:])
        test(hash[:-1])
        test(hash + 'x')

    def test_81_crypt_fallback(self):
        mock_crypt = self._use_mock_crypt()
        mock_crypt.return_value = None
        if self.has_os_crypt_fallback:
            h1 = self.do_encrypt('stub')
            h2 = self.do_genhash('stub', h1)
            self.assertEqual(h2, h1)
            self.assertTrue(self.do_verify('stub', h1))
        else:
            from otp.ai.passlib.exc import MissingBackendError
            hash = self.get_sample_hash()[1]
            self.assertRaises(MissingBackendError, self.do_encrypt, 'stub')
            self.assertRaises(MissingBackendError, self.do_genhash, 'stub', hash)
            self.assertRaises(MissingBackendError, self.do_verify, 'stub', hash)
        return

    def test_82_crypt_support(self):
        if hasattr(self.handler, 'orig_prefix'):
            raise self.skipTest('not applicable to wrappers')
        platform = sys.platform
        for pattern, state in self.platform_crypt_support:
            if re.match(pattern, platform):
                break
        else:
            raise self.skipTest('no data for %r platform' % platform)

        if state is None:
            raise self.skipTest('varied support on %r platform' % platform)
        else:
            if state != self.using_patched_crypt:
                return
            if state:
                self.fail('expected %r platform would have native support for %r' % (
                 platform, self.handler.name))
            else:
                self.fail('did not expect %r platform would have native support for %r' % (
                 platform, self.handler.name))
        return

    def fuzz_verifier_crypt(self):
        handler = self.handler
        if self.using_patched_crypt or hasattr(handler, 'wrapped'):
            return None
        from crypt import crypt
        encoding = self.FuzzHashGenerator.password_encoding

        def check_crypt(secret, hash):
            if not self.crypt_supports_variant(hash):
                return 'skip'
            secret = to_native_str(secret, encoding)
            return crypt(secret, hash) == hash

        return check_crypt

    def crypt_supports_variant(self, hash):
        return True


class UserHandlerMixin(HandlerCase):
    default_user = 'user'
    requires_user = True
    user_case_insensitive = False
    __unittest_skip = True

    def test_80_user(self):
        handler = self.handler
        password = 'stub'
        hash = handler.hash(password, user=self.default_user)
        if self.requires_user:
            self.assertRaises(TypeError, handler.hash, password)
            self.assertRaises(TypeError, handler.genhash, password, hash)
            self.assertRaises(TypeError, handler.verify, password, hash)
        else:
            handler.hash(password)
            handler.genhash(password, hash)
            handler.verify(password, hash)

    def test_81_user_case(self):
        lower = self.default_user.lower()
        upper = lower.upper()
        hash = self.do_encrypt('stub', context=dict(user=lower))
        if self.user_case_insensitive:
            self.assertTrue(self.do_verify('stub', hash, user=upper), 'user should not be case sensitive')
        else:
            self.assertFalse(self.do_verify('stub', hash, user=upper), 'user should be case sensitive')

    def test_82_user_salt(self):
        config = self.do_stub_encrypt()
        h1 = self.do_genhash('stub', config, user='admin')
        h2 = self.do_genhash('stub', config, user='admin')
        self.assertEqual(h2, h1)
        h3 = self.do_genhash('stub', config, user='root')
        self.assertNotEqual(h3, h1)

    def populate_context(self, secret, kwds):
        if isinstance(secret, tuple):
            secret, user = secret
        else:
            if not self.requires_user:
                return secret
            user = self.default_user
        if 'user' not in kwds:
            kwds['user'] = user
        return secret

    class FuzzHashGenerator(HandlerCase.FuzzHashGenerator):
        context_map = HandlerCase.FuzzHashGenerator.context_map.copy()
        context_map.update(user='random_user')
        user_alphabet = u('asdQWE123')

        def random_user(self):
            rng = self.rng
            if not self.test.requires_user and rng.random() < 0.1:
                return None
            return getrandstr(rng, self.user_alphabet, rng.randint(2, 10))


class EncodingHandlerMixin(HandlerCase):
    __unittest_skip = True
    stock_passwords = [
     u('test'),
     'test',
     u('\\u00AC\\u00BA')]

    class FuzzHashGenerator(HandlerCase.FuzzHashGenerator):
        password_alphabet = u('qwerty1234<>.@*#! \\u00AC')

    def populate_context(self, secret, kwds):
        if isinstance(secret, tuple):
            secret, encoding = secret
            kwds.setdefault('encoding', encoding)
        return secret


class reset_warnings(warnings.catch_warnings):

    def __init__(self, reset_filter='always', reset_registry='.*', **kwds):
        super(reset_warnings, self).__init__(**kwds)
        self._reset_filter = reset_filter
        self._reset_registry = re.compile(reset_registry) if reset_registry else None
        return

    def __enter__(self):
        ret = super(reset_warnings, self).__enter__()
        if self._reset_filter:
            warnings.resetwarnings()
            warnings.simplefilter(self._reset_filter)
        pattern = self._reset_registry
        if pattern:
            backup = self._orig_registry = {}
            for name, mod in list(sys.modules.items()):
                if mod is None or not pattern.match(name):
                    continue
                reg = getattr(mod, '__warningregistry__', None)
                if reg:
                    backup[name] = reg.copy()
                    reg.clear()

        return ret

    def __exit__(self, *exc_info):
        pattern = self._reset_registry
        if pattern:
            backup = self._orig_registry
            for name, mod in list(sys.modules.items()):
                if mod is None or not pattern.match(name):
                    continue
                reg = getattr(mod, '__warningregistry__', None)
                if reg:
                    reg.clear()
                orig = backup.get(name)
                if orig:
                    if reg is None:
                        setattr(mod, '__warningregistry__', orig)
                    else:
                        reg.update(orig)

        super(reset_warnings, self).__exit__(*exc_info)
        return