from __future__ import absolute_import, division, print_function
import logging
log = logging.getLogger(__name__)
import sys
from otp.ai.passlib import apps as _apps, exc, registry
from otp.ai.passlib.apps import django10_context, django14_context, django16_context
from otp.ai.passlib.context import CryptContext
from otp.ai.passlib.ext.django.utils import DJANGO_VERSION, MIN_DJANGO_VERSION, DjangoTranslator
from otp.ai.passlib.utils.compat import iteritems, get_method_function, u
from otp.ai.passlib.utils.decor import memoized_property
from otp.ai.passlib.tests.utils import TestCase, TEST_MODE, handler_derived_from
from otp.ai.passlib.tests.test_handlers import get_handler_case, conditionally_available_hashes
__all__ = [
 'DjangoBehaviorTest',
 'ExtensionBehaviorTest',
 '_ExtensionSupport']
has_min_django = DJANGO_VERSION >= MIN_DJANGO_VERSION
if has_min_django:
    from django.conf import settings, LazySettings
    if not isinstance(settings, LazySettings):
        raise RuntimeError('expected django.conf.settings to be LazySettings: %r' % (settings,))
    if not settings.configured:
        settings.configure()
    from django.apps import apps
    apps.populate(['django.contrib.contenttypes', 'django.contrib.auth'])
UNSET = object()

def update_settings(**kwds):
    for k, v in iteritems(kwds):
        if v is UNSET:
            if hasattr(settings, k):
                delattr(settings, k)
        else:
            setattr(settings, k, v)


if has_min_django:
    from django.contrib.auth.models import User

    class FakeUser(User):

        class Meta:
            app_label = __name__

        @memoized_property
        def saved_passwords(self):
            return []

        def pop_saved_passwords(self):
            try:
                return self.saved_passwords[:]
            finally:
                del self.saved_passwords[:]

        def save(self, update_fields=None):
            self.saved_passwords.append(self.password)


def create_mock_setter():
    state = []

    def setter(password):
        state.append(password)

    def popstate():
        try:
            return state[:]
        finally:
            del state[:]

    setter.popstate = popstate
    return setter


if DJANGO_VERSION >= (1, 10):
    stock_config = _apps.django110_context.to_dict()
    stock_rounds = 30000
else:
    if DJANGO_VERSION >= (1, 9):
        stock_config = _apps.django16_context.to_dict()
        stock_rounds = 24000
    else:
        stock_config = _apps.django16_context.to_dict()
        stock_rounds = 20000
stock_config.update(deprecated='auto', django_pbkdf2_sha1__default_rounds=stock_rounds, django_pbkdf2_sha256__default_rounds=stock_rounds)
from otp.ai.passlib.hash import django_pbkdf2_sha256
sample_hashes = dict(django_pbkdf2_sha256=(
 'not a password',
 django_pbkdf2_sha256.using(rounds=stock_config.get('django_pbkdf2_sha256__default_rounds')).hash('not a password')))

class _ExtensionSupport(object):

    @classmethod
    def _iter_patch_candidates(cls):
        from django.contrib.auth import models, hashers
        user_attrs = [
         'check_password', 'set_password']
        model_attrs = ['check_password', 'make_password']
        hasher_attrs = ['check_password', 'make_password', 'get_hasher', 'identify_hasher',
         'get_hashers']
        objs = [(models, model_attrs),
         (
          models.User, user_attrs),
         (
          hashers, hasher_attrs)]
        for obj, patched in objs:
            for attr in dir(obj):
                if attr.startswith('_'):
                    continue
                value = obj.__dict__.get(attr, UNSET)
                if value is UNSET and attr not in patched:
                    continue
                value = get_method_function(value)
                source = getattr(value, '__module__', None)
                if source:
                    yield (
                     obj, attr, source, attr in patched)

        return

    def assert_unpatched(self):
        mod = sys.modules.get('passlib.ext.django.models')
        self.assertFalse(mod and mod.adapter.patched, 'patch should not be enabled')
        for obj, attr, source, patched in self._iter_patch_candidates():
            if patched:
                self.assertTrue(source.startswith('django.contrib.auth.'), 'obj=%r attr=%r was not reverted: %r' % (
                 obj, attr, source))
            else:
                self.assertFalse(source.startswith('passlib.'), 'obj=%r attr=%r should not have been patched: %r' % (
                 obj, attr, source))

    def assert_patched(self, context=None):
        mod = sys.modules.get('passlib.ext.django.models')
        self.assertTrue(mod and mod.adapter.patched, 'patch should have been enabled')
        for obj, attr, source, patched in self._iter_patch_candidates():
            if patched:
                self.assertTrue(source == 'passlib.ext.django.utils', 'obj=%r attr=%r should have been patched: %r' % (
                 obj, attr, source))
            else:
                self.assertFalse(source.startswith('passlib.'), 'obj=%r attr=%r should not have been patched: %r' % (
                 obj, attr, source))

        if context is not None:
            context = CryptContext._norm_source(context)
            self.assertEqual(mod.password_context.to_dict(resolve=True), context.to_dict(resolve=True))
        return

    _config_keys = [
     'PASSLIB_CONFIG', 'PASSLIB_CONTEXT', 'PASSLIB_GET_CATEGORY']

    def load_extension(self, check=True, **kwds):
        self.unload_extension()
        if check:
            config = kwds.get('PASSLIB_CONFIG') or kwds.get('PASSLIB_CONTEXT')
        for key in self._config_keys:
            kwds.setdefault(key, UNSET)

        update_settings(**kwds)
        import otp.ai.passlib.ext.django.models
        if check:
            self.assert_patched(context=config)

    def unload_extension(self):
        mod = sys.modules.get('passlib.ext.django.models')
        if mod:
            mod.adapter.remove_patch()
            del sys.modules['passlib.ext.django.models']
        update_settings(**dict((key, UNSET) for key in self._config_keys))
        self.assert_unpatched()


class _ExtensionTest(TestCase, _ExtensionSupport):

    def setUp(self):
        super(_ExtensionTest, self).setUp()
        self.require_TEST_MODE('default')
        if not DJANGO_VERSION:
            raise self.skipTest('Django not installed')
        else:
            if not has_min_django:
                raise self.skipTest('Django version too old')
        self.unload_extension()
        self.addCleanup(self.unload_extension)


class DjangoBehaviorTest(_ExtensionTest):
    descriptionPrefix = 'verify django behavior'
    patched = False
    config = stock_config

    @property
    def context(self):
        return CryptContext._norm_source(self.config)

    def assert_unusable_password(self, user):
        self.assertTrue(user.password.startswith('!'))
        self.assertFalse(user.has_usable_password())
        self.assertEqual(user.pop_saved_passwords(), [])

    def assert_valid_password(self, user, hash=UNSET, saved=None):
        if hash is UNSET:
            self.assertNotEqual(user.password, '!')
            self.assertNotEqual(user.password, None)
        else:
            self.assertEqual(user.password, hash)
        self.assertTrue(user.has_usable_password(), 'hash should be usable: %r' % (user.password,))
        self.assertEqual(user.pop_saved_passwords(), [] if saved is None else [saved])
        return

    def test_config(self):
        patched, config = self.patched, self.config
        ctx = self.context
        setter = create_mock_setter()
        PASS1 = 'toomanysecrets'
        WRONG1 = 'letmein'
        from django.contrib.auth.hashers import check_password, make_password, is_password_usable, identify_hasher
        if patched:
            from otp.ai.passlib.ext.django.models import password_context
            self.assertEqual(password_context.to_dict(resolve=True), ctx.to_dict(resolve=True))
            from django.contrib.auth.models import check_password as check_password2
            self.assertEqual(check_password2, check_password)
        user = FakeUser()
        user.set_password(PASS1)
        self.assertTrue(ctx.handler().verify(PASS1, user.password))
        self.assert_valid_password(user)
        hash = make_password(PASS1)
        self.assertTrue(ctx.handler().verify(PASS1, hash))
        user = FakeUser()
        user.set_password('')
        hash = user.password
        self.assertTrue(ctx.handler().verify('', hash))
        self.assert_valid_password(user, hash)
        self.assertTrue(user.check_password(''))
        self.assert_valid_password(user, hash)
        self.assertTrue(check_password('', hash))
        user = FakeUser()
        user.set_unusable_password()
        self.assert_unusable_password(user)
        user = FakeUser()
        user.set_password(None)
        self.assert_unusable_password(user)
        self.assertFalse(user.check_password(None))
        self.assertFalse(user.check_password('None'))
        self.assertFalse(user.check_password(''))
        self.assertFalse(user.check_password(PASS1))
        self.assertFalse(user.check_password(WRONG1))
        self.assert_unusable_password(user)
        self.assertTrue(make_password(None).startswith('!'))
        self.assertFalse(check_password(PASS1, '!'))
        self.assertFalse(is_password_usable(user.password))
        self.assertRaises(ValueError, identify_hasher, user.password)
        user = FakeUser()
        user.password = None
        self.assertFalse(user.check_password(PASS1))
        self.assertFalse(user.has_usable_password())
        self.assertFalse(check_password(PASS1, None))
        self.assertRaises(TypeError, identify_hasher, None)
        for hash in ('', '$789$foo'):
            user = FakeUser()
            user.password = hash
            self.assertFalse(user.check_password(PASS1))
            self.assertEqual(user.password, hash)
            self.assertEqual(user.pop_saved_passwords(), [])
            self.assertFalse(user.has_usable_password())
            self.assertFalse(check_password(PASS1, hash))
            self.assertRaises(ValueError, identify_hasher, hash)

        for scheme in ctx.schemes():
            handler = ctx.handler(scheme)
            deprecated = ctx.handler(scheme).deprecated
            try:
                testcase = get_handler_case(scheme)
            except exc.MissingBackendError:
                continue
            else:
                if handler.is_disabled:
                    continue
                if not registry.has_backend(handler):
                    continue
                try:
                    secret, hash = sample_hashes[scheme]
                except KeyError:
                    get_sample_hash = testcase('setUp').get_sample_hash
                    while True:
                        secret, hash = get_sample_hash()
                        if secret:
                            break

                else:
                    other = 'dontletmein'
                    user = FakeUser()
                    user.password = hash
                    self.assertFalse(user.check_password(None))
                    self.assertFalse(user.check_password(other))
                    self.assert_valid_password(user, hash)
                    self.assertTrue(user.check_password(secret))
                    needs_update = deprecated
                    if needs_update:
                        self.assertNotEqual(user.password, hash)
                        self.assertFalse(handler.identify(user.password))
                        self.assertTrue(ctx.handler().verify(secret, user.password))
                        self.assert_valid_password(user, saved=user.password)
                    else:
                        self.assert_valid_password(user, hash)
                    if TEST_MODE(max='default'):
                        continue
                    alg = DjangoTranslator().passlib_to_django_name(scheme)
                    hash2 = make_password(secret, hasher=alg)
                    self.assertTrue(handler.verify(secret, hash2))
                    self.assertTrue(check_password(secret, hash, setter=setter))
                    self.assertEqual(setter.popstate(), [secret] if needs_update else [])
                    self.assertFalse(check_password(other, hash, setter=setter))
                    self.assertEqual(setter.popstate(), [])
                    self.assertTrue(is_password_usable(hash))
                    name = DjangoTranslator().django_to_passlib_name(identify_hasher(hash).algorithm)
                    self.assertEqual(name, scheme)

        return


class ExtensionBehaviorTest(DjangoBehaviorTest):
    descriptionPrefix = 'verify extension behavior'
    patched = True
    config = dict(schemes='sha256_crypt,md5_crypt,des_crypt', deprecated='des_crypt')

    def setUp(self):
        super(ExtensionBehaviorTest, self).setUp()
        self.load_extension(PASSLIB_CONFIG=self.config)


class DjangoExtensionTest(_ExtensionTest):
    descriptionPrefix = 'passlib.ext.django plugin'

    def test_00_patch_control(self):
        self.load_extension(PASSLIB_CONFIG='disabled', check=False)
        self.assert_unpatched()
        with self.assertWarningList('PASSLIB_CONFIG=None is deprecated'):
            self.load_extension(PASSLIB_CONFIG=None, check=False)
        self.assert_unpatched()
        self.load_extension(PASSLIB_CONFIG='django-1.0', check=False)
        self.assert_patched(context=django10_context)
        self.unload_extension()
        self.load_extension(PASSLIB_CONFIG='django-1.4', check=False)
        self.assert_patched(context=django14_context)
        self.unload_extension()
        return

    def test_01_overwrite_detection(self):
        config = '[passlib]\nschemes=des_crypt\n'
        self.load_extension(PASSLIB_CONFIG=config)
        import django.contrib.auth.models as models
        from otp.ai.passlib.ext.django.models import adapter

        def dummy():
            pass

        orig = models.User.set_password
        models.User.set_password = dummy
        with self.assertWarningList('another library has patched.*User\\.set_password'):
            adapter._manager.check_all()
        models.User.set_password = orig
        orig = models.check_password
        models.check_password = dummy
        with self.assertWarningList('another library has patched.*models:check_password'):
            adapter._manager.check_all()
        models.check_password = orig

    def test_02_handler_wrapper(self):
        from django.contrib.auth import hashers
        passlib_to_django = DjangoTranslator().passlib_to_django
        if DJANGO_VERSION > (1, 10):
            self.assertRaises(ValueError, passlib_to_django, 'hex_md5')
        else:
            hasher = passlib_to_django('hex_md5')
            self.assertIsInstance(hasher, hashers.UnsaltedMD5PasswordHasher)
        hasher = passlib_to_django('django_bcrypt')
        self.assertIsInstance(hasher, hashers.BCryptPasswordHasher)
        from otp.ai.passlib.hash import sha256_crypt
        hasher = passlib_to_django('sha256_crypt')
        self.assertEqual(hasher.algorithm, 'passlib_sha256_crypt')
        encoded = hasher.encode('stub')
        self.assertTrue(sha256_crypt.verify('stub', encoded))
        self.assertTrue(hasher.verify('stub', encoded))
        self.assertFalse(hasher.verify('xxxx', encoded))
        encoded = hasher.encode('stub', 'abcdabcdabcdabcd', rounds=1234)
        self.assertEqual(encoded, '$5$rounds=1234$abcdabcdabcdabcd$v2RWkZQzctPdejyRqmmTDQpZN6wTh7.RUy9zF2LftT6')
        self.assertEqual(hasher.safe_summary(encoded), {'algorithm': 'sha256_crypt', 'salt': u('abcdab**********'), 
           'rounds': 1234, 
           'hash': u('v2RWkZ*************************************')})

    def test_11_config_disabled(self):
        with self.assertWarningList('PASSLIB_CONFIG=None is deprecated'):
            self.load_extension(PASSLIB_CONFIG=None, check=False)
        self.assert_unpatched()
        self.load_extension(PASSLIB_CONFIG='disabled', check=False)
        self.assert_unpatched()
        return

    def test_12_config_presets(self):
        self.load_extension(PASSLIB_CONTEXT='django-default', check=False)
        ctx = django16_context
        self.assert_patched(ctx)
        self.load_extension(PASSLIB_CONFIG='django-1.0', check=False)
        self.assert_patched(django10_context)
        self.load_extension(PASSLIB_CONFIG='django-1.4', check=False)
        self.assert_patched(django14_context)

    def test_13_config_defaults(self):
        from otp.ai.passlib.ext.django.utils import PASSLIB_DEFAULT
        default = CryptContext.from_string(PASSLIB_DEFAULT)
        self.load_extension()
        self.assert_patched(PASSLIB_DEFAULT)
        self.load_extension(PASSLIB_CONTEXT='passlib-default', check=False)
        self.assert_patched(PASSLIB_DEFAULT)
        self.load_extension(PASSLIB_CONTEXT=PASSLIB_DEFAULT, check=False)
        self.assert_patched(PASSLIB_DEFAULT)

    def test_14_config_invalid(self):
        update_settings(PASSLIB_CONTEXT=123, PASSLIB_CONFIG=UNSET)
        self.assertRaises(TypeError, __import__, 'passlib.ext.django.models')
        self.unload_extension()
        update_settings(PASSLIB_CONFIG='missing-preset', PASSLIB_CONTEXT=UNSET)
        self.assertRaises(ValueError, __import__, 'passlib.ext.django.models')

    def test_21_category_setting(self):
        config = dict(schemes=[
         'sha256_crypt'], sha256_crypt__default_rounds=1000, staff__sha256_crypt__default_rounds=2000, superuser__sha256_crypt__default_rounds=3000)
        from otp.ai.passlib.hash import sha256_crypt

        def run(**kwds):
            user = FakeUser(**kwds)
            user.set_password('stub')
            return sha256_crypt.from_string(user.password).rounds

        self.load_extension(PASSLIB_CONFIG=config)
        self.assertEqual(run(), 1000)
        self.assertEqual(run(is_staff=True), 2000)
        self.assertEqual(run(is_superuser=True), 3000)

        def get_category(user):
            return user.first_name or None

        self.load_extension(PASSLIB_CONTEXT=config, PASSLIB_GET_CATEGORY=get_category)
        self.assertEqual(run(), 1000)
        self.assertEqual(run(first_name='other'), 1000)
        self.assertEqual(run(first_name='staff'), 2000)
        self.assertEqual(run(first_name='superuser'), 3000)

        def get_category(user):
            return

        self.load_extension(PASSLIB_CONTEXT=config, PASSLIB_GET_CATEGORY=get_category)
        self.assertEqual(run(), 1000)
        self.assertEqual(run(first_name='other'), 1000)
        self.assertEqual(run(first_name='staff', is_staff=True), 1000)
        self.assertEqual(run(first_name='superuser', is_superuser=True), 1000)
        self.assertRaises(TypeError, self.load_extension, PASSLIB_CONTEXT=config, PASSLIB_GET_CATEGORY='x')