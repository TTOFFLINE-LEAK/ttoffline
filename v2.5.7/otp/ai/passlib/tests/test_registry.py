from __future__ import with_statement
from logging import getLogger
import warnings, sys
from otp.ai.passlib import hash, registry, exc
from otp.ai.passlib.registry import register_crypt_handler, register_crypt_handler_path, get_crypt_handler, list_crypt_handlers, _unload_handler_name as unload_handler_name
import otp.ai.passlib.utils.handlers as uh
from otp.ai.passlib.tests.utils import TestCase
log = getLogger(__name__)

class dummy_0(uh.StaticHandler):
    name = 'dummy_0'


class alt_dummy_0(uh.StaticHandler):
    name = 'dummy_0'


dummy_x = 1

class RegistryTest(TestCase):
    descriptionPrefix = 'passlib.registry'

    def setUp(self):
        super(RegistryTest, self).setUp()
        locations = dict(registry._locations)
        handlers = dict(registry._handlers)

        def restore():
            registry._locations.clear()
            registry._locations.update(locations)
            registry._handlers.clear()
            registry._handlers.update(handlers)

        self.addCleanup(restore)

    def test_hash_proxy(self):
        dir(hash)
        repr(hash)
        self.assertRaises(AttributeError, getattr, hash, 'fooey')
        old = getattr(hash, '__loader__', None)
        test = object()
        hash.__loader__ = test
        self.assertIs(hash.__loader__, test)
        if old is None:
            del hash.__loader__
            self.assertFalse(hasattr(hash, '__loader__'))
        else:
            hash.__loader__ = old
            self.assertIs(hash.__loader__, old)

        class dummy_1(uh.StaticHandler):
            name = 'dummy_1'

        hash.dummy_1 = dummy_1
        self.assertIs(get_crypt_handler('dummy_1'), dummy_1)
        self.assertRaises(ValueError, setattr, hash, 'dummy_1x', dummy_1)
        return

    def test_register_crypt_handler_path(self):
        paths = registry._locations
        self.assertTrue('dummy_0' not in paths)
        self.assertFalse(hasattr(hash, 'dummy_0'))
        self.assertRaises(ValueError, register_crypt_handler_path, 'dummy_0', '.test_registry')
        self.assertRaises(ValueError, register_crypt_handler_path, 'dummy_0', __name__ + ':dummy_0:xxx')
        self.assertRaises(ValueError, register_crypt_handler_path, 'dummy_0', __name__ + ':dummy_0.xxx')
        register_crypt_handler_path('dummy_0', __name__)
        self.assertTrue('dummy_0' in list_crypt_handlers())
        self.assertTrue('dummy_0' not in list_crypt_handlers(loaded_only=True))
        self.assertIs(hash.dummy_0, dummy_0)
        self.assertTrue('dummy_0' in list_crypt_handlers(loaded_only=True))
        unload_handler_name('dummy_0')
        register_crypt_handler_path('dummy_0', __name__ + ':alt_dummy_0')
        self.assertIs(hash.dummy_0, alt_dummy_0)
        unload_handler_name('dummy_0')
        register_crypt_handler_path('dummy_x', __name__)
        self.assertRaises(TypeError, get_crypt_handler, 'dummy_x')
        register_crypt_handler_path('alt_dummy_0', __name__)
        self.assertRaises(ValueError, get_crypt_handler, 'alt_dummy_0')
        unload_handler_name('alt_dummy_0')
        sys.modules.pop('passlib.tests._test_bad_register', None)
        register_crypt_handler_path('dummy_bad', 'passlib.tests._test_bad_register')
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore', 'xxxxxxxxxx', DeprecationWarning)
            h = get_crypt_handler('dummy_bad')
        from otp.ai.passlib.tests import _test_bad_register as tbr
        self.assertIs(h, tbr.alt_dummy_bad)
        return

    def test_register_crypt_handler(self):
        self.assertRaises(TypeError, register_crypt_handler, {})
        self.assertRaises(ValueError, register_crypt_handler, type('x', (uh.StaticHandler,), dict(name=None)))
        self.assertRaises(ValueError, register_crypt_handler, type('x', (uh.StaticHandler,), dict(name='AB_CD')))
        self.assertRaises(ValueError, register_crypt_handler, type('x', (uh.StaticHandler,), dict(name='ab-cd')))
        self.assertRaises(ValueError, register_crypt_handler, type('x', (uh.StaticHandler,), dict(name='ab__cd')))
        self.assertRaises(ValueError, register_crypt_handler, type('x', (uh.StaticHandler,), dict(name='default')))

        class dummy_1(uh.StaticHandler):
            name = 'dummy_1'

        class dummy_1b(uh.StaticHandler):
            name = 'dummy_1'

        self.assertTrue('dummy_1' not in list_crypt_handlers())
        register_crypt_handler(dummy_1)
        register_crypt_handler(dummy_1)
        self.assertIs(get_crypt_handler('dummy_1'), dummy_1)
        self.assertRaises(KeyError, register_crypt_handler, dummy_1b)
        self.assertIs(get_crypt_handler('dummy_1'), dummy_1)
        register_crypt_handler(dummy_1b, force=True)
        self.assertIs(get_crypt_handler('dummy_1'), dummy_1b)
        self.assertTrue('dummy_1' in list_crypt_handlers())
        return

    def test_get_crypt_handler(self):

        class dummy_1(uh.StaticHandler):
            name = 'dummy_1'

        self.assertRaises(KeyError, get_crypt_handler, 'dummy_1')
        self.assertIs(get_crypt_handler('dummy_1', None), None)
        register_crypt_handler(dummy_1)
        self.assertIs(get_crypt_handler('dummy_1'), dummy_1)
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore', 'handler names should be lower-case, and use underscores instead of hyphens:.*', UserWarning)
            self.assertIs(get_crypt_handler('DUMMY-1'), dummy_1)
            register_crypt_handler_path('dummy_0', __name__)
            self.assertIs(get_crypt_handler('DUMMY-0'), dummy_0)
        import otp.ai.passlib.hash
        passlib.hash.__dict__['_fake'] = 'dummy'
        for name in ['_fake', '__package__']:
            self.assertRaises(KeyError, get_crypt_handler, name)
            self.assertIs(get_crypt_handler(name, None), None)

        return

    def test_list_crypt_handlers(self):
        from otp.ai.passlib.registry import list_crypt_handlers
        import otp.ai.passlib.hash
        passlib.hash.__dict__['_fake'] = 'dummy'
        for name in list_crypt_handlers():
            self.assertFalse(name.startswith('_'), '%r: ' % name)

        unload_handler_name('_fake')

    def test_handlers(self):
        from otp.ai.passlib.registry import list_crypt_handlers
        from otp.ai.passlib.tests.test_handlers import get_handler_case, conditionally_available_hashes
        for name in list_crypt_handlers():
            if name.startswith('ldap_') and name[5:] in list_crypt_handlers():
                continue
            if name in ('roundup_plaintext', ):
                continue
            try:
                self.assertTrue(get_handler_case(name))
            except exc.MissingBackendError:
                if name in conditionally_available_hashes:
                    continue
                raise